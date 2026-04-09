from datetime import date

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.db.models import Q
from django.test import TestCase
from django.utils import timezone

from accounts.models import Role, User
from documents.models import Document, DocumentType
from exchange.models import (
    Application,
    ApplicationStatus,
    Comment,
    Program,
    TimelineEvent,
)
from notifications.models import Notification


class TestCleanupDemoDataCommand(TestCase):
    """Test the cleanup_demo_data management command with real assertions."""

    def setUp(self):
        """Set up test data that will be cleaned up."""
        # Create roles
        self.admin_role, _ = Role.objects.get_or_create(name="admin")
        self.coordinator_role, _ = Role.objects.get_or_create(name="coordinator")
        self.student_role, _ = Role.objects.get_or_create(name="student")

        # Create demo users with specific usernames that match cleanup patterns
        self.demo_users = []

        # Create admin users (should be cleaned up)
        for i in range(2):
            user = User.objects.create_user(
                username=f"admin{i+1}",
                email=f"admin{i+1}@seim.edu",
                password="admin123",
                first_name=f"Admin{i+1}",
                last_name="Demo",
                is_email_verified=True,
                is_active=True
            )
            user.roles.add(self.admin_role)
            self.demo_users.append(user)

        # Create coordinator users (should be cleaned up)
        for i in range(2):
            user = User.objects.create_user(
                username=f"coordinator{i+1}",
                email=f"coordinator{i+1}@seim.edu",
                password="coordinator123",
                first_name=f"Coordinator{i+1}",
                last_name="Demo",
                is_email_verified=True,
                is_active=True
            )
            user.roles.add(self.coordinator_role)
            self.demo_users.append(user)

        # Create student users (should be cleaned up)
        for i in range(3):
            user = User.objects.create_user(
                username=f"student{i+1}",
                email=f"student{i+1}@university.edu",
                password="student123",
                first_name=f"Student{i+1}",
                last_name="Demo",
                is_email_verified=True,
                is_active=True
            )
            user.roles.add(self.student_role)
            self.demo_users.append(user)

        # Create a regular user (should NOT be cleaned up)
        self.regular_user = User.objects.create_user(
            username="regular_user",
            email="regular@example.com",
            password="regular123",
            first_name="Regular",
            last_name="User",
            is_email_verified=True,
            is_active=True
        )

        # Create demo programs (should be cleaned up)
        self.demo_programs = []
        demo_program_names = [
            "Erasmus+ Computer Science Exchange",
            "Business Administration in Spain",
            "Engineering Exchange in Germany",
            "Arts and Culture in France",
        ]

        for name in demo_program_names:
            program = Program.objects.create(
                name=name,
                description=f"Demo program: {name}",
                start_date=date(2024, 1, 1),
                end_date=date(2024, 12, 31),
                min_gpa=3.0,
                required_language="English",
                recurring=True
            )
            self.demo_programs.append(program)

        # Create a regular program (should NOT be cleaned up)
        self.regular_program = Program.objects.create(
            name="Regular Exchange Program",
            description="This should not be cleaned up",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            min_gpa=3.0,
            required_language="English",
            recurring=True
        )

        # Create demo applications (should be cleaned up)
        self.demo_applications = []
        # Create a status for all applications
        self.status, _ = ApplicationStatus.objects.get_or_create(name="pending", defaults={"order": 1})
        for i, student in enumerate([u for u in self.demo_users if u.username.startswith("student")]):
            application = Application.objects.create(
                student=student,
                program=self.demo_programs[i % len(self.demo_programs)],
                status=self.status,
                created_at=timezone.now()
            )
            self.demo_applications.append(application)

        # Create a regular application (should NOT be cleaned up)
        self.regular_application = Application.objects.create(
            student=self.regular_user,
            program=self.regular_program,
            status=self.status,
            created_at=timezone.now()
        )

        # Create demo documents (should be cleaned up)
        self.demo_documents = []
        for application in self.demo_applications:
            doc_type, _ = DocumentType.objects.get_or_create(name="Transcript")
            document = Document.objects.create(
                application=application,
                type=doc_type,
                file=SimpleUploadedFile(f"demo_transcript_{application.id}.pdf", b"dummy content"),
                uploaded_by=application.student
            )
            self.demo_documents.append(document)

        # Create a regular document (should NOT be cleaned up)
        doc_type, _ = DocumentType.objects.get_or_create(name="Regular Document")
        self.regular_document = Document.objects.create(
            application=self.regular_application,
            type=doc_type,
            file=SimpleUploadedFile("regular_document.pdf", b"dummy content"),
            uploaded_by=self.regular_user
        )

        # Create demo comments (should be cleaned up)
        self.demo_comments = []
        for application in self.demo_applications:
            comment = Comment.objects.create(
                application=application,
                author=self.demo_users[0],  # Use first demo user
                text=f"Demo comment for application {application.id}",
                created_at=timezone.now()
            )
            self.demo_comments.append(comment)

        # Create a regular comment (should NOT be cleaned up)
        self.regular_comment = Comment.objects.create(
            application=self.regular_application,
            author=self.regular_user,
            text="Regular comment",
            created_at=timezone.now()
        )

        # Create demo timeline events (should be cleaned up)
        self.demo_timeline_events = []
        for application in self.demo_applications:
            event = TimelineEvent.objects.create(
                application=application,
                event_type="status_change",
                description=f"Demo timeline event for application {application.id}",
                created_at=timezone.now()
            )
            self.demo_timeline_events.append(event)

        # Create a regular timeline event (should NOT be cleaned up)
        self.regular_timeline_event = TimelineEvent.objects.create(
            application=self.regular_application,
            event_type="status_change",
            description="Regular timeline event",
            created_at=timezone.now()
        )

        # Create demo notifications (should be cleaned up)
        self.demo_notifications = []
        for user in self.demo_users:
            notification = Notification.objects.create(
                recipient=user,
                title=f"Demo notification for {user.username}",
                message=f"This is a demo notification for {user.username}",
                notification_type="in_app"
            )
            self.demo_notifications.append(notification)

        # Create a regular notification (should NOT be cleaned up)
        self.regular_notification = Notification.objects.create(
            recipient=self.regular_user,
            title="Regular notification",
            message="This should not be cleaned up",
            notification_type="in_app"
        )

    def test_cleanup_demo_data_command(self):
        """Test that the cleanup_demo_data command properly removes demo data."""
        # Debug: Check what users were actually created
        print(f"DEBUG: Total users in database: {User.objects.count()}")
        print(f"DEBUG: Users with admin prefix: {User.objects.filter(username__startswith='admin').count()}")
        print(f"DEBUG: Users with coordinator prefix: {User.objects.filter(username__startswith='coordinator').count()}")
        print(f"DEBUG: Users with student prefix: {User.objects.filter(username__startswith='student').count()}")
        print(f"DEBUG: All usernames: {list(User.objects.values_list('username', flat=True))}")

        # Verify initial state - demo data exists
        demo_user_count = User.objects.filter(
            Q(username__startswith="admin") |
            Q(username__startswith="coordinator") |
            Q(username__startswith="student")
        ).count()
        print(f"DEBUG: Demo user count from filter: {demo_user_count}")
        self.assertEqual(demo_user_count, 7)
        self.assertEqual(Program.objects.filter(name__in=[
            "Erasmus+ Computer Science Exchange",
            "Business Administration in Spain",
            "Engineering Exchange in Germany",
            "Arts and Culture in France",
        ]).count(), 4)
        self.assertEqual(Application.objects.filter(student__username__startswith="student").count(), 3)
        self.assertEqual(Document.objects.filter(uploaded_by__username__startswith="student").count(), 3)
        self.assertEqual(Comment.objects.filter(application__student__username__startswith="student").count(), 3)
        self.assertEqual(TimelineEvent.objects.filter(application__student__username__startswith="student").count(), 3)
        self.assertEqual(Notification.objects.filter(
            Q(recipient__username__startswith="admin") |
            Q(recipient__username__startswith="coordinator") |
            Q(recipient__username__startswith="student")
        ).count(), 7)

        # Verify regular data exists
        self.assertEqual(User.objects.filter(username="regular_user").count(), 1)
        self.assertEqual(Program.objects.filter(name="Regular Exchange Program").count(), 1)
        self.assertEqual(Application.objects.filter(student__username="regular_user").count(), 1)
        self.assertEqual(Document.objects.filter(uploaded_by__username="regular_user").count(), 1)
        self.assertEqual(Comment.objects.filter(author__username="regular_user").count(), 1)
        self.assertEqual(TimelineEvent.objects.filter(application__student__username="regular_user").count(), 1)
        self.assertEqual(Notification.objects.filter(recipient__username="regular_user").count(), 1)

        # Run the cleanup command
        call_command('cleanup_demo_data')

        # Debug: Check what users remain after cleanup
        print(f"DEBUG AFTER CLEANUP: Total users in database: {User.objects.count()}")
        print(f"DEBUG AFTER CLEANUP: Users with admin prefix: {User.objects.filter(username__startswith='admin').count()}")
        print(f"DEBUG AFTER CLEANUP: Users with coordinator prefix: {User.objects.filter(username__startswith='coordinator').count()}")
        print(f"DEBUG AFTER CLEANUP: Users with student prefix: {User.objects.filter(username__startswith='student').count()}")
        print(f"DEBUG AFTER CLEANUP: All usernames: {list(User.objects.values_list('username', flat=True))}")

        # Verify demo data is cleaned up
        # After cleanup
        demo_user_count_after = User.objects.filter(
            Q(username__startswith="admin") |
            Q(username__startswith="coordinator") |
            Q(username__startswith="student")
        ).count()
        print(f"DEBUG AFTER CLEANUP: Demo user count from filter: {demo_user_count_after}")
        self.assertEqual(demo_user_count_after, 0)
        self.assertEqual(Program.objects.filter(name__in=[
            "Erasmus+ Computer Science Exchange",
            "Business Administration in Spain",
            "Engineering Exchange in Germany",
            "Arts and Culture in France",
        ]).count(), 0)
        self.assertEqual(Application.objects.filter(student__username__startswith="student").count(), 0)
        self.assertEqual(Document.objects.filter(uploaded_by__username__startswith="student").count(), 0)
        self.assertEqual(Comment.objects.filter(application__student__username__startswith="student").count(), 0)
        self.assertEqual(TimelineEvent.objects.filter(application__student__username__startswith="student").count(), 0)
        self.assertEqual(Notification.objects.filter(
            Q(recipient__username__startswith="admin") |
            Q(recipient__username__startswith="coordinator") |
            Q(recipient__username__startswith="student")
        ).count(), 0)

        # Verify regular data is preserved
        self.assertEqual(User.objects.filter(username="regular_user").count(), 1)
        self.assertEqual(Program.objects.filter(name="Regular Exchange Program").count(), 1)
        self.assertEqual(Application.objects.filter(student__username="regular_user").count(), 1)
        self.assertEqual(Document.objects.filter(uploaded_by__username="regular_user").count(), 1)
        self.assertEqual(Comment.objects.filter(author__username="regular_user").count(), 1)
        self.assertEqual(TimelineEvent.objects.filter(application__student__username="regular_user").count(), 1)
        self.assertEqual(Notification.objects.filter(recipient__username="regular_user").count(), 1)

        # Verify that related objects are also cleaned up (cascade deletes)
        self.assertEqual(Comment.objects.count(), 1)  # Only the regular comment remains
        self.assertEqual(TimelineEvent.objects.count(), 1)  # Only the regular event remains
        self.assertEqual(Document.objects.count(), 1)  # Only the regular document remains


class TestCleanupDemoDataCommandSafety(TestCase):
    """Ensure cleanup targets seeded demo accounts, not arbitrary prefix matches."""

    def setUp(self):
        self.student_role, _ = Role.objects.get_or_create(name="student")
        self.status, _ = ApplicationStatus.objects.get_or_create(
            name="draft",
            defaults={"order": 1},
        )

        self.student_like_user = User.objects.create_user(
            username="student_real",
            email="student.real@company.com",
            password="real123",
            first_name="Real",
            last_name="Student",
            is_email_verified=True,
            is_active=True,
        )
        self.student_like_user.roles.add(self.student_role)

        self.program = Program.objects.create(
            name="Regular Safety Program",
            description="Program that should survive cleanup.",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            min_gpa=3.0,
            required_language="English",
            recurring=True,
        )

        self.application = Application.objects.create(
            student=self.student_like_user,
            program=self.program,
            status=self.status,
            created_at=timezone.now(),
        )

        self.notification = Notification.objects.create(
            recipient=self.student_like_user,
            title="Real user notification",
            message="This should remain after cleanup.",
            notification_type="in_app",
        )

    def test_cleanup_demo_data_preserves_non_demo_prefix_users(self):
        call_command("cleanup_demo_data")

        self.assertTrue(User.objects.filter(username="student_real").exists())
        self.assertTrue(
            Application.objects.filter(student__username="student_real").exists()
        )
        self.assertTrue(
            Notification.objects.filter(recipient__username="student_real").exists()
        )
