"""
FilterSets for advanced search and filtering of programs and applications.
"""

from django.contrib.postgres.search import SearchVector
from django.db.models import Q
import django_filters

from .models import Application, Program


class ProgramFilter(django_filters.FilterSet):
    """
    Advanced filter for Program model.
    
    Supports filtering by:
    - Name (contains search)
    - Description (full-text search)
    - Date range (start_date, end_date)
    - Eligibility criteria (GPA, language, age)
    - Active status
    """
    
    # Text search
    search = django_filters.CharFilter(method='filter_search', label='Search')
    name = django_filters.CharFilter(lookup_expr='icontains', label='Program Name')
    description = django_filters.CharFilter(lookup_expr='icontains', label='Description')
    
    # Date filters
    start_date_after = django_filters.DateFilter(field_name='start_date', lookup_expr='gte', label='Start After')
    start_date_before = django_filters.DateFilter(field_name='start_date', lookup_expr='lte', label='Start Before')
    end_date_after = django_filters.DateFilter(field_name='end_date', lookup_expr='gte', label='End After')
    end_date_before = django_filters.DateFilter(field_name='end_date', lookup_expr='lte', label='End Before')
    
    # Eligibility filters
    min_gpa_max = django_filters.NumberFilter(field_name='min_gpa', lookup_expr='lte', label='Max GPA Requirement')
    min_gpa_min = django_filters.NumberFilter(field_name='min_gpa', lookup_expr='gte', label='Min GPA Requirement')
    required_language = django_filters.CharFilter(lookup_expr='icontains', label='Required Language')
    min_language_level = django_filters.ChoiceFilter(
        choices=[
            ('A1', 'Beginner (A1)'),
            ('A2', 'Elementary (A2)'),
            ('B1', 'Intermediate (B1)'),
            ('B2', 'Upper Intermediate (B2)'),
            ('C1', 'Advanced (C1)'),
            ('C2', 'Proficient (C2)'),
        ],
        label='Minimum Language Level'
    )
    
    # Age filters
    max_age_max = django_filters.NumberFilter(field_name='max_age', lookup_expr='lte', label='Max Age Limit')
    min_age_min = django_filters.NumberFilter(field_name='min_age', lookup_expr='gte', label='Min Age Limit')
    
    # Status filters
    is_active = django_filters.BooleanFilter(label='Active')
    recurring = django_filters.BooleanFilter(label='Recurring')
    auto_reject_ineligible = django_filters.BooleanFilter(label='Auto-reject Ineligible')
    
    # Ordering
    ordering = django_filters.OrderingFilter(
        fields=(
            ('created_at', 'created_at'),
            ('start_date', 'start_date'),
            ('end_date', 'end_date'),
            ('name', 'name'),
        ),
        field_labels={
            'created_at': 'Date Created',
            'start_date': 'Start Date',
            'end_date': 'End Date',
            'name': 'Name',
        }
    )
    
    class Meta:
        model = Program
        fields = [
            'name', 'description', 'is_active', 'recurring',
            'required_language', 'min_language_level',
            'auto_reject_ineligible'
        ]
    
    def filter_search(self, queryset, name, value):
        """
        Full-text search across name and description.
        Uses PostgreSQL SearchVector for better search performance.
        """
        if not value:
            return queryset
        
        # Try PostgreSQL full-text search first
        try:
            return queryset.annotate(
                search=SearchVector('name', 'description'),
            ).filter(search=value)
        except Exception:
            # Fallback to simple Q-based search
            return queryset.filter(
                Q(name__icontains=value) | Q(description__icontains=value)
            )


class ApplicationFilter(django_filters.FilterSet):
    """
    Advanced filter for Application model.
    
    Supports filtering by:
    - Student (name, email)
    - Program (name)
    - Status
    - Date range (submitted, created)
    - Withdrawn status
    """
    
    # Student filters
    student_name = django_filters.CharFilter(method='filter_student_name', label='Student Name')
    student_email = django_filters.CharFilter(method='filter_student_email', label='Student Email')
    student_id = django_filters.UUIDFilter(field_name='student__id', label='Student ID')
    
    # Program filters
    program_name = django_filters.CharFilter(field_name='program__name', lookup_expr='icontains', label='Program Name')
    program_id = django_filters.UUIDFilter(field_name='program__id', label='Program ID')
    
    # Status filters
    status_name = django_filters.CharFilter(field_name='status__name', lookup_expr='iexact', label='Status')
    status_id = django_filters.NumberFilter(field_name='status__id', label='Status ID')
    
    # Date filters
    submitted_after = django_filters.DateTimeFilter(field_name='submitted_at', lookup_expr='gte', label='Submitted After')
    submitted_before = django_filters.DateTimeFilter(field_name='submitted_at', lookup_expr='lte', label='Submitted Before')
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte', label='Created After')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte', label='Created Before')
    
    # Withdrawn filter
    withdrawn = django_filters.BooleanFilter(label='Withdrawn')
    active = django_filters.BooleanFilter(method='filter_active', label='Active (Not Withdrawn)')
    
    # Search across multiple fields
    search = django_filters.CharFilter(method='filter_search', label='Search')
    
    # Ordering
    ordering = django_filters.OrderingFilter(
        fields=(
            ('created_at', 'created_at'),
            ('submitted_at', 'submitted_at'),
            ('student__username', 'student_username'),
            ('program__name', 'program_name'),
            ('status__name', 'status_name'),
        ),
        field_labels={
            'created_at': 'Date Created',
            'submitted_at': 'Date Submitted',
            'student__username': 'Student',
            'program__name': 'Program',
            'status__name': 'Status',
        }
    )
    
    class Meta:
        model = Application
        fields = ['withdrawn']
    
    def filter_student_name(self, queryset, name, value):
        """Filter by student first name or last name."""
        if not value:
            return queryset
        return queryset.filter(
            Q(student__first_name__icontains=value) |
            Q(student__last_name__icontains=value) |
            Q(student__username__icontains=value)
        )
    
    def filter_student_email(self, queryset, name, value):
        """Filter by student email."""
        if not value:
            return queryset
        return queryset.filter(student__email__icontains=value)
    
    def filter_active(self, queryset, name, value):
        """Filter for active (not withdrawn) applications."""
        if value is True:
            return queryset.filter(withdrawn=False)
        elif value is False:
            return queryset.filter(withdrawn=True)
        return queryset
    
    def filter_search(self, queryset, name, value):
        """
        Search across student name, email, and program name.
        """
        if not value:
            return queryset
        return queryset.filter(
            Q(student__first_name__icontains=value) |
            Q(student__last_name__icontains=value) |
            Q(student__username__icontains=value) |
            Q(student__email__icontains=value) |
            Q(program__name__icontains=value) |
            Q(status__name__icontains=value)
        )

