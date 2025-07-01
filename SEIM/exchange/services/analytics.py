"""
Analytics service for generating reports and statistics from exchange data.
"""

import datetime

from django.db.models import Avg, Count, F, Max, Min, Q, Sum
from django.db.models.functions import TruncMonth, TruncYear
from django.utils import timezone

from ..models import Document  # , Exchange, WorkflowLog


class AnalyticsService:
    """Service for generating analytics reports and statistics"""

    @staticmethod
    def get_exchange_status_summary():
        """
        Get a summary of exchanges by status

        Returns:
            dict: Count of exchanges by status
        """
        return []  # Placeholder for disabled functionality

    @staticmethod
    def get_applications_by_university(limit=10):
        """
        Get top destinations by number of applications

        Args:
            limit: Maximum number of destinations to return

        Returns:
            dict: Application counts by destination university
        """
        university_counts = (
            Exchange.objects.values("destination_university").annotate(count=Count("id")).order_by("-count")[:limit]
        )

        result = {
            "labels": [],
            "data": [],
        }

        for item in university_counts:
            result["labels"].append(item["destination_university"])
            result["data"].append(item["count"])

        return result

    @staticmethod
    def get_applications_by_country(limit=10):
        """
        Get top destination countries by number of applications

        Args:
            limit: Maximum number of countries to return

        Returns:
            dict: Application counts by destination country
        """
        country_counts = (
            Exchange.objects.values("destination_country").annotate(count=Count("id")).order_by("-count")[:limit]
        )

        result = {
            "labels": [],
            "data": [],
        }

        for item in country_counts:
            result["labels"].append(item["destination_country"])
            result["data"].append(item["count"])

        return result

    @staticmethod
    def get_monthly_applications(months=12):
        """
        Get application counts by month for the last X months

        Args:
            months: Number of months to include

        Returns:
            dict: Monthly application counts
        """
        end_date = timezone.now().date()
        start_date = end_date - datetime.timedelta(days=30 * months)

        monthly_counts = (
            Exchange.objects.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        )

        result = {
            "labels": [],
            "data": [],
        }

        # Create a complete series of months
        current = start_date.replace(day=1)
        end = end_date.replace(day=1)
        month_dict = {item["month"].date(): item["count"] for item in monthly_counts}

        while current <= end:
            month_label = current.strftime("%b %Y")
            count = month_dict.get(current, 0)

            result["labels"].append(month_label)
            result["data"].append(count)

            # Move to next month
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)

        return result

    @staticmethod
    def get_processing_time_metrics():
        """
        Get metrics on application processing times

        Returns:
            dict: Average, min, and max processing times in days
        """
        exchanges = Exchange.objects.filter(submission_date__isnull=False, decision_date__isnull=False).annotate(
            processing_days=(F("decision_date") - F("submission_date")),
        )

        if not exchanges:
            return {"avg_days": 0, "min_days": 0, "max_days": 0, "count": 0}

        # Calculate days
        processing_days = [(ex.decision_date - ex.submission_date).days for ex in exchanges]

        return {
            "avg_days": (sum(processing_days) / len(processing_days) if processing_days else 0),
            "min_days": min(processing_days) if processing_days else 0,
            "max_days": max(processing_days) if processing_days else 0,
            "count": len(processing_days),
        }

    @staticmethod
    def get_approval_rate(period_days=None):
        """
        Get approval rate statistics

        Args:
            period_days: Optional, limit to exchanges from the last X days

        Returns:
            dict: Approval rate statistics
        """
        query = Exchange.objects.filter(status__in=["APPROVED", "REJECTED"])

        if period_days:
            cutoff_date = timezone.now() - datetime.timedelta(days=period_days)
            query = query.filter(decision_date__gte=cutoff_date)

        total = query.count()
        approved = query.filter(status="APPROVED").count()

        return {
            "total_decided": total,
            "approved": approved,
            "rejected": total - approved,
            "approval_rate": (approved / total * 100) if total > 0 else 0,
        }

    @staticmethod
    def get_document_statistics():
        """
        Get statistics about document uploads and verifications

        Returns:
            dict: Document statistics
        """
        total_docs = Document.objects.count()
        verified_docs = Document.objects.filter(verified=True).count()

        category_counts = Document.objects.values("category").annotate(count=Count("id")).order_by("-count")

        result = {
            "total": total_docs,
            "verified": verified_docs,
            "verification_rate": ((verified_docs / total_docs * 100) if total_docs > 0 else 0),
            "categories": {
                "labels": [],
                "data": [],
            },
        }

        for item in category_counts:
            result["categories"]["labels"].append(item["category"])
            result["categories"]["data"].append(item["count"])

        return result

    @staticmethod
    def generate_activity_report(days=30):
        """
        Generate a report of all activity for the last X days

        Args:
            days: Number of days to include

        Returns:
            dict: Activity report
        """
        cutoff_date = timezone.now() - datetime.timedelta(days=days)

        # Get new applications
        new_applications = Exchange.objects.filter(created_at__gte=cutoff_date).count()

        # Get status changes
        status_changes = WorkflowLog.objects.filter(timestamp__gte=cutoff_date).select_related("exchange", "user")

        # Get document uploads
        new_documents = Document.objects.filter(uploaded_at__gte=cutoff_date).count()

        # Get verified documents
        verified_documents = Document.objects.filter(verified_at__gte=cutoff_date).count()

        return {
            "period_days": days,
            "new_applications": new_applications,
            "status_changes": status_changes.count(),
            "new_documents": new_documents,
            "verified_documents": verified_documents,
            "recent_activity": status_changes.order_by("-timestamp")[:20],
        }

    @staticmethod
    def export_exchange_data(start_date=None, end_date=None, status=None):
        """
        Export exchange data for reporting

        Args:
            start_date: Optional filter by start date
            end_date: Optional filter by end date
            status: Optional filter by status

        Returns:
            QuerySet: Filtered exchange data
        """
        query = Exchange.objects.all()

        if start_date:
            query = query.filter(created_at__date__gte=start_date)

        if end_date:
            query = query.filter(created_at__date__lte=end_date)

        if status:
            query = query.filter(status=status)

        return query.select_related("student", "reviewed_by")
