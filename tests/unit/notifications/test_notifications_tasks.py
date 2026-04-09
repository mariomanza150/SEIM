"""
Comprehensive tests for notification tasks.

Tests for email sending and reminder Celery tasks.
"""

import uuid

import pytest
from datetime import timedelta
from unittest.mock import Mock, patch, MagicMock, call
from django.contrib.auth import get_user_model
from django.core import mail
from django.utils import timezone

from notifications.models import Notification, Reminder
from notifications.tasks import (
    send_notification_email,
    send_email_notification,
    send_notification_by_id,
    send_deadline_reminders,
    get_user_email,
    settings_category_for_reminder_event,
)

User = get_user_model()


@pytest.fixture
def user(db):
    """Create a test user."""
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123"
    )


@pytest.fixture
def another_user(db):
    """Create another test user."""
    return User.objects.create_user(
        username="anotheruser",
        email="another@example.com",
        password="testpass123"
    )


@pytest.fixture
def notification(user, db):
    """Create a test notification."""
    return Notification.objects.create(
        recipient=user,
        title="Test Notification",
        message="This is a test notification message",
        category="info"
    )


@pytest.mark.django_db
class TestGetUserEmail:
    """Test helper function for getting user email."""
    
    def test_get_user_email_returns_email(self, user):
        """Test getting user email."""
        email = get_user_email(user)
        assert email == "test@example.com"
    
    def test_get_user_email_with_different_users(self, user, another_user):
        """Test getting email for different users."""
        email1 = get_user_email(user)
        email2 = get_user_email(another_user)
        
        assert email1 == "test@example.com"
        assert email2 == "another@example.com"
        assert email1 != email2


@pytest.mark.django_db
@pytest.mark.celery
class TestSendNotificationEmailTask:
    """Test send_notification_email Celery task."""
    
    def test_send_notification_email_success(self, user):
        """Test sending notification email successfully."""
        subject = "Test Subject"
        message = "Test message body"
        
        # Clear mail outbox
        mail.outbox = []
        
        send_notification_email(str(user.id), subject, message)
        
        # Verify email was sent
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == subject
        assert mail.outbox[0].body == message
        assert user.email in mail.outbox[0].to
    
    def test_send_notification_email_with_long_subject(self, user):
        """Test sending email with long subject."""
        subject = "A" * 200
        message = "Short message"
        
        mail.outbox = []
        
        send_notification_email(str(user.id), subject, message)
        
        # Should still send successfully
        assert len(mail.outbox) == 1
    
    def test_send_notification_email_with_html_content(self, user):
        """Test sending email with HTML in message."""
        subject = "HTML Test"
        message = "<html><body><h1>Test</h1></body></html>"
        
        mail.outbox = []
        
        send_notification_email(str(user.id), subject, message)
        
        assert len(mail.outbox) == 1
        assert message in mail.outbox[0].body
    
    def test_send_notification_email_from_address(self, user):
        """Test email from address is correct."""
        mail.outbox = []
        
        send_notification_email(str(user.id), "Subject", "Message")
        
        assert len(mail.outbox) == 1
        assert mail.outbox[0].from_email == "noreply@seim.local"
    
    def test_send_notification_email_user_not_found(self):
        """Test sending email to non-existent user."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        with pytest.raises(Exception):
            send_notification_email(fake_id, "Subject", "Message")
    
    def test_send_notification_email_multiple_users(self, user, another_user):
        """Test sending emails to multiple users."""
        mail.outbox = []
        
        send_notification_email(str(user.id), "Subject 1", "Message 1")
        send_notification_email(str(another_user.id), "Subject 2", "Message 2")
        
        assert len(mail.outbox) == 2
        assert user.email in mail.outbox[0].to
        assert another_user.email in mail.outbox[1].to
    
    def test_send_notification_email_empty_subject(self, user):
        """Test sending email with empty subject."""
        mail.outbox = []
        
        send_notification_email(str(user.id), "", "Message")
        
        # Should still send
        assert len(mail.outbox) == 1
    
    def test_send_notification_email_empty_message(self, user):
        """Test sending email with empty message."""
        mail.outbox = []
        
        send_notification_email(str(user.id), "Subject", "")
        
        # Should still send
        assert len(mail.outbox) == 1
    
    def test_send_notification_email_unicode_content(self, user):
        """Test sending email with unicode characters."""
        subject = "Notificación con acentos"
        message = "Mensaje con caracteres especiales: ñ, á, é, í, ó, ú"
        
        mail.outbox = []
        
        send_notification_email(str(user.id), subject, message)
        
        assert len(mail.outbox) == 1
        assert subject in mail.outbox[0].subject
    
    @patch('notifications.tasks.send_mail')
    def test_send_notification_email_fail_silently_false(self, mock_send_mail, user):
        """Test that fail_silently is False."""
        mock_send_mail.side_effect = Exception("SMTP error")
        
        with pytest.raises(Exception):
            send_notification_email(str(user.id), "Subject", "Message")
        
        # Verify send_mail was called with fail_silently=False
        assert mock_send_mail.called
        call_kwargs = mock_send_mail.call_args[1]
        assert call_kwargs['fail_silently'] is False


@pytest.mark.django_db
@pytest.mark.celery
class TestSendEmailNotificationTask:
    """Test send_email_notification Celery task (alias)."""
    
    def test_send_email_notification_is_alias(self, user):
        """Test that send_email_notification is an alias."""
        mail.outbox = []
        
        send_email_notification(str(user.id), "Subject", "Message")
        
        # Should work identically to send_notification_email
        assert len(mail.outbox) == 1
    
    def test_send_email_notification_compatibility(self, user):
        """Test backward compatibility of alias."""
        mail.outbox = []
        
        # Both should produce same result
        send_email_notification(str(user.id), "Test", "Message")
        send_notification_email(str(user.id), "Test", "Message")
        
        assert len(mail.outbox) == 2
        # Both should have same structure
        assert mail.outbox[0].subject == mail.outbox[1].subject


@pytest.mark.django_db
@pytest.mark.celery
class TestSendNotificationByIdTask:
    """Test send_notification_by_id Celery task."""
    
    def test_send_notification_by_id_success(self, notification):
        """Test sending notification by ID."""
        mail.outbox = []
        
        result = send_notification_by_id(str(notification.id))
        
        # Verify success
        assert result is True
        
        # Verify email sent
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == notification.title
        assert mail.outbox[0].body == notification.message
        assert notification.recipient.email in mail.outbox[0].to
    
    def test_send_notification_by_id_not_found(self):
        """Test sending non-existent notification."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        result = send_notification_by_id(fake_id)
        
        # Should return False, not crash
        assert result is False
    
    def test_send_notification_by_id_from_address(self, notification):
        """Test email from address."""
        mail.outbox = []
        
        send_notification_by_id(str(notification.id))
        
        assert len(mail.outbox) == 1
        assert mail.outbox[0].from_email == "noreply@seim.local"
    
    def test_send_notification_by_id_multiple_notifications(self, user, another_user):
        """Test sending multiple notifications by ID."""
        notif1 = Notification.objects.create(
            recipient=user,
            title="Notification 1",
            message="Message 1",
            category="info"
        )
        
        notif2 = Notification.objects.create(
            recipient=another_user,
            title="Notification 2",
            message="Message 2",
            category="warning"
        )
        
        mail.outbox = []
        
        result1 = send_notification_by_id(str(notif1.id))
        result2 = send_notification_by_id(str(notif2.id))
        
        assert result1 is True
        assert result2 is True
        assert len(mail.outbox) == 2
    
    @patch('notifications.tasks.send_mail')
    def test_send_notification_by_id_fail_silently_false(self, mock_send_mail, notification):
        """Test that fail_silently is False."""
        mock_send_mail.side_effect = Exception("SMTP error")
        
        with pytest.raises(Exception):
            send_notification_by_id(str(notification.id))
    
    def test_send_notification_by_id_with_empty_title(self, user):
        """Test sending notification with empty title."""
        notif = Notification.objects.create(
            recipient=user,
            title="",
            message="Message with no title",
            category="info"
        )
        
        mail.outbox = []
        
        result = send_notification_by_id(str(notif.id))
        
        assert result is True
        assert len(mail.outbox) == 1
    
    def test_send_notification_by_id_idempotency(self, notification):
        """Test that sending same notification multiple times is safe."""
        mail.outbox = []
        
        # Send same notification multiple times
        for _ in range(3):
            result = send_notification_by_id(str(notification.id))
            assert result is True
        
        # Should have sent 3 emails
        assert len(mail.outbox) == 3


@pytest.mark.parametrize(
    "event_type,expected",
    [
        ("application_deadline", "applications"),
        ("document_deadline", "documents"),
        ("program_start", "programs"),
        ("program_end", "programs"),
        ("custom", "programs"),
        ("application", "applications"),
        ("document", "documents"),
        ("program", "programs"),
        ("unknown_future_type", "programs"),
    ],
)
def test_settings_category_for_reminder_event(event_type, expected):
    assert settings_category_for_reminder_event(event_type) == expected


@pytest.mark.django_db
@pytest.mark.celery
class TestSendDeadlineRemindersTask:
    """Test send_deadline_reminders Celery task."""
    
    def test_send_deadline_reminders_no_reminders(self):
        """Test when there are no due reminders."""
        count = send_deadline_reminders()
        
        assert count == 0
    
    def test_send_deadline_reminders_one_reminder(self, user):
        """Test sending one due reminder."""
        # Create a due reminder
        reminder = Reminder.objects.create(
            user=user,
            event_title="Application Deadline",
            event_type="application",
            event_id=uuid.UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"),
            remind_at=timezone.now() - timedelta(minutes=5),
            sent=False
        )
        
        count = send_deadline_reminders()
        
        # Verify reminder sent
        assert count == 1
        
        # Verify reminder marked as sent
        reminder.refresh_from_db()
        assert reminder.sent is True
        
        # Verify notification created
        assert reminder.notification is not None
        assert "Reminder:" in reminder.notification.title
        assert reminder.event_title in reminder.notification.title
    
    def test_send_deadline_reminders_multiple_reminders(self, user, another_user):
        """Test sending multiple due reminders."""
        # Create multiple due reminders
        Reminder.objects.create(
            user=user,
            event_title="Deadline 1",
            event_type="application",
            event_id=uuid.UUID("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"),
            remind_at=timezone.now() - timedelta(hours=1),
            sent=False
        )
        
        Reminder.objects.create(
            user=another_user,
            event_title="Deadline 2",
            event_type="document",
            event_id=uuid.UUID("cccccccc-cccc-4ccc-8ccc-cccccccccccc"),
            remind_at=timezone.now() - timedelta(minutes=30),
            sent=False
        )
        
        count = send_deadline_reminders()
        
        # Verify both sent
        assert count == 2
        
        # Verify all marked as sent
        assert Reminder.objects.filter(sent=False).count() == 0
    
    def test_send_deadline_reminders_skips_future_reminders(self, user):
        """Test that future reminders are not sent."""
        # Create future reminder
        Reminder.objects.create(
            user=user,
            event_title="Future Deadline",
            event_type="application",
            event_id=uuid.UUID("dddddddd-dddd-4ddd-8ddd-dddddddddddd"),
            remind_at=timezone.now() + timedelta(hours=1),
            sent=False
        )
        
        count = send_deadline_reminders()
        
        # Should not send future reminders
        assert count == 0
    
    def test_send_deadline_reminders_skips_already_sent(self, user):
        """Test that already sent reminders are skipped."""
        # Create already-sent reminder
        Reminder.objects.create(
            user=user,
            event_title="Already Sent",
            event_type="application",
            event_id=uuid.UUID("eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee"),
            remind_at=timezone.now() - timedelta(hours=1),
            sent=True
        )
        
        count = send_deadline_reminders()
        
        # Should not send already-sent reminders
        assert count == 0
    
    def test_send_deadline_reminders_notification_type(self, user):
        """Test that reminders use correct notification type."""
        reminder = Reminder.objects.create(
            user=user,
            event_title="Test Deadline",
            event_type="application",
            event_id=uuid.UUID("ffffffff-ffff-4fff-8fff-ffffffffffff"),
            remind_at=timezone.now() - timedelta(minutes=5),
            sent=False
        )
        
        with patch(
            "notifications.services.NotificationService.send_notification"
        ) as mock_send:
            mock_send.return_value = Notification.objects.create(
                recipient=user,
                title="Test",
                message="Test",
                category="warning"
            )
            
            send_deadline_reminders()
            
            # Verify NotificationService was called with correct params
            assert mock_send.called
            call_kwargs = mock_send.call_args[1]
            assert call_kwargs['notification_type'] == "both"
            assert call_kwargs['category'] == "warning"
            assert call_kwargs["settings_category"] == "applications"
    
    def test_send_deadline_reminders_includes_event_data(self, user):
        """Test that reminder notification includes event data."""
        event_type = "document"
        event_id = uuid.UUID("12121212-1212-4121-8121-121212121212")
        
        reminder = Reminder.objects.create(
            user=user,
            event_title="Document Upload",
            event_type=event_type,
            event_id=event_id,
            remind_at=timezone.now() - timedelta(minutes=5),
            sent=False
        )
        
        with patch(
            "notifications.services.NotificationService.send_notification"
        ) as mock_send:
            mock_send.return_value = Notification.objects.create(
                recipient=user,
                title="Test",
                message="Test",
                category="warning"
            )
            
            send_deadline_reminders()
            
            # Verify event data included
            call_kwargs = mock_send.call_args[1]
            assert 'data' in call_kwargs
            assert call_kwargs['data']['event_type'] == event_type
            assert call_kwargs['data']['event_id'] == str(event_id)
            assert call_kwargs["settings_category"] == "documents"
    
    def test_send_deadline_reminders_error_handling(self, user):
        """Test that task continues despite errors."""
        # Create multiple reminders
        Reminder.objects.create(
            user=user,
            event_title="Reminder 1",
            event_type="application",
            event_id=uuid.UUID("13131313-1313-4131-8131-131313131313"),
            remind_at=timezone.now() - timedelta(minutes=5),
            sent=False
        )
        
        Reminder.objects.create(
            user=user,
            event_title="Reminder 2",
            event_type="application",
            event_id=uuid.UUID("14141414-1414-4141-8141-141414141414"),
            remind_at=timezone.now() - timedelta(minutes=3),
            sent=False
        )
        
        with patch(
            "notifications.services.NotificationService.send_notification"
        ) as mock_send:
            # First call fails, second succeeds
            mock_send.side_effect = [
                Exception("Error sending notification"),
                Notification.objects.create(
                    recipient=user,
                    title="Success",
                    message="Success",
                    category="info"
                )
            ]
            
            count = send_deadline_reminders()
            
            # Should still send the second one
            assert count == 1
    
    def test_send_deadline_reminders_links_notification(self, user):
        """Test that reminder is linked to created notification."""
        reminder = Reminder.objects.create(
            user=user,
            event_title="Link Test",
            event_type="application",
            event_id=uuid.UUID("15151515-1515-4151-8151-151515151515"),
            remind_at=timezone.now() - timedelta(minutes=5),
            sent=False
        )
        
        send_deadline_reminders()
        
        # Verify reminder linked to notification
        reminder.refresh_from_db()
        assert reminder.notification is not None
        assert reminder.notification.recipient == user
    
    def test_send_deadline_reminders_boundary_condition(self, user):
        """Test reminder at exact current time."""
        # Create reminder at exactly current time
        now = timezone.now()
        reminder = Reminder.objects.create(
            user=user,
            event_title="Boundary Test",
            event_type="application",
            event_id=uuid.UUID("16161616-1616-4161-8161-161616161616"),
            remind_at=now,
            sent=False
        )
        
        count = send_deadline_reminders()
        
        # Should send reminders at current time
        assert count == 1
        
        reminder.refresh_from_db()
        assert reminder.sent is True
    
    def test_send_deadline_reminders_selects_related(self, user):
        """Test that query uses select_related for efficiency."""
        Reminder.objects.create(
            user=user,
            event_title="Performance Test",
            event_type="application",
            event_id=uuid.UUID("17171717-1717-4171-8171-171717171717"),
            remind_at=timezone.now() - timedelta(minutes=5),
            sent=False
        )
        
        with patch('notifications.models.Reminder.objects.filter') as mock_filter:
            # Mock queryset that tracks select_related call
            mock_qs = Mock()
            mock_qs.select_related.return_value = []
            mock_filter.return_value = mock_qs
            
            send_deadline_reminders()
            
            # Verify select_related was called
            assert mock_qs.select_related.called
    
    def test_send_deadline_reminders_returns_count(self, user):
        """Test that task returns correct count."""
        # Create known number of reminders
        for i in range(5):
            Reminder.objects.create(
                user=user,
                event_title=f"Reminder {i}",
                event_type="application",
                event_id=uuid.UUID(int=i + 0xA000000000000000),
                remind_at=timezone.now() - timedelta(minutes=5+i),
                sent=False
            )
        
        count = send_deadline_reminders()
        
        assert count == 5


@pytest.mark.django_db
class TestNotificationTaskIntegration:
    """Integration tests for notification tasks."""
    
    def test_complete_notification_workflow(self, user):
        """Test complete workflow of creating and sending notification."""
        # Create notification
        notification = Notification.objects.create(
            recipient=user,
            title="Integration Test",
            message="Complete workflow test",
            category="info"
        )
        
        mail.outbox = []
        
        # Send via task
        result = send_notification_by_id(str(notification.id))
        
        # Verify complete workflow
        assert result is True
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to[0] == user.email
    
    def test_reminder_to_notification_to_email_workflow(self, user):
        """Test complete workflow from reminder to email."""
        # Create reminder
        reminder = Reminder.objects.create(
            user=user,
            event_title="Complete Workflow",
            event_type="application",
            event_id=uuid.UUID("18181818-1818-4181-8181-181818181818"),
            remind_at=timezone.now() - timedelta(minutes=5),
            sent=False
        )
        
        mail.outbox = []
        
        # Process reminders
        count = send_deadline_reminders()
        
        # Verify complete workflow
        assert count == 1
        
        reminder.refresh_from_db()
        assert reminder.sent is True
        assert reminder.notification is not None
    
    def test_multiple_reminders_different_times(self, user):
        """Test processing reminders with different timestamps."""
        future_eid = uuid.UUID("19191919-1919-4191-8191-191919191919")
        # Create reminders at different times
        Reminder.objects.create(
            user=user,
            event_title="Old Reminder",
            event_type="application",
            event_id=uuid.UUID("1a1a1a1a-1a1a-41a1-81a1-1a1a1a1a1a1a"),
            remind_at=timezone.now() - timedelta(days=1),
            sent=False
        )
        
        Reminder.objects.create(
            user=user,
            event_title="Recent Reminder",
            event_type="application",
            event_id=uuid.UUID("1b1b1b1b-1b1b-41b1-81b1-1b1b1b1b1b1b"),
            remind_at=timezone.now() - timedelta(minutes=5),
            sent=False
        )
        
        Reminder.objects.create(
            user=user,
            event_title="Future Reminder",
            event_type="application",
            event_id=future_eid,
            remind_at=timezone.now() + timedelta(hours=1),
            sent=False
        )
        
        count = send_deadline_reminders()
        
        # Should send the two past reminders
        assert count == 2
        
        # Future one should not be sent
        future_reminder = Reminder.objects.get(event_id=future_eid)
        assert future_reminder.sent is False

