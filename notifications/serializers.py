import re

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import (
    Notification,
    NotificationPreference,
    NotificationRoutingOverride,
    NotificationType,
    Reminder,
)
from .services import NotificationService

_TYPE_SLUG_RE = re.compile(r"^[a-z][a-z0-9_]*$")


class NotificationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationType
        fields = "__all__"

    def validate_name(self, value):
        name = (value or "").strip()
        if not _TYPE_SLUG_RE.match(name):
            raise serializers.ValidationError(
                "Use a lowercase slug starting with a letter "
                "(letters, numbers, and underscores only)."
            )
        return name


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"
        read_only_fields = (
            "id",
            "recipient",
            "sent_at",
            "created_at",
            "updated_at",
        )

    def create(self, validated_data):
        # Staff create path: prefer NotificationService / batch_send over raw create.
        request = self.context.get("request")
        recipient = validated_data.get("recipient")
        if recipient is None and request is not None:
            recipient = request.user
            validated_data["recipient"] = recipient
        title = validated_data.get("title") or "Notice"
        message = validated_data.get("message") or ""
        notification = NotificationService.send_notification(
            recipient=recipient,
            title=title,
            message=message,
            notification_type=validated_data.get("notification_type", "in_app"),
            category=validated_data.get("category", "info"),
        )
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

    user = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(), required=False
    )
    user_email = serializers.EmailField(source="user.email", read_only=True)
    notification = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Reminder
        fields = "__all__"

    def create(self, validated_data):
        request = self.context.get("request")
        actor = getattr(request, "user", None)
        is_admin = bool(
            actor
            and actor.is_authenticated
            and (actor.is_staff or getattr(actor, "is_admin", False))
        )
        if (
            actor
            and actor.is_authenticated
            and (not is_admin or "user" not in validated_data)
        ):
            validated_data["user"] = actor
        return super().create(validated_data)


class NotificationRoutingReferenceSerializer(serializers.Serializer):
    """OpenAPI schema for ``GET /api/notifications/routing-reference/`` (response is a plain dict)."""

    schema_version = serializers.IntegerField(read_only=True)
    reference_api_access = serializers.JSONField(read_only=True)
    settings_categories = serializers.JSONField(read_only=True)
    transactional_routes = serializers.JSONField(read_only=True)
    transactional_route_keys_by_settings_category = serializers.JSONField(
        read_only=True
    )
    reminder_event_type_to_settings_category = serializers.JSONField(read_only=True)
    reminder_event_types_by_settings_category = serializers.JSONField(read_only=True)
    reminder_event_type_descriptions = serializers.JSONField(read_only=True)
    reminder_event_type_recipient_summaries = serializers.JSONField(read_only=True)
    reminder_default_settings_category = serializers.CharField(read_only=True)
    digest = serializers.JSONField(read_only=True)


class NotificationRoutingOverrideSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationRoutingOverride
        fields = "__all__"
