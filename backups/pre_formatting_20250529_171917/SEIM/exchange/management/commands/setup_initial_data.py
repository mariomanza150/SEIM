from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = "Sets up initial data for the SEIM application"

    def handle(self, *args, **kwargs):
        self.stdout.write("Setting up initial data...")

        with transaction.atomic():
            # Create default superuser if it doesn't exist
            if not User.objects.filter(username="admin").exists():
                User.objects.create_superuser(
                    username="admin", email="admin@example.com", password="changeme123"
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        "Created default admin user (username: admin, password: changeme123)"
                    )
                )
            else:
                self.stdout.write("Admin user already exists")

            # Create test users for development
            if User.objects.count() == 1:  # Only admin exists
                # Create a manager user
                manager, created = User.objects.get_or_create(
                    username="manager",
                    defaults={
                        "email": "manager@example.com",
                        "first_name": "Test",
                        "last_name": "Manager",
                        "is_staff": True,
                    },
                )
                if created:
                    manager.set_password("manager123")
                    manager.save()
                    self.stdout.write(self.style.SUCCESS("Created test manager user"))

                # Create a student user
                student, created = User.objects.get_or_create(
                    username="student",
                    defaults={
                        "email": "student@example.com",
                        "first_name": "Test",
                        "last_name": "Student",
                        "is_staff": False,
                    },
                )
                if created:
                    student.set_password("student123")
                    student.save()
                    self.stdout.write(self.style.SUCCESS("Created test student user"))

            # Create cache table for production settings
            from django.core.management import call_command

            try:
                call_command("createcachetable", "seim_cache_table", verbosity=0)
                self.stdout.write(self.style.SUCCESS("Created cache table"))
            except Exception:
                pass  # Table might already exist

        self.stdout.write(self.style.SUCCESS("Initial data setup complete"))
