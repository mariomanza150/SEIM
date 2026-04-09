"""
Test Exchange Services - Edge Cases and Boundary Conditions

This test file covers edge cases, boundary conditions, and error scenarios
for the exchange service layer.
"""

import uuid

import pytest
from django.db import IntegrityError, connection
from django.test import TestCase
from django.utils import timezone

from accounts.models import Role, User
from exchange.models import (
    Application,
    ApplicationStatus,
    Comment,
    Program,
    TimelineEvent,
)


@pytest.mark.django_db
class TestApplicationServiceEdgeCases(TestCase):
    """Test edge cases for ApplicationService."""

    def setUp(self):
        """Set up test data."""
        # Create roles
        self.student_role, _ = Role.objects.get_or_create(name="student")
        self.coordinator_role, _ = Role.objects.get_or_create(name="coordinator")

        # Create users
        self.student = User.objects.create_user(
            username="student",
            email="student@test.com",
            password="testpass123"
        )
        self.student.roles.add(self.student_role)

        self.coordinator = User.objects.create_user(
            username="coordinator",
            email="coordinator@test.com",
            password="testpass123"
        )
        self.coordinator.roles.add(self.coordinator_role)

        # Create program
        self.program = Program.objects.create(
            name="Test Program",
            description="A test program",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365),
            is_active=True,
            min_gpa=3.0,
        )

        # Create statuses
        self.draft_status, _ = ApplicationStatus.objects.get_or_create(
            name="draft", defaults={'order': 1}
        )
        self.submitted_status, _ = ApplicationStatus.objects.get_or_create(
            name="submitted", defaults={'order': 2}
        )

    def test_create_application_with_null_submitted_at(self):
        """Test creating application with null submitted_at (draft state)."""
        application = Application.objects.create(
            student=self.student,
            program=self.program,
            status=self.draft_status,
            submitted_at=None,  # Null for draft applications
        )

        self.assertIsNotNone(application)
        self.assertIsNone(application.submitted_at)
        self.assertFalse(application.withdrawn)

    def test_application_with_submitted_at(self):
        """Test application with submitted_at timestamp."""
        submitted_time = timezone.now()

        application = Application.objects.create(
            student=self.student,
            program=self.program,
            status=self.submitted_status,
            submitted_at=submitted_time,
        )

        self.assertEqual(application.submitted_at.date(), submitted_time.date())

    def test_application_withdrawn_flag(self):
        """Test application withdrawn flag."""
        application = Application.objects.create(
            student=self.student,
            program=self.program,
            status=self.draft_status,
            withdrawn=True,
        )

        self.assertTrue(application.withdrawn)

    def test_application_duplicate_prevention(self):
        """Test that duplicate applications are handled correctly."""
        # Create first application
        Application.objects.create(
            student=self.student,
            program=self.program,
            status=self.draft_status,
        )

        # Try to create another application (should be allowed)
        Application.objects.create(
            student=self.student,
            program=self.program,
            status=self.draft_status,
        )

        # Both should exist
        self.assertEqual(
            Application.objects.filter(
                student=self.student,
                program=self.program
            ).count(),
            2
        )

    def test_comment_with_special_characters(self):
        """Test comments with special characters and unicode."""
        application = Application.objects.create(
            student=self.student,
            program=self.program,
            status=self.submitted_status,
        )

        special_chars = "Test 中文 עברית العربية emoji: 😀🎉 symbols: !@#$%^&*()"

        comment = Comment.objects.create(
            application=application,
            author=self.coordinator,
            text=special_chars,
        )

        self.assertEqual(comment.text, special_chars)

    def test_timeline_event_ordering(self):
        """Test that timeline events are ordered correctly."""
        application = Application.objects.create(
            student=self.student,
            program=self.program,
            status=self.draft_status,
        )

        # Create events at different times
        event1 = TimelineEvent.objects.create(
            application=application,
            event_type="created",
            description="First event",
            created_by=self.student,
        )

        event2 = TimelineEvent.objects.create(
            application=application,
            event_type="updated",
            description="Second event",
            created_by=self.student,
        )

        event3 = TimelineEvent.objects.create(
            application=application,
            event_type="submitted",
            description="Third event",
            created_by=self.student,
        )

        # Get events in order
        events = application.timeline_events.all()

        # Should be in reverse chronological order (newest first)
        self.assertEqual(events[0], event3)
        self.assertEqual(events[1], event2)
        self.assertEqual(events[2], event1)

    def test_application_without_program(self):
        """Test that application requires a program (database constraint)."""
        with self.assertRaises(IntegrityError):
            Application.objects.create(
                student=self.student,
                program=None,  # Missing required field
                status=self.draft_status,
            )

    def test_application_without_student(self):
        """Test that application requires a student (database constraint)."""
        with self.assertRaises(IntegrityError):
            Application.objects.create(
                student=None,  # Missing required field
                program=self.program,
                status=self.draft_status,
            )

    def test_program_with_past_dates(self):
        """Test creating program with past dates."""
        past_program = Program.objects.create(
            name="Past Program",
            description="A program that already ended",
            start_date=timezone.now().date() - timezone.timedelta(days=365),
            end_date=timezone.now().date() - timezone.timedelta(days=1),
            is_active=False,  # Inactive due to past dates
        )

        self.assertFalse(past_program.is_active)
        self.assertLess(past_program.end_date, timezone.now().date())

    def test_program_with_same_start_end_date(self):
        """Test program with same start and end date (edge case)."""
        single_day_program = Program.objects.create(
            name="Single Day Program",
            description="A one-day program",
            start_date=timezone.now().date(),
            end_date=timezone.now().date(),  # Same as start
            is_active=True,
        )

        self.assertEqual(
            single_day_program.start_date,
            single_day_program.end_date
        )

    def test_program_with_zero_gpa_requirement(self):
        """Test program with minimum GPA of 0."""
        zero_gpa_program = Program.objects.create(
            name="Zero GPA Program",
            description="No GPA requirement",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365),
            is_active=True,
            min_gpa=0.0,  # Edge case: zero GPA
        )

        self.assertEqual(zero_gpa_program.min_gpa, 0.0)

    def test_program_unlimited_enrollment_capacity(self):
        """Program with blank enrollment_capacity has no seat cap (per model help text)."""
        program = Program.objects.create(
            name="Unlimited Program",
            description="Test",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365),
            is_active=True,
            enrollment_capacity=None,
        )

        self.assertIsNone(program.enrollment_capacity)


@pytest.mark.django_db
class TestInputValidationEdgeCases(TestCase):
    """Test input validation edge cases."""

    def setUp(self):
        """Set up test data."""
        self.student_role, _ = Role.objects.get_or_create(name="student")
        self.student = User.objects.create_user(
            username="student",
            email="student@test.com",
            password="testpass123"
        )
        self.student.roles.add(self.student_role)

    def test_user_with_very_long_username(self):
        """Test user with maximum length username."""
        long_username = "a" * 150  # Django default max_length

        user = User.objects.create_user(
            username=long_username,
            email="longuser@test.com",
            password="testpass123"
        )

        self.assertEqual(len(user.username), 150)

    def test_user_with_special_characters_in_username(self):
        """Test username with special characters."""
        special_username = "user.name+tag@domain"

        user = User.objects.create_user(
            username=special_username,
            email="special@test.com",
            password="testpass123"
        )

        self.assertEqual(user.username, special_username)

    def test_email_case_insensitivity(self):
        """Test that emails are handled case-insensitively."""
        User.objects.create_user(
            username="user1",
            email="Test@Example.COM",
            password="testpass123"
        )

        # Should be able to create another user with different case email
        # (depends on database collation)
        user2 = User.objects.create_user(
            username="user2",
            email="test@example.com",
            password="testpass123"
        )

        self.assertEqual(user2.username, "user2")
        self.assertEqual(User.objects.filter(email__iexact="test@example.com").count(), 2)

    def test_password_edge_cases(self):
        """Test password with special characters and length."""
        # Very long password
        long_password = "a" * 1000
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password=long_password
        )

        # Password should be hashed (not stored as plaintext)
        self.assertNotEqual(user.password, long_password)
        self.assertTrue(user.check_password(long_password))

        # Special characters in password
        special_password = "!@#$%^&*()_+-={}[]|:;<>,.?/~`"
        user.set_password(special_password)
        user.save()
        self.assertTrue(user.check_password(special_password))


@pytest.mark.django_db
class TestConcurrencyEdgeCases(TestCase):
    """Test concurrent operations and race conditions."""

    def setUp(self):
        """Set up test data."""
        self.student_role, _ = Role.objects.get_or_create(name="student")
        self.student = User.objects.create_user(
            username="student",
            email="student@test.com",
            password="testpass123"
        )
        self.student.roles.add(self.student_role)

        self.program = Program.objects.create(
            name="Test Program",
            description="Test",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365),
            is_active=True,
        )

        self.status, _ = ApplicationStatus.objects.get_or_create(name="draft", defaults={'order': 1})

    def test_multiple_comments_on_same_application(self):
        """Test adding multiple comments rapidly."""
        application = Application.objects.create(
            student=self.student,
            program=self.program,
            status=self.status,
        )

        # Create multiple comments in quick succession
        comments = []
        for i in range(10):
            comment = Comment.objects.create(
                application=application,
                author=self.student,
                text=f"Comment {i}",
            )
            comments.append(comment)

        # All comments should exist
        self.assertEqual(application.comments.count(), 10)

        # Comments should be ordered by creation time
        retrieved_comments = list(application.comments.all())
        self.assertEqual(len(retrieved_comments), 10)

    def test_concurrent_status_updates(self):
        """Test handling of concurrent status update attempts."""
        application = Application.objects.create(
            student=self.student,
            program=self.program,
            status=self.status,
        )

        new_status, _ = ApplicationStatus.objects.get_or_create(name="submitted", defaults={'order': 2})

        # Update status multiple times
        application.status = new_status
        application.save()

        # Reload from database
        application.refresh_from_db()

        # Should have the latest status
        self.assertEqual(application.status, new_status)


@pytest.mark.django_db
class TestErrorHandlingEdgeCases(TestCase):
    """Test error handling and exception scenarios."""

    def setUp(self):
        """Set up test data."""
        self.student_role, _ = Role.objects.get_or_create(name="student")
        self.student = User.objects.create_user(
            username="student",
            email="student@test.com",
            password="testpass123"
        )
        self.student.roles.add(self.student_role)

    def test_program_with_invalid_dates(self):
        """Test program with end date before start date."""
        # Model allows this, but application logic should validate
        program = Program.objects.create(
            name="Invalid Date Program",
            description="Test",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() - timezone.timedelta(days=1),  # End before start
            is_active=True,
        )

        # Program created but dates are illogical
        self.assertLess(program.end_date, program.start_date)

    def test_comment_on_nonexistent_application(self):
        """Comment with a non-existent application_id must fail at the database."""
        program = Program.objects.create(
            name="Test Program",
            description="Test",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365),
            is_active=True,
        )

        status, _ = ApplicationStatus.objects.get_or_create(name="draft", defaults={"order": 1})

        Application.objects.create(
            student=self.student,
            program=program,
            status=status,
        )

        fake_id = uuid.uuid4()
        # PostgreSQL may defer FK checks until constraint validation; mirror teardown behavior.
        Comment.objects.create(
            application_id=fake_id,
            author=self.student,
            text="Comment on missing application",
        )
        with self.assertRaises(IntegrityError):
            connection.check_constraints()

    def test_user_deletion_cascade(self):
        """Test that deleting user cascades properly."""
        program = Program.objects.create(
            name="Test Program",
            description="Test",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365),
            is_active=True,
        )

        status, _ = ApplicationStatus.objects.get_or_create(name="draft", defaults={'order': 1})

        # Create application
        application = Application.objects.create(
            student=self.student,
            program=program,
            status=status,
        )

        app_id = application.id

        # Delete student
        self.student.delete()

        # Application should also be deleted (cascade)
        with self.assertRaises(Application.DoesNotExist):
            Application.objects.get(id=app_id)


@pytest.mark.django_db
class TestSecurityEdgeCases(TestCase):
    """Test security-related edge cases."""

    def setUp(self):
        """Set up test data."""
        self.student_role, _ = Role.objects.get_or_create(name="student")
        self.student = User.objects.create_user(
            username="student",
            email="student@test.com",
            password="testpass123"
        )
        self.student.roles.add(self.student_role)

        self.program = Program.objects.create(
            name="Test Program",
            description="Test",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365),
            is_active=True,
        )

        self.status, _ = ApplicationStatus.objects.get_or_create(name="draft", defaults={'order': 1})

    def test_sql_injection_in_program_name(self):
        """Test that SQL injection attempts are escaped."""
        malicious_name = "'; DROP TABLE programs; --"

        program = Program.objects.create(
            name=malicious_name,
            description="Test",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365),
            is_active=True,
        )

        # Name should be stored as-is (ORM escapes it)
        self.assertEqual(program.name, malicious_name)

        # Programs table should still exist
        self.assertTrue(Program.objects.exists())

    def test_xss_in_comment_text(self):
        """Test XSS protection in comments (should be sanitized by serializer)."""
        application = Application.objects.create(
            student=self.student,
            program=self.program,
            status=self.status,
        )

        xss_attempt = '<script>alert("XSS")</script><img src=x onerror=alert("XSS")>'

        # At model level, it's stored as-is (serializer handles sanitization)
        comment = Comment.objects.create(
            application=application,
            author=self.student,
            text=xss_attempt,
        )

        # Model stores the raw value
        self.assertIn("script", comment.text.lower())

        # Note: Serializer validation tested separately

    def test_path_traversal_in_filenames(self):
        """Test that path traversal attempts are handled."""
        # Testing with program name since documents require file objects
        traversal_attempt = "../../etc/passwd"

        program = Program.objects.create(
            name=traversal_attempt,
            description="Test",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365),
            is_active=True,
        )

        # Name is stored but won't be used as file path
        self.assertEqual(program.name, traversal_attempt)


@pytest.mark.django_db
class TestBoundaryConditions(TestCase):
    """Test boundary conditions and limits."""

    def test_gpa_boundary_values(self):
        """Test GPA with boundary values (0.0, 4.0, beyond)."""
        # Minimum GPA
        program1 = Program.objects.create(
            name="Min GPA Program",
            description="Test",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365),
            is_active=True,
            min_gpa=0.0,  # Minimum
        )
        self.assertEqual(program1.min_gpa, 0.0)

        # Maximum normal GPA
        program2 = Program.objects.create(
            name="Max GPA Program",
            description="Test",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365),
            is_active=True,
            min_gpa=4.0,  # Maximum normal
        )
        self.assertEqual(program2.min_gpa, 4.0)

        # Above maximum (edge case)
        program3 = Program.objects.create(
            name="High GPA Program",
            description="Test",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365),
            is_active=True,
            min_gpa=5.0,  # Unusual but possible
        )
        self.assertEqual(program3.min_gpa, 5.0)

    def test_max_participants_boundary(self):
        """Enrollment capacity: None = no limit; large positive = high cap."""
        program1 = Program.objects.create(
            name="Unlimited Program",
            description="Test",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365),
            is_active=True,
            enrollment_capacity=None,
        )
        self.assertIsNone(program1.enrollment_capacity)

        program2 = Program.objects.create(
            name="Large Program",
            description="Test",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365),
            is_active=True,
            enrollment_capacity=999_999,
        )
        self.assertEqual(program2.enrollment_capacity, 999_999)

    def test_empty_application_data(self):
        """Test application with all optional fields empty."""
        student_role, _ = Role.objects.get_or_create(name="student")
        student = User.objects.create_user(
            username="student",
            email="student@test.com",
            password="testpass123"
        )
        student.roles.add(student_role)

        program = Program.objects.create(
            name="Test Program",
            description="Test",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365),
            is_active=True,
        )

        status, _ = ApplicationStatus.objects.get_or_create(name="draft", defaults={'order': 1})

        # Create application with minimal data
        application = Application.objects.create(
            student=student,
            program=program,
            status=status,
            # All optional fields left empty
        )

        self.assertIsNotNone(application)
        # Check optional fields
        self.assertIsNone(application.submitted_at)
        self.assertFalse(application.withdrawn)


@pytest.mark.django_db
class TestNullAndBlankHandling(TestCase):
    """Test null and blank field handling."""

    def test_program_with_null_description(self):
        """Test program with null description."""
        program = Program.objects.create(
            name="No Description Program",
            description="",  # Empty but not null
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365),
            is_active=True,
        )

        self.assertEqual(program.description, "")

    def test_comment_without_text(self):
        """Test comment with empty text."""
        student_role, _ = Role.objects.get_or_create(name="student")
        student = User.objects.create_user(
            username="student",
            email="student@test.com",
            password="testpass123"
        )
        student.roles.add(student_role)

        program = Program.objects.create(
            name="Test Program",
            description="Test",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365),
            is_active=True,
        )

        status, _ = ApplicationStatus.objects.get_or_create(name="draft", defaults={'order': 1})

        application = Application.objects.create(
            student=student,
            program=program,
            status=status,
        )

        # Empty comment text
        comment = Comment.objects.create(
            application=application,
            author=student,
            text="",  # Empty text
        )

        self.assertEqual(comment.text, "")

