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
