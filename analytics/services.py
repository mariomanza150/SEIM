from datetime import timedelta

from django.core.cache import cache
from django.db import connection
from django.db.models import Count
from django.utils import timezone

from accounts.models import User
from core.cache import cache_analytics, generate_cache_key
from exchange.models import Application, ApplicationStatus, Program

from .tasks import generate_report


class AnalyticsService:
    @staticmethod
    def trigger_report(report):
        generate_report.delay(str(report.id))

    @staticmethod
    @cache_analytics(timeout=1800)  # Cache for 30 minutes
    def get_application_statistics():
        """Get comprehensive application statistics."""
        total_applications = Application.objects.count()
        total_users = User.objects.filter(application__isnull=False).distinct().count()
        total_programs = Program.objects.count()

        applications_by_status = {}
        for status in ApplicationStatus.objects.all():
            count = Application.objects.filter(status=status).count()
            applications_by_status[status.name] = count

        return {
            'total_applications': total_applications,
            'total_users': total_users,
            'total_programs': total_programs,
            'applications_by_status': applications_by_status
        }

    @staticmethod
    @cache_analytics(timeout=1800)
    def get_program_statistics():
        """Get statistics for all programs."""
        programs = Program.objects.all()
        stats = []

        for program in programs:
            total_applications = Application.objects.filter(program=program).count()
            stats.append({
                'name': program.name,
                'total_applications': total_applications,
                'is_active': program.is_active
            })

        return stats

    @staticmethod
    @cache_analytics(timeout=1800)
    def get_user_statistics():
        """Get statistics for all users with applications."""
        users = User.objects.filter(application__isnull=False).distinct()
        stats = []

        for user in users:
            total_applications = Application.objects.filter(student=user).count()
            stats.append({
                'username': user.username,
                'total_applications': total_applications
            })

        return stats

    @staticmethod
    @cache_analytics(timeout=1800)
    def get_timeline_statistics(days=30):
        """Get application trends over time."""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        applications = Application.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        ).extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(
            applications=Count('id')
        ).order_by('day')

        return list(applications)

    @staticmethod
    @cache_analytics(timeout=1800)
    def get_conversion_rates():
        """Get conversion rates between application statuses."""
        draft_count = Application.objects.filter(status__name='draft').count()
        submitted_count = Application.objects.filter(status__name='submitted').count()
        approved_count = Application.objects.filter(status__name='approved').count()

        draft_to_submitted = (submitted_count / draft_count * 100) if draft_count > 0 else 0
        submitted_to_approved = (approved_count / submitted_count * 100) if submitted_count > 0 else 0

        return {
            'draft_to_submitted': draft_to_submitted,
            'submitted_to_approved': submitted_to_approved
        }

    @staticmethod
    @cache_analytics(timeout=1800)
    def get_user_engagement_metrics():
        """Get user engagement metrics."""
        active_users = User.objects.filter(application__isnull=False).distinct().count()
        total_applications = Application.objects.count()
        average_applications = total_applications / active_users if active_users > 0 else 0

        return {
            'active_users': active_users,
            'average_applications_per_user': average_applications
        }

    @staticmethod
    @cache_analytics(timeout=1800)
    def get_program_performance_metrics():
        """Get performance metrics for all programs."""
        programs = Program.objects.all()
        metrics = []

        for program in programs:
            total_applications = Application.objects.filter(program=program).count()
            metrics.append({
                'name': program.name,
                'total_applications': total_applications,
                'is_active': program.is_active
            })

        return metrics

    @staticmethod
    @cache_analytics(timeout=1800)
    def get_application_trends(days=30):
        """Get application trends over time."""
        return AnalyticsService.get_timeline_statistics(days)

    @staticmethod
    @cache_analytics(timeout=1800)
    def get_user_demographics():
        """Get user demographics."""
        total_users = User.objects.count()
        users_by_role = {}

        for user in User.objects.all():
            role = user.primary_role or 'unknown'
            users_by_role[role] = users_by_role.get(role, 0) + 1

        return {
            'total_users': total_users,
            'users_by_role': users_by_role
        }

    @staticmethod
    @cache_analytics(timeout=1800)
    def get_system_health_metrics():
        """Get system health metrics."""
        total_programs = Program.objects.count()
        total_applications = Application.objects.count()
        total_users = User.objects.count()

        return {
            'total_programs': total_programs,
            'total_applications': total_applications,
            'total_users': total_users
        }

    @staticmethod
    def get_custom_analytics(query):
        """Execute custom analytics query."""
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            result = dict(zip(columns, cursor.fetchone(), strict=False))
            return result

    @staticmethod
    @cache_analytics(timeout=1800)  # Cache for 30 minutes
    def get_dashboard_metrics():
        """Get key metrics for admin dashboard."""
        now = timezone.now()

        # Total students (users with applications)
        total_students = (
            User.objects.filter(application__isnull=False).distinct().count()
        )

        # Applications by status
        applications_by_status = Application.objects.values("status__name").annotate(
            count=Count("id")
        )

        # Ongoing applications (submitted or under_review)
        ongoing_applications = Application.objects.filter(
            status__name__in=["submitted", "under_review"], withdrawn=False
        ).count()

        # Approved applications
        approved_applications = Application.objects.filter(
            status__name="approved", withdrawn=False
        ).count()

        # Rejected applications
        rejected_applications = Application.objects.filter(
            status__name="rejected", withdrawn=False
        ).count()

        # Withdrawn applications
        withdrawn_applications = Application.objects.filter(withdrawn=True).count()

        # Recent applications (last 30 days)
        recent_applications = Application.objects.filter(
            created_at__gte=now - timezone.timedelta(days=30)
        ).count()

        # Applications this month
        this_month_applications = Application.objects.filter(
            created_at__year=now.year, created_at__month=now.month
        ).count()

        return {
            "total_students": total_students,
            "ongoing_applications": ongoing_applications,
            "approved_applications": approved_applications,
            "rejected_applications": rejected_applications,
            "withdrawn_applications": withdrawn_applications,
            "recent_applications": recent_applications,
            "this_month_applications": this_month_applications,
            "applications_by_status": list(applications_by_status),
        }

    @staticmethod
    @cache_analytics(timeout=1800)  # Cache for 30 minutes
    def get_program_metrics(program_id=None):
        """Get metrics for specific program or all programs."""
        if program_id:
            applications = Application.objects.filter(program_id=program_id)
        else:
            applications = Application.objects.all()

        return {
            "total_applications": applications.count(),
            "approved": applications.filter(
                status__name="approved", withdrawn=False
            ).count(),
            "rejected": applications.filter(
                status__name="rejected", withdrawn=False
            ).count(),
            "ongoing": applications.filter(
                status__name__in=["submitted", "under_review"], withdrawn=False
            ).count(),
            "withdrawn": applications.filter(withdrawn=True).count(),
        }

    @staticmethod
    @cache_analytics(timeout=1800)  # Cache for 30 minutes
    def get_coordinator_metrics(coordinator_id):
        """Get metrics for coordinator's assigned programs."""
        # This would need to be implemented based on how coordinators are assigned to programs
        # For now, return basic metrics
        return {
            "assigned_applications": Application.objects.count(),  # Placeholder
            "pending_review": Application.objects.filter(
                status__name="submitted"
            ).count(),
        }

    @staticmethod
    def invalidate_analytics_cache():
        """Invalidate all analytics cache entries."""
        from core.cache import invalidate_cache_pattern

        invalidate_cache_pattern("analytics")

    @staticmethod
    @cache_analytics(timeout=1800)
    def get_user_activity(days=30):
        """Get user activity metrics over time."""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        # Get user login activity
        from accounts.models import UserSession

        user_activity = UserSession.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        ).extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(
            logins=Count('id')
        ).order_by('day')

        return list(user_activity)

    @staticmethod
    def get_cached_metrics_with_fallback(metric_type: str, *args, **kwargs):
        """
        Get metrics with cache fallback strategy.

        Args:
            metric_type: Type of metrics to retrieve
            *args: Arguments for the metric function
            **kwargs: Keyword arguments for the metric function
        """
        cache_key = generate_cache_key(f"analytics:{metric_type}", *args, **kwargs)

        # Try to get from cache
        cached_result = cache.get(cache_key, version=None)
        if cached_result is not None:
            return cached_result

        # If not in cache, calculate and cache
        if metric_type == "dashboard":
            result = AnalyticsService.get_dashboard_metrics()
        elif metric_type == "program":
            result = AnalyticsService.get_program_metrics(*args, **kwargs)
        elif metric_type == "coordinator":
            result = AnalyticsService.get_coordinator_metrics(*args, **kwargs)
        elif metric_type == "activity":
            result = AnalyticsService.get_user_activity(*args, **kwargs)
        else:
            raise ValueError(f"Unknown metric type: {metric_type}")

        # Cache the result for 30 minutes
        cache.set(cache_key, result, 1800, version=None)
        return result
