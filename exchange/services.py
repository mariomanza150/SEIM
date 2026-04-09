from typing import Dict, Any, Optional, List
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from accounts.models import User
from notifications.services import NotificationService

from .models import Application, ApplicationStatus, Comment, TimelineEvent, Program


class ApplicationService:
    """
    Service for application workflow: submission, withdrawal, status transitions, comments, timeline events.
    """

    @staticmethod
    def check_eligibility(student: User, program: Program) -> Dict[str, Any]:
        """
        Comprehensive eligibility check for student applying to program.

        Checks:
        - GPA requirement (with grade translation support)
        - Language requirement
        - Language proficiency level (CEFR scale)
        - Age requirements (min/max)

        Raises:
            ValueError: With detailed message if any requirement is not met

        Returns:
            dict: Detailed eligibility result with status and messages
        """
        profile = getattr(student, "profile", None)
        if not profile:
            raise ValueError("Student profile is missing.")

        eligibility_issues = []

        # Check GPA requirement with grade translation support
        if hasattr(program, "min_gpa") and program.min_gpa and profile.gpa is not None:
            # If student has a grade scale, use translation
            if profile.grade_scale:
                # Get the GPA equivalent of student's grade
                student_gpa_equivalent = profile.get_gpa_equivalent()

                # Compare using GPA equivalents (normalized to 4.0 scale)
                if student_gpa_equivalent < program.min_gpa:
                    eligibility_issues.append(
                        f"GPA below program minimum. Your GPA equivalent: {student_gpa_equivalent:.2f}, "
                        f"Required: {program.min_gpa:.2f}"
                    )
            else:
                # No grade scale specified, use direct comparison (legacy behavior)
                if profile.gpa < program.min_gpa:
                    eligibility_issues.append(
                        f"GPA below program minimum. Your GPA: {profile.gpa:.2f}, "
                        f"Required: {program.min_gpa:.2f}"
                    )

        # Check language requirement
        if (
            hasattr(program, "required_language")
            and program.required_language
            and profile.language != program.required_language
        ):
            eligibility_issues.append(
                f"Language requirement not met. Required: {program.required_language}, "
                f"Your language: {profile.language or 'Not specified'}"
            )

        # Check language proficiency level (CEFR scale)
        if hasattr(program, "min_language_level") and program.min_language_level:
            cefr_levels = {'A1': 1, 'A2': 2, 'B1': 3, 'B2': 4, 'C1': 5, 'C2': 6}

            if hasattr(profile, "language_level") and profile.language_level:
                student_level = cefr_levels.get(profile.language_level, 0)
                required_level = cefr_levels.get(program.min_language_level, 0)

                if student_level < required_level:
                    eligibility_issues.append(
                        f"Language proficiency below requirement. "
                        f"Required: {program.min_language_level}, "
                        f"Your level: {profile.language_level}"
                    )
            else:
                eligibility_issues.append(
                    f"Language proficiency not specified. Required: {program.min_language_level}"
                )

        # Check age requirements
        if hasattr(profile, "date_of_birth") and profile.date_of_birth:
            from datetime import date
            today = date.today()
            age = today.year - profile.date_of_birth.year - (
                (today.month, today.day) < (profile.date_of_birth.month, profile.date_of_birth.day)
            )

            if hasattr(program, "min_age") and program.min_age and age < program.min_age:
                eligibility_issues.append(
                    f"Age below minimum requirement. Your age: {age}, Required: {program.min_age}+"
                )

            if hasattr(program, "max_age") and program.max_age and age > program.max_age:
                eligibility_issues.append(
                    f"Age above maximum requirement. Your age: {age}, Maximum: {program.max_age}"
                )

        # If there are any eligibility issues, raise error with all details
        if eligibility_issues:
            raise ValueError("Eligibility requirements not met:\n- " + "\n- ".join(eligibility_issues))

        return {
            "eligible": True,
            "message": "All eligibility requirements met",
            "checks_passed": [
                "GPA requirement" if program.min_gpa else None,
                "Language requirement" if program.required_language else None,
                "Language proficiency" if program.min_language_level else None,
                "Age requirements" if (program.min_age or program.max_age) else None,
            ]
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
    def can_submit_application(user: User, program: Program) -> bool:
        """Check if user has another active application for this program."""
        return not Application.objects.filter(
            student=user,
            program=program,
            withdrawn=False,
            status__name__in=["submitted", "under_review"],
        ).exists()

    @staticmethod
    def get_default_coordinator(program: Program) -> Optional[User]:
        """Return the sole program coordinator when exactly one is assigned."""
        coordinator_ids = list(program.coordinators.values_list("id", flat=True)[:2])
        if len(coordinator_ids) != 1:
            return None
        return program.coordinators.get(id=coordinator_ids[0])

    @staticmethod
    def _ensure_application_form_complete(application: Application) -> None:
        """Raise ValueError if the program's dynamic form exists but responses are incomplete."""
        ft = application.program.application_form
        if not ft:
            return
        sub = ApplicationService.get_dynamic_form_submission(application)
        if not sub:
            raise ValueError("Complete the program application form before submitting.")
        from application_forms.services import FormSubmissionService

        try:
            FormSubmissionService.validate_responses(ft, sub.responses)
        except ValidationError as exc:
            msgs = list(exc.messages) if hasattr(exc, "messages") else [str(exc)]
            raise ValueError("; ".join(msgs)) from exc

    @staticmethod
    def _ensure_submission_requirements(application: Application) -> None:
        """Dynamic form completeness and required documents (if configured)."""
        ApplicationService._ensure_application_form_complete(application)
        from documents.services import DocumentService

        DocumentService.ensure_required_documents_approved(application)

    @staticmethod
    @transaction.atomic
    def submit_application(application: Application, user: User) -> Application:
        """Submit an application (draft -> submitted) with eligibility and single active check."""
        if application.status.name != "draft":
            raise ValueError("Only draft applications can be submitted.")
        ApplicationService.check_eligibility(user, application.program)
        if not ApplicationService.can_submit_application(user, application.program):
            raise ValueError("You already have an active application for this program.")
        ApplicationService._ensure_submission_requirements(application)
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
            action_text="View Application"
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
        
        # Check if status exists first (will raise DoesNotExist if not)
        new_status = ApplicationStatus.objects.get(name=new_status_name)
        
        # Then check permissions
        if not ApplicationService.can_transition_status(
            user, application, new_status_name
        ):
            raise ValueError("You do not have permission to perform this transition.")

        if new_status_name == "submitted":
            ApplicationService._ensure_submission_requirements(application)

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
            action_text="View Application"
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

            if form_type.is_multi_step():
                if current_step_key is None or str(current_step_key).strip() == "":
                    raise ValidationError(
                        "dynamic_form_current_step is required when saving a multi-step application form."
                    )
                step_field_names = form_type.get_step_field_names(str(current_step_key))
                if step_field_names is None:
                    raise ValidationError(f"Unknown form step: {current_step_key}")
                FormSubmissionService.validate_step_patch(
                    form_type, responses_patch, step_field_names
                )
                step_keys = [s["key"] for s in form_type.get_multi_step_layout()]
                try:
                    idx = step_keys.index(str(current_step_key))
                except ValueError:
                    application.dynamic_form_current_step = str(current_step_key)
                else:
                    if idx + 1 < len(step_keys):
                        application.dynamic_form_current_step = step_keys[idx + 1]
                    else:
                        application.dynamic_form_current_step = step_keys[idx]
                application.save(update_fields=["dynamic_form_current_step", "updated_at"])
            else:
                FormSubmissionService.validate_responses(form_type, merged)

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
