"""
Database Query Optimization Service for SGII DataTables
Provides optimized querysets and query optimization utilities
"""

from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models
from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, When
from django.db.models.functions import Coalesce

from ..models import Comment, Document, Exchange, Timeline


class DataTableOptimizer:
    """Optimize DataTable queries for performance"""

    @staticmethod
    def optimize_exchange_queryset(user=None):
        """
        Optimized queryset for exchange DataTable with permission filtering
        """
        # Base queryset with select_related for foreign keys
        queryset = (
            Exchange.objects.select_related(
                "student", "student__profile", "reviewed_by", "reviewed_by__profile"
            )
            .prefetch_related(
                # Prefetch related documents with only needed fields
                Prefetch(
                    "documents",
                    queryset=Document.objects.only(
                        "id", "status", "category", "file_size", "uploaded_at"
                    ),
                ),
                # Prefetch timeline with only needed fields
                Prefetch(
                    "timeline",
                    queryset=Timeline.objects.select_related("created_by")
                    .only(
                        "id",
                        "action",
                        "created_at",
                        "created_by__id",
                        "created_by__first_name",
                        "created_by__last_name",
                    )
                    .order_by("-created_at")[:5],  # Only latest 5 timeline entries
                ),
            )
            .annotate(
                # Annotate with computed fields
                document_count=Count("documents"),
                pending_document_count=Count(
                    "documents", filter=Q(documents__status="PENDING")
                ),
                last_activity=Max("timeline__created_at"),
                days_since_created=models.functions.Extract(
                    models.functions.Now() - F("created_at"), "days"
                ),
            )
        )

        # Apply user-based filtering
        if user:
            if hasattr(user, "profile"):
                if user.profile.role == "STUDENT":
                    queryset = queryset.filter(student=user)
                elif user.profile.role not in ["COORDINATOR", "MANAGER", "ADMIN"]:
                    # For other roles, return empty queryset
                    queryset = queryset.none()

        return queryset

    @staticmethod
    def optimize_document_queryset(user=None):
        """
        Optimized queryset for document DataTable
        """
        queryset = (
            Document.objects.select_related(
                "exchange",
                "exchange__student",
                "exchange__student__profile",
                "uploaded_by",
            )
            .only(
                # Only select needed fields to reduce memory usage
                "id",
                "original_name",
                "category",
                "status",
                "file_size",
                "uploaded_at",
                "file_hash",
                "mime_type",
                "exchange__id",
                "exchange__student__id",
                "exchange__student__first_name",
                "exchange__student__last_name",
                "uploaded_by__id",
                "uploaded_by__first_name",
                "uploaded_by__last_name",
            )
            .annotate(
                # Add computed fields
                student_name=models.functions.Concat(
                    "exchange__student__first_name",
                    models.Value(" "),
                    "exchange__student__last_name",
                ),
                days_since_upload=models.functions.Extract(
                    models.functions.Now() - F("uploaded_at"), "days"
                ),
            )
        )

        # Apply user-based filtering
        if user and hasattr(user, "profile"):
            if user.profile.role == "STUDENT":
                queryset = queryset.filter(exchange__student=user)
            elif user.profile.role not in ["COORDINATOR", "MANAGER", "ADMIN"]:
                queryset = queryset.none()

        return queryset

    @staticmethod
    def optimize_timeline_queryset(user=None):
        """
        Optimized queryset for timeline/activity DataTable
        """
        queryset = (
            Timeline.objects.select_related(
                "exchange",
                "exchange__student",
                "exchange__student__profile",
                "created_by",
            )
            .only(
                "id",
                "action",
                "description",
                "created_at",
                "exchange__id",
                "exchange__student__id",
                "exchange__student__first_name",
                "exchange__student__last_name",
                "created_by__id",
                "created_by__first_name",
                "created_by__last_name",
            )
            .annotate(
                student_name=models.functions.Concat(
                    "exchange__student__first_name",
                    models.Value(" "),
                    "exchange__student__last_name",
                ),
                created_by_name=Case(
                    When(
                        created_by__isnull=False,
                        then=models.functions.Concat(
                            "created_by__first_name",
                            models.Value(" "),
                            "created_by__last_name",
                        ),
                    ),
                    default=models.Value("System"),
                    output_field=models.CharField(),
                ),
            )
        )

        # Apply user-based filtering
        if user and hasattr(user, "profile"):
            if user.profile.role == "STUDENT":
                queryset = queryset.filter(exchange__student=user)
            elif user.profile.role not in ["COORDINATOR", "MANAGER", "ADMIN"]:
                queryset = queryset.none()

        return queryset

    @staticmethod
    def get_cached_stats(cache_key, calculator_func, timeout=300):
        """
        Generic caching for expensive calculations

        Args:
            cache_key: Unique cache key
            calculator_func: Function that calculates the stats
            timeout: Cache timeout in seconds (default 5 minutes)
        """
        stats = cache.get(cache_key)
        if stats is None:
            stats = calculator_func()
            cache.set(cache_key, stats, timeout)
        return stats

    @staticmethod
    def optimize_search_query(queryset, search_value, search_fields=None):
        """
        Optimized full-text search with ranking

        Args:
            queryset: Base queryset
            search_value: Search term
            search_fields: List of fields to search in
        """
        if not search_value:
            return queryset

        # Default search fields for Exchange model
        if search_fields is None:
            search_fields = [
                "student__first_name",
                "student__last_name",
                "student__email",
                "destination_university",
                "destination_country",
                "exchange_program",
                "status",
                "notes",
            ]

        # Build search query with OR conditions
        search_query = Q()
        search_terms = search_value.split()

        for term in search_terms:
            term_query = Q()
            for field in search_fields:
                term_query |= Q(**{f"{field}__icontains": term})
            search_query &= term_query

        # Apply search filter
        queryset = queryset.filter(search_query)

        # Add search ranking (simple implementation)
        # This could be enhanced with full-text search capabilities
        queryset = queryset.annotate(
            search_rank=models.Value(1, output_field=models.IntegerField())
        )

        return queryset

    @staticmethod
    def get_dashboard_stats(user=None):
        """
        Optimized dashboard statistics calculation
        """
        cache_key = f'dashboard_stats_{user.id if user else "all"}'

        def calculate_stats():
            base_queryset = DataTableOptimizer.optimize_exchange_queryset(user)

            stats = base_queryset.aggregate(
                total_exchanges=Count("id"),
                pending_count=Count("id", filter=Q(status="SUBMITTED")),
                approved_count=Count("id", filter=Q(status="APPROVED")),
                rejected_count=Count("id", filter=Q(status="REJECTED")),
                completed_count=Count("id", filter=Q(status="COMPLETED")),
                avg_processing_days=Avg(
                    models.functions.Extract(
                        F("decision_date") - F("created_at"), "days"
                    ),
                    filter=Q(decision_date__isnull=False),
                ),
            )

            # Add document statistics
            doc_stats = Document.objects.filter(exchange__in=base_queryset).aggregate(
                total_documents=Count("id"),
                pending_documents=Count("id", filter=Q(status="PENDING")),
                verified_documents=Count("id", filter=Q(status="VERIFIED")),
                total_file_size=models.Sum("file_size"),
            )

            stats.update(doc_stats)
            return stats

        return DataTableOptimizer.get_cached_stats(
            cache_key, calculate_stats, timeout=600  # 10 minutes cache
        )

    @staticmethod
    def optimize_bulk_action_queryset(exchange_ids, user=None):
        """
        Optimized queryset for bulk actions

        Args:
            exchange_ids: List of exchange IDs
            user: User performing the action (for permission filtering)
        """
        queryset = (
            Exchange.objects.filter(id__in=exchange_ids)
            .select_related("student", "student__profile")
            .only(
                "id",
                "status",
                "student__id",
                "student__email",
                "student__first_name",
                "student__last_name",
                "destination_university",
                "exchange_program",
            )
        )

        # Apply user-based filtering for security
        if user and hasattr(user, "profile"):
            if user.profile.role == "STUDENT":
                queryset = queryset.filter(student=user)
            elif user.profile.role not in ["COORDINATOR", "MANAGER", "ADMIN"]:
                queryset = queryset.none()

        return queryset

    @staticmethod
    def get_popular_destinations(limit=10, user=None):
        """
        Get popular destinations with caching
        """
        cache_key = f'popular_destinations_{user.id if user else "all"}_{limit}'

        def calculate_destinations():
            queryset = DataTableOptimizer.optimize_exchange_queryset(user)
            return list(
                queryset.values("destination_country")
                .annotate(count=Count("id"))
                .order_by("-count")[:limit]
            )

        return DataTableOptimizer.get_cached_stats(
            cache_key, calculate_destinations, timeout=3600  # 1 hour cache
        )

    @staticmethod
    def get_monthly_trends(months=12, user=None):
        """
        Get monthly application trends with caching
        """
        cache_key = f'monthly_trends_{months}_{user.id if user else "all"}'

        def calculate_trends():
            from datetime import datetime, timedelta

            from django.utils import timezone

            end_date = timezone.now()
            start_date = end_date - timedelta(days=months * 30)

            queryset = DataTableOptimizer.optimize_exchange_queryset(user).filter(
                created_at__gte=start_date
            )

            return list(
                queryset.extra(
                    select={
                        "month": "DATE_TRUNC('month', created_at)",
                    }
                )
                .values("month")
                .annotate(
                    total=Count("id"),
                    approved=Count("id", filter=Q(status="APPROVED")),
                    rejected=Count("id", filter=Q(status="REJECTED")),
                )
                .order_by("month")
            )

        return DataTableOptimizer.get_cached_stats(
            cache_key, calculate_trends, timeout=1800  # 30 minutes cache
        )

    @staticmethod
    def prefetch_for_export(queryset, export_format="csv"):
        """
        Optimize queryset for data export

        Args:
            queryset: Base queryset
            export_format: Export format (csv, excel, pdf)
        """
        # For exports, we need all data but can optimize the queries
        return queryset.select_related(
            "student", "student__profile", "reviewed_by"
        ).prefetch_related("documents", "timeline__created_by")

    @staticmethod
    def optimize_filtering_queryset(queryset, filters):
        """
        Apply filters in an optimized way

        Args:
            queryset: Base queryset
            filters: Dictionary of filters to apply
        """
        # Apply most selective filters first
        filter_order = [
            "status__in",  # Usually most selective
            "student__id",  # Highly selective
            "destination_country__in",
            "created_at__date__gte",
            "created_at__date__lte",
            "exchange_program__in",
        ]

        applied_filters = {}

        for filter_key in filter_order:
            if filter_key in filters and filters[filter_key]:
                applied_filters[filter_key] = filters[filter_key]

        # Add remaining filters
        for key, value in filters.items():
            if key not in applied_filters and value:
                applied_filters[key] = value

        return queryset.filter(**applied_filters)


class QueryOptimizationMixin:
    """
    Mixin class for optimizing DataTable API views
    """

    def get_optimized_queryset(self):
        """
        Get optimized queryset for the specific view
        Override in subclasses for model-specific optimizations
        """
        return self.model.objects.all()

    def apply_search_optimization(self, queryset, search_value):
        """
        Apply optimized search to queryset
        """
        if hasattr(self, "search_fields") and self.search_fields:
            return DataTableOptimizer.optimize_search_query(
                queryset, search_value, self.search_fields
            )
        return queryset

    def get_cached_count(self, queryset, cache_key_suffix=""):
        """
        Get cached count for queryset
        """
        cache_key = f"datatable_count_{self.__class__.__name__}_{cache_key_suffix}"

        def calculate_count():
            return queryset.count()

        return DataTableOptimizer.get_cached_stats(
            cache_key, calculate_count, timeout=300  # 5 minutes
        )

    def optimize_pagination(self, queryset, start, length):
        """
        Optimize pagination queries
        """
        # Use iterator for large datasets to reduce memory usage
        if length > 100:
            return queryset[start : start + length].iterator()
        return queryset[start : start + length]
