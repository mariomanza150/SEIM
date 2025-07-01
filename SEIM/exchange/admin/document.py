"""
Admin configuration for Document model.
"""

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from ..models.applications.document import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Admin interface for Document model"""

    list_display = (
        "id",
        "title",
        "category",
        "exchange_link",
        "status",
        "verified",
        "uploaded_at",
        "file_size_display",
    )
    list_filter = ("category", "status", "verified", "uploaded_at")
    search_fields = (
        "title",
        "description",
        "exchange__student__first_name",
        "exchange__student__last_name",
    )
    readonly_fields = (
        "file_size",
        "file_hash",
        "version",
        "uploaded_at",
        "updated_at",
        "file_preview",
    )
    fieldsets = (
        (
            _("Document Information"),
            {
                "fields": (
                    "title",
                    "category",
                    "description",
                    "file",
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
            _("Status and Verification"),
            {
                "fields": (
                    "status",
                    "verified",
                    "verified_by",
                    "verified_at",
                )
            },
        ),
        (
            _("File Details"),
            {
                "fields": (
                    "file_size",
                    "file_hash",
                    "version",
                    "file_preview",
                )
            },
        ),
        (
            _("System Information"),
            {
                "fields": ("uploaded_at", "updated_at"),
                "classes": ("collapse",)
            },
        ),
    )

    def exchange_link(self, obj):
        """Display link to related exchange"""
        url = reverse("admin:exchange_exchange_change", args=[obj.exchange.id])
        return format_html('<a href="{}">{}</a>', url, str(obj.exchange))

    exchange_link.short_description = _("Exchange")

    def file_size_display(self, obj):
        """Display human-readable file size"""
        return obj.get_human_readable_size()

    file_size_display.short_description = _("File Size")

    def file_preview(self, obj):
        """Display file preview or download link"""
        if obj.get_file_extension() in [".pdf", ".jpg", ".jpeg", ".png"]:
            return format_html(
                '<a href="{}" target="_blank">View File</a>',
                reverse("exchange:document-detail", args=[obj.exchange.id, obj.id]),
            )
        return format_html('<a href="{}" download>Download File</a>', obj.file.url)

    file_preview.short_description = _("File Preview")
