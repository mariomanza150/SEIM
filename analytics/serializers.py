from rest_framework import serializers

from .models import DashboardConfig, Metric, Report


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = "__all__"


class MetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metric
        fields = "__all__"


class DashboardConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardConfig
        fields = "__all__"


# Admin Dashboard Response Serializers
class DashboardMetricsSerializer(serializers.Serializer):
    """Serializer for dashboard metrics response."""
    total_users = serializers.IntegerField()
    total_applications = serializers.IntegerField()
    total_programs = serializers.IntegerField()
    pending_reviews = serializers.IntegerField()
    application_status = serializers.DictField()
    ongoing_applications = serializers.IntegerField(required=False)
    approved_applications = serializers.IntegerField(required=False)
    rejected_applications = serializers.IntegerField(required=False)


class ActivitySerializer(serializers.Serializer):
    """Serializer for activity timeline entry."""
    id = serializers.IntegerField()
    type = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()
    user = serializers.CharField(allow_null=True)
    timestamp = serializers.CharField()
    related_object = serializers.DictField()


class PerformanceMetricsSerializer(serializers.Serializer):
    """Serializer for system performance metrics."""
    cpu_usage = serializers.IntegerField()
    memory_usage = serializers.IntegerField()
    db_connections = serializers.IntegerField()
    cache_hit_rate = serializers.IntegerField()
    response_time = serializers.FloatField()
    active_users = serializers.IntegerField()


class AlertSerializer(serializers.Serializer):
    """Serializer for system alert."""
    level = serializers.CharField()
    title = serializers.CharField()
    message = serializers.CharField()
    timestamp = serializers.CharField()


class SystemInfoSerializer(serializers.Serializer):
    """Serializer for system information."""
    django_version = serializers.CharField()
    python_version = serializers.CharField()
    database = serializers.CharField()
    redis = serializers.CharField()
    environment = serializers.CharField()
    debug = serializers.BooleanField()
    timezone = serializers.CharField()
    static_files = serializers.CharField()
    media_files = serializers.CharField()


# Simple API Response Serializers
class ApplicationStatisticsSerializer(serializers.Serializer):
    """Serializer for application statistics."""
    total_applications = serializers.IntegerField()
    total_users = serializers.IntegerField(required=False)
    total_programs = serializers.IntegerField(required=False)
    applications_by_status = serializers.DictField(required=False)


class ProgramStatisticsSerializer(serializers.Serializer):
    """Serializer for program statistics."""
    total_programs = serializers.IntegerField()
    active_programs = serializers.IntegerField(required=False)
    program_performance = serializers.ListField(child=serializers.DictField(), required=False)


class UserActivitySerializer(serializers.Serializer):
    """Serializer for user activity statistics."""
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField(required=False)
    user_activity = serializers.ListField(child=serializers.DictField(), required=False)


class TrackEventRequestSerializer(serializers.Serializer):
    """Serializer for event tracking request."""
    event_type = serializers.CharField()


class GenericAnalyticsSerializer(serializers.Serializer):
    """Generic serializer for analytics responses."""
    metrics = serializers.DictField(required=False)
    reports = serializers.ListField(child=serializers.DictField(), required=False)
    application_analytics = serializers.DictField(required=False)
    document_analytics = serializers.DictField(required=False)
    notification_analytics = serializers.DictField(required=False)
    program_analytics = serializers.ListField(child=serializers.DictField(), required=False)
    user_analytics = serializers.DictField(required=False)


class ErrorResponseSerializer(serializers.Serializer):
    """Serializer for error responses."""
    error = serializers.CharField()