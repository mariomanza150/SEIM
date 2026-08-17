from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import Profile, Role, UserSettings
from accounts.profile_seed import complete_apply_profile
from analytics.models import DashboardConfig, Metric, Report
from application_forms.models import FormStepTemplate, FormSubmission, FormType
from documents.models import (
    Document,
    DocumentComment,
    DocumentResubmissionRequest,
    DocumentType,
    DocumentValidation,
    ExchangeAgreementDocument,
)
from exchange.demo_seed import (
    DEMO_AGREEMENT_SPECS,
    DEMO_APPLICATION_SPECS,
    DEMO_BPMN_XML,
    DEMO_CLOSED_WINDOW_PROGRAM,
    DEMO_ELIGIBILITY_RULESET_NAME,
    DEMO_FORM_NAME,
    DEMO_FORM_STEP_TEMPLATE_SLUG,
    DEMO_HOST_SPECS,
    DEMO_LIFECYCLE_PROGRAM,
    DEMO_PARTNER_AGREEMENT_REF,
    DEMO_PROGRAM_SPECS,
    DEMO_RESUBMIT_PROGRAM,
    DEMO_SUBMIT_GATE_PROGRAM,
    DEMO_USER_SPECS,
    DEMO_WORKFLOW_NAME,
    DEMO_WORKFLOW_SLUG,
)
from exchange.eligibility_rules import ELIGIBILITY_SCHEMA_VERSION
from exchange.models import (
    AgreementComment,
    Application,
    ApplicationStatus,
    ApplicationSubjectSelection,
    Comment,
    EligibilityRuleSet,
    ExchangeAgreement,
    HostAcademicProgram,
    HostInstitution,
    HostSchool,
    HostSubject,
    PartnerContact,
    Program,
    ProgramDocumentRequirement,
    SavedSearch,
    ScholarshipAward,
    ScholarshipDisbursement,
    TimelineEvent,
)
from grades.models import GradeScale, GradeTranslation, GradeValue
from notifications.models import (
    Notification,
    NotificationPreference,
    NotificationRoutingOverride,
    NotificationType,
    Reminder,
)
from workflows.models import (
    WorkflowDefinition,
    WorkflowEvent,
    WorkflowInstance,
    WorkflowVersion,
)

User = get_user_model()


class Command(BaseCommand):
    help = "Seed a deterministic, demo-ready dataset covering SEIM domain surfaces."

    def handle(self, *args, **options):
        self.stdout.write("Seeding demo-ready data for SEIM...")

        call_command("create_initial_data", verbosity=0)

        try:
            call_command("seed_grade_scales", verbosity=0)
        except Exception as exc:  # pragma: no cover - best effort
            self.stdout.write(self.style.WARNING(f"  Skipped grade scale seed: {exc}"))

        with transaction.atomic():
            users = self._create_users()
            form_type = self._create_forms(users)
            workflow_version = self._create_workflow(users)
            ruleset = self._create_eligibility_ruleset()
            programs = self._create_programs(
                users, form_type, workflow_version, ruleset
            )
            self._create_host_destinations(programs)
            self._create_exchange_agreements(programs)
            self._create_partner_portal(users)
            applications = self._create_applications(users, programs)
            self._create_subject_selections(applications)
            self._create_documents(applications, users)
            self._create_comments_and_events(applications, users)
            self._create_notifications(applications, users)
            self._create_scholarships(applications, users)
            self._create_form_submissions(applications, form_type)
            self._create_workflow_instances(applications, workflow_version, users)
            self._create_saved_searches(users)
            self._create_reminders(users, programs)
            self._create_notification_routing()
            self._create_analytics(users)
            self._create_grade_translations(users)

        try:
            from exchange.views import _invalidate_program_api_caches

            _invalidate_program_api_caches()
        except Exception as exc:  # pragma: no cover - cache backend optional
            self.stdout.write(self.style.WARNING(f"  Program cache bust skipped: {exc}"))

        self.stdout.write(self.style.SUCCESS("Demo-ready seed completed."))
        self.stdout.write("Manual QA fixtures:")
        self.stdout.write(f"  Closed window: {DEMO_CLOSED_WINDOW_PROGRAM}")
        self.stdout.write(f"  Submit gate draft: {DEMO_SUBMIT_GATE_PROGRAM}")
        self.stdout.write(f"  Open resubmit: {DEMO_RESUBMIT_PROGRAM}")
        self.stdout.write(f"  Section 8 reserved (no student app): {DEMO_LIFECYCLE_PROGRAM}")
        self.stdout.write("Demo credentials:")
        self.stdout.write("  Admin: admin@test.com / admin123")
        self.stdout.write("  Coordinator: coordinator@test.com / coordinator123")
        self.stdout.write("  Student: student@test.com / student123")
        self.stdout.write("  Partner: partner@test.com / partner123")

    def _create_users(self):
        users = {}

        for spec in DEMO_USER_SPECS:
            role = Role.objects.get(name=spec["role"])
            user = (
                User.objects.filter(email=spec["email"]).first()
                or User.objects.filter(username=spec["username"]).first()
            )
            created = user is None
            if created:
                user = User(username=spec["username"])
            user.username = spec["username"]
            user.email = spec["email"]
            user.first_name = spec["first_name"]
            user.last_name = spec["last_name"]
            user.is_email_verified = True
            user.is_active = True
            user.is_staff = spec["is_staff"]
            user.is_superuser = spec["is_superuser"]
            user.set_password(spec["password"])
            user.save()
            user.roles.set([role])
            UserSettings.objects.get_or_create(user=user)

            profile_data = spec.get("profile", {})
            if profile_data:
                profile, _ = Profile.objects.get_or_create(user=user)
                for field_name, value in profile_data.items():
                    setattr(profile, field_name, value)
                profile.save()
            if spec["role"] == "student":
                complete_apply_profile(user)

            for ntype in NotificationType.objects.all():
                NotificationPreference.objects.get_or_create(
                    user=user, type=ntype, defaults={"enabled": True}
                )

            action = "Created" if created else "Updated"
            self.stdout.write(f"  {action} user: {user.email}")
            users[spec["username"]] = user

        return users

    def _create_forms(self, users):
        admin = users["admin"]
        form_type, created = FormType.objects.update_or_create(
            name=DEMO_FORM_NAME,
            defaults={
                "form_type": "application",
                "description": "Demo multi-step application form for Barcelona.",
                "created_by": admin,
                "is_active": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "motivation": {"type": "string", "title": "Motivation"},
                        "emergency_contact": {
                            "type": "string",
                            "title": "Emergency contact",
                        },
                    },
                    "required": ["motivation"],
                },
                "ui_schema": {
                    "motivation": {"ui:widget": "textarea"},
                },
                "step_definitions": [
                    {
                        "key": "motivation",
                        "title": "Motivation",
                        "field_names": ["motivation"],
                    },
                    {
                        "key": "contacts",
                        "title": "Contacts",
                        "field_names": ["emergency_contact"],
                    },
                ],
            },
        )
        FormStepTemplate.objects.update_or_create(
            slug=DEMO_FORM_STEP_TEMPLATE_SLUG,
            defaults={
                "name": "Demo motivation step",
                "description": "Reusable motivation fields for demo forms.",
                "step_title": "Motivation",
                "default_step_key": "motivation",
                "schema_properties": {
                    "motivation": {"type": "string", "title": "Motivation"}
                },
                "required_field_names": ["motivation"],
            },
        )
        action = "Created" if created else "Updated"
        self.stdout.write(f"  {action} application form: {form_type.name}")
        return form_type

    def _create_workflow(self, users):
        definition, _ = WorkflowDefinition.objects.update_or_create(
            slug=DEMO_WORKFLOW_SLUG,
            defaults={
                "name": DEMO_WORKFLOW_NAME,
                "description": "Demo published workflow for coordinator review.",
                "is_active": True,
            },
        )
        version, created = WorkflowVersion.objects.update_or_create(
            definition=definition,
            version=1,
            defaults={
                "status": WorkflowVersion.Status.PUBLISHED,
                "bpmn_xml": DEMO_BPMN_XML,
                "created_by": users["admin"],
                "published_at": timezone.now(),
            },
        )
        action = "Created" if created else "Updated"
        self.stdout.write(f"  {action} workflow: {definition.name} v{version.version}")
        return version

    def _create_eligibility_ruleset(self):
        ruleset, created = EligibilityRuleSet.objects.update_or_create(
            name=DEMO_ELIGIBILITY_RULESET_NAME,
            defaults={
                "description": "Demo overlay tightening Fulbright GPA/language.",
                "schema_version": ELIGIBILITY_SCHEMA_VERSION,
                "is_active": True,
                "rules_json": {
                    "program_overrides": {
                        "min_gpa": 3.7,
                        "required_language": "English",
                        "min_language_level": "C1",
                    }
                },
            },
        )
        action = "Created" if created else "Updated"
        self.stdout.write(f"  {action} eligibility ruleset: {ruleset.name}")
        return ruleset

    def _create_programs(self, users, form_type, workflow_version, ruleset):
        programs = {}
        base_date = timezone.now().date()
        coordinator = users["coordinator"]
        transcript = DocumentType.objects.get(name="transcript")
        passport = DocumentType.objects.get(name="passport")

        for index, spec in enumerate(DEMO_PROGRAM_SPECS):
            if spec.get("window") == "closed":
                start_date = base_date + timedelta(days=45)
                end_date = start_date + timedelta(days=160)
                open_date = base_date - timedelta(days=90)
                deadline = base_date - timedelta(days=14)
            else:
                start_date = base_date + timedelta(days=45 + (index * 20))
                end_date = start_date + timedelta(days=160 + (index * 15))
                open_date = base_date - timedelta(days=14)
                deadline = start_date - timedelta(days=7)

            defaults = {
                "description": spec["description"],
                "start_date": start_date,
                "end_date": end_date,
                "application_open_date": open_date,
                "application_deadline": deadline,
                "is_active": spec["is_active"],
                "min_gpa": spec["min_gpa"],
                "required_language": spec["required_language"],
                "min_language_level": spec["min_language_level"],
                "recurring": True,
                "enrollment_capacity": spec.get("enrollment_capacity"),
                "waitlist_when_full": spec.get("waitlist_when_full", True),
            }
            if spec.get("application_form_name") == DEMO_FORM_NAME:
                defaults["application_form"] = form_type
            if spec.get("workflow_slug") == DEMO_WORKFLOW_SLUG:
                defaults["workflow_version"] = workflow_version
            if spec.get("eligibility_ruleset_name") == DEMO_ELIGIBILITY_RULESET_NAME:
                defaults["eligibility_ruleset"] = ruleset

            program, created = Program.objects.update_or_create(
                name=spec["name"],
                defaults=defaults,
            )
            program.coordinators.set([coordinator])
            for sort_order, doc_type in enumerate((transcript, passport)):
                ProgramDocumentRequirement.objects.update_or_create(
                    program=program,
                    document_type=doc_type,
                    defaults={"is_required": True, "sort_order": sort_order},
                )

            action = "Created" if created else "Updated"
            self.stdout.write(f"  {action} program: {program.name}")
            programs[spec["name"]] = program

        for scheme in Program.objects.filter(name__in=DEMO_HOST_SPECS):
            programs.setdefault(scheme.name, scheme)
            if not scheme.coordinators.exists():
                scheme.coordinators.add(coordinator)

        return programs

    def _create_host_destinations(self, programs):
        for program_name, spec in DEMO_HOST_SPECS.items():
            program = programs.get(program_name)
            if program is None:
                continue
            institution, _ = HostInstitution.objects.update_or_create(
                program=program,
                name=spec["institution"],
                defaults={"country": spec["country"], "is_active": True},
            )
            school, _ = HostSchool.objects.update_or_create(
                institution=institution,
                name=spec["school"],
                defaults={"is_active": True},
            )
            academic, _ = HostAcademicProgram.objects.update_or_create(
                school=school,
                name=spec["academic"],
                defaults={"code": spec["academic_code"], "is_active": True},
            )
            for subject_spec in spec.get("subjects") or ():
                HostSubject.objects.update_or_create(
                    academic_program=academic,
                    name=subject_spec["name"],
                    code=subject_spec["code"],
                    defaults={
                        "credits": Decimal(subject_spec["credits"]),
                        "is_active": True,
                    },
                )
        self.stdout.write(
            f"  Ensured host destination trees for {len(DEMO_HOST_SPECS)} programs"
        )

    def _create_exchange_agreements(self, programs):
        """Operational agreements for staff registry UI and API filters (idempotent)."""
        base_date = timezone.now().date()

        for spec in DEMO_AGREEMENT_SPECS:
            start_date = base_date + timedelta(days=spec["start_offset_days"])
            end_date = None
            if "end_offset_days" in spec:
                end_date = base_date + timedelta(days=spec["end_offset_days"])
            renewal_due = None
            if spec.get("renewal_follow_up_due_offset_days") is not None:
                renewal_due = base_date + timedelta(
                    days=spec["renewal_follow_up_due_offset_days"]
                )

            agreement, created = ExchangeAgreement.objects.update_or_create(
                internal_reference=spec["internal_reference"],
                defaults={
                    "title": spec["title"],
                    "partner_institution_name": spec["partner_institution_name"],
                    "partner_country": spec.get("partner_country", ""),
                    "required_gpa": spec.get("required_gpa"),
                    "language_requirements": spec.get("language_requirements", []),
                    "custom_tags": spec.get("custom_tags", ""),
                    "application_limit": spec.get("application_limit"),
                    "notify_on_limit_reached": spec.get(
                        "notify_on_limit_reached", True
                    ),
                    "agreement_type": spec["agreement_type"],
                    "status": spec["status"],
                    "notes": spec.get("notes", ""),
                    "start_date": start_date,
                    "end_date": end_date,
                    "renewal_follow_up_due": renewal_due,
                },
            )
            program_names = spec.get("program_names") or []
            agreement.programs.set([programs[name] for name in program_names])

            action = "Created" if created else "Updated"
            self.stdout.write(f"  {action} exchange agreement: {agreement.title}")

        self.stdout.write(
            f"  Ensured {len(DEMO_AGREEMENT_SPECS)} demo exchange agreements"
        )

    def _create_partner_portal(self, users):
        agreement = ExchangeAgreement.objects.filter(
            internal_reference=DEMO_PARTNER_AGREEMENT_REF
        ).first()
        if agreement is None:
            return
        PartnerContact.objects.update_or_create(
            user=users["partner"],
            agreement=agreement,
            defaults={"title": "International office liaison", "is_active": True},
        )
        AgreementComment.objects.update_or_create(
            agreement=agreement,
            author=users["coordinator"],
            text="Staff note: partner liaison confirmed for the Barcelona cluster.",
            defaults={"is_private": True},
        )
        AgreementComment.objects.update_or_create(
            agreement=agreement,
            author=users["partner"],
            text="Nomination package received. We will confirm seats next week.",
            defaults={"is_private": False},
        )
        fake_file = SimpleUploadedFile(
            "demo-erasmus-signed.pdf",
            self._build_pdf_bytes_text("Demo signed Erasmus framework agreement"),
            content_type="application/pdf",
        )
        ExchangeAgreementDocument.objects.get_or_create(
            agreement=agreement,
            title="Demo signed Erasmus framework",
            defaults={
                "category": ExchangeAgreementDocument.Category.SIGNED_COPY,
                "file": fake_file,
                "notes": "Seeded signed copy for the agreement repository.",
                "uploaded_by": users["admin"],
            },
        )
        self.stdout.write(
            "  Ensured partner portal contacts, comments, and agreement documents"
        )

    def _host_tree_for(self, program):
        institution = HostInstitution.objects.filter(
            program=program, is_active=True
        ).first()
        if institution is None:
            return None, None, None
        school = institution.schools.filter(is_active=True).first()
        academic = (
            school.academic_programs.filter(is_active=True).first() if school else None
        )
        return institution, school, academic

    def _create_applications(self, users, programs):
        applications = []
        status_map = {status.name: status for status in ApplicationStatus.objects.all()}
        coordinator = users["coordinator"]

        for spec in DEMO_APPLICATION_SPECS:
            submitted_at = None
            if spec["submitted_days_ago"] is not None:
                submitted_at = timezone.now() - timedelta(
                    days=spec["submitted_days_ago"]
                )

            program = programs[spec["program_name"]]
            student = users[spec["student_username"]]
            institution, school, academic = self._host_tree_for(program)
            profile = getattr(student, "profile", None)

            defaults = {
                "status": status_map[spec["status"]],
                "submitted_at": submitted_at,
                "withdrawn": spec["withdrawn"],
                "assigned_coordinator": coordinator
                if spec["status"] != "draft"
                else None,
                "nomination_rank": spec.get("nomination_rank"),
                "host_institution": institution,
                "host_school": school,
                "host_academic_program": academic,
            }
            if profile and spec["status"] != "draft":
                defaults.update(
                    {
                        "semester_at_apply": profile.get_effective_semester(),
                        "gpa_at_apply": profile.gpa,
                        "grade_scale_at_apply": profile.grade_scale,
                        "credits_percent_at_apply": profile.credits_approved_percent,
                        "language_at_apply": profile.language,
                        "language_level_at_apply": profile.language_level,
                    }
                )

            application, created = Application.objects.get_or_create(
                student=student,
                program=program,
                defaults=defaults,
            )

            if not created:
                for field, value in defaults.items():
                    setattr(application, field, value)
                application.save()

            applications.append(application)

        self.stdout.write(
            f"  Ensured {len(applications)} applications across all statuses"
        )
        return applications

    def _create_subject_selections(self, applications):
        count = 0
        for application in applications:
            if application.status.name not in {"approved", "completed", "under_review"}:
                continue
            if not application.host_academic_program_id:
                continue
            subject = HostSubject.objects.filter(
                academic_program=application.host_academic_program, is_active=True
            ).first()
            if subject is None:
                continue
            ApplicationSubjectSelection.objects.update_or_create(
                application=application,
                host_subject=subject,
                defaults={
                    "home_course_label": "Home equivalent course",
                    "home_course_code": "HOME101",
                    "credits": subject.credits,
                },
            )
            count += 1
        self.stdout.write(f"  Ensured {count} host subject selections")

    def _create_documents(self, applications, users):
        document_types = {
            "transcript": DocumentType.objects.get(name="transcript"),
            "passport": DocumentType.objects.get(name="passport"),
            "language_certificate": DocumentType.objects.get(
                name="language_certificate"
            ),
        }
        coordinator = users["coordinator"]

        seeded_docs = []
        for application in applications:
            seeded_docs.append(
                self._upsert_document(
                    application=application,
                    doc_type=document_types["transcript"],
                    is_valid=application.status.name
                    in {"under_review", "approved", "completed"},
                )
            )

            seed_all_required_unapproved = (
                application.program.name == DEMO_SUBMIT_GATE_PROGRAM
            )
            if application.status.name != "draft" or seed_all_required_unapproved:
                seeded_docs.append(
                    self._upsert_document(
                        application=application,
                        doc_type=document_types["passport"],
                        is_valid=(
                            False
                            if seed_all_required_unapproved
                            else application.status.name in {"approved", "completed"}
                        ),
                    )
                )

            if application.program.required_language and application.status.name in {
                "approved",
                "completed",
                "rejected",
            }:
                seeded_docs.append(
                    self._upsert_document(
                        application=application,
                        doc_type=document_types["language_certificate"],
                        is_valid=application.status.name in {"approved", "completed"},
                    )
                )

        review_doc = next(
            (
                doc
                for doc in seeded_docs
                if doc and doc.application.status.name == "under_review"
            ),
            None,
        )
        if review_doc:
            DocumentValidation.objects.update_or_create(
                document=review_doc,
                validator=coordinator,
                defaults={
                    "result": "passed",
                    "details": "Demo virus scan and integrity check passed.",
                },
            )
            DocumentComment.objects.update_or_create(
                document=review_doc,
                author=coordinator,
                text="Please confirm the transcript includes the latest semester.",
                defaults={"is_private": False},
            )
            DocumentResubmissionRequest.objects.update_or_create(
                document=review_doc,
                requested_by=coordinator,
                defaults={
                    "reason": "Demo resubmission request for coordinator document review.",
                    "resolved": False,
                },
            )

        student_resubmit_doc = next(
            (
                doc
                for doc in seeded_docs
                if doc
                and doc.application.program.name == DEMO_RESUBMIT_PROGRAM
                and doc.type_id == document_types["passport"].id
            ),
            None,
        )
        if student_resubmit_doc:
            DocumentResubmissionRequest.objects.update_or_create(
                document=student_resubmit_doc,
                requested_by=coordinator,
                defaults={
                    "reason": (
                        "DEMO-SEED: passport scan is blurry. Replace this file "
                        "so coordinator review can continue."
                    ),
                    "resolved": False,
                },
            )

        self.stdout.write("  Ensured supporting documents for all demo applications")

    def _upsert_document(self, application, doc_type, is_valid):
        filename = f"{application.student.username}-{doc_type.name}.pdf"
        fake_file = SimpleUploadedFile(
            filename,
            self._build_pdf_bytes(application, doc_type.name),
            content_type="application/pdf",
        )

        document, created = Document.objects.get_or_create(
            application=application,
            type=doc_type,
            uploaded_by=application.student,
            defaults={
                "file": fake_file,
                "is_valid": is_valid,
                "validated_at": timezone.now() if is_valid else None,
            },
        )

        if not created:
            document.file = fake_file
            document.is_valid = is_valid
            document.validated_at = timezone.now() if is_valid else None
            document.save()
        return document

    def _create_comments_and_events(self, applications, users):
        coordinator = users["coordinator"]
        admin = users["admin"]

        for application in applications:
            TimelineEvent.objects.update_or_create(
                application=application,
                event_type="application_created",
                defaults={
                    "description": "Application created for demo walkthrough.",
                    "created_by": application.student,
                },
            )

            if application.submitted_at:
                TimelineEvent.objects.update_or_create(
                    application=application,
                    event_type="status_change",
                    description=f"Application status changed to {application.status.name}",
                    defaults={
                        "created_by": coordinator,
                    },
                )

            if application.status.name != "draft":
                Comment.objects.update_or_create(
                    application=application,
                    author=coordinator,
                    text=(
                        f"Coordinator review note for {application.student.first_name}'s "
                        f"{application.program.name} application."
                    ),
                    defaults={"is_private": application.status.name == "rejected"},
                )

            if application.status.name in {"approved", "completed"}:
                Comment.objects.update_or_create(
                    application=application,
                    author=admin,
                    text=(
                        "Admin follow-up: financial and travel guidance has been prepared "
                        "for this student."
                    ),
                    defaults={"is_private": False},
                )

        self.stdout.write("  Ensured comments and timeline events")

    def _create_notifications(self, applications, users):
        for application in applications:
            recipient = application.student
            title = (
                f"{application.program.name} application is {application.status.name}"
            )
            Notification.objects.update_or_create(
                recipient=recipient,
                title=title,
                defaults={
                    "message": (
                        f"Your application for {application.program.name} is currently "
                        f"marked as {application.status.name}."
                    ),
                    "notification_type": "in_app",
                    "category": self._notification_category(application.status.name),
                    "is_read": application.status.name in {"approved", "completed"},
                    "action_url": f"/applications/{application.id}",
                    "action_text": "View application",
                },
            )

        Notification.objects.update_or_create(
            recipient=users["coordinator"],
            title="Coordinator inbox ready",
            defaults={
                "message": "Submitted and under-review applications are available for review.",
                "notification_type": "in_app",
                "category": "info",
                "is_read": False,
                "action_url": "/applications",
                "action_text": "Review applications",
            },
        )

        Notification.objects.update_or_create(
            recipient=users["admin"],
            title="Demo analytics dataset prepared",
            defaults={
                "message": "The system now has seeded applications, documents, and notifications.",
                "notification_type": "in_app",
                "category": "success",
                "is_read": False,
                "action_url": "/dashboard",
                "action_text": "Open dashboard",
            },
        )

        Notification.objects.update_or_create(
            recipient=users["partner"],
            title="Partner portal ready",
            defaults={
                "message": "Your linked exchange agreement is available in the partner portal.",
                "notification_type": "in_app",
                "category": "info",
                "is_read": False,
                "action_url": "/partner",
                "action_text": "Open partner portal",
            },
        )

        self.stdout.write("  Ensured read and unread notifications")

    def _create_scholarships(self, applications, users):
        admin = users["admin"]
        for application in applications:
            if application.status.name == "approved":
                award, _ = ScholarshipAward.objects.update_or_create(
                    application=application,
                    defaults={
                        "status": ScholarshipAward.Status.AWARDED,
                        "amount": Decimal("25000.00"),
                        "currency": "MXN",
                        "notes": "Demo awarded scholarship.",
                        "decided_by": admin,
                        "decided_at": timezone.now(),
                    },
                )
                ScholarshipDisbursement.objects.update_or_create(
                    award=award,
                    label="Fall disbursement",
                    defaults={
                        "amount": Decimal("12500.00"),
                        "due_date": timezone.now().date() + timedelta(days=30),
                        "status": ScholarshipDisbursement.Status.PENDING,
                        "sort_order": 0,
                    },
                )
                ScholarshipDisbursement.objects.update_or_create(
                    award=award,
                    label="Spring disbursement",
                    defaults={
                        "amount": Decimal("12500.00"),
                        "due_date": timezone.now().date() + timedelta(days=150),
                        "status": ScholarshipDisbursement.Status.PENDING,
                        "sort_order": 1,
                    },
                )
            elif application.status.name == "completed":
                award, _ = ScholarshipAward.objects.update_or_create(
                    application=application,
                    defaults={
                        "status": ScholarshipAward.Status.DISBURSED,
                        "amount": Decimal("18000.00"),
                        "currency": "MXN",
                        "notes": "Demo fully disbursed scholarship.",
                        "decided_by": admin,
                        "decided_at": timezone.now() - timedelta(days=40),
                    },
                )
                ScholarshipDisbursement.objects.update_or_create(
                    award=award,
                    label="Full disbursement",
                    defaults={
                        "amount": Decimal("18000.00"),
                        "due_date": timezone.now().date() - timedelta(days=10),
                        "paid_at": timezone.now() - timedelta(days=8),
                        "status": ScholarshipDisbursement.Status.PAID,
                        "sort_order": 0,
                    },
                )
            elif application.status.name == "under_review":
                ScholarshipAward.objects.update_or_create(
                    application=application,
                    defaults={
                        "status": ScholarshipAward.Status.NOMINATED,
                        "amount": Decimal("20000.00"),
                        "currency": "MXN",
                        "notes": "Demo nomination pending decision.",
                        "decided_by": None,
                        "decided_at": None,
                    },
                )
        self.stdout.write("  Ensured scholarship awards and disbursements")

    def _create_form_submissions(self, applications, form_type):
        for application in applications:
            if application.program.application_form_id != form_type.id:
                continue
            FormSubmission.objects.update_or_create(
                form_type=form_type,
                application=application,
                defaults={
                    "submitted_by": application.student,
                    "program": application.program,
                    "responses": {
                        "motivation": "I want to study in Barcelona as part of the demo dataset.",
                        "emergency_contact": "Camila Coordinator +52 81 1234 5678",
                    },
                },
            )
        self.stdout.write("  Ensured dynamic form submissions")

    def _create_workflow_instances(self, applications, workflow_version, users):
        for application in applications:
            if application.program.workflow_version_id != workflow_version.id:
                continue
            if application.status.name == "draft":
                continue
            instance, created = WorkflowInstance.objects.update_or_create(
                application=application,
                defaults={
                    "workflow_version": workflow_version,
                    "engine_state": {"seeded": True},
                    "current_tasks": ["submitted"],
                    "status": application.status.name,
                    "last_event_at": timezone.now(),
                },
            )
            if created or not instance.events.exists():
                WorkflowEvent.objects.create(
                    instance=instance,
                    event_type="seeded",
                    payload={"status": application.status.name},
                    actor=users["coordinator"],
                )
        self.stdout.write("  Ensured workflow instances")

    def _create_saved_searches(self, users):
        coordinator = users["coordinator"]
        admin = users["admin"]
        specs = (
            (
                coordinator,
                "Under review queue",
                "application",
                {"status": "under_review"},
                True,
            ),
            (
                coordinator,
                "Active agreements",
                "exchange_agreement",
                {"status": "active"},
                True,
            ),
            (
                admin,
                "Capacity forecasts",
                "analytics_forecast",
                {"horizon": "semester"},
                True,
            ),
        )
        for user, name, search_type, filters, is_default in specs:
            SavedSearch.objects.update_or_create(
                user=user,
                name=name,
                search_type=search_type,
                defaults={"filters": filters, "is_default": is_default},
            )
        self.stdout.write("  Ensured saved searches")

    def _create_reminders(self, users, programs):
        student = users["student"]
        program = programs["Erasmus+ Exchange - University of Barcelona, Spain"]
        Reminder.objects.update_or_create(
            user=student,
            event_type="application_deadline",
            event_id=program.id,
            defaults={
                "event_title": f"Deadline: {program.name}",
                "remind_at": timezone.now() + timedelta(days=3),
                "sent": False,
            },
        )
        Reminder.objects.update_or_create(
            user=users["coordinator"],
            event_type="program_start",
            event_id=program.id,
            defaults={
                "event_title": f"Program start: {program.name}",
                "remind_at": timezone.now() + timedelta(days=40),
                "sent": False,
            },
        )
        self.stdout.write("  Ensured calendar reminders")

    def _create_notification_routing(self):
        NotificationRoutingOverride.objects.update_or_create(
            kind=NotificationRoutingOverride.KIND_REMINDER_EVENT_TYPE,
            key="application_deadline",
            defaults={
                "settings_category": NotificationRoutingOverride.SETTINGS_CATEGORY_APPLICATIONS,
                "is_active": True,
            },
        )
        NotificationRoutingOverride.objects.update_or_create(
            kind=NotificationRoutingOverride.KIND_TRANSACTIONAL_ROUTE_KEY,
            key="document_validated",
            defaults={
                "settings_category": NotificationRoutingOverride.SETTINGS_CATEGORY_DOCUMENTS,
                "is_active": True,
            },
        )
        self.stdout.write("  Ensured notification routing overrides")

    def _create_analytics(self, users):
        admin = users["admin"]
        report, _ = Report.objects.update_or_create(
            name="Demo applications by status",
            defaults={
                "description": "Seeded snapshot for analytics dashboards.",
                "created_by": admin,
            },
        )
        for name, value in (
            ("draft", 2.0),
            ("submitted", 1.0),
            ("under_review", 1.0),
            ("approved", 1.0),
            ("waitlist", 1.0),
        ):
            Metric.objects.update_or_create(
                report=report,
                name=name,
                defaults={"value": value},
            )
        DashboardConfig.objects.update_or_create(
            user=admin,
            defaults={
                "config": {"layout": "default", "widgets": ["status", "capacity"]}
            },
        )
        self.stdout.write("  Ensured analytics reports and dashboard config")

    def _create_grade_translations(self, users):
        us_scale = GradeScale.objects.filter(code="US_GPA_4").first()
        ects_scale = GradeScale.objects.filter(code="ECTS").first()
        if us_scale is None or ects_scale is None:
            self.stdout.write("  Skipped grade translations (scales missing)")
            return
        mapping = {"A": "A", "B": "C", "C": "D", "D": "E", "F": "F"}
        created = 0
        for source_label, target_label in mapping.items():
            source = GradeValue.objects.filter(
                grade_scale=us_scale, label=source_label
            ).first()
            target = GradeValue.objects.filter(
                grade_scale=ects_scale, label=target_label
            ).first()
            if source is None or target is None:
                continue
            _, was_created = GradeTranslation.objects.get_or_create(
                source_grade=source,
                target_grade=target,
                defaults={
                    "confidence": 0.9,
                    "notes": "Demo US GPA → ECTS mapping.",
                    "created_by": users["admin"],
                },
            )
            if was_created:
                created += 1
        self.stdout.write(f"  Ensured grade translations (+{created} new)")

    def _notification_category(self, status_name):
        if status_name in {"approved", "completed"}:
            return "success"
        if status_name in {"rejected", "cancelled"}:
            return "warning"
        return "info"

    def _build_pdf_bytes(self, application, doc_type_name):
        text = f"Demo {doc_type_name} — {application.student.username} — {application.program.name}"
        return self._build_pdf_bytes_text(text)

    def _build_pdf_bytes_text(self, text):
        # Build a small *valid* PDF so browser previews work (Chrome/PDF.js rejects header-only stubs).
        try:
            from io import BytesIO

            from reportlab.pdfgen import canvas

            buf = BytesIO()
            c = canvas.Canvas(buf, pagesize=(300, 200))
            c.setFont("Helvetica", 12)
            c.drawString(24, 140, text[:80])
            c.showPage()
            c.save()
            return buf.getvalue()
        except Exception:
            return (
                b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n" + text.encode("utf-8") + b"\n%%EOF\n"
            )
