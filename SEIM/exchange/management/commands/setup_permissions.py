"""
Management command to set up permission groups for the exchange app.
"""

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from exchange.models import Course, Document, Exchange, Grade


class Command(BaseCommand):
    help = "Set up permission groups for the exchange app"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be done without actually creating groups and permissions",
        )

    def handle(self, *args, **options):
        dry_run = options.get("dry_run", False)

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be made"))

        try:
            # Get content types
            exchange_ct = ContentType.objects.get_for_model(Exchange)
            document_ct = ContentType.objects.get_for_model(Document)
            course_ct = ContentType.objects.get_for_model(Course)
            grade_ct = ContentType.objects.get_for_model(Grade)

            self.stdout.write("Found content types for all models")

            # Helper function to get permissions safely
            def get_permission(codename, content_type):
                try:
                    return Permission.objects.get(codename=codename, content_type=content_type)
                except Permission.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f"Permission {codename} does not exist for {content_type.model}")
                    )
                    return None

            # Create groups
            if not dry_run:
                student_group, student_created = Group.objects.get_or_create(name="Students")
                coordinator_group, coordinator_created = Group.objects.get_or_create(name="Coordinators")
                manager_group, manager_created = Group.objects.get_or_create(name="Managers")
                admin_group, admin_created = Group.objects.get_or_create(name="Administrators")

                self.stdout.write("Created/found all permission groups")

                # Clear existing permissions from groups
                student_group.permissions.clear()
                coordinator_group.permissions.clear()
                manager_group.permissions.clear()
                admin_group.permissions.clear()

                self.stdout.write("Cleared existing permissions from groups")
            else:
                self.stdout.write("Would create/find groups: Students, Coordinators, Managers, Administrators")

            # Define student permissions (basic CRUD operations they can perform)
            student_perms = []
            student_perm_codes = [
                ("add_exchange", exchange_ct),
                ("change_exchange", exchange_ct),
                ("view_exchange", exchange_ct),
                ("add_document", document_ct),
                ("change_document", document_ct),
                ("view_document", document_ct),
                ("view_course", course_ct),
                ("view_grade", grade_ct),
            ]

            for codename, content_type in student_perm_codes:
                perm = get_permission(codename, content_type)
                if perm:
                    student_perms.append(perm)

            self.stdout.write(f"Student permissions: {len(student_perms)} permissions")

            # Coordinator permissions (student permissions + additional ones)
            coordinator_perms = student_perms.copy()
            coordinator_perm_codes = [
                ("delete_document", document_ct),
                (
                    "can_verify_documents",
                    document_ct,
                ),  # Custom permission from Document model
                ("add_course", course_ct),
                ("change_course", course_ct),
            ]

            for codename, content_type in coordinator_perm_codes:
                perm = get_permission(codename, content_type)
                if perm:
                    coordinator_perms.append(perm)

            self.stdout.write(f"Coordinator permissions: {len(coordinator_perms)} permissions")

            # Manager permissions (coordinator permissions + approval/management ones)
            manager_perms = coordinator_perms.copy()
            manager_perm_codes = [
                (
                    "can_review_exchange",
                    exchange_ct,
                ),  # Custom permission from Exchange model
                (
                    "can_approve_exchange",
                    exchange_ct,
                ),  # Custom permission from Exchange model
                ("delete_exchange", exchange_ct),
                ("delete_course", course_ct),
                ("add_grade", grade_ct),
                ("change_grade", grade_ct),
                ("delete_grade", grade_ct),
            ]

            for codename, content_type in manager_perm_codes:
                perm = get_permission(codename, content_type)
                if perm:
                    manager_perms.append(perm)

            self.stdout.write(f"Manager permissions: {len(manager_perms)} permissions")

            # Admin group gets all permissions for the models
            all_perms = Permission.objects.filter(content_type__in=[exchange_ct, document_ct, course_ct, grade_ct])

            self.stdout.write(f"Administrator permissions: {all_perms.count()} permissions")

            # Set permissions to groups
            if not dry_run:
                student_group.permissions.set(student_perms)
                coordinator_group.permissions.set(coordinator_perms)
                manager_group.permissions.set(manager_perms)
                admin_group.permissions.set(all_perms)

                self.stdout.write(self.style.SUCCESS("Successfully set up permission groups"))

                # Print final summary
                self.stdout.write("\nFinal Permission Summary:")
                self.stdout.write(f"Students: {student_group.permissions.count()} permissions")
                self.stdout.write(f"Coordinators: {coordinator_group.permissions.count()} permissions")
                self.stdout.write(f"Managers: {manager_group.permissions.count()} permissions")
                self.stdout.write(f"Administrators: {admin_group.permissions.count()} permissions")

                # Show specific permissions for each group
                self.stdout.write("\nDetailed Permissions:")

                self.stdout.write("\nStudents:")
                for perm in student_group.permissions.all():
                    self.stdout.write(f"  - {perm.content_type.model}.{perm.codename}: {perm.name}")

                self.stdout.write("\nCoordinators (additional to Students):")
                coordinator_additional = set(coordinator_group.permissions.all()) - set(student_group.permissions.all())
                for perm in coordinator_additional:
                    self.stdout.write(f"  - {perm.content_type.model}.{perm.codename}: {perm.name}")

                self.stdout.write("\nManagers (additional to Coordinators):")
                manager_additional = set(manager_group.permissions.all()) - set(coordinator_group.permissions.all())
                for perm in manager_additional:
                    self.stdout.write(f"  - {perm.content_type.model}.{perm.codename}: {perm.name}")

            else:
                self.stdout.write("\nWould set the following permissions:")
                self.stdout.write(f"Students: {len(student_perms)} permissions")
                self.stdout.write(f"Coordinators: {len(coordinator_perms)} permissions")
                self.stdout.write(f"Managers: {len(manager_perms)} permissions")
                self.stdout.write(f"Administrators: {all_perms.count()} permissions")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error setting up permissions: {str(e)}"))
            raise
