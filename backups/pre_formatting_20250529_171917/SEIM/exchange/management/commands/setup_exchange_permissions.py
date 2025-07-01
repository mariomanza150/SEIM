"""
Management command to setup exchange application permissions and groups
"""

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from exchange.models import Exchange


class Command(BaseCommand):
    help = "Setup exchange application permissions and groups"

    def handle(self, *args, **options):
        self.stdout.write("Setting up exchange permissions and groups...")

        try:
            # Get or create groups
            coordinator_group, created = Group.objects.get_or_create(
                name="Exchange Coordinators"
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS("Created Exchange Coordinators group")
                )

            administrator_group, created = Group.objects.get_or_create(
                name="Exchange Administrators"
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS("Created Exchange Administrators group")
                )

            # Get content type for Exchange model
            exchange_ct = ContentType.objects.get_for_model(Exchange)

            # Create or get permissions
            review_perm, created = Permission.objects.get_or_create(
                codename="can_review_exchange",
                name="Can review exchange applications",
                content_type=exchange_ct,
            )
            if created:
                self.stdout.write(self.style.SUCCESS("Created review permission"))

            approve_perm, created = Permission.objects.get_or_create(
                codename="can_approve_exchange",
                name="Can approve/reject exchange applications",
                content_type=exchange_ct,
            )
            if created:
                self.stdout.write(self.style.SUCCESS("Created approve permission"))

            view_all_perm, created = Permission.objects.get_or_create(
                codename="can_view_all_exchanges",
                name="Can view all exchange applications",
                content_type=exchange_ct,
            )
            if created:
                self.stdout.write(self.style.SUCCESS("Created view all permission"))

            # Assign permissions to groups
            coordinator_group.permissions.add(review_perm, view_all_perm)
            administrator_group.permissions.add(
                review_perm, approve_perm, view_all_perm
            )

            self.stdout.write(self.style.SUCCESS("Assigned permissions to groups"))

            # Display summary
            self.stdout.write("\n=== PERMISSION SETUP SUMMARY ===")
            self.stdout.write(
                f"Exchange Coordinators: {coordinator_group.permissions.count()} permissions"
            )
            self.stdout.write(
                f"Exchange Administrators: {administrator_group.permissions.count()} permissions"
            )

            self.stdout.write("\n=== NEXT STEPS ===")
            self.stdout.write("1. Add users to appropriate groups via Django admin")
            self.stdout.write(
                "2. Or use: python manage.py assign_user_group <username> <group_name>"
            )

            self.stdout.write(
                self.style.SUCCESS(
                    "\nExchange permissions setup completed successfully!"
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error setting up permissions: {str(e)}")
            )
            raise
