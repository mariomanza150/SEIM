"""
Filters for Exchange model using django-filter.
"""

import django_filters
from django.db.models import Q

from .models import Exchange


class ExchangeFilter(django_filters.FilterSet):
    """
    Advanced filtering for Exchange applications.
    """

    # Status filtering
    status = django_filters.ChoiceFilter(
        choices=Exchange.STATUS_CHOICES, empty_label="All Statuses"
    )

    # Date range filters
    submission_date_from = django_filters.DateFilter(
        field_name="submission_date", lookup_expr="gte", label="Submission Date From"
    )
    submission_date_to = django_filters.DateFilter(
        field_name="submission_date", lookup_expr="lte", label="Submission Date To"
    )
    start_date_from = django_filters.DateFilter(
        field_name="start_date", lookup_expr="gte", label="Exchange Start Date From"
    )
    start_date_to = django_filters.DateFilter(
        field_name="start_date", lookup_expr="lte", label="Exchange Start Date To"
    )

    # Student information filters
    first_name = django_filters.CharFilter(lookup_expr="icontains")
    last_name = django_filters.CharFilter(lookup_expr="icontains")
    email = django_filters.CharFilter(lookup_expr="icontains")
    student_id = django_filters.CharFilter(lookup_expr="exact")

    # Academic filters
    current_university = django_filters.CharFilter(lookup_expr="icontains")
    current_program = django_filters.CharFilter(lookup_expr="icontains")
    current_year = django_filters.NumberFilter()
    gpa_min = django_filters.NumberFilter(field_name="gpa", lookup_expr="gte")
    gpa_max = django_filters.NumberFilter(field_name="gpa", lookup_expr="lte")

    # Exchange details filters
    destination_university = django_filters.CharFilter(lookup_expr="icontains")
    destination_country = django_filters.CharFilter(lookup_expr="icontains")
    exchange_program = django_filters.CharFilter(lookup_expr="icontains")

    # Full-text search across multiple fields
    search = django_filters.CharFilter(method="search_filter", label="Search")

    # Order by any field
    ordering = django_filters.OrderingFilter(
        fields=(
            ("created_at", "created_at"),
            ("submission_date", "submission_date"),
            ("start_date", "start_date"),
            ("gpa", "gpa"),
            ("first_name", "first_name"),
            ("last_name", "last_name"),
        ),
        field_labels={
            "created_at": "Creation Date",
            "submission_date": "Submission Date",
            "start_date": "Exchange Start Date",
            "gpa": "GPA",
            "first_name": "First Name",
            "last_name": "Last Name",
        },
    )

    class Meta:
        model = Exchange
        fields = {
            "status": ["exact"],
            "student": ["exact"],
            "reviewed_by": ["exact"],
        }

    def search_filter(self, queryset, name, value):
        """
        Full-text search across multiple fields.
        """
        return queryset.filter(
            Q(first_name__icontains=value)
            | Q(last_name__icontains=value)
            | Q(email__icontains=value)
            | Q(student_id__icontains=value)
            | Q(current_university__icontains=value)
            | Q(destination_university__icontains=value)
            | Q(destination_country__icontains=value)
            | Q(exchange_program__icontains=value)
            | Q(motivation_letter__icontains=value)
        )
