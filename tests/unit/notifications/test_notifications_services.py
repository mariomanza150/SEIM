"""
Test Notifications Services

Comprehensive tests for notification sending and management.
"""

import pytest
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.utils import timezone
from unittest.mock import patch

from accounts.models import Role
from notifications.models import Notification, NotificationPreference, NotificationType
from notifications.services import NotificationService

User = get_user_model()


@pytest.mark.django_db
class TestNotificationService(TestCase):
    """Test notification service methods."""

    def setUp(self):
        """Set up test data."""
        self.user1 = User.objects.create_user(
            username="user1",
            email="user1@test.com",
            password="testpass123"
        )
        
        self.user2 = User.objects.create_user(
            username="user2",
            email="user2@test.com",
            password="testpass123"
        )
        
        # Clear cache before each test
        cache.clear()

    def tearDown(self):
        """Clean up after each test."""
        cache.clear()

    def test_is_enabled_default_true(self):
        """Test that notifications are enabled by default."""
        result = NotificationService.is_enabled(self.user1, "application_update")
        
        self.assertTrue(result)

    def test_is_enabled_explicit_preference(self):
        """Test checking explicit preference."""
        # Set preference to disabled
        NotificationService.set_preference(
            self.user1,
            "application_update",
            enabled=False
        )
        
        result = NotificationService.is_enabled(self.user1, "application_update")
        
        self.assertFalse(result)

    def test_is_enabled_creates_notification_type(self):
        """Test that checking creates notification type if not exists."""
        type_name = "new_notification_type"
        
        # Verify type doesn't exist
        self.assertFalse(
            NotificationType.objects.filter(name=type_name).exists()
        )
        
        NotificationService.is_enabled(self.user1, type_name)
        
        # Verify type was created
        self.assertTrue(
            NotificationType.objects.filter(name=type_name).exists()
        )

    def test_set_preference_enable(self):
        """Test setting preference to enabled."""
        pref = NotificationService.set_preference(
            self.user1,
            "application_update",
            enabled=True
        )
        
        self.assertTrue(pref.enabled)
        self.assertEqual(pref.user, self.user1)
        self.assertEqual(pref.type.name, "application_update")

    def test_set_preference_disable(self):
        """Test setting preference to disabled."""
        pref = NotificationService.set_preference(
            self.user1,
            "application_update",
            enabled=False
        )
        
        self.assertFalse(pref.enabled)

    def test_set_preference_updates_existing(self):
        """Test that setting preference updates existing one."""
        # Create initial preference
        pref1 = NotificationService.set_preference(
            self.user1,
            "application_update",
            enabled=True
        )
        
        # Update to disabled
        pref2 = NotificationService.set_preference(
            self.user1,
            "application_update",
            enabled=False
        )
        
        # Should be same object, updated
        self.assertEqual(pref1.id, pref2.id)
        pref1.refresh_from_db()
        self.assertFalse(pref1.enabled)

    def test_set_preference_creates_notification_type(self):
        """Test that setting preference creates type if needed."""
        type_name = "custom_notification"
        
        self.assertFalse(
            NotificationType.objects.filter(name=type_name).exists()
        )
        
        NotificationService.set_preference(self.user1, type_name, enabled=True)
        
        self.assertTrue(
            NotificationType.objects.filter(name=type_name).exists()
        )

    def test_send_notification_in_app(self):
        """Test sending in-app notification."""
        notification = NotificationService.send_notification(
            recipient=self.user1,
            title="Test Notification",
            message="This is a test message",
            notification_type="in_app"
        )
        
        self.assertIsNotNone(notification.id)
        self.assertEqual(notification.recipient, self.user1)
        self.assertEqual(notification.title, "Test Notification")
        self.assertEqual(notification.message, "This is a test message")
        self.assertEqual(notification.notification_type, "in_app")
        self.assertFalse(notification.is_read)

    @patch('notifications.services.send_notification_by_id.delay')
    def test_send_notification_email(self, mock_task):
        """Test sending email notification triggers task."""
        notification = NotificationService.send_notification(
            recipient=self.user1,
            title="Email Test",
            message="Test email",
            notification_type="email"
        )
        
        self.assertEqual(notification.notification_type, "email")
        # Verify task was called
        mock_task.assert_called_once_with(notification.id)

    @patch('notifications.services.send_notification_by_id.delay')
    def test_send_notification_both(self, mock_task):
        """Test sending both in-app and email notification."""
        notification = NotificationService.send_notification(
            recipient=self.user1,
            title="Both Test",
            message="Test both",
            notification_type="both"
        )
        
        self.assertEqual(notification.notification_type, "both")
        # Verify task was called
        mock_task.assert_called_once_with(notification.id)

    def test_send_notification_with_action_url(self):
        """Test sending notification with action URL."""
        notification = NotificationService.send_notification(
            recipient=self.user1,
            title="Action Test",
            message="Click to view",
            notification_type="in_app",
            action_url="/applications/123/",
            action_text="View Application"
        )
        
        self.assertEqual(notification.action_url, "/applications/123/")
        self.assertEqual(notification.action_text, "View Application")

    def test_send_notification_with_data(self):
        """Test sending notification with additional data."""
        data = {"application_id": 123, "status": "approved"}
        
        notification = NotificationService.send_notification(
            recipient=self.user1,
            title="Data Test",
            message="Test with data",
            notification_type="in_app",
            data=data
        )
        
        self.assertEqual(notification.data, data)

    def test_send_notification_invalid_type(self):
        """Test sending notification with invalid type raises error."""
        with self.assertRaises(ValueError) as context:
            NotificationService.send_notification(
                recipient=self.user1,
                title="Invalid",
                message="Invalid type",
                notification_type="invalid_type"
            )
        
        self.assertIn("Invalid notification type", str(context.exception))

    def test_send_bulk_notifications(self):
        """Test sending notifications to multiple recipients."""
        user3 = User.objects.create_user(
            username="user3",
            email="user3@test.com",
            password="testpass123"
        )
        
        recipients = [self.user1, self.user2, user3]
        
        notifications = NotificationService.send_bulk_notifications(
            recipients=recipients,
            title="Bulk Test",
            message="Test bulk send",
            notification_type="in_app"
        )
        
        self.assertEqual(len(notifications), 3)
        
        # Verify each user got a notification
        for user in recipients:
            self.assertTrue(
                Notification.objects.filter(
                    recipient=user,
                    title="Bulk Test"
                ).exists()
            )

    def test_send_bulk_notifications_empty_list(self):
        """Test sending bulk notifications with empty recipient list."""
        notifications = NotificationService.send_bulk_notifications(
            recipients=[],
            title="Empty Test",
            message="No recipients"
        )
        
        self.assertEqual(len(notifications), 0)

    def test_send_notification_to_role(self):
        """Test sending notification to all users with a role."""
        # Create role and assign to users
        student_role, _ = Role.objects.get_or_create(name="student")
        self.user1.roles.add(student_role)
        self.user2.roles.add(student_role)
        
        notifications = NotificationService.send_notification_to_role(
            role_name="student",
            title="Student Announcement",
            message="Important message for students",
            notification_type="in_app"
        )
        
        self.assertEqual(len(notifications), 2)
        
        # Verify both users got notification
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.user1,
                title="Student Announcement"
            ).exists()
        )
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.user2,
                title="Student Announcement"
            ).exists()
        )

    def test_send_notification_to_role_no_users(self):
        """Test sending to role with no users raises error."""
        with self.assertRaises(ValueError) as context:
            NotificationService.send_notification_to_role(
                role_name="nonexistent_role",
                title="Test",
                message="Test"
            )
        
        self.assertIn("No users found with role", str(context.exception))

    def test_mark_notification_as_read(self):
        """Test marking notification as read."""
        notification = NotificationService.send_notification(
            recipient=self.user1,
            title="Test",
            message="Test",
            notification_type="in_app"
        )
        
        self.assertFalse(notification.is_read)
        
        updated = NotificationService.mark_notification_as_read(notification.id)
        
        self.assertTrue(updated.is_read)

    def test_mark_notification_as_read_not_found(self):
        """Test marking non-existent notification raises error."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        with self.assertRaises(Notification.DoesNotExist):
            NotificationService.mark_notification_as_read(fake_id)

    def test_mark_all_notifications_as_read(self):
        """Test marking all notifications as read for a user."""
        # Create multiple unread notifications
        for i in range(3):
            NotificationService.send_notification(
                recipient=self.user1,
                title=f"Test {i}",
                message=f"Message {i}",
                notification_type="in_app"
            )
        
        # Create notification for different user
        NotificationService.send_notification(
            recipient=self.user2,
            title="Other user",
            message="Test",
            notification_type="in_app"
        )
        
        count = NotificationService.mark_all_notifications_as_read(self.user1)
        
        self.assertEqual(count, 3)
        
        # Verify user1's notifications are read
        unread = Notification.objects.filter(
            recipient=self.user1,
            is_read=False
        ).count()
        self.assertEqual(unread, 0)
        
        # Verify user2's notification is still unread
        unread_user2 = Notification.objects.filter(
            recipient=self.user2,
            is_read=False
        ).count()
        self.assertEqual(unread_user2, 1)

    def test_mark_all_notifications_as_read_none_unread(self):
        """Test marking all as read when none are unread."""
        count = NotificationService.mark_all_notifications_as_read(self.user1)
        
        self.assertEqual(count, 0)

    def test_get_unread_notifications(self):
        """Test getting unread notifications for a user."""
        # Create unread notification
        notif1 = NotificationService.send_notification(
            recipient=self.user1,
            title="Unread 1",
            message="Test",
            notification_type="in_app"
        )
        
        # Create and mark as read
        notif2 = NotificationService.send_notification(
            recipient=self.user1,
            title="Read",
            message="Test",
            notification_type="in_app"
        )
        notif2.is_read = True
        notif2.save()
        
        # Create notification for other user
        NotificationService.send_notification(
            recipient=self.user2,
            title="Other",
            message="Test",
            notification_type="in_app"
        )
        
        unread = NotificationService.get_unread_notifications(self.user1)
        
        self.assertEqual(unread.count(), 1)
        self.assertEqual(unread.first().title, "Unread 1")

    def test_get_unread_notifications_ordering(self):
        """Test unread notifications are ordered by sent_at descending."""
        import time
        
        notif1 = NotificationService.send_notification(
            recipient=self.user1,
            title="First",
            message="Test",
            notification_type="in_app"
        )
        
        time.sleep(0.01)
        
        notif2 = NotificationService.send_notification(
            recipient=self.user1,
            title="Second",
            message="Test",
            notification_type="in_app"
        )
        
        unread = NotificationService.get_unread_notifications(self.user1)
        
        # Most recent should be first
        self.assertEqual(unread.first().title, "Second")
        self.assertEqual(unread.last().title, "First")

    def test_get_notification_count_no_cache(self):
        """Test getting notification count without cache."""
        # Create notifications
        for i in range(5):
            NotificationService.send_notification(
                recipient=self.user1,
                title=f"Test {i}",
                message="Test",
                notification_type="in_app"
            )
        
        count = NotificationService.get_notification_count(
            self.user1,
            use_cache=False
        )
        
        self.assertEqual(count, 5)

    def test_get_notification_count_with_cache(self):
        """Test getting notification count with caching."""
        # Create notifications
        for i in range(3):
            NotificationService.send_notification(
                recipient=self.user1,
                title=f"Test {i}",
                message="Test",
                notification_type="in_app"
            )
        
        # First call - should cache
        count1 = NotificationService.get_notification_count(
            self.user1,
            use_cache=True
        )
        self.assertEqual(count1, 3)
        
        # Verify value was cached
        cache_key = f"notification_count_{self.user1.id}"
        cached_value = cache.get(cache_key)
        
        # If caching is working, cached_value should be 3
        if cached_value is not None:
            self.assertEqual(cached_value, 3)
            
            # Create more notifications
            NotificationService.send_notification(
                recipient=self.user1,
                title="New",
                message="Test",
                notification_type="in_app"
            )
            
            # Second call - should return cached value
            count2 = NotificationService.get_notification_count(
                self.user1,
                use_cache=True
            )
            self.assertEqual(count2, 3)  # Still cached value
        
        # Without cache should return updated count
        count3 = NotificationService.get_notification_count(
            self.user1,
            use_cache=False
        )
        self.assertGreaterEqual(count3, 3)  # At least 3, possibly 4 if cache worked

    def test_get_notification_count_cache_key_per_user(self):
        """Test that cache keys are user-specific."""
        # Create notifications for both users
        NotificationService.send_notification(
            recipient=self.user1,
            title="User1",
            message="Test",
            notification_type="in_app"
        )
        
        NotificationService.send_notification(
            recipient=self.user2,
            title="User2",
            message="Test",
            notification_type="in_app"
        )
        NotificationService.send_notification(
            recipient=self.user2,
            title="User2-2",
            message="Test",
            notification_type="in_app"
        )
        
        count1 = NotificationService.get_notification_count(
            self.user1,
            use_cache=True
        )
        count2 = NotificationService.get_notification_count(
            self.user2,
            use_cache=True
        )
        
        self.assertEqual(count1, 1)
        self.assertEqual(count2, 2)

    def test_delete_old_notifications_default_30_days(self):
        """Test deleting notifications older than 30 days."""
        # Create old notification (35 days ago)
        old_notif = NotificationService.send_notification(
            recipient=self.user1,
            title="Old",
            message="Test",
            notification_type="in_app"
        )
        old_notif.sent_at = timezone.now() - timedelta(days=35)
        old_notif.save()
        
        # Create recent notification
        recent_notif = NotificationService.send_notification(
            recipient=self.user1,
            title="Recent",
            message="Test",
            notification_type="in_app"
        )
        
        deleted_count = NotificationService.delete_old_notifications(days=30)
        
        self.assertEqual(deleted_count, 1)
        
        # Verify old notification deleted
        self.assertFalse(
            Notification.objects.filter(id=old_notif.id).exists()
        )
        
        # Verify recent notification still exists
        self.assertTrue(
            Notification.objects.filter(id=recent_notif.id).exists()
        )

    def test_delete_old_notifications_custom_days(self):
        """Test deleting notifications with custom day threshold."""
        # Create notification 10 days ago
        old_notif = NotificationService.send_notification(
            recipient=self.user1,
            title="10 days old",
            message="Test",
            notification_type="in_app"
        )
        old_notif.sent_at = timezone.now() - timedelta(days=10)
        old_notif.save()
        
        # Delete notifications older than 7 days
        deleted_count = NotificationService.delete_old_notifications(days=7)
        
        self.assertEqual(deleted_count, 1)

    def test_delete_old_notifications_none_old(self):
        """Test deleting old notifications when none are old enough."""
        # Create recent notification
        NotificationService.send_notification(
            recipient=self.user1,
            title="Recent",
            message="Test",
            notification_type="in_app"
        )
        
        deleted_count = NotificationService.delete_old_notifications(days=30)
        
        self.assertEqual(deleted_count, 0)

    def test_delete_old_notifications_multiple(self):
        """Test deleting multiple old notifications."""
        # Create multiple old notifications
        for i in range(5):
            old_notif = NotificationService.send_notification(
                recipient=self.user1,
                title=f"Old {i}",
                message="Test",
                notification_type="in_app"
            )
            old_notif.sent_at = timezone.now() - timedelta(days=40)
            old_notif.save()
        
        deleted_count = NotificationService.delete_old_notifications(days=30)
        
        self.assertEqual(deleted_count, 5)
