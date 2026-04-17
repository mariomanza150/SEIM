from typing import Dict, Any, Optional, List
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from accounts.models import User
from notifications.services import NotificationService

from exchange.eligibility_rules import checks_passed_labels, evaluate_eligibility

from .models import (
    Application,
    ApplicationStatus,
    Comment,
    Program,
    SEAT_HOLDING_APPLICATION_STATUS_NAMES,
    TimelineEvent,
)


class ApplicationService:
    """
    Service for application workflow: submission, withdrawal, status transitions, comments, timeline events.
    """

    @staticmethod
    def check_eligibility(
        student: User,
        program: Program,
        application: Optional[Application] = None,
    ) -> Dict[str, Any]:
        """
        Comprehensive eligibility check for student applying to program.

        Delegates to :func:`exchange.eligibility_rules.evaluate_eligibility` (structured rules;
        ``rules`` + ``schema_version`` in the success payload for API clients
        (``schema_version`` increments when rule set or order changes).

        When ``application`` is provided (same program/student), required document types
        are evaluated against that application's uploads (submit parity).

        Raises:
            ValueError: With detailed message if any requirement is not met

        Returns:
            dict: Detailed eligibility result with status, ``rules``, and legacy ``checks_passed``.
        """
        ev = evaluate_eligibility(student, program, application=application)
        if not ev.eligible:
            if len(ev.failures) == 1 and ev.failures[0] == "Student profile is missing.":
                raise ValueError("Student profile is missing.")
            raise ValueError("Eligibility requirements not met:\n- " + "\n- ".join(ev.failures))
        return {
            "eligible": True,
            "message": "All eligibility requirements met",
            "checks_passed": checks_passed_labels(program),
            "rules": ev.rules_as_dicts(),
            "schema_version": 4,
        }

    @staticmethod
    def check_application_window(program: Program, on_date=None) -> Dict[str, Any]:
        """
        Validate whether a program is currently accepting new applications.

        Raises:
            ValueError: If the application window is not currently open.
        """
        window_status = program.get_application_window_status(on_date=on_date)
        if not window_status["is_open"]:
            raise ValueError(window_status["message"])
        return window_status

    @staticmethod
    def can_submit_application(
        user: User,
        program: Program,
        exclude_application: Optional[Application] = None,
    ) -> bool:
        """Check if user has another active application for this program.

        When updating an existing application via the API, pass ``exclude_application``
        so the row being edited does not count as a duplicate of itself.
        """
        qs = Application.objects.filter(
            student=user,
            program=program,
            withdrawn=False,
            status__name__in=["submitted", "under_review", "waitlist"],
        )
        if exclude_application is not None:
            qs = qs.exclude(pk=exclude_application.pk)
        return not qs.exists()

    @staticmethod
    def get_default_coordinator(program: Program) -> Optional[User]:
        """Return the sole program coordinator when exactly one is assigned."""
        coordinator_ids = list(program.coordinators.values_list("id", flat=True)[:2])
        if len(coordinator_ids) != 1:
            return None
        return program.coordinators.get(id=coordinator_ids[0])

    @staticmethod
    def _viewer_roles_for_user(user: Optional[User]) -> List[str]:
        """Role names for dynamic-form visibility (``staff_only`` / ``roles_any``)."""
        if not user or not getattr(user, "is_authenticated", False):
            return []
        names = list(user.get_all_roles())
        if getattr(user, "is_superuser", False) and "admin" not in names:
            names = [*names, "admin"]
        return names

    @staticmethod
    def _visibility_context_for_application(
        application: Application, user: Optional[User] = None
    ) -> dict:
        """Context for ``visible_when`` / ``x-seim-visibleWhen`` (program, coordinator, viewer roles)."""
        return {
            "program_id": application.program_id,
            "has_assigned_coordinator": bool(application.assigned_coordinator_id),
            "viewer_roles": ApplicationService._viewer_roles_for_user(user),
        }

    @staticmethod
    @transaction.atomic
    def submit_application(application: Application, user: User) -> Application:
        """Submit an application (draft -> submitted) with eligibility and single active check."""
        if application.status.name != "draft":
            raise ValueError("Only draft applications can be submitted.")
        ApplicationService.check_eligibility(
            application.student,
            application.program,
            application=application,
        )
        if not ApplicationService.can_submit_application(user, application.program):
            raise ValueError("You already have an active application for this program.")

        program = Program.objects.select_for_update().get(pk=application.program_id)
        seat_count = Application.objects.filter(
            program_id=program.pk,
            withdrawn=False,
            status__name__in=SEAT_HOLDING_APPLICATION_STATUS_NAMES,
        ).count()
        capacity_full = (
            program.enrollment_capacity is not None
            and seat_count >= program.enrollment_capacity
        )

        if capacity_full:
            if program.waitlist_when_full:
                # Workflow-aware transition: prefer workflow action if configured.
                if getattr(program, "workflow_version_id", None):
                    from workflows.runtime import WorkflowRuntimeService

                    WorkflowRuntimeService.trigger_action(application, "waitlist", user=user)
                else:
                    application.status = ApplicationStatus.objects.get(name="waitlist")
                application.submitted_at = timezone.now()
                application.save()
                TimelineEvent.objects.create(
                    application=application,
                    event_type="waitlisted",
                    description=(
                        "Application received; the program is at capacity — placed on the waitlist."
                    ),
                    created_by=user,
                )
                NotificationService.broadcast_application_sync(
                    str(application.id), "application_waitlisted"
                )
                NotificationService.send_notification(
                    user,
                    "Application received (waitlist)",
                    (
                        f"Your application for {program.name} was received. The program is at "
                        "capacity; you are on the waitlist and will be notified if a seat opens."
                    ),
                    notification_type="both",
                    action_url=f"/applications/{application.id}/",
                    action_text="View Application",
                    settings_category="applications",
                    transactional_route_key="application_waitlist_received",
                )
                return application
            raise ValueError("This program has reached enrollment capacity.")

        # Workflow-aware transition: prefer workflow action if configured.
        if getattr(program, "workflow_version_id", None):
            from workflows.runtime import WorkflowRuntimeService

            WorkflowRuntimeService.trigger_action(application, "submitted", user=user)
        else:
            application.status = ApplicationStatus.objects.get(name="submitted")
        application.submitted_at = timezone.now()
        application.save()
        TimelineEvent.objects.create(
            application=application,
            event_type="submitted",
            description="Application submitted.",
            created_by=user,
        )

        NotificationService.broadcast_application_sync(str(application.id), "application_submitted")

        # Notify student that submission was successful with link to application
        NotificationService.send_notification(
            user,
            "Application Submitted",
            f"Your application for {application.program.name} has been submitted successfully.",
            notification_type="both",
            action_url=f"/applications/{application.id}/",
            action_text="View Application",
            settings_category="applications",
            transactional_route_key="application_submitted",
        )

        return application

    @staticmethod
    def can_transition_status(user: User, application: Application, new_status: str) -> bool:
        """
        Check if user can transition application to new status.
        
        Rules:
        - Students can only transition draft -> submitted
        - Students cannot modify submitted/reviewed applications  
        - Coordinators/admins can perform any transition
        """
        # Coordinators and admins can perform any transition
        if user.has_role("coordinator") or user.has_role("admin"):
            return True
        
        # Students can only transition draft -> submitted
        if user.has_role("student"):
            if application.status.name == "draft" and new_status == "submitted":
                return True
            return False
        
        # Default: deny
        return False

    @staticmethod
    @transaction.atomic
    def transition_status(application: Application, user: User, new_status_name: str) -> Application:
        """Transition application status with role validation."""
        from django.utils import timezone
        
        # Workflow-aware: if the program has a workflow, route through runtime actions.
        if getattr(application.program, "workflow_version_id", None):
            from workflows.runtime import WorkflowRuntimeService

            WorkflowRuntimeService.trigger_action(application, new_status_name, user=user)
            application.refresh_from_db()
            return application

        # Check if status exists first (will raise DoesNotExist if not)
        new_status = ApplicationStatus.objects.get(name=new_status_name)
        
        # Then check permissions
        if not ApplicationService.can_transition_status(
            user, application, new_status_name
        ):
            raise ValueError("You do not have permission to perform this transition.")

        if new_status_name == "submitted":
            ApplicationService.check_eligibility(
                application.student,
                application.program,
                application=application,
            )

        application.status = new_status
        
        # Set submitted_at timestamp when transitioning to submitted status
        if new_status_name == "submitted" and application.submitted_at is None:
            application.submitted_at = timezone.now()
        
        application.save()
        TimelineEvent.objects.create(
            application=application,
            event_type=f"status_{new_status_name}",
            description=f"Status changed to {new_status_name}.",
            created_by=user,
        )

        NotificationService.broadcast_application_sync(str(application.id), "application_status_changed")

        # Notify student about status change with link to application
        NotificationService.send_notification(
            application.student,
            "Application Status Update",
            f"Your application for {application.program.name} status has changed to {new_status_name}.",
            notification_type="both",
            action_url=f"/applications/{application.id}/",
            action_text="View Application",
            settings_category="applications",
            transactional_route_key="application_status_update",
        )

        return application

    @staticmethod
    def can_withdraw_application(application: Application):
        """Check if an application can be withdrawn."""
        # Can withdraw if not already withdrawn and not in final states
        return (not application.withdrawn and 
                application.status.name not in ["approved", "rejected", "completed", "cancelled"])

    @staticmethod
    @transaction.atomic
    def withdraw_application(application: Application, user: User) -> Application:
        """Withdraw an application (if not in final status)."""
        if not ApplicationService.can_withdraw_application(application):
            raise ValueError("Application cannot be withdrawn in its current status.")
        application.withdrawn = True
        # Set withdrawn status if it exists, otherwise keep current status
        try:
            application.status = ApplicationStatus.objects.get(name="withdrawn")
        except ApplicationStatus.DoesNotExist:
            pass  # Keep current status if withdrawn status doesn't exist
        application.save()
        TimelineEvent.objects.create(
            application=application,
            event_type="withdrawn",
            description="Application withdrawn.",
            created_by=user,
        )
        NotificationService.broadcast_application_sync(str(application.id), "application_withdrawn")
        return application

    @staticmethod
    def get_status_history(application: Application):
        """Get timeline events for an application (status history)."""
        return TimelineEvent.objects.filter(application=application).order_by('created_at')

    @staticmethod
    @transaction.atomic
    def add_comment(application: Application, author, text, is_private=False):
        """Add a comment to an application."""
        comment = Comment.objects.create(
            application=application, author=author, text=text, is_private=is_private
        )
        TimelineEvent.objects.create(
            application=application,
            event_type="comment",
            description="Comment added.",
            created_by=author,
        )
        NotificationService.broadcast_application_sync(str(application.id), "comment_added")
        return comment

    @staticmethod
    @transaction.atomic
    def process_dynamic_form_submission(application: Application, form_data: dict, user):
        """
        Process and save dynamic form submission for an application.

        Args:
            application: Application instance
            form_data: Dict with keys ``df_*`` and optional ``dynamic_form_current_step``
            user: User submitting the form

        Returns:
            FormSubmission instance if form was submitted, None otherwise

        Raises:
            ValidationError: If form validation fails
        """
        if not application.program.application_form:
            return None

        form_type = application.program.application_form

        responses_patch = {}
        current_step_key = form_data.get("dynamic_form_current_step")

        for key, value in form_data.items():
            if key.startswith("df_"):
                responses_patch[key[3:]] = value

        if not responses_patch:
            return None

        try:
            from application_forms.models import FormSubmission
            from application_forms.services import FormSubmissionService

            existing_submission = FormSubmission.objects.filter(
                application=application,
                form_type=form_type,
            ).first()

            merged = {
                **(existing_submission.responses if existing_submission else {}),
                **responses_patch,
            }

            vctx = ApplicationService._visibility_context_for_application(application, user)

            if form_type.is_multi_step():
                if current_step_key is None or str(current_step_key).strip() == "":
                    raise ValidationError(
                        "dynamic_form_current_step is required when saving a multi-step application form."
                    )
                from application_forms.visibility import iter_visible_steps_from_form_type

                visible_steps = list(iter_visible_steps_from_form_type(form_type, merged, vctx))
                if not visible_steps:
                    raise ValidationError(
                        "No form steps apply to the current answers; check form configuration."
                    )
                step_keys = [s["key"] for s in visible_steps]
                sk = str(current_step_key)
                if sk not in step_keys:
                    raise ValidationError(
                        f"This form step is not available for your current answers: {sk}"
                    )
                step_field_names = form_type.get_step_field_names(sk)
                if step_field_names is None:
                    raise ValidationError(f"Unknown form step: {current_step_key}")
                FormSubmissionService.validate_step_patch(
                    form_type,
                    responses_patch,
                    step_field_names,
                    merged_responses=merged,
                    visibility_context=vctx,
                )
                is_first_multistep_save = existing_submission is None
                try:
                    idx = step_keys.index(sk)
                except ValueError:
                    application.dynamic_form_current_step = sk
                else:
                    if is_first_multistep_save:
                        # Keep user on the same step until an application exists; step-level
                        # document rules run on subsequent saves before advancing.
                        application.dynamic_form_current_step = step_keys[idx]
                    else:
                        from documents.services import DocumentService

                        DocumentService.ensure_step_documents_approved(
                            application, form_type, sk
                        )
                        if idx + 1 < len(step_keys):
                            application.dynamic_form_current_step = step_keys[idx + 1]
                        else:
                            application.dynamic_form_current_step = step_keys[idx]
                application.save(update_fields=["dynamic_form_current_step", "updated_at"])
            else:
                FormSubmissionService.validate_responses(
                    form_type, merged, visibility_context=vctx
                )

            is_update = existing_submission is not None
            if existing_submission:
                existing_submission.responses = merged
                existing_submission.save()
                submission = existing_submission
            else:
                submission = FormSubmissionService.create_submission(
                    form_type=form_type,
                    submitted_by=user,
                    responses=merged,
                    program=application.program,
                    application=application,
                )

            should_log_timeline = (not form_type.is_multi_step()) or (not is_update)
            if should_log_timeline:
                TimelineEvent.objects.create(
                    application=application,
                    event_type="form_submitted",
                    description=f"Dynamic form '{form_type.name}' submitted.",
                    created_by=user,
                )

            return submission

        except ImportError:
            return None
        except ValidationError as e:
            raise ValidationError(f"Dynamic form validation failed: {str(e)}")

    @staticmethod
    def get_dynamic_form_submission(application: Application):
        """
        Get the dynamic form submission for an application.

        Args:
            application: Application instance

        Returns:
            FormSubmission instance if exists, None otherwise
        """
        if not application.program.application_form:
            return None

        try:
            from application_forms.models import FormSubmission

            return FormSubmission.objects.filter(
                application=application,
                form_type=application.program.application_form
            ).first()
        except ImportError:
            return None
