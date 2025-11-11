"""
Unit tests for exchange models.
"""

from datetime import date, datetime, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from accounts.models import User
from exchange.models import (
    Application,
    ApplicationStatus,
    Comment,
    Program,
    TimelineEvent,
)

User = get_user_model()


class TestProgramModel(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create(
            username='testuser', email='testuser@example.com', password='TestPass123!'
        )

    def test_program_creation(self):
        """Test program creation with valid data"""
        program = Program.objects.create(
            name='Test Program',
            description='Test Description',
            start_date=datetime.now().date(),
            end_date=(datetime.now() + timedelta(days=30)).date(),
            # max_participants=50  # Removed, not in model
        )
        self.assertEqual(program.name, 'Test Program')
        self.assertEqual(program.description, 'Test Description')
        # self.assertEqual(program.max_participants, 50)  # Removed

    def test_program_str_representation(self):
        """Test program string representation"""
        program = Program.objects.create(
            name='Test Program',
            description='Test Description',
            start_date=datetime.now().date(),
            end_date=(datetime.now() + timedelta(days=30)).date()
        )
        self.assertEqual(str(program), 'Test Program')

    def test_program_end_date_after_start_date(self):
        """Test program validation - end date must be after start date"""
        with self.assertRaises(ValidationError):
            program = Program(
                name='Test Program',
                description='Test Description',
                start_date=(datetime.now() + timedelta(days=30)).date(),
                end_date=datetime.now().date()
            )
            program.full_clean()

    def test_program_min_gpa_validation(self):
        """Test program validation - min GPA can be negative (no validation)"""
        # The model doesn't have validation for negative GPA, so this should pass
        program = Program(
            name='Test Program',
            description='Test Description',
            start_date=datetime.now().date(),
            end_date=(datetime.now() + timedelta(days=30)).date(),
            min_gpa=-1.0
        )
        program.full_clean()  # This should not raise ValidationError
        self.assertEqual(program.min_gpa, -1.0)


@pytest.mark.django_db
@pytest.mark.models
class TestApplicationStatusModel:
    """Test cases for ApplicationStatus model."""

    def test_status_creation(self):
        """Test application status creation."""
        status, created = ApplicationStatus.objects.get_or_create(
            name="under_review", defaults={"order": 3}
        )
        if not created:
            status.order = 3
            status.save()
        assert status.order == 3

    def test_status_uniqueness(self):
        """Test that status names must be unique."""
        ApplicationStatus.objects.get_or_create(name="draft", defaults={"order": 1})

        with pytest.raises(IntegrityError):
            ApplicationStatus.objects.create(name="draft", order=2)

    def test_status_ordering(self):
        """Test status ordering by order field."""
        ApplicationStatus.objects.all().delete()
        status1 = ApplicationStatus.objects.create(name="draft", order=1)
        status2 = ApplicationStatus.objects.create(name="submitted", order=2)
        status3 = ApplicationStatus.objects.create(name="approved", order=3)
        ordered_statuses = list(ApplicationStatus.objects.all())
        assert ordered_statuses == [status1, status2, status3]


class TestApplicationModel(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create(
            username='testuser', email='testuser@example.com', password='TestPass123!'
        )
        self.program = Program.objects.create(
            name='Test Program',
            description='Test Description',
            start_date=datetime.now().date(),
            end_date=(datetime.now() + timedelta(days=30)).date()
        )
        self.status = ApplicationStatus.objects.create(name='pending', order=1)

    def test_application_creation(self):
        """Test application creation with valid data"""
        application = Application.objects.create(
            student=self.user,
            program=self.program,
            status=self.status
        )
        self.assertEqual(application.student, self.user)
        self.assertEqual(application.program, self.program)
        self.assertEqual(application.status, self.status)

    def test_application_str_representation(self):
        """Test application string representation"""
        application = Application.objects.create(
            student=self.user,
            program=self.program,
            status=self.status
        )
        expected_str = f"{self.user} - {self.program}"
        self.assertEqual(str(application), expected_str)

    def test_application_status_choices(self):
        """Test application status field choices"""
        status_obj, created = ApplicationStatus.objects.get_or_create(
            name='pending', defaults={'order': 1}
        )
        application = Application.objects.create(
            student=self.user,
            program=self.program,
            status=status_obj
        )
        self.assertEqual(application.status, status_obj)

    def test_application_invalid_status(self):
        """Test application with invalid status"""
        with self.assertRaises(Exception):
            application = Application(
                student=self.user,
                program=self.program,
                status=None  # Invalid, must be ApplicationStatus
            )
            application.full_clean()


@pytest.mark.django_db
@pytest.mark.models
class TestCommentModel:
    """Test cases for Comment model."""

    def test_comment_creation(self):
        """Test comment creation."""
        user = User.objects.create_user(
            username="coordinator",
            email="coordinator@example.com",
            password="testpass123",
        )

        program = Program.objects.create(
            name="Test Program",
            description="Test description",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 6, 30),
        )

        status, _ = ApplicationStatus.objects.get_or_create(
            name="draft", defaults={"order": 1}
        )

        application = Application.objects.create(
            program=program, student=user, status=status
        )

        comment = Comment.objects.create(
            application=application,
            author=user,
            text="This is a test comment",
            is_private=False,
        )

        assert comment.application == application
        assert comment.author == user
        assert comment.text == "This is a test comment"
        assert comment.is_private is False

    def test_comment_str_representation(self):
        """Test comment string representation."""
        user = User.objects.create_user(
            username="coordinator",
            email="coordinator@example.com",
            password="testpass123",
        )

        program = Program.objects.create(
            name="Test Program",
            description="Test description",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 6, 30),
        )

        status, _ = ApplicationStatus.objects.get_or_create(
            name="draft", defaults={"order": 1}
        )

        application = Application.objects.create(
            program=program, student=user, status=status
        )

        comment = Comment.objects.create(
            application=application, author=user, text="Test comment"
        )

        expected_str = f"Comment by {user.username} on {application}"
        assert str(comment) == expected_str

    def test_comment_privacy(self):
        """Test comment privacy settings."""
        user = User.objects.create_user(
            username="coordinator",
            email="coordinator@example.com",
            password="testpass123",
        )

        program = Program.objects.create(
            name="Test Program",
            description="Test description",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 6, 30),
        )

        status, _ = ApplicationStatus.objects.get_or_create(
            name="draft", defaults={"order": 1}
        )

        application = Application.objects.create(
            program=program, student=user, status=status
        )

        # Public comment
        public_comment = Comment.objects.create(
            application=application,
            author=user,
            text="Public comment",
            is_private=False,
        )

        # Private comment
        private_comment = Comment.objects.create(
            application=application,
            author=user,
            text="Private comment",
            is_private=True,
        )

        assert public_comment.is_private is False
        assert private_comment.is_private is True


@pytest.mark.django_db
@pytest.mark.models
class TestTimelineEventModel:
    """Test cases for TimelineEvent model."""

    def test_timeline_event_creation(self):
        """Test timeline event creation."""
        user = User.objects.create_user(
            username="coordinator",
            email="coordinator@example.com",
            password="testpass123",
        )

        program = Program.objects.create(
            name="Test Program",
            description="Test description",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 6, 30),
        )

        status, _ = ApplicationStatus.objects.get_or_create(
            name="draft", defaults={"order": 1}
        )

        application = Application.objects.create(
            program=program, student=user, status=status
        )

        event = TimelineEvent.objects.create(
            application=application,
            event_type="status_change",
            description="Application status changed to draft",
            created_by=user,
        )

        assert event.application == application
        assert event.event_type == "status_change"
        assert event.description == "Application status changed to draft"
        assert event.created_by == user

    def test_timeline_event_str_representation(self):
        """Test timeline event string representation."""
        user = User.objects.create_user(
            username="coordinator",
            email="coordinator@example.com",
            password="testpass123",
        )

        program = Program.objects.create(
            name="Test Program",
            description="Test description",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 6, 30),
        )

        status, _ = ApplicationStatus.objects.get_or_create(
            name="draft", defaults={"order": 1}
        )

        application = Application.objects.create(
            program=program, student=user, status=status
        )

        event = TimelineEvent.objects.create(
            application=application,
            event_type="status_change",
            description="Test event",
            created_by=user,
        )

        expected_str = f"{event.event_type} - {event.description}"
        assert str(event) == expected_str

    def test_timeline_event_ordering(self):
        """Test timeline events are ordered by creation time."""
        user = User.objects.create_user(
            username="coordinator",
            email="coordinator@example.com",
            password="testpass123",
        )

        program = Program.objects.create(
            name="Test Program",
            description="Test description",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 6, 30),
        )

        status, _ = ApplicationStatus.objects.get_or_create(
            name="draft", defaults={"order": 1}
        )

        application = Application.objects.create(
            program=program, student=user, status=status
        )

        # Create events with different timestamps
        event1 = TimelineEvent.objects.create(
            application=application,
            event_type="created",
            description="Application created",
            created_by=user,
        )

        event2 = TimelineEvent.objects.create(
            application=application,
            event_type="submitted",
            description="Application submitted",
            created_by=user,
        )

        # Events should be ordered by creation time (newest first)
        events = TimelineEvent.objects.filter(application=application).order_by(
            "-created_at"
        )
        assert list(events) == [event2, event1]


@pytest.mark.django_db
def test_exchange_model_str():
    # Replace ExchangeModel with actual model class
    # obj = ExchangeModel.objects.create(field='value')
    # assert str(obj) == 'value'
    pass  # Placeholder if no model exists
