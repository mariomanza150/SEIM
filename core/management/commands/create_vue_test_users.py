"""
Management command to create test users for Vue.js frontend testing.
Creates users with different roles: admin, coordinator, and student.
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from accounts.models import Role
from accounts.profile_seed import complete_apply_profile
from qa.gating import assert_not_production, demo_password, demo_password_is_configured

User = get_user_model()


class Command(BaseCommand):
    help = "Create test users for Vue.js frontend development and testing"

    def handle(self, *args, **options):
        assert_not_production("create_vue_test_users")
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
                # Shared demo credentials must never grant superuser.
                "is_superuser": False,
                "is_email_verified": True,
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
                "is_email_verified": True,
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
                "is_email_verified": True,
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
                "is_email_verified": True,
            },
        ]

        created_count = 0
        updated_count = 0
        pw_label = (
            "TESTER_DEMO_PASSWORD"
            if demo_password_is_configured()
            else "legacy dev password"
        )

        for user_data in test_users:
            email = user_data.pop("email")
            password = demo_password(user_data.pop("password"))
            user_data["is_demo_account"] = True
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
                        f"  ✓ Created: {email} (password: {pw_label}) - Role: {role.name}"
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
                        f"  ↻ Updated: {email} (password: {pw_label}) - Role: {role.name}"
                    )
                )

            if role.name == "student":
                complete_apply_profile(user)

        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(self.style.SUCCESS(f"✓ Created {created_count} new users"))
        self.stdout.write(
            self.style.WARNING(f"↻ Updated {updated_count} existing users")
        )
        self.stdout.write("=" * 70)
        self.stdout.write("\nTest Credentials:")
        self.stdout.write("-" * 70)
        for label, email in (
            ("Admin", "admin@test.com"),
            ("Coordinator", "coordinator@test.com"),
            ("Student", "student@test.com"),
            ("Generic", "test@example.com"),
        ):
            self.stdout.write(f"  {label + ':':<13} {email} / {pw_label}")
        self.stdout.write("-" * 70)
        self.stdout.write("\nUse these credentials to test the Vue.js login at:")
        self.stdout.write("  http://localhost:5173/login")
        self.stdout.write("\n")
