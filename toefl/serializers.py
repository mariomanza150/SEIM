from rest_framework import serializers

from toefl.models import PracticeAttempt


class PracticeAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = PracticeAttempt
        fields = [
            "id",
            "user",
            "external_session_id",
            "exam_code",
            "macro_id",
            "client_ref",
            "earned",
            "total",
            "percent",
            "categories",
            "weakest",
            "items",
            "completed_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class PracticeAttemptListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PracticeAttempt
        fields = [
            "id",
            "external_session_id",
            "exam_code",
            "macro_id",
            "earned",
            "total",
            "percent",
            "weakest",
            "completed_at",
            "created_at",
        ]
        read_only_fields = fields


class LaunchRequestSerializer(serializers.Serializer):
    exam_code = serializers.CharField(required=False, allow_blank=True, max_length=128)
    macro_id = serializers.CharField(required=False, allow_blank=True, max_length=128)
    categories = serializers.ListField(
        child=serializers.CharField(max_length=128),
        required=False,
        allow_empty=True,
    )
    n = serializers.IntegerField(required=False, min_value=1, max_value=50)


class LaunchResponseSerializer(serializers.Serializer):
    launch_url = serializers.URLField()
    token = serializers.CharField(required=False, allow_blank=True)
