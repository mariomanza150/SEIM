from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import User
from core.cache import cache_api_response
from exchange.models import Application, Program

from .models import DashboardConfig, Metric, Report
from .serializers import (
    ActivitySerializer,
    AlertSerializer,
    ApplicationStatisticsSerializer,
    DashboardConfigSerializer,
    DashboardMetricsSerializer,
    ErrorResponseSerializer,
    GenericAnalyticsSerializer,
    MetricSerializer,
    PerformanceMetricsSerializer,
    ProgramStatisticsSerializer,
    ReportSerializer,
    SystemInfoSerializer,
    TrackEventRequestSerializer,
    UserActivitySerializer,
)
from .services import AnalyticsService

# Create your views here.


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer

    @cache_api_response(timeout=600)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_api_response(timeout=600)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def generate(self, request, pk=None):
        report = self.get_object()
        AnalyticsService.trigger_report(report)
        return Response({"status": "report generation started"})


class MetricViewSet(viewsets.ModelViewSet):
    queryset = Metric.objects.all()
    serializer_class = MetricSerializer

    @cache_api_response(timeout=600)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_api_response(timeout=600)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @action(detail=False, methods=["get"])
    @cache_api_response(timeout=300)
    def dashboard(self, request):
        """Get dashboard metrics for admin."""
        metrics = AnalyticsService.get_dashboard_metrics()
        return Response(metrics)

    @action(detail=False, methods=["get"])
    @cache_api_response(timeout=300)
    def program(self, request):
        """Get metrics for specific program or all programs."""
        program_id = request.query_params.get("program_id")
        metrics = AnalyticsService.get_program_metrics(program_id)
        return Response(metrics)


class DashboardConfigViewSet(viewsets.ModelViewSet):
    queryset = DashboardConfig.objects.all()
    serializer_class = DashboardConfigSerializer

    @cache_api_response(timeout=600)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_api_response(timeout=600)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


@extend_schema_view(
    metrics=extend_schema(
        responses={200: DashboardMetricsSerializer, 403: ErrorResponseSerializer, 500: ErrorResponseSerializer}
    ),
    activity=extend_schema(
        responses={200: ActivitySerializer(many=True), 403: ErrorResponseSerializer, 500: ErrorResponseSerializer}
    ),
    performance=extend_schema(
        responses={200: PerformanceMetricsSerializer, 403: ErrorResponseSerializer, 500: ErrorResponseSerializer}
    ),
    alerts=extend_schema(
        responses={200: AlertSerializer(many=True), 403: ErrorResponseSerializer, 500: ErrorResponseSerializer}
    ),
    system_info=extend_schema(
        responses={200: SystemInfoSerializer, 403: ErrorResponseSerializer, 500: ErrorResponseSerializer}
    ),
)
class AdminDashboardViewSet(viewsets.ViewSet):
    """Admin dashboard API endpoints."""
    permission_classes = [IsAuthenticated]

    def is_admin(self, user):
        return user.has_role("admin")

    @action(detail=False, methods=["get"])
    @cache_api_response(timeout=300)
    def metrics(self, request):
        """Get comprehensive dashboard metrics."""
        if not self.is_admin(request.user):
            return Response({"error": "Admin access required"}, status=403)

        try:
            # Get basic metrics
            metrics = AnalyticsService.get_dashboard_metrics()

            # Add additional metrics
            total_users = User.objects.count()
            total_programs = Program.objects.filter(is_active=True).count()
            pending_reviews = Application.objects.filter(
                status__name="submitted"
            ).count()

            # Application status breakdown
            application_status = {}
            for status_name in ["draft", "submitted", "under_review", "approved", "rejected", "withdrawn"]:
                application_status[status_name] = Application.objects.filter(
                    status__name=status_name
                ).count()

            return Response({
                "total_users": total_users,
                "total_applications": metrics.get("ongoing_applications", 0) + metrics.get("approved_applications", 0) + metrics.get("rejected_applications", 0),
                "total_programs": total_programs,
                "pending_reviews": pending_reviews,
                "application_status": application_status,
                **metrics
            })
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=False, methods=["get"])
    @cache_api_response(timeout=300)
    def activity(self, request):
        """Get recent activity timeline."""
        if not self.is_admin(request.user):
            return Response({"error": "Admin access required"}, status=403)

        try:
            from datetime import timedelta

            from django.utils import timezone

            from exchange.models import TimelineEvent

            # Get recent events (last 7 days)
            recent_events = TimelineEvent.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=7)
            ).select_related('application', 'created_by').order_by('-created_at')[:20]

            activities = []
            for event in recent_events:
                activities.append({
                    "id": event.id,
                    "type": event.event_type,
                    "title": getattr(event, 'title', ''),
                    "description": event.description,
                    "user": (event.created_by.get_full_name() if event.created_by else None) or (event.created_by.username if event.created_by else None),
                    "timestamp": event.created_at.strftime("%Y-%m-%d %H:%M"),
                    "related_object": {
                        "type": "application",
                        "id": event.application.id
                    }
                })

            return Response(activities)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=False, methods=["get"])
    @cache_api_response(timeout=300)
    def performance(self, request):
        """Get system performance metrics."""
        if not self.is_admin(request.user):
            return Response({"error": "Admin access required"}, status=403)

        try:
            # Mock performance data for now
            # In production, this would come from system monitoring
            import random
            performance_data = {
                "cpu_usage": random.randint(10, 80),
                "memory_usage": random.randint(20, 90),
                "db_connections": random.randint(5, 25),
                "cache_hit_rate": random.randint(70, 95),
                "response_time": random.uniform(50, 200),
                "active_users": User.objects.filter(is_active=True).count()
            }

            return Response(performance_data)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=False, methods=["get"])
    @cache_api_response(timeout=300)
    def alerts(self, request):
        """Get system alerts."""
        if not self.is_admin(request.user):
            return Response({"error": "Admin access required"}, status=403)

        try:
            # Mock system alerts for now
            # In production, this would come from monitoring systems
            alerts = []

            # Check for applications pending review for too long
            old_pending = Application.objects.filter(
                status__name="submitted",
                created_at__lt=timezone.now() - timezone.timedelta(days=7)
            ).count()

            if old_pending > 0:
                alerts.append({
                    "level": "warning",
                    "title": "Applications Pending Review",
                    "message": f"{old_pending} applications have been pending review for over 7 days",
                    "timestamp": timezone.now().strftime("%Y-%m-%d %H:%M")
                })

            # Check for system issues (mock)
            import random
            if random.random() < 0.1:  # 10% chance of mock alert
                alerts.append({
                    "level": "info",
                    "title": "System Maintenance",
                    "message": "Scheduled maintenance completed successfully",
                    "timestamp": timezone.now().strftime("%Y-%m-%d %H:%M")
                })

            return Response(alerts)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=False, methods=["get"])
    @cache_api_response(timeout=300)
    def system_info(self, request):
        """Get system information."""
        if not self.is_admin(request.user):
            return Response({"error": "Admin access required"}, status=403)

        try:
            import sys

            from django.conf import settings
            from django.db import connection

            # Get system information
            system_info = {
                "django_version": "5.2.3",  # Hardcoded for now
                "python_version": sys.version,
                "database": connection.vendor,
                "redis": "Connected" if settings.CACHES else "Not configured",
                "environment": getattr(settings, 'ENVIRONMENT', 'development'),
                "debug": settings.DEBUG,
                "timezone": str(settings.TIME_ZONE),
                "static_files": "Served" if settings.STATIC_URL else "Not configured",
                "media_files": "Served" if settings.MEDIA_URL else "Not configured"
            }

            return Response(system_info)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

@login_required
def dashboard_view(request):
    return render(request, 'frontend/admin/dashboard.html')

@login_required
def application_statistics_view(request):
    return render(request, 'frontend/admin/analytics.html')

@login_required
def program_statistics_view(request):
    return render(request, 'frontend/admin/analytics.html')

@login_required
def user_activity_view(request):
    return render(request, 'frontend/admin/analytics.html')

@login_required
def export_data_view(request):
    return render(request, 'frontend/admin/analytics.html')

@extend_schema(
    responses={200: ApplicationStatisticsSerializer}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_application_statistics(request):
    """Get application statistics."""
    return Response({"total_applications": 0}, status=status.HTTP_200_OK)


@extend_schema(
    responses={200: ProgramStatisticsSerializer}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_program_statistics(request):
    """Get program statistics."""
    return Response({"total_programs": 0}, status=status.HTTP_200_OK)


@extend_schema(
    responses={200: UserActivitySerializer}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_user_activity(request):
    """Get user activity statistics."""
    return Response({"total_users": 0}, status=status.HTTP_200_OK)


@extend_schema(
    request=TrackEventRequestSerializer,
    responses={201: None, 400: None, 401: None}
)
@api_view(['POST'])
def track_event(request):
    """Track an analytics event."""
    if not request.user.is_authenticated:
        return Response({}, status=status.HTTP_401_UNAUTHORIZED)
    event_type = request.data.get('event_type', '')
    if not event_type:
        return Response({}, status=status.HTTP_400_BAD_REQUEST)
    return Response({}, status=status.HTTP_201_CREATED)


@extend_schema(
    responses={200: GenericAnalyticsSerializer}
)
@api_view(['GET'])
def metrics_view(request):
    """Get metrics stub."""
    return Response({'metrics': 'stub'}, status=200)


@extend_schema(
    responses={200: GenericAnalyticsSerializer}
)
@api_view(['GET'])
def reports_view(request):
    """Get reports stub."""
    return Response({'reports': 'stub'}, status=200)


@extend_schema(
    responses={200: GenericAnalyticsSerializer}
)
@api_view(['GET'])
def application_analytics_view(request):
    """Get application analytics stub."""
    return Response({'application_analytics': 'stub'}, status=200)


@extend_schema(
    responses={200: GenericAnalyticsSerializer}
)
@api_view(['GET'])
def document_analytics_view(request):
    """Get document analytics stub."""
    return Response({'document_analytics': 'stub'}, status=200)


@extend_schema(
    responses={200: GenericAnalyticsSerializer}
)
@api_view(['GET'])
def notification_analytics_view(request):
    """Get notification analytics stub."""
    return Response({'notification_analytics': 'stub'}, status=200)


@extend_schema(
    responses={200: GenericAnalyticsSerializer}
)
@api_view(['GET'])
def program_analytics_view(request):
    """Get program analytics stub."""
    return Response({'program_analytics': 'stub'}, status=200)


@extend_schema(
    responses={200: GenericAnalyticsSerializer}
)
@api_view(['GET'])
def user_analytics_view(request):
    """Get user analytics stub."""
    return Response({'user_analytics': 'stub'}, status=200)
