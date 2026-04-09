import logging
from datetime import timedelta

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

from .models import Notification, NotificationPreference, NotificationType
from .tasks import (
    send_notification_by_id,
)

logger = logging.getLogger(__name__)


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
                         action_url=None, action_text="View Details", category="info"):
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
            category: Notification category ('info', 'success', 'warning', 'error')

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
            data=data or {},
            category=category
        )

        # Send email notification if type is email or both
        if notification_type in ['email', 'both']:
            send_notification_by_id.delay(notification.id)

        # Send real-time notification via WebSocket
        NotificationService._broadcast_notification(recipient, notification)

        return notification
    
    @staticmethod
    def _broadcast_notification(recipient, notification):
        """
        Broadcast notification to user's WebSocket channel via Django Channels.
        
        This method sends real-time notifications to connected clients through WebSocket.
        If the user is not connected or WebSocket broadcasting fails, the notification
        is still saved in the database and can be retrieved via API.
        
        Args:
            recipient: User to send notification to
            notification: Notification instance
        """
        try:
            channel_layer = get_channel_layer()
            if not channel_layer:
                logger.warning("Channel layer not configured. WebSocket notifications disabled.")
                return
                
            notification_group = f"notifications_{recipient.id}"
            
            # Prepare notification data for WebSocket
            notification_data = {
                'type': 'notification_new',
                'notification': {
                    'id': str(notification.id),
                    'title': notification.title,
                    'message': notification.message,
                    'category': notification.category,
                    'action_url': notification.action_url,
                    'action_text': notification.action_text,
                    'sent_at': notification.sent_at.isoformat(),
                    'is_read': notification.is_read,
                    'data': notification.data or {},
                }
            }
            
            # Send to user's notification group
            async_to_sync(channel_layer.group_send)(
                notification_group,
                notification_data
            )
            
            logger.debug(
                f"Broadcast notification {notification.id} to user {recipient.id} via WebSocket"
            )
            
        except Exception as e:
            # Log error but don't fail the notification
            # The notification is still saved in database and accessible via API
            logger.error(
                f"Failed to broadcast notification {notification.id} via WebSocket: {e}",
                exc_info=True
            )

    @staticmethod
    def broadcast_application_sync(application_id, change_type, document_id=None):
        """
        Push a lightweight sync hint to all stakeholders (student, assigned coordinator,
        program coordinators) so SPA detail views can refetch without a new notification row.
        """
        try:
            channel_layer = get_channel_layer()
            if not channel_layer:
                return
            from exchange.models import Application

            app = (
                Application.objects.select_related("student", "assigned_coordinator")
                .prefetch_related("program__coordinators")
                .filter(pk=application_id)
                .first()
            )
            if not app:
                return
            user_ids = set()
            if app.student_id:
                user_ids.add(app.student_id)
            if app.assigned_coordinator_id:
                user_ids.add(app.assigned_coordinator_id)
            user_ids.update(app.program.coordinators.values_list("id", flat=True))
            doc_part = str(document_id) if document_id is not None else None
            for uid in user_ids:
                async_to_sync(channel_layer.group_send)(
                    f"notifications_{uid}",
                    {
                        "type": "application.sync",
                        "application_id": str(application_id),
                        "change_type": change_type,
                        "document_id": doc_part,
                    },
                )
        except Exception as e:
            logger.debug("broadcast_application_sync skipped: %s", e, exc_info=True)

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
