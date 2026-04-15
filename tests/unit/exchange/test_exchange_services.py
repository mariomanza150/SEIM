"""
Unit tests for exchange services.
"""

from datetime import date, timedelta
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model

from exchange.models import (
    Application,
    ApplicationStatus,
    Comment,
    Program,
    TimelineEvent,
)
from exchange.services import ApplicationService

User = get_user_model()


@pytest.fixture
def test_data():
    """Create test data for all tests."""
    from accounts.models import Role
    
    user = User.objects.create(
        username="testuser",
        email="test@example.com",
        password="testpass123",
    )
    # Assign student role
    student_role, _ = Role.objects.get_or_create(name="student")
    user.roles.add(student_role)
    
    # Create application statuses using get_or_create
    draft_status, _ = ApplicationStatus.objects.get_or_create(name="draft")
    submitted_status, _ = ApplicationStatus.objects.get_or_create(name="submitted")
    approved_status, _ = ApplicationStatus.objects.get_or_create(name="approved")
    rejected_status, _ = ApplicationStatus.objects.get_or_create(name="rejected")
    withdrawn_status, _ = ApplicationStatus.objects.get_or_create(name="withdrawn")
    # Create programs
    today = date.today()
    program = Program.objects.create(
        name="Test Program",
        description="Test Description",
        is_active=True,
        start_date=today,
        end_date=today + timedelta(days=30)
    )
    # Create applications
    application = Application.objects.create(
        student=user,
        program=program,
        status=draft_status
    )
    return {
        'user': user,
        'draft_status': draft_status,
        'submitted_status': submitted_status,
        'approved_status': approved_status,
        'rejected_status': rejected_status,
        'withdrawn_status': withdrawn_status,
        'program': program,
        'application': application
    }

@pytest.fixture
def test_data_no_profile():
    """Create test data with a user that has no profile (for testing missing profile scenarios)."""
    # Temporarily disable the profile creation signal
    from django.db.models.signals import post_save

    from accounts.signals import create_user_profile

    # Disconnect the signal
    post_save.disconnect(create_user_profile, sender=User)

    # Create user normally
    user = User.objects.create(
        username="testuser_noprofile",
        email="test_noprofile@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User"
    )

    # Reconnect the signal
    post_save.connect(create_user_profile, sender=User)

    # Ensure no profile exists
    from accounts.models import Profile
    Profile.objects.filter(user=user).delete()

    # Create application statuses using get_or_create
    draft_status, _ = ApplicationStatus.objects.get_or_create(name="draft")
    submitted_status, _ = ApplicationStatus.objects.get_or_create(name="submitted")
    approved_status, _ = ApplicationStatus.objects.get_or_create(name="approved")
    rejected_status, _ = ApplicationStatus.objects.get_or_create(name="rejected")
    withdrawn_status, _ = ApplicationStatus.objects.get_or_create(name="withdrawn")

    # Create programs
    today = date.today()
    program = Program.objects.create(
        name="Test Program No Profile",
        description="Test Description",
        is_active=True,
        start_date=today,
        end_date=today + timedelta(days=30)
    )

    # Create applications
    application = Application.objects.create(
        student=user,
        program=program,
        status=draft_status
    )

    return {
        'user': user,
        'draft_status': draft_status,
        'submitted_status': submitted_status,
        'approved_status': approved_status,
        'rejected_status': rejected_status,
        'withdrawn_status': withdrawn_status,
        'program': program,
        'application': application
    }

@pytest.mark.django_db
class TestApplicationService:

    def test_check_eligibility_success(self, test_data):
        """Test successful eligibility check."""
        from accounts.models import Profile
        Profile.objects.update_or_create(
            user=test_data['user'],
            defaults={
                'gpa': 3.5,
                'language': "English"
            }
        )
        result = ApplicationService.check_eligibility(test_data['user'], test_data['program'])
        assert isinstance(result, dict)
        assert result['eligible'] is True
        assert result['message'] == "All eligibility requirements met"
        assert result.get("schema_version") == 4

    def test_check_eligibility_missing_profile(self, test_data_no_profile):
        """Test eligibility check with missing profile."""
        with pytest.raises(ValueError, match="Student profile is missing"):
            ApplicationService.check_eligibility(test_data_no_profile['user'], test_data_no_profile['program'])

    def test_check_eligibility_low_gpa(self, test_data):
        """Test eligibility check with low GPA."""
        from accounts.models import Profile
        # Ensure no profile exists first, then create one with low GPA
        Profile.objects.filter(user=test_data['user']).delete()
        Profile.objects.update_or_create(
            user=test_data['user'],
            defaults={
                'gpa': 2.0,
                'language': "English"
            }
        )

        # Set program minimum GPA
        test_data['program'].min_gpa = 3.0
        test_data['program'].save()

        with pytest.raises(ValueError, match="GPA below program minimum"):
            ApplicationService.check_eligibility(test_data['user'], test_data['program'])

    def test_check_eligibility_language_mismatch(self, test_data):
        """Test eligibility check with language mismatch."""
        from accounts.models import Profile
        Profile.objects.update_or_create(
            user=test_data['user'],
            defaults={
                'gpa': 3.5,
                'language': "Spanish"
            }
        )

        # Set program required language
        test_data['program'].required_language = "English"
        test_data['program'].save()

        with pytest.raises(ValueError, match="Language requirement not met"):
            ApplicationService.check_eligibility(test_data['user'], test_data['program'])

    def test_can_submit_application_no_existing(self, test_data):
        """Test can submit application when no existing active application."""
        result = ApplicationService.can_submit_application(test_data['user'], test_data['program'])
        assert result is True

    def test_can_submit_application_existing_draft(self, test_data):
        """Test can submit application when existing draft application."""
        # Create another draft application
        Application.objects.create(
            student=test_data['user'],
            program=test_data['program'],
            status=test_data['draft_status']
        )

        result = ApplicationService.can_submit_application(test_data['user'], test_data['program'])
        assert result is True  # Draft applications don't block submission

    def test_can_submit_application_existing_submitted(self, test_data):
        """Test can submit application when existing submitted application."""
        # Create a submitted application
        Application.objects.create(
            student=test_data['user'],
            program=test_data['program'],
            status=test_data['submitted_status']
        )

        result = ApplicationService.can_submit_application(test_data['user'], test_data['program'])
        assert result is False  # Submitted applications block new submissions

    def test_can_submit_application_excludes_current_application(self, test_data):
        """Excluding the instance allows PATCH/update validation for that same application."""
        app = Application.objects.create(
            student=test_data["user"],
            program=test_data["program"],
            status=test_data["submitted_status"],
        )
        assert (
            ApplicationService.can_submit_application(
                test_data["user"], test_data["program"], exclude_application=app
            )
            is True
        )

    def test_can_submit_application_existing_waitlist(self, test_data):
        """Waitlisted applications block creating another for the same program."""
        waitlist_status, _ = ApplicationStatus.objects.get_or_create(
            name="waitlist", defaults={"order": 15}
        )
        Application.objects.create(
            student=test_data['user'],
            program=test_data['program'],
            status=waitlist_status,
        )
        assert ApplicationService.can_submit_application(test_data['user'], test_data['program']) is False

    def test_submit_application_waitlist_when_at_capacity(self, test_data):
        """When capacity is full and waitlist is enabled, submit places the app on the waitlist."""
        waitlist_status, _ = ApplicationStatus.objects.get_or_create(
            name="waitlist", defaults={"order": 15}
        )
        from accounts.models import Profile

        other = User.objects.create(
            username="other_student",
            email="other@example.com",
            password="testpass123",
        )
        from accounts.models import Role

        student_role, _ = Role.objects.get_or_create(name="student")
        other.roles.add(student_role)
        Profile.objects.update_or_create(
            user=other,
            defaults={"gpa": 3.5, "language": "English"},
        )
        Profile.objects.update_or_create(
            user=test_data['user'],
            defaults={"gpa": 3.5, "language": "English"},
        )

        test_data["program"].enrollment_capacity = 1
        test_data["program"].waitlist_when_full = True
        test_data["program"].save(update_fields=["enrollment_capacity", "waitlist_when_full"])

        Application.objects.create(
            student=other,
            program=test_data["program"],
            status=test_data["submitted_status"],
        )

        with patch("exchange.services.NotificationService.send_notification"), patch(
            "exchange.services.NotificationService.broadcast_application_sync"
        ):
            result = ApplicationService.submit_application(
                test_data["application"], test_data["user"]
            )

        result.refresh_from_db()
        assert result.status == waitlist_status
        assert result.submitted_at is not None

    def test_submit_application_raises_when_at_capacity_no_waitlist(self, test_data):
        from accounts.models import Profile

        other = User.objects.create(
            username="other_student2",
            email="other2@example.com",
            password="testpass123",
        )
        from accounts.models import Role

        student_role, _ = Role.objects.get_or_create(name="student")
        other.roles.add(student_role)
        Profile.objects.update_or_create(
            user=other,
            defaults={"gpa": 3.5, "language": "English"},
        )
        Profile.objects.update_or_create(
            user=test_data['user'],
            defaults={"gpa": 3.5, "language": "English"},
        )

        test_data["program"].enrollment_capacity = 1
        test_data["program"].waitlist_when_full = False
        test_data["program"].save(update_fields=["enrollment_capacity", "waitlist_when_full"])

        Application.objects.create(
            student=other,
            program=test_data["program"],
            status=test_data["submitted_status"],
        )

        with pytest.raises(ValueError, match="enrollment capacity"):
            with patch("exchange.services.NotificationService.send_notification"):
                ApplicationService.submit_application(
                    test_data["application"], test_data["user"]
                )

    def test_submit_application_success(self, test_data):
        """Test successful application submission."""
        from accounts.models import Profile
        Profile.objects.update_or_create(
            user=test_data['user'],
            defaults={
                'gpa': 3.5,
                'language': "English"
            }
        )

        with patch('exchange.services.NotificationService.send_notification') as mock_notify:
            result = ApplicationService.submit_application(test_data['application'], test_data['user'])

            assert result.status == test_data['submitted_status']
            assert result.submitted_at is not None
            assert mock_notify.called

    def test_submit_application_not_draft(self, test_data):
        """Test submitting non-draft application."""
        test_data['application'].status = test_data['submitted_status']
        test_data['application'].save()

        with pytest.raises(ValueError, match="Only draft applications can be submitted"):
            ApplicationService.submit_application(test_data['application'], test_data['user'])

    def test_submit_application_eligibility_failure(self, test_data_no_profile):
        """Test submitting application with eligibility failure."""
        with pytest.raises(ValueError, match="Student profile is missing"):
            ApplicationService.submit_application(test_data_no_profile['application'], test_data_no_profile['user'])

    def test_submit_application_fails_when_application_window_closed(self, test_data):
        from accounts.models import Profile

        Profile.objects.update_or_create(
            user=test_data["user"],
            defaults={"gpa": 3.5, "language": "English"},
        )
        program = test_data["program"]
        program.application_open_date = date.today() - timedelta(days=20)
        program.application_deadline = date.today() - timedelta(days=1)
        program.save(update_fields=["application_open_date", "application_deadline"])
        with pytest.raises(ValueError, match="Applications closed on"):
            ApplicationService.submit_application(test_data["application"], test_data["user"])

    def test_submit_application_existing_active(self, test_data):
        """Test submitting application when existing active application."""
        from accounts.models import Profile
        Profile.objects.update_or_create(
            user=test_data['user'],
            defaults={
                'gpa': 3.5,
                'language': "English"
            }
        )

        # Create an existing submitted application
        Application.objects.create(
            student=test_data['user'],
            program=test_data['program'],
            status=test_data['submitted_status']
        )

        with pytest.raises(ValueError, match="You already have an active application"):
            ApplicationService.submit_application(test_data['application'], test_data['user'])

    def test_submit_application_withdrawn(self, test_data):
        """Test that a withdrawn application cannot be submitted."""
        test_data['application'].status = test_data['withdrawn_status']
        test_data['application'].withdrawn = True
        test_data['application'].save()
        with pytest.raises(ValueError, match="Only draft applications can be submitted"):
            ApplicationService.submit_application(test_data['application'], test_data['user'])

    def test_can_transition_status_student_to_approved(self, test_data):
        """Test that students cannot transition to approved status."""
        result = ApplicationService.can_transition_status(test_data['user'], test_data['application'], "approved")
        assert result is False

    def test_can_transition_status_student_to_submitted(self, test_data):
        """Test that students can transition to submitted status."""
        result = ApplicationService.can_transition_status(test_data['user'], test_data['application'], "submitted")
        assert result is True

    def test_can_transition_status_coordinator_to_approved(self, test_data):
        """Test that coordinators can transition to approved status."""
        # Create a coordinator user
        coordinator = User.objects.create(
            username="coordinator",
            email="coordinator@example.com",
            password="testpass123",
        )

        # Mock the has_role method
        with patch.object(coordinator, 'has_role') as mock_has_role:
            mock_has_role.return_value = True

            result = ApplicationService.can_transition_status(coordinator, test_data['application'], "approved")
            assert result is True

    def test_transition_status_success(self, test_data):
        """Test successful status transition."""
        with patch('exchange.services.NotificationService.send_notification') as mock_notify:
            result = ApplicationService.transition_status(test_data['application'], test_data['user'], "submitted")

            assert result.status == test_data['submitted_status']
            assert mock_notify.called

    def test_transition_status_permission_denied(self, test_data):
        """Test status transition with permission denied."""
        with pytest.raises(ValueError, match="You do not have permission"):
            ApplicationService.transition_status(test_data['application'], test_data['user'], "approved")

    def test_transition_status_invalid_status(self, test_data):
        """Test transition to a non-existent status raises error."""
        with pytest.raises(ApplicationStatus.DoesNotExist):
            ApplicationService.transition_status(test_data['application'], test_data['user'], "nonexistent")

    def test_withdraw_application_success(self, test_data):
        """Test successful application withdrawal."""
        result = ApplicationService.withdraw_application(test_data['application'], test_data['user'])

        assert result.withdrawn is True
        assert result.status == test_data['withdrawn_status']

    def test_withdraw_application_not_draft(self, test_data):
        """Test withdrawing non-draft application."""
        test_data['application'].status = test_data['approved_status']  # Use approved (final state)
        test_data['application'].save()

        with pytest.raises(ValueError, match="Application cannot be withdrawn in its current status"):
            ApplicationService.withdraw_application(test_data['application'], test_data['user'])

    def test_add_comment_success(self, test_data):
        """Test successful comment addition."""
        result = ApplicationService.add_comment(test_data['application'], test_data['user'], "Test comment")

        assert result.application == test_data['application']
        assert result.author == test_data['user']
        assert result.text == "Test comment"
        assert result.is_private is False

    def test_add_comment_empty_text(self, test_data):
        """Test adding a comment with empty text."""
        result = ApplicationService.add_comment(test_data['application'], test_data['user'], "")
        assert result.text == ""

    def test_add_comment_long_text(self, test_data):
        """Test adding a comment with very long text."""
        long_text = "x" * 10000
        result = ApplicationService.add_comment(test_data['application'], test_data['user'], long_text)
        assert result.text == long_text

    def test_add_comment_private(self, test_data):
        """Test adding private comment."""
        result = ApplicationService.add_comment(test_data['application'], test_data['user'], "Private comment", is_private=True)

        assert result.is_private is True

    def test_add_comment_creates_timeline_event(self, test_data):
        """Test that adding comment creates timeline event."""
        ApplicationService.add_comment(test_data['application'], test_data['user'], "Test comment")

        # Check that timeline event was created
        timeline_event = TimelineEvent.objects.filter(
            application=test_data['application'],
            event_type="comment"
        ).first()

        assert timeline_event is not None
        assert timeline_event.created_by == test_data['user']
        assert timeline_event.description == "Comment added."

    def test_submit_application_creates_timeline_event(self, test_data):
        """Test that submitting application creates timeline event."""
        from accounts.models import Profile
        Profile.objects.update_or_create(
            user=test_data['user'],
            defaults={
                'gpa': 3.5,
                'language': "English"
            }
        )

        with patch('exchange.services.NotificationService.send_notification'):
            ApplicationService.submit_application(test_data['application'], test_data['user'])

            # Check that timeline event was created
            timeline_event = TimelineEvent.objects.filter(
                application=test_data['application'],
                event_type="submitted"
            ).first()

            assert timeline_event is not None
            assert timeline_event.created_by == test_data['user']
            assert timeline_event.description == "Application submitted."

    def test_transition_status_creates_timeline_event(self, test_data):
        """Test that status transition creates timeline event."""
        with patch('exchange.services.NotificationService.send_notification'):
            ApplicationService.transition_status(test_data['application'], test_data['user'], "submitted")

            # Check that timeline event was created
            timeline_event = TimelineEvent.objects.filter(
                application=test_data['application'],
                event_type="status_submitted"
            ).first()

            assert timeline_event is not None
            assert timeline_event.created_by == test_data['user']
            assert timeline_event.description == "Status changed to submitted."

    def test_withdraw_application_creates_timeline_event(self, test_data):
        """Test that withdrawing application creates timeline event."""
        ApplicationService.withdraw_application(test_data['application'], test_data['user'])

        # Check that timeline event was created
        timeline_event = TimelineEvent.objects.filter(
            application=test_data['application'],
            event_type="withdrawn"
        ).first()

        assert timeline_event is not None
        assert timeline_event.created_by == test_data['user']
        assert timeline_event.description == "Application withdrawn."

    def test_notification_sent_on_submission(self, test_data):
        """Test that notification is sent on application submission."""
        from accounts.models import Profile
        Profile.objects.update_or_create(
            user=test_data['user'],
            defaults={
                'gpa': 3.5,
                'language': "English"
            }
        )

        with patch('exchange.services.NotificationService.send_notification') as mock_notify:
            ApplicationService.submit_application(test_data['application'], test_data['user'])

            mock_notify.assert_called_once()
            call_args = mock_notify.call_args
            assert call_args[0][0] == test_data['user']  # First argument is user
            assert call_args[0][1] == "Application Submitted"  # Second argument is notification title

    def test_notification_sent_on_status_change(self, test_data):
        """Test that notification is sent on status change."""
        with patch('exchange.services.NotificationService.send_notification') as mock_notify:
            ApplicationService.transition_status(test_data['application'], test_data['user'], "submitted")

            mock_notify.assert_called_once()
            call_args = mock_notify.call_args
            assert call_args[0][0] == test_data['application'].student  # First argument is student
            assert call_args[0][1] == "Application Status Update"  # Second argument is notification title

    def test_transaction_rollback_on_error(self, test_data):
        """Test that transaction rolls back on error."""
        from accounts.models import Profile
        Profile.objects.update_or_create(
            user=test_data['user'],
            defaults={
                'gpa': 3.5,
                'language': "English"
            }
        )

        # Mock NotificationService to raise an exception
        with patch('exchange.services.NotificationService.send_notification', side_effect=Exception("Test error")):
            with pytest.raises(Exception):
                ApplicationService.submit_application(test_data['application'], test_data['user'])

            # Check that application status was not changed
            test_data['application'].refresh_from_db()
            assert test_data['application'].status == test_data['draft_status']
            assert test_data['application'].submitted_at is None

    def test_multiple_comments_same_application(self, test_data):
        """Test adding multiple comments to the same application."""
        comment1 = ApplicationService.add_comment(test_data['application'], test_data['user'], "First comment")
        comment2 = ApplicationService.add_comment(test_data['application'], test_data['user'], "Second comment")

        assert comment1.id != comment2.id
        assert comment1.application == comment2.application

        # Check that both timeline events were created
        timeline_events = TimelineEvent.objects.filter(
            application=test_data['application'],
            event_type="comment"
        )
        assert timeline_events.count() == 2

    def test_application_with_comments_and_events(self, test_data):
        """Test application with multiple comments and timeline events."""
        # Add comments
        ApplicationService.add_comment(test_data['application'], test_data['user'], "Comment 1")
        ApplicationService.add_comment(test_data['application'], test_data['user'], "Comment 2")

        # Submit application
        from accounts.models import Profile
        Profile.objects.update_or_create(
            user=test_data['user'],
            defaults={
                'gpa': 3.5,
                'language': "English"
            }
        )

        with patch('exchange.services.NotificationService.send_notification'):
            ApplicationService.submit_application(test_data['application'], test_data['user'])

        # Check total timeline events
        timeline_events = TimelineEvent.objects.filter(application=test_data['application'])
        assert timeline_events.count() == 3  # 2 comments + 1 submission

        # Check comments
        comments = Comment.objects.filter(application=test_data['application'])
        assert comments.count() == 2
