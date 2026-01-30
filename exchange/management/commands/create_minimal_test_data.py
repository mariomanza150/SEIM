"""
Management command to create minimal test data for local development.
Creates: 1 admin, 1 coordinator, 1 student, 1 program, 1 application.
"""

from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Role, User
from exchange.models import Application, ApplicationStatus, Program


class Command(BaseCommand):
    help = "Create minimal test data (1 admin, 1 coordinator, 1 student, 1 program, 1 application)"

    def handle(self, *args, **options):
        self.stdout.write("Creating minimal test data...")

        # Get or create roles
        admin_role, _ = Role.objects.get_or_create(name="admin")
        coordinator_role, _ = Role.objects.get_or_create(name="coordinator")
        student_role, _ = Role.objects.get_or_create(name="student")

        # Create admin user
        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@seim.local",
                "first_name": "Admin",
                "last_name": "User",
                "is_email_verified": True,
                "is_active": True,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin_user.set_password("admin123")
            admin_user.save()
            self.stdout.write("  ✓ Created admin user: admin / admin123")
        else:
            self.stdout.write("  ✓ Admin user already exists: admin")
        admin_user.roles.add(admin_role)

        # Create coordinator user
        coordinator_user, created = User.objects.get_or_create(
            username="coordinator",
            defaults={
                "email": "coordinator@seim.local",
                "first_name": "Coordinator",
                "last_name": "User",
                "is_email_verified": True,
                "is_active": True,
            },
        )
        if created:
            coordinator_user.set_password("coordinator123")
            coordinator_user.save()
            self.stdout.write("  ✓ Created coordinator user: coordinator / coordinator123")
        else:
            self.stdout.write("  ✓ Coordinator user already exists: coordinator")
        coordinator_user.roles.add(coordinator_role)

        # Create student user
        student_user, created = User.objects.get_or_create(
            username="student",
            defaults={
                "email": "student@university.edu",
                "first_name": "Student",
                "last_name": "User",
                "is_email_verified": True,
                "is_active": True,
            },
        )
        if created:
            student_user.set_password("student123")
            student_user.save()
            # Update profile
            profile = student_user.profile
            profile.gpa = 3.5
            profile.language = "English"
            profile.save()
            self.stdout.write("  ✓ Created student user: student / student123")
        else:
            self.stdout.write("  ✓ Student user already exists: student")
        student_user.roles.add(student_role)

        # Create a program
        start_date = date.today() + timedelta(days=30)
        end_date = start_date + timedelta(days=180)
        program, created = Program.objects.get_or_create(
            name="Sample Exchange Program",
            defaults={
                "description": "A sample exchange program for testing purposes.",
                "start_date": start_date,
                "end_date": end_date,
                "is_active": True,
                "min_gpa": 3.0,
                "required_language": "English",
                "recurring": True,
            },
        )
        if created:
            self.stdout.write(f"  ✓ Created program: {program.name}")
        else:
            self.stdout.write(f"  ✓ Program already exists: {program.name}")

        # Create an application
        draft_status = ApplicationStatus.objects.get(name="draft")
        application, created = Application.objects.get_or_create(
            student=student_user,
            program=program,
            defaults={
                "status": draft_status,
            },
        )
        if created:
            self.stdout.write(f"  ✓ Created application: {student_user.username} -> {program.name}")
        else:
            self.stdout.write(f"  ✓ Application already exists: {student_user.username} -> {program.name}")

        self.stdout.write(self.style.SUCCESS("\n✅ Minimal test data created successfully!"))
        self.stdout.write("\n📋 Test Credentials:")
        self.stdout.write("   Admin: admin / admin123")
        self.stdout.write("   Coordinator: coordinator / coordinator123")
        self.stdout.write("   Student: student / student123")
        self.stdout.write("\n🌐 Access: http://localhost:8000")

