from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import (
    AcademicLevel,
    AllowedEmailDomain,
    BankInstitution,
    GoogleCalendarConnection,
    HomeAcademicProgram,
    Permission,
    Profile,
    Role,
    SchoolFaculty,
    SpokenLanguage,
    Unidad,
    User,
    UserSession,
    UserSettings,
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "username", "is_active", "is_staff", "is_superuser")
    search_fields = (
        "email",
        "username",
        "first_name",
        "middle_name",
        "last_name",
        "mothers_last_name",
    )
    ordering = ("email",)
    fieldsets = BaseUserAdmin.fieldsets + (
        (_("Additional names"), {"fields": ("middle_name", "mothers_last_name")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (_("Additional names"), {"fields": ("middle_name", "mothers_last_name")}),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "matricula",
        "academic_level",
        "school",
        "is_ready_to_apply",
    )
    list_filter = ("academic_level", "school", "unidad", "gender")
    search_fields = ("user__email", "secondary_email", "matricula", "rfc")

    @admin.display(boolean=True, description=_("Ready to apply"))
    def is_ready_to_apply(self, obj):
        return obj.is_ready_to_apply


class CatalogAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active", "ordering")
    list_editable = ("is_active", "ordering")
    list_filter = ("is_active",)
    search_fields = ("name", "code")
    ordering = ("ordering", "name")


@admin.register(AllowedEmailDomain)
class AllowedEmailDomainAdmin(CatalogAdmin):
    pass


@admin.register(AcademicLevel)
class AcademicLevelAdmin(CatalogAdmin):
    pass


@admin.register(SchoolFaculty)
class SchoolFacultyAdmin(CatalogAdmin):
    pass


@admin.register(Unidad)
class UnidadAdmin(CatalogAdmin):
    pass


@admin.register(BankInstitution)
class BankInstitutionAdmin(CatalogAdmin):
    pass


@admin.register(HomeAcademicProgram)
class HomeAcademicProgramAdmin(CatalogAdmin):
    list_display = ("name", "school", "code", "is_active", "ordering")
    list_filter = ("school", "is_active")


@admin.register(SpokenLanguage)
class SpokenLanguageAdmin(CatalogAdmin):
    list_display = ("name", "code", "is_active", "ordering", "alias_preview")

    @admin.display(description=_("Aliases"))
    def alias_preview(self, obj):
        aliases = obj.aliases or []
        if not aliases:
            return "—"
        return ", ".join(str(item) for item in aliases[:5])


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    """Admin interface for user settings."""

    list_display = ["user", "theme", "font_size", "profile_public", "share_analytics"]
    list_filter = ["theme", "font_size", "profile_public", "share_analytics"]
    search_fields = ["user__username", "user__email"]
    readonly_fields = [
        "user",
        "notification_digest_last_sent_at",
        "notification_routing_documentation",
    ]

    @admin.display(description=_("Notification routing reference"))
    def notification_routing_documentation(self, obj):
        """Staff links to the live routing matrix and API docs (P2 notification rules / discoverability)."""
        return format_html(
            '<p class="help">{}</p><ul class="mb-0">'
            '<li><a href="{}" target="_blank" rel="noopener noreferrer">{}</a> ({})</li>'
            '<li><a href="{}" target="_blank" rel="noopener noreferrer">{}</a></li>'
            "</ul>",
            _(
                "How these toggles map to reminder event types and transactional notification "
                "routes is documented in the staff routing matrix and in the API schema."
            ),
            "/seim/notification-routing",
            _("Vue: notification routing matrix"),
            _("requires staff login in the SPA"),
            "/api/docs/",
            _("OpenAPI documentation"),
        )

    fieldsets = (
        ("User", {"fields": ("user",)}),
        (
            "Appearance",
            {"fields": ("theme", "font_size", "high_contrast", "reduce_motion")},
        ),
        (
            _("Notification routing reference"),
            {
                "classes": ("collapse",),
                "fields": ("notification_routing_documentation",),
            },
        ),
        (
            "Notifications",
            {
                "fields": (
                    "email_applications",
                    "email_documents",
                    "email_comments",
                    "email_programs",
                    "email_system",
                    "inapp_applications",
                    "inapp_documents",
                    "inapp_comments",
                    "inapp_programs",
                    "inapp_system",
                    "notification_digest_frequency",
                    "email_notification_digest",
                    "notification_digest_last_sent_at",
                )
            },
        ),
        ("Privacy", {"fields": ("profile_public", "share_analytics")}),
    )


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """Admin interface for user sessions."""

    list_display = ["user", "device", "location", "is_active", "last_activity"]
    list_filter = ["is_active", "last_activity"]
    search_fields = ["user__username", "user__email", "device", "location"]
    readonly_fields = [
        "user",
        "session_key",
        "user_agent",
        "ip_address",
        "device",
        "location",
        "last_activity",
    ]

    def has_add_permission(self, request):
        return False  # Sessions are created automatically


@admin.register(GoogleCalendarConnection)
class GoogleCalendarConnectionAdmin(admin.ModelAdmin):
    list_display = ("user", "google_email", "last_synced_at")
    search_fields = ("user__email", "google_email")
    readonly_fields = (
        "user",
        "google_email",
        "token_expiry",
        "last_synced_at",
        "last_sync_error",
        "created_at",
        "updated_at",
    )
    exclude = ("access_token", "refresh_token", "event_map")
