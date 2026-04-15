from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import Profile, Role
from documents.models import Document, DocumentType
from exchange.demo_seed import (
    DEMO_AGREEMENT_SPECS,
    DEMO_APPLICATION_SPECS,
    DEMO_PROGRAM_SPECS,
    DEMO_USER_SPECS,
)
from exchange.models import (
    Application,
    ApplicationStatus,
    Comment,
    ExchangeAgreement,
    Program,
    TimelineEvent,
)
from notifications.models import Notification

User = get_user_model()


class Command(BaseCommand):
    help = "Seed a deterministic, demo-ready dataset for SEIM."

    def handle(self, *args, **options):
        self.stdout.write("Seeding demo-ready data for SEIM...")

        call_command("create_initial_data", verbosity=0)

        try:
            call_command("seed_grade_scales", verbosity=0)
        except Exception as exc:  # pragma: no cover - best effort
            self.stdout.write(
                self.style.WARNING(f"  Skipped grade scale seed: {exc}")
            )

        with transaction.atomic():
            users = self._create_users()
            programs = self._create_programs()
            self._create_exchange_agreements(programs)
            applications = self._create_applications(users, programs)
            self._create_documents(applications)
            self._create_comments_and_events(applications, users)
            self._create_notifications(applications, users)

        self.stdout.write(self.style.SUCCESS("Demo-ready seed completed."))
        self.stdout.write("Demo credentials:")
        self.stdout.write("  Admin: admin@test.com / admin123")
        self.stdout.write("  Coordinator: coordinator@test.com / coordinator123")
        self.stdout.write("  Student: student@test.com / student123")

    def _create_users(self):
        users = {}

        for spec in DEMO_USER_SPECS:
            role = Role.objects.get(name=spec["role"])
            user, created = User.objects.update_or_create(
                username=spec["username"],
                defaults={
                    "email": spec["email"],
                    "first_name": spec["first_name"],
                    "last_name": spec["last_name"],
                    "is_email_verified": True,
                    "is_active": True,
                    "is_staff": spec["is_staff"],
                    "is_superuser": spec["is_superuser"],
                },
            )
            user.set_password(spec["password"])
            user.save()
            user.roles.set([role])

            profile_data = spec.get("profile", {})
            if profile_data:
                profile, _ = Profile.objects.get_or_create(user=user)
                for field_name, value in profile_data.items():
                    setattr(profile, field_name, value)
                profile.save()

            action = "Created" if created else "Updated"
            self.stdout.write(f"  {action} user: {user.email}")
            users[spec["username"]] = user

        return users

    def _create_programs(self):
        programs = {}
        base_date = timezone.now().date()

        for index, spec in enumerate(DEMO_PROGRAM_SPECS):
            start_date = base_date + timedelta(days=45 + (index * 20))
            end_date = start_date + timedelta(days=160 + (index * 15))

            program, created = Program.objects.update_or_create(
                name=spec["name"],
                defaults={
                    "description": spec["description"],
                    "start_date": start_date,
                    "end_date": end_date,
                    "is_active": spec["is_active"],
                    "min_gpa": spec["min_gpa"],
                    "required_language": spec["required_language"],
                    "min_language_level": spec["min_language_level"],
                    "recurring": True,
                },
            )
            action = "Created" if created else "Updated"
            self.stdout.write(f"  {action} program: {program.name}")
            programs[spec["name"]] = program

        return programs

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
                    "partner_reference_id": spec.get("partner_reference_id", ""),
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

    def _create_applications(self, users, programs):
        applications = []
        status_map = {
            status.name: status
            for status in ApplicationStatus.objects.all()
        }

        for spec in DEMO_APPLICATION_SPECS:
            submitted_at = None
            if spec["submitted_days_ago"] is not None:
                submitted_at = timezone.now() - timedelta(days=spec["submitted_days_ago"])

            application, created = Application.objects.get_or_create(
                student=users[spec["student_username"]],
                program=programs[spec["program_name"]],
                defaults={
                    "status": status_map[spec["status"]],
                    "submitted_at": submitted_at,
                    "withdrawn": spec["withdrawn"],
                },
            )

            if not created:
                application.status = status_map[spec["status"]]
                application.submitted_at = submitted_at
                application.withdrawn = spec["withdrawn"]
                application.save(update_fields=["status", "submitted_at", "withdrawn", "updated_at"])

            applications.append(application)

        self.stdout.write(f"  Ensured {len(applications)} applications across all statuses")
        return applications

    def _create_documents(self, applications):
        document_types = {
            "transcript": DocumentType.objects.get(name="transcript"),
            "passport": DocumentType.objects.get(name="passport"),
            "language_certificate": DocumentType.objects.get(name="language_certificate"),
        }

        for application in applications:
            self._upsert_document(
                application=application,
                doc_type=document_types["transcript"],
                is_valid=application.status.name in {"under_review", "approved", "completed"},
            )

            if application.status.name != "draft":
                self._upsert_document(
                    application=application,
                    doc_type=document_types["passport"],
                    is_valid=application.status.name in {"approved", "completed"},
                )

            if application.program.required_language and application.status.name in {
                "approved",
                "completed",
                "rejected",
            }:
                self._upsert_document(
                    application=application,
                    doc_type=document_types["language_certificate"],
                    is_valid=application.status.name in {"approved", "completed"},
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
            title = f"{application.program.name} application is {application.status.name}"
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

        self.stdout.write("  Ensured read and unread notifications")

    def _notification_category(self, status_name):
        if status_name in {"approved", "completed"}:
            return "success"
        if status_name in {"rejected", "cancelled"}:
            return "warning"
        return "info"

    def _build_pdf_bytes(self, application, doc_type_name):
        # Build a small *valid* PDF so browser previews work (Chrome/PDF.js rejects header-only stubs).
        text = f"Demo {doc_type_name} — {application.student.username} — {application.program.name}"
        try:
            from io import BytesIO

            from reportlab.pdfgen import canvas

            buf = BytesIO()
            c = canvas.Canvas(buf, pagesize=(300, 200))
            c.setFont("Helvetica", 12)
            c.drawString(24, 140, text)
            c.showPage()
            c.save()
            return buf.getvalue()
        except Exception:
            # Fallback: very small handcrafted PDF (best-effort).
            return (b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n" + text.encode("utf-8") + b"\n%%EOF\n")
