"""
Admin configuration for Timeline and WorkflowLog models.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ..models.applications.timeline import Timeline, WorkflowLog


@admin.register(Timeline)
class TimelineAdmin(admin.ModelAdmin):
    """Admin interface for Timeline model (legacy)"""

    list_display = (
        "id",
        "exchange",
        "event_type",
        "description",
        "actor",
        "timestamp",
    )
    list_filter = ("event_type", "timestamp")
    search_fields = (
        "exchange__student__first_name",
        "exchange__student__last_name",
        "description",
        "actor__username",
    )
    readonly_fields = ("timestamp",)
    date_hierarchy = "timestamp"
    fieldsets = (
        (
            _("Event Information"),
            {
                "fields": (
                    "exchange",
                    "event_type",
                    "description",
                    "actor",
                )
            },
        ),
        (
            _("Additional Data"),
            {
                "fields": (
                    "metadata",
                )
            },
        ),
        (
            _("System Information"),
            {
                "fields": ("timestamp",),
                "classes": ("collapse",)
            },
        ),
    )

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
        """Allow staff, Exchange Managers, or owner to edit."""
        if request.user.is_superuser or request.user.is_staff:
            return True
        if request.user.groups.filter(name="Exchange Managers").exists():
            return True
        if obj and hasattr(obj, "exchange") and hasattr(obj.exchange, "student"):
            return obj.exchange.student == request.user
        return False

    def has_delete_permission(self, request, obj=None):
        """Allow staff, Exchange Managers, or owner to delete."""
        if request.user.is_superuser or request.user.is_staff:
            return True
        if request.user.groups.filter(name="Exchange Managers").exists():
            return True
        if obj and hasattr(obj, "exchange") and hasattr(obj.exchange, "student"):
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


@admin.register(WorkflowLog)
class WorkflowLogAdmin(admin.ModelAdmin):
    """Admin interface for WorkflowLog model"""

    list_display = (
        "id",
        "exchange",
        "from_status",
        "to_status",
        "user",
        "timestamp",
    )
    list_filter = ("from_status", "to_status", "timestamp")
    search_fields = (
        "exchange__student__first_name",
        "exchange__student__last_name",
        "comment",
        "user__username",
    )
    readonly_fields = ("timestamp",)
    date_hierarchy = "timestamp"
    fieldsets = (
        (
            _("Transition Information"),
            {
                "fields": (
                    "exchange",
                    "from_status",
                    "to_status",
                    "user",
                )
            },
        ),
        (
            _("Details"),
            {
                "fields": (
                    "comment",
                    "metadata",
                )
            },
        ),
        (
            _("System Information"),
            {
                "fields": ("timestamp",),
                "classes": ("collapse",)
            },
        ),
    )

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
        """Allow staff, Exchange Managers, or owner to edit."""
        if request.user.is_superuser or request.user.is_staff:
            return True
        if request.user.groups.filter(name="Exchange Managers").exists():
            return True
        if obj and hasattr(obj, "exchange") and hasattr(obj.exchange, "student"):
            return obj.exchange.student == request.user
        return False

    def has_delete_permission(self, request, obj=None):
        """Allow staff, Exchange Managers, or owner to delete."""
        if request.user.is_superuser or request.user.is_staff:
            return True
        if request.user.groups.filter(name="Exchange Managers").exists():
            return True
        if obj and hasattr(obj, "exchange") and hasattr(obj.exchange, "student"):
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
