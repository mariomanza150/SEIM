"""
Notification serializers for the exchange application.

Handles serialization for notification-related models.
"""

from rest_framework import serializers
from ...models import NotificationType
from .base import TimestampedModelSerializer


class NotificationTypeSerializer(TimestampedModelSerializer):
    """
    Serializer for NotificationType model.
    """
    
    class Meta:
        model = NotificationType
        fields = '__all__'


# Create alias for backward compatibility
NotificationSerializer = NotificationTypeSerializer
