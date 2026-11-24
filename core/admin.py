from django.contrib import admin

from core.models import DeferredEmail, EmailDailyUsage, InstitutionFeatureSettings


@admin.register(EmailDailyUsage)
class EmailDailyUsageAdmin(admin.ModelAdmin):
    list_display = ("usage_date", "sent_count", "updated_at")
    ordering = ("-usage_date",)
    readonly_fields = ("usage_date", "sent_count", "updated_at")
    search_fields = ("usage_date",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(DeferredEmail)
class DeferredEmailAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "status",
        "priority",
        "subject",
        "scheduled_for",
        "attempts",
        "created_at",
        "updated_at",
        "sent_at",
    )
    list_filter = ("status", "priority")
    search_fields = ("subject", "from_email", "last_error")
    readonly_fields = (
        "priority",
        "status",
        "subject",
        "from_email",
        "to",
        "cc",
        "bcc",
        "reply_to",
        "headers",
        "scheduled_for",
        "attempts",
        "last_error",
        "created_at",
        "updated_at",
        "sent_at",
        "body",
        "html_body",
        "attachments",
    )
    ordering = ("-created_at",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "status",
                    "priority",
                    "subject",
                    "from_email",
                    "to",
                    "cc",
                    "bcc",
                    "reply_to",
                    "headers",
                    "scheduled_for",
                    "attempts",
                    "last_error",
                    "created_at",
                    "sent_at",
                )
            },
        ),
        (
            "Message body (sensitive)",
            {
                "classes": ("collapse",),
                "fields": ("body", "html_body", "attachments"),
            },
        ),
    )

    def has_add_permission(self, request):
        return False


@admin.register(InstitutionFeatureSettings)
class InstitutionFeatureSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "scholarships_enabled",
        "document_version_history_enabled",
        "updated_at",
    )
    readonly_fields = ("updated_at", "created_at")
    fieldsets = (
        (None, {"fields": ("scholarships_enabled",)}),
        (
            "Document version history",
            {
                "fields": (
                    "document_version_history_enabled",
                    "document_version_history_student",
                    "document_version_history_coordinator",
                    "document_version_history_admin",
                )
            },
        ),
        ("Audit", {"fields": ("created_at", "updated_at")}),
    )

    def has_add_permission(self, request):
        return not InstitutionFeatureSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
