from rest_framework import serializers

from .models import Notification, NotificationPreference, NotificationType, Reminder
from .services import NotificationService


class NotificationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationType
        fields = "__all__"


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"

    def create(self, validated_data):
        user = validated_data["user"]
        type_name = validated_data["type"].name
        message = validated_data["message"]
        notification = NotificationService.send_notification(user, type_name, message)
        if notification is None:
            raise serializers.ValidationError(
                "User has disabled this notification type."
            )
        return notification


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = "__all__"


class ReminderSerializer(serializers.ModelSerializer):
    """Serializer for Reminder model."""
    
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    notification = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Reminder
        fields = "__all__"
    
    def create(self, validated_data):
        """Set user from request context."""
        request = self.context.get('request')
        if request and request.user:
            validated_data['user'] = request.user
        return super().create(validated_data)


class NotificationRoutingReferenceSerializer(serializers.Serializer):
    """OpenAPI schema for ``GET /api/notifications/routing-reference/`` (response is a plain dict)."""

    schema_version = serializers.IntegerField(read_only=True)
    reference_api_access = serializers.JSONField(read_only=True)
    settings_categories = serializers.JSONField(read_only=True)
    reminder_event_type_to_settings_category = serializers.JSONField(read_only=True)
    reminder_event_type_descriptions = serializers.JSONField(read_only=True)
    reminder_default_settings_category = serializers.CharField(read_only=True)
    digest = serializers.JSONField(read_only=True)
