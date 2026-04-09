"""
Management command to create initial system data required for SEIM to function.
This includes ApplicationStatus, DocumentType, NotificationType, and Roles.
"""

from django.core.management.base import BaseCommand

from accounts.models import Role
from documents.models import DocumentType
from exchange.models import ApplicationStatus
from notifications.models import NotificationType


class Command(BaseCommand):
    help = "Create initial system data (statuses, document types, notification types, roles)"

    def handle(self, *args, **options):
        self.stdout.write("Creating initial system data...")

        # Create ApplicationStatus objects
        statuses = [
            ("draft", 1),
            ("submitted", 2),
            ("under_review", 3),
            ("approved", 4),
            ("rejected", 5),
            ("completed", 6),
            ("cancelled", 7),
            ("waitlist", 15),
        ]
        for name, order in statuses:
            ApplicationStatus.objects.get_or_create(
                name=name, defaults={"order": order}
            )
            self.stdout.write(f"  ✓ ApplicationStatus: {name}")

        # Create DocumentType objects
        document_types = [
            ("transcript", "Academic transcript"),
            ("passport", "Passport or ID"),
            ("recommendation", "Recommendation letter"),
            ("language_certificate", "Language proficiency certificate"),
            ("cv", "Curriculum Vitae"),
        ]
        for name, description in document_types:
            DocumentType.objects.get_or_create(
                name=name, defaults={"description": description}
            )
            self.stdout.write(f"  ✓ DocumentType: {name}")

        # Create NotificationType objects
        notification_types = [
            "status_change",
            "comment",
            "document_uploaded",
            "document_validated",
            "reminder",
            "deadline",
        ]
        for name in notification_types:
            NotificationType.objects.get_or_create(name=name)
            self.stdout.write(f"  ✓ NotificationType: {name}")

        # Create Role objects
        roles = ["admin", "coordinator", "student"]
        for role_name in roles:
            Role.objects.get_or_create(name=role_name)
            self.stdout.write(f"  ✓ Role: {role_name}")

        self.stdout.write(self.style.SUCCESS("Initial system data created successfully!"))

