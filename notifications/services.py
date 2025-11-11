from datetime import timedelta

from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

from .models import Notification, NotificationPreference, NotificationType
from .tasks import (
    send_notification_by_id,
)


class NotificationService:
    """
    Service for sending notifications and managing user preferences.
    """

    @staticmethod
    def is_enabled(user, type_name):
        """Check if user has enabled notifications for this type."""
        ntype, _ = NotificationType.objects.get_or_create(name=type_name)
        pref = NotificationPreference.objects.filter(user=user, type=ntype).first()
        return pref.enabled if pref else True  # Default to enabled

    @staticmethod
    @transaction.atomic
    def set_preference(user, type_name, enabled=True):
        """Set a user's notification preference."""
        ntype, _ = NotificationType.objects.get_or_create(name=type_name)
        pref, _ = NotificationPreference.objects.get_or_create(user=user, type=ntype)
        pref.enabled = enabled
        pref.save()
        return pref

    @staticmethod
    def send_notification(recipient, title, message, notification_type="in_app", data=None,
                         action_url=None, action_text="View Details"):
        """
        Send a notification to a user with optional action link.

        Args:
            recipient: User to receive notification
            title: Notification title
            message: Notification message
            notification_type: Type of notification ('in_app', 'email', 'both')
            data: Additional JSON data
            action_url: Direct link to related resource (e.g., '/applications/123/')
            action_text: Text for the action button (default: "View Details")

        Returns:
            Notification instance
        """
        # Validate notification type
        valid_types = ['in_app', 'email', 'both']
        if notification_type not in valid_types:
            raise ValueError(f"Invalid notification type: {notification_type}. Must be one of {valid_types}")

        notification = Notification.objects.create(
            recipient=recipient,
            title=title,
            message=message,
            notification_type=notification_type,
            action_url=action_url,
            action_text=action_text,
            data=data or {}
        )

        # Send email notification if type is email or both
        if notification_type in ['email', 'both']:
            send_notification_by_id.delay(notification.id)

        return notification

    @staticmethod
    def send_bulk_notifications(recipients, title, message, notification_type="in_app"):
        """Send notifications to multiple recipients."""
        notifications = []
        for recipient in recipients:
            notification = NotificationService.send_notification(
                recipient=recipient,
                title=title,
                message=message,
                notification_type=notification_type
            )
            notifications.append(notification)
        return notifications

    @staticmethod
    def send_notification_to_role(role_name, title, message, notification_type="in_app"):
        """Send notification to all users with a specific role."""
        from accounts.models import User

        users_with_role = User.objects.filter(roles__name=role_name)
        if not users_with_role.exists():
            raise ValueError(f"No users found with role: {role_name}")

        return NotificationService.send_bulk_notifications(
            recipients=users_with_role,
            title=title,
            message=message,
            notification_type=notification_type
        )

    @staticmethod
    def mark_notification_as_read(notification_id):
        """Mark a notification as read."""
        notification = Notification.objects.get(id=notification_id)
        notification.is_read = True
        notification.save()
        return notification

    @staticmethod
    def mark_all_notifications_as_read(user):
        """Mark all notifications as read for a user."""
        count = Notification.objects.filter(
            recipient=user,
            is_read=False
        ).update(is_read=True)
        return count

    @staticmethod
    def get_unread_notifications(user):
        """Get unread notifications for a user."""
        return Notification.objects.filter(
            recipient=user,
            is_read=False
        ).order_by('-sent_at')

    @staticmethod
    def get_notification_count(user, use_cache=False):
        """Get notification count for a user."""
        if use_cache:
            cache_key = f"notification_count_{user.id}"
            cached_count = cache.get(cache_key)
            if cached_count is not None:
                return cached_count

        count = Notification.objects.filter(recipient=user).count()

        if use_cache:
            cache.set(cache_key, count, 300)  # Cache for 5 minutes

        return count

    @staticmethod
    def delete_old_notifications(days=30):
        """Delete notifications older than specified days."""
        cutoff_date = timezone.now() - timedelta(days=days)
        deleted_count, _ = Notification.objects.filter(
            sent_at__lt=cutoff_date
        ).delete()
        return deleted_count
