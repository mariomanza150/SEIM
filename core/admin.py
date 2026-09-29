from django.contrib import admin

from core.models import InstitutionFeatureSettings


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
