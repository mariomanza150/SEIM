"""
Seed data required for Vue E2E tests so skipped tests can run.

Creates: student@test.com (via create_vue_test_users), a draft application,
one document for that application, and unread notifications.

Run before Vue E2E: python manage.py seed_vue_e2e
Or: docker compose exec web python manage.py seed_vue_e2e
"""

from datetime import date, timedelta
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Role
from documents.models import Document, DocumentType
from exchange.models import Application, ApplicationStatus, Program
from notifications.models import Notification
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Seed data for Vue E2E tests (draft application, document, unread notifications)"

    def handle(self, *args, **options):
        self.stdout.write("Seeding Vue E2E data...")

        call_command("create_initial_data", verbosity=0)
        call_command("create_vue_test_users", verbosity=0)

        try:
            student = User.objects.get(email="student@test.com")
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("student@test.com not found. Run create_vue_test_users first."))
            return

        draft_status = ApplicationStatus.objects.get(name="draft")
        start = date.today() + timedelta(days=30)
        end = start + timedelta(days=180)
        program, _ = Program.objects.get_or_create(
            name="Vue E2E Test Program",
            defaults={
                "description": "Program for Vue E2E tests.",
                "start_date": start,
                "end_date": end,
                "is_active": True,
                "min_gpa": 2.5,
                "required_language": "English",
            },
        )
        application, created = Application.objects.get_or_create(
            student=student,
            program=program,
            defaults={"status": draft_status},
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"  ✓ Created draft application: {program.name}"))
        else:
            self.stdout.write(f"  ✓ Draft application exists: {program.name}")

        doc_type, _ = DocumentType.objects.get_or_create(
            name="transcript",
            defaults={"description": "Academic transcript"},
        )
        if not Document.objects.filter(application=application, type=doc_type).exists():
            fake_file = SimpleUploadedFile(
                "e2e_transcript.pdf",
                b"%PDF-1.4 E2E test document content",
                content_type="application/pdf",
            )
            Document.objects.create(
                application=application,
                type=doc_type,
                file=fake_file,
                uploaded_by=student,
                is_valid=False,
            )
            self.stdout.write(self.style.SUCCESS("  ✓ Created document for application"))
        else:
            self.stdout.write("  ✓ Document already exists for application")

        unread = Notification.objects.filter(recipient=student, is_read=False).count()
        if unread < 2:
            for i, (title, msg) in enumerate([
                ("E2E Test Notification 1", "First unread notification for Vue E2E."),
                ("E2E Test Notification 2", "Second unread notification for Vue E2E."),
            ]):
                Notification.objects.get_or_create(
                    recipient=student,
                    title=title,
                    defaults={
                        "message": msg,
                        "category": "info",
                        "is_read": False,
                        "action_url": "/applications",
                        "action_text": "View",
                    },
                )
            self.stdout.write(self.style.SUCCESS("  ✓ Created unread notifications"))
        else:
            self.stdout.write(f"  ✓ Unread notifications already exist ({unread})")

        self.stdout.write(self.style.SUCCESS("\n✅ Vue E2E seed completed. Run Vue E2E tests."))
