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

    def has_view_permission(self, request, obj=None):
        """Allow staff, Exchange Managers, or owner to view."""
        if request.user.is_superuser or request.user.is_staff:
            return True
        if request.user.groups.filter(name="Exchange Managers").exists():
            return True
        if obj and hasattr(obj, "exchange") and hasattr(obj.exchange, "student"):
            return obj.exchange.student == request.user
        return False

    def has_change_permission(self, request, obj=None):
        """Allow staff, Exchange Managers, or owner (if planned) to edit."""
        if request.user.is_superuser or request.user.is_staff:
            return True
        if request.user.groups.filter(name="Exchange Managers").exists():
            return True
        if obj and hasattr(obj, "exchange") and hasattr(obj.exchange, "student") and obj.status == obj.Status.PLANNED:
            return obj.exchange.student == request.user
        return False

    def has_delete_permission(self, request, obj=None):
        """Allow staff, Exchange Managers, or owner (if planned) to delete."""
        if request.user.is_superuser or request.user.is_staff:
            return True
        if request.user.groups.filter(name="Exchange Managers").exists():
            return True
        if obj and hasattr(obj, "exchange") and hasattr(obj.exchange, "student") and obj.status == obj.Status.PLANNED:
            return obj.exchange.student == request.user
        return False

    def has_add_permission(self, request):
        """Allow staff, Exchange Managers, or students to add."""
        if request.user.is_superuser or request.user.is_staff:
            return True
        if request.user.groups.filter(name="Exchange Managers").exists():
            return True
        if request.user.groups.filter(name="Students").exists():
            return True
        return False

    def get_queryset(self, request):
        """Staff and Exchange Managers see all; students see only their own."""
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.is_staff:
            return qs
        if request.user.groups.filter(name="Exchange Managers").exists():
            return qs
        return qs.filter(exchange__student=request.user)


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

    def has_view_permission(self, request, obj=None):
        """Allow staff, Exchange Managers, or owner to view."""
        if request.user.is_superuser or request.user.is_staff:
            return True
        if request.user.groups.filter(name="Exchange Managers").exists():
            return True
        if obj and hasattr(obj, "course") and hasattr(obj.course, "exchange") and hasattr(obj.course.exchange, "student"):
            return obj.course.exchange.student == request.user
        return False

    def has_change_permission(self, request, obj=None):
        """Allow staff, Exchange Managers, or owner (if provisional) to edit."""
        if request.user.is_superuser or request.user.is_staff:
            return True
        if request.user.groups.filter(name="Exchange Managers").exists():
            return True
        if obj and hasattr(obj, "course") and hasattr(obj.course, "exchange") and hasattr(obj.course.exchange, "student") and obj.status == obj.Status.PROVISIONAL:
            return obj.course.exchange.student == request.user
        return False

    def has_delete_permission(self, request, obj=None):
        """Allow staff, Exchange Managers, or owner (if provisional) to delete."""
        if request.user.is_superuser or request.user.is_staff:
            return True
        if request.user.groups.filter(name="Exchange Managers").exists():
            return True
        if obj and hasattr(obj, "course") and hasattr(obj.course, "exchange") and hasattr(obj.course.exchange, "student") and obj.status == obj.Status.PROVISIONAL:
            return obj.course.exchange.student == request.user
        return False

    def has_add_permission(self, request):
        """Allow staff, Exchange Managers, or students to add."""
        if request.user.is_superuser or request.user.is_staff:
            return True
        if request.user.groups.filter(name="Exchange Managers").exists():
            return True
        if request.user.groups.filter(name="Students").exists():
            return True
        return False

    def get_queryset(self, request):
        """Staff and Exchange Managers see all; students see only their own."""
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.is_staff:
            return qs
        if request.user.groups.filter(name="Exchange Managers").exists():
            return qs
        return qs.filter(course__exchange__student=request.user)


class GradeInline(admin.TabularInline):
    """Inline admin for grades within course admin"""
    model = Grade
    extra = 0
    fields = ("host_grade", "converted_grade", "status", "date_received")
    readonly_fields = ("date_processed",)


# Add the inline to CourseAdmin
CourseAdmin.inlines = [GradeInline]
