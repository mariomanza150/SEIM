"""
Tests for notifications services.
"""
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models import Profile, Role
from notifications.models import Notification
from notifications.services import NotificationService

User = get_user_model()


class NotificationServiceTestCase(TestCase):
    """Test case for notification services."""

    def setUp(self):
        """Set up test data."""
        # Create roles
        self.student_role, _ = Role.objects.get_or_create(name="student")
        self.coordinator_role, _ = Role.objects.get_or_create(name="coordinator")
        self.admin_role, _ = Role.objects.get_or_create(name="admin")

        # Create users
        self.student = User.objects.create_user(
            username="student",
            email="student@example.com",
            password="testpass123"
        )
        self.student.roles.add(self.student_role)

        self.coordinator = User.objects.create_user(
            username="coordinator",
            email="coordinator@example.com",
            password="testpass123"
        )
        self.coordinator.roles.add(self.coordinator_role)

        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="testpass123"
        )
        self.admin.roles.add(self.admin_role)

        # Create profiles
        Profile.objects.get_or_create(user=self.student, defaults={'gpa': 3.5, 'language': 'English'})
        Profile.objects.get_or_create(user=self.coordinator, defaults={'gpa': 3.8, 'language': 'English'})
        Profile.objects.get_or_create(user=self.admin, defaults={'gpa': 4.0, 'language': 'English'})

    def test_send_notification_success(self):
        """Test successful notification sending."""
        notification = NotificationService.send_notification(
            recipient=self.student,
            title="Test Notification",
            message="This is a test notification",
            notification_type="in_app"
        )

        self.assertIsNotNone(notification)
        self.assertEqual(notification.recipient, self.student)
        self.assertEqual(notification.title, "Test Notification")
        self.assertEqual(notification.message, "This is a test notification")
        self.assertEqual(notification.notification_type, "in_app")
        self.assertFalse(notification.is_read)

    def test_send_notification_email(self):
        """Test email notification sending."""
        with patch('notifications.services.send_notification_by_id.delay') as mock_send_email:
            notification = NotificationService.send_notification(
                recipient=self.student,
                title="Email Notification",
                message="This is an email notification",
                notification_type="email"
            )

            self.assertIsNotNone(notification)
            mock_send_email.assert_called_once_with(notification.id)

    def test_send_notification_both(self):
        """Test both email and in-app notification sending."""
        with patch('notifications.services.send_notification_by_id.delay') as mock_send_email:
            notification = NotificationService.send_notification(
                recipient=self.student,
                title="Both Notification",
                message="This is both email and in-app notification",
                notification_type="both"
            )

            self.assertIsNotNone(notification)
            mock_send_email.assert_called_once_with(notification.id)

    def test_send_notification_invalid_type(self):
        """Test notification sending with invalid type."""
        with self.assertRaises(ValueError):
            NotificationService.send_notification(
                recipient=self.student,
                title="Invalid Notification",
                message="This has invalid type",
                notification_type="invalid"
            )

    def test_send_bulk_notifications(self):
        """Test bulk notification sending."""
        recipients = [self.student, self.coordinator, self.admin]

        notifications = NotificationService.send_bulk_notifications(
            recipients=recipients,
            title="Bulk Notification",
            message="This is a bulk notification",
            notification_type="in_app"
        )

        self.assertEqual(len(notifications), 3)
        for notification in notifications:
            self.assertIn(notification.recipient, recipients)
            self.assertEqual(notification.title, "Bulk Notification")
            self.assertEqual(notification.message, "This is a bulk notification")

    def test_send_notification_to_role(self):
        """Test sending notification to all users with a specific role."""
        with patch('notifications.services.NotificationService.send_bulk_notifications') as mock_bulk:
            NotificationService.send_notification_to_role(
                role_name="student",
                title="Role Notification",
                message="This is a role notification",
                notification_type="in_app"
            )

            mock_bulk.assert_called_once()
            call_args = mock_bulk.call_args
            self.assertEqual(call_args[1]['title'], "Role Notification")
            self.assertEqual(call_args[1]['message'], "This is a role notification")

    def test_send_notification_to_role_invalid(self):
        """Test sending notification to invalid role."""
        with self.assertRaises(ValueError):
            NotificationService.send_notification_to_role(
                role_name="invalid_role",
                title="Invalid Role Notification",
                message="This should fail",
                notification_type="in_app"
            )

    def test_mark_notification_as_read(self):
        """Test marking notification as read."""
        notification = Notification.objects.create(
            recipient=self.student,
            title="Test Notification",
            message="This is a test notification",
            notification_type="in_app"
        )

        NotificationService.mark_notification_as_read(notification.id)
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)

    def test_mark_notification_as_read_invalid_id(self):
        """Test marking non-existent notification as read."""
        with self.assertRaises(Notification.DoesNotExist):
            NotificationService.mark_notification_as_read(99999)

    def test_mark_all_notifications_as_read(self):
        """Test marking all notifications as read for a user."""
        # Create multiple notifications
        Notification.objects.create(
            recipient=self.student,
            title="Notification 1",
            message="First notification",
            notification_type="in_app"
        )
        Notification.objects.create(
            recipient=self.student,
            title="Notification 2",
            message="Second notification",
            notification_type="in_app"
        )

        count = NotificationService.mark_all_notifications_as_read(self.student)
        self.assertEqual(count, 2)

        # Verify all notifications are marked as read
        unread_count = Notification.objects.filter(
            recipient=self.student,
            is_read=False
        ).count()
        self.assertEqual(unread_count, 0)

    def test_get_unread_notifications(self):
        """Test getting unread notifications for a user."""
        # Create read and unread notifications
        Notification.objects.create(
            recipient=self.student,
            title="Read Notification",
            message="This is read",
            notification_type="in_app",
            is_read=True
        )
        Notification.objects.create(
            recipient=self.student,
            title="Unread Notification",
            message="This is unread",
            notification_type="in_app",
            is_read=False
        )

        unread_notifications = NotificationService.get_unread_notifications(self.student)
        self.assertEqual(len(unread_notifications), 1)
        self.assertEqual(unread_notifications[0].title, "Unread Notification")

    def test_get_notification_count(self):
        """Test getting notification count for a user."""
        # Create multiple notifications
        Notification.objects.create(
            recipient=self.student,
            title="Notification 1",
            message="First notification",
            notification_type="in_app"
        )
        Notification.objects.create(
            recipient=self.student,
            title="Notification 2",
            message="Second notification",
            notification_type="in_app"
        )
        Notification.objects.create(
            recipient=self.coordinator,
            title="Other User Notification",
            message="This is for another user",
            notification_type="in_app"
        )

        count = NotificationService.get_notification_count(self.student)
        self.assertEqual(count, 2)

    def test_delete_old_notifications(self):
        """Test deleting old notifications."""
        from datetime import timedelta

        from django.utils import timezone

        # Create old notification by directly setting sent_at
        old_date = timezone.now() - timedelta(days=31)
        old_notification = Notification.objects.create(
            recipient=self.student,
            title="Old Notification",
            message="This is old",
            notification_type="in_app"
        )
        # Update the sent_at field directly
        old_notification.sent_at = old_date
        old_notification.save()

        # Create recent notification
        recent_notification = Notification.objects.create(
            recipient=self.student,
            title="Recent Notification",
            message="This is recent",
            notification_type="in_app"
        )

        deleted_count = NotificationService.delete_old_notifications(days=30)
        self.assertEqual(deleted_count, 1)

        # Verify old notification is deleted, recent one remains
        self.assertFalse(Notification.objects.filter(id=old_notification.id).exists())
        self.assertTrue(Notification.objects.filter(id=recent_notification.id).exists())

    def test_send_notification_with_data(self):
        """Test sending notification with additional data."""
        notification = NotificationService.send_notification(
            recipient=self.student,
            title="Data Notification",
            message="This has data",
            notification_type="in_app",
            data={"key": "value", "number": 123}
        )

        self.assertIsNotNone(notification)
        self.assertEqual(notification.data, {"key": "value", "number": 123})

    @patch('notifications.services.cache.get')
    def test_get_notification_count_cached(self, mock_cache_get):
        """Test getting notification count with cache."""
        mock_cache_get.return_value = 5

        count = NotificationService.get_notification_count(self.student, use_cache=True)
        self.assertEqual(count, 5)
        mock_cache_get.assert_called_once()

    def test_get_notification_count_no_cache(self):
        """Test getting notification count without cache."""
        Notification.objects.create(
            recipient=self.student,
            title="Test Notification",
            message="Test message",
            notification_type="in_app"
        )

        count = NotificationService.get_notification_count(self.student, use_cache=False)
        self.assertEqual(count, 1)
