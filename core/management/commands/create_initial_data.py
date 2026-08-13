"""
Management command to create initial system data required for SEIM to function.
This includes ApplicationStatus, DocumentType, NotificationType, and Roles.
"""

from django.core.management.base import BaseCommand

from accounts.models import Role
from accounts.profile_catalogs import seed_profile_catalogs
from documents.mobility_document_catalog import (
    assign_scheme_document_requirements,
    seed_mobility_document_types,
)
from documents.models import DocumentType
from exchange.mobility_schemes import seed_mobility_schemes
from exchange.models import ApplicationStatus
from notifications.models import NotificationType


class Command(BaseCommand):
    help = (
        "Create initial system data (statuses, document types, notification types, "
        "roles, profile catalogs, three mobility schemes, and MX document catalog "
        "requirements)"
    )

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

        # Legacy English seeds (kept for older tests/fixtures); mapped by Phase 4 catalog.
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
        roles = ["admin", "coordinator", "student", "partner"]
        for role_name in roles:
            Role.objects.get_or_create(name=role_name)
            self.stdout.write(f"  ✓ Role: {role_name}")

        schools, programs, banks = seed_profile_catalogs()
        self.stdout.write(
            f"  ✓ Profile catalogs: {len(schools)} schools, "
            f"{len(programs)} programs, {len(banks)} banks"
        )

        for program in seed_mobility_schemes():
            self.stdout.write(f"  ✓ Mobility scheme: {program.name}")

        for dt in seed_mobility_document_types():
            self.stdout.write(f"  ✓ Mobility DocumentType: {dt.slug or dt.name}")
        n_req = assign_scheme_document_requirements()
        self.stdout.write(f"  ✓ Scheme document requirements ensured (+{n_req} new)")

        self.stdout.write(
            self.style.SUCCESS("Initial system data created successfully!")
        )
