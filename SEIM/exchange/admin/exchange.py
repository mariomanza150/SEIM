"""
Admin configuration for Exchange model.
"""

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from ..models.applications.exchange import Exchange


@admin.register(Exchange)
class ExchangeAdmin(admin.ModelAdmin):
    """Admin interface for Exchange model"""

    list_display = (
        "id",
        "student",
        "host_university",
        "destination_country",
        "status",
        "submission_date",
        "decision_date",
        "has_all_documents",
    )
    list_filter = (
        "status",
        "destination_country",
        "submission_date",
        "decision_date",
    )
    search_fields = (
        "student__username",
        "student__email",
        "student__first_name",
        "student__last_name",
        "host_university",
        "destination_country",
    )
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at", "workflow_history")
    fieldsets = (
        (
            _("Student Information"),
            {
                "fields": (
                    "student",
                )
            },
        ),
        (
            _("Academic Information"),
            {
                "fields": (
                    "home_university",
                    "degree",
                    "major",
                    "program",
                    "academic_year",
                    "current_semester",
                )
            },
        ),
        (
            _("Exchange Details"),
            {
                "fields": (
                    "host_university",
                    "destination_country",
                )
            },
        ),
        (
            _("Application Details"),
            {
                "fields": (
                    "study_goals",
                    "referral_source",
                )
            },
        ),
        (
            _("Status and Workflow"),
            {
                "fields": (
                    "status",
                    "submission_date",
                    "review_date",
                    "decision_date",
                    "reviewed_by",
                    "notes",
                    "workflow_history",
                )
            },
        ),
        (
            _("System Information"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def has_view_permission(self, request, obj=None):
        """Allow staff, Exchange Managers, or owner to view."""
        if request.user.is_superuser or request.user.is_staff:
            return True
        if request.user.groups.filter(name="Exchange Managers").exists():
            return True
        if obj and hasattr(obj, "student"):
            return obj.student == request.user
        return False

    def has_change_permission(self, request, obj=None):
        """Allow staff, Exchange Managers, or owner (if status is DRAFT) to edit."""
        if request.user.is_superuser or request.user.is_staff:
            return True
        if request.user.groups.filter(name="Exchange Managers").exists():
            return True
        if obj and hasattr(obj, "student") and obj.status == "DRAFT":
            return obj.student == request.user
        return False

    def has_delete_permission(self, request, obj=None):
        """Allow staff, Exchange Managers, or owner (if status is DRAFT) to delete."""
        if request.user.is_superuser or request.user.is_staff:
            return True
        if request.user.groups.filter(name="Exchange Managers").exists():
            return True
        if obj and hasattr(obj, "student") and obj.status == "DRAFT":
            return obj.student == request.user
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
        return qs.filter(student=request.user)

    def has_all_documents(self, obj):
        """Display if exchange has all required documents"""
        has_docs = obj.has_required_documents()
        icon = "✅" if has_docs else "❌"
        return format_html(
            '{} <a href="{}">View Documents</a>',
            icon,
            reverse("admin:exchange_document_changelist") + f"?exchange__id={obj.id}",
        )

    has_all_documents.short_description = _("Required Documents")

    def workflow_history(self, obj):
        """Display workflow history in admin"""
        logs = obj.workflow_logs.all().order_by("-timestamp")
        if not logs:
            return _("No workflow history")

        html = "<table><tr><th>Date</th><th>From</th><th>To</th><th>User</th><th>Comment</th></tr>"
        for log in logs:
            html += f"<tr><td>{log.timestamp}</td><td>{log.from_status}</td><td>{log.to_status}</td>"
            html += f'<td>{log.user.username if log.user else "System"}</td><td>{log.comment}</td></tr>'
        html += "</table>"

        return format_html(html)

    workflow_history.short_description = _("Workflow History")
