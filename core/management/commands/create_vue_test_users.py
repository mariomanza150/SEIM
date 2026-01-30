"""
Management command to create test users for Vue.js frontend testing.
Creates users with different roles: admin, coordinator, and student.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Role

User = get_user_model()


class Command(BaseCommand):
    help = "Create test users for Vue.js frontend development and testing"

    def handle(self, *args, **options):
        self.stdout.write("Creating test users for Vue.js...")

        # Ensure roles exist
        admin_role, _ = Role.objects.get_or_create(name="admin")
        coordinator_role, _ = Role.objects.get_or_create(name="coordinator")
        student_role, _ = Role.objects.get_or_create(name="student")

        # Test users configuration
        test_users = [
            {
                "email": "admin@test.com",
                "username": "admin",
                "password": "admin123",
                "first_name": "Admin",
                "last_name": "User",
                "role": admin_role,
                "is_staff": True,
                "is_superuser": True,
            },
            {
                "email": "coordinator@test.com",
                "username": "coordinator",
                "password": "coordinator123",
                "first_name": "Coordinator",
                "last_name": "User",
                "role": coordinator_role,
                "is_staff": True,
                "is_superuser": False,
            },
            {
                "email": "student@test.com",
                "username": "student",
                "password": "student123",
                "first_name": "Student",
                "last_name": "User",
                "role": student_role,
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "email": "test@example.com",
                "username": "testuser",
                "password": "testpass123",
                "first_name": "Test",
                "last_name": "Example",
                "role": student_role,
                "is_staff": False,
                "is_superuser": False,
            },
        ]

        created_count = 0
        updated_count = 0

        for user_data in test_users:
            email = user_data.pop("email")
            password = user_data.pop("password")
            role = user_data.pop("role")

            user, created = User.objects.get_or_create(
                email=email,
                defaults=user_data,
            )

            if created:
                user.set_password(password)
                user.save()
                # Add role (ManyToMany relationship)
                user.roles.clear()
                user.roles.add(role)
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✓ Created: {email} (password: {password}) - Role: {role.name}"
                    )
                )
            else:
                # Update existing user
                user.set_password(password)
                for key, value in user_data.items():
                    setattr(user, key, value)
                user.save()
                # Update role (ManyToMany relationship)
                user.roles.clear()
                user.roles.add(role)
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"  ↻ Updated: {email} (password: {password}) - Role: {role.name}"
                    )
                )

        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(self.style.SUCCESS(f"✓ Created {created_count} new users"))
        self.stdout.write(self.style.WARNING(f"↻ Updated {updated_count} existing users"))
        self.stdout.write("=" * 70)
        self.stdout.write("\nTest Credentials:")
        self.stdout.write("-" * 70)
        self.stdout.write("  Admin:        admin@test.com / admin123")
        self.stdout.write("  Coordinator:  coordinator@test.com / coordinator123")
        self.stdout.write("  Student:      student@test.com / student123")
        self.stdout.write("  Generic:      test@example.com / testpass123")
        self.stdout.write("-" * 70)
        self.stdout.write("\nUse these credentials to test the Vue.js login at:")
        self.stdout.write("  http://localhost:5173/login")
        self.stdout.write("\n")
