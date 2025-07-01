"""
Admin configuration for Course and Grade models.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ..models.applications.course import Course
from ..models import Grade


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Admin interface for Course model"""

    list_display = (
        "course_code",
        "course_name",
        "exchange",
        "host_university",
        "credits",
        "status",
    )
    list_filter = ("status", "host_university")
    search_fields = (
        "course_code",
        "course_name",
        "host_university",
        "exchange__student__first_name",
        "exchange__student__last_name",
    )
    readonly_fields = ("approved_at",)
    fieldsets = (
        (
            _("Course Information"),
            {
                "fields": (
                    "course_code",
                    "course_name",
                    "description",
                    "credits",
                    "host_university",
                )
            },
        ),
        (
            _("Exchange Information"),
            {
                "fields": (
                    "exchange",
                )
            },
        ),
        (
            _("Approval Status"),
            {
                "fields": (
                    "status",
                    "approved_by",
                    "approved_at",
                    "notes",
                )
            },
        ),
        (
            _("Home University Equivalence"),
            {
                "fields": (
                    "home_course_code",
                    "home_course_name",
                    "home_credits",
                )
            },
        ),
    )
    inlines = []  # We'll add GradeInline here if needed


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    """Admin interface for Grade model"""

    list_display = (
        "course",
        "host_grade",
        "converted_grade",
        "status",
        "date_received",
        "date_processed",
    )
    list_filter = ("status", "date_received", "date_processed")
    search_fields = (
        "course__course_code",
        "course__course_name",
        "course__exchange__student__first_name",
        "course__exchange__student__last_name",
    )
    readonly_fields = ("date_processed",)
    fieldsets = (
        (
            _("Course Information"),
            {
                "fields": (
                    "course",
                )
            },
        ),
        (
            _("Grade Information"),
            {
                "fields": (
                    "host_grade",
                    "host_scale",
                    "converted_grade",
                    "home_scale",
                    "credit_earned",
                )
            },
        ),
        (
            _("Processing Information"),
            {
                "fields": (
                    "status",
                    "date_received",
                    "date_processed",
                    "processed_by",
                    "notes",
                )
            },
        ),
    )


class GradeInline(admin.TabularInline):
    """Inline admin for grades within course admin"""
    model = Grade
    extra = 0
    fields = ("host_grade", "converted_grade", "status", "date_received")
    readonly_fields = ("date_processed",)


# Add the inline to CourseAdmin
CourseAdmin.inlines = [GradeInline]
