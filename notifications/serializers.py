from rest_framework import serializers

from .models import Notification, NotificationPreference, NotificationType
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
