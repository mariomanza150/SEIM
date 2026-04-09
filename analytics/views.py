from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Count
from django.shortcuts import render
from django.utils import timezone
from django.utils.dateparse import parse_date
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import User
from core.cache import cache_api_response
from documents.models import Document
from exchange.models import Application, Program
from notifications.models import Notification

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
from .dashboard_export import render_dashboard_export_csv, render_dashboard_export_xlsx
from .services import AnalyticsService

# Create your views here.


def _request_params(request):
    return getattr(request, "query_params", request.GET)


def _parse_analytics_filters(request):
    params = _request_params(request)
    start_date = parse_date(params.get("date_start") or "")
    end_date = parse_date(params.get("date_end") or "")
    program_id = params.get("program")
    return start_date, end_date, program_id


def _filter_by_date_range(queryset, field_name, start_date=None, end_date=None):
    if start_date:
        queryset = queryset.filter(**{f"{field_name}__date__gte": start_date})
    if end_date:
        queryset = queryset.filter(**{f"{field_name}__date__lte": end_date})
    return queryset


def _get_filtered_applications(request):
    start_date, end_date, program_id = _parse_analytics_filters(request)
    applications = Application.objects.select_related("program", "status", "student")
    applications = _filter_by_date_range(applications, "created_at", start_date, end_date)

    if program_id:
        applications = applications.filter(program_id=program_id)

    return applications, start_date, end_date, program_id


def _days_from_filters(start_date, end_date, default_days=30):
    if start_date and end_date and end_date >= start_date:
        return max((end_date - start_date).days + 1, 1)
    return default_days


def _status_breakdown(queryset):
    return {
        item["status__name"] or "unknown": item["count"]
        for item in queryset.values("status__name").annotate(count=Count("id")).order_by("status__name")
    }


def _average_processing_time_days(queryset):
    processed = list(
        queryset.filter(status__name__in=["approved", "rejected", "completed"])
    )
    if not processed:
        return 0

    total_days = 0
    now = timezone.now()
    for application in processed:
        reference_time = application.submitted_at or application.created_at or now
        total_days += max((now - reference_time).total_seconds(), 0) / 86400

    return round(total_days / len(processed), 1)


def _build_monthly_trend(queryset):
    trend = (
        queryset.extra(select={"day": "date(created_at)"})
        .values("day")
        .annotate(total=Count("id"))
        .order_by("day")
    )
    return {
        "labels": [str(item["day"]) for item in trend],
        "values": [item["total"] for item in trend],
    }


def _build_user_activity_payload(days):
    activity = AnalyticsService.get_user_activity(days=days)
    return {
        "labels": [str(item["day"]) for item in activity],
        "values": [item.get("logins", 0) for item in activity],
    }


def _build_program_performance(queryset, program_id=None):
    programs = Program.objects.all().order_by("name")
    if program_id:
        programs = programs.filter(id=program_id)

    performance = []
    for program in programs:
        program_applications = queryset.filter(program=program)
        processed_count = program_applications.filter(
            status__name__in=["approved", "rejected", "completed"],
            withdrawn=False,
        ).count()
        approved_count = program_applications.filter(
            status__name="approved",
            withdrawn=False,
        ).count()
        approval_rate = round((approved_count / processed_count) * 100) if processed_count else 0

        performance.append(
            {
                "name": program.name,
                "institution": "N/A",
                "applications": program_applications.count(),
                "approval_rate": approval_rate,
                "avg_processing_time": _average_processing_time_days(program_applications),
            }
        )

    max_applications = max((item["applications"] for item in performance), default=0)
    for item in performance:
        item["popularity_score"] = (
            round((item["applications"] / max_applications) * 100)
            if max_applications
            else 0
        )

    return performance


def _build_dashboard_payload(request):
    applications, start_date, end_date, program_id = _get_filtered_applications(request)
    days = _days_from_filters(start_date, end_date)
    application_status = _status_breakdown(applications)
    total_applications = applications.count()
    approved_count = applications.filter(status__name="approved", withdrawn=False).count()
    processed_count = applications.filter(
        status__name__in=["approved", "rejected", "completed"],
        withdrawn=False,
    ).count()
    active_programs = Program.objects.filter(is_active=True)
    if program_id:
        active_programs = active_programs.filter(id=program_id)

    return {
        "metrics": {
            "total_applications": total_applications,
            "approval_rate": round((approved_count / processed_count) * 100) if processed_count else 0,
            "avg_processing_time": _average_processing_time_days(applications),
            "active_programs": active_programs.count(),
        },
        "application_status": application_status,
        "monthly_trend": _build_monthly_trend(applications),
        "user_activity": _build_user_activity_payload(days),
        "demographics": AnalyticsService.get_user_demographics().get("users_by_role", {}),
        "program_performance": _build_program_performance(applications, program_id=program_id),
    }


def _build_detailed_report(report_type, request):
    applications, _, _, program_id = _get_filtered_applications(request)

    if report_type == "applications":
        status_rows = _status_breakdown(applications)
        data = [
            {"status": status_name, "applications": count}
            for status_name, count in status_rows.items()
        ]
        summary = f"{applications.count()} applications grouped into {len(data)} status buckets."
    elif report_type == "programs":
        data = _build_program_performance(applications, program_id=program_id)
        summary = f"{len(data)} program performance rows generated from current analytics filters."
    elif report_type == "users":
        data = list(
            applications.values("student__username")
            .annotate(total_applications=Count("id"))
            .order_by("-total_applications", "student__username")
        )
        data = [
            {
                "username": item["student__username"],
                "total_applications": item["total_applications"],
            }
            for item in data
        ]
        summary = f"{len(data)} user activity rows generated from application ownership."
    else:
        return None

    return {
        "report_type": report_type,
        "summary": summary,
        "data": data,
    }


def _build_export_response(request):
    dashboard_payload = _build_dashboard_payload(request)
    # Avoid query param name `format` — DRF uses it for content negotiation and can 404 unknown values.
    fmt = (_request_params(request).get("export_format") or "csv").strip().lower()
    if fmt in ("xlsx", "excel"):
        body = render_dashboard_export_xlsx(dashboard_payload)
        response = HttpResponse(
            body,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="analytics-report.xlsx"'
        return response

    body = render_dashboard_export_csv(dashboard_payload)
    response = HttpResponse(body, content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="analytics-report.csv"'
    return response


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
    return Response(
        AnalyticsService.get_application_statistics(),
        status=status.HTTP_200_OK,
    )


@extend_schema(
    responses={200: ProgramStatisticsSerializer}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_program_statistics(request):
    """Get program statistics."""
    program_stats = AnalyticsService.get_program_statistics()
    return Response(
        {
            "total_programs": len(program_stats),
            "active_programs": sum(1 for program in program_stats if program.get("is_active")),
            "program_performance": program_stats,
        },
        status=status.HTTP_200_OK,
    )


@extend_schema(
    responses={200: UserActivitySerializer}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_user_activity(request):
    """Get user activity statistics."""
    start_date, end_date, _ = _parse_analytics_filters(request)
    days = _days_from_filters(start_date, end_date)
    user_activity = AnalyticsService.get_user_activity(days=days)
    active_users = User.objects.filter(
        sessions__created_at__gte=timezone.now() - timezone.timedelta(days=days)
    ).distinct().count()
    return Response(
        {
            "total_users": User.objects.count(),
            "active_users": active_users,
            "user_activity": user_activity,
        },
        status=status.HTTP_200_OK,
    )


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
@permission_classes([IsAuthenticated])
def metrics_view(request):
    """Get aggregated analytics metrics for the admin analytics UI."""
    return Response(_build_dashboard_payload(request), status=200)


@extend_schema(
    responses={200: GenericAnalyticsSerializer}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reports_view(request):
    """List available detailed analytics reports."""
    return Response(
        {
            "reports": [
                {"type": "applications", "label": "Applications", "endpoint": "/api/analytics/reports/applications/"},
                {"type": "programs", "label": "Programs", "endpoint": "/api/analytics/reports/programs/"},
                {"type": "users", "label": "Users", "endpoint": "/api/analytics/reports/users/"},
            ]
        },
        status=200,
    )


@extend_schema(
    responses={200: GenericAnalyticsSerializer}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def application_analytics_view(request):
    """Get application-focused analytics."""
    applications, start_date, end_date, _ = _get_filtered_applications(request)
    days = _days_from_filters(start_date, end_date)
    return Response(
        {
            "application_analytics": {
                "summary": AnalyticsService.get_application_statistics(),
                "conversion_rates": AnalyticsService.get_conversion_rates(),
                "trend": _build_monthly_trend(applications),
                "time_window_days": days,
            }
        },
        status=200,
    )


@extend_schema(
    responses={200: GenericAnalyticsSerializer}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def document_analytics_view(request):
    """Get document-focused analytics."""
    start_date, end_date, _ = _parse_analytics_filters(request)
    documents = Document.objects.select_related("application", "type")
    documents = _filter_by_date_range(documents, "created_at", start_date, end_date)
    by_type = {
        item["type__name"]: item["count"]
        for item in documents.values("type__name").annotate(count=Count("id")).order_by("type__name")
    }
    return Response(
        {
            "document_analytics": {
                "total_documents": documents.count(),
                "valid_documents": documents.filter(is_valid=True).count(),
                "pending_documents": documents.filter(is_valid=False).count(),
                "documents_by_type": by_type,
            }
        },
        status=200,
    )


@extend_schema(
    responses={200: GenericAnalyticsSerializer}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_analytics_view(request):
    """Get notification-focused analytics."""
    start_date, end_date, _ = _parse_analytics_filters(request)
    notifications = Notification.objects.all()
    notifications = _filter_by_date_range(notifications, "sent_at", start_date, end_date)
    by_category = {
        item["category"]: item["count"]
        for item in notifications.values("category").annotate(count=Count("id")).order_by("category")
    }
    by_channel = {
        item["notification_type"]: item["count"]
        for item in notifications.values("notification_type").annotate(count=Count("id")).order_by("notification_type")
    }
    return Response(
        {
            "notification_analytics": {
                "total_notifications": notifications.count(),
                "unread_notifications": notifications.filter(is_read=False).count(),
                "notifications_by_category": by_category,
                "notifications_by_channel": by_channel,
            }
        },
        status=200,
    )


@extend_schema(
    responses={200: GenericAnalyticsSerializer}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def program_analytics_view(request):
    """Get program-focused analytics."""
    applications, _, _, program_id = _get_filtered_applications(request)
    return Response(
        {
            "program_analytics": _build_program_performance(
                applications,
                program_id=program_id,
            )
        },
        status=200,
    )


@extend_schema(
    responses={200: GenericAnalyticsSerializer}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_analytics_view(request):
    """Get user-focused analytics."""
    start_date, end_date, _ = _parse_analytics_filters(request)
    days = _days_from_filters(start_date, end_date)
    return Response(
        {
            "user_analytics": {
                "demographics": AnalyticsService.get_user_demographics(),
                "engagement": AnalyticsService.get_user_engagement_metrics(),
                "activity": AnalyticsService.get_user_activity(days=days),
            }
        },
        status=200,
    )


@extend_schema(
    responses={200: GenericAnalyticsSerializer, 401: ErrorResponseSerializer}
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def analytics_dashboard_api(request):
    """Get the analytics dashboard payload expected by the admin analytics page."""
    return Response(_build_dashboard_payload(request), status=status.HTTP_200_OK)


@extend_schema(
    responses={200: GenericAnalyticsSerializer, 401: ErrorResponseSerializer, 404: ErrorResponseSerializer}
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def analytics_report_detail_api(request, report_type):
    """Get a detailed analytics report by type."""
    report = _build_detailed_report(report_type, request)
    if report is None:
        return Response({"error": "Unknown report type"}, status=status.HTTP_404_NOT_FOUND)
    return Response(report, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def analytics_export_api(request):
    """Export current analytics dashboard data as CSV (default) or Excel (`export_format=xlsx`)."""
    return _build_export_response(request)
