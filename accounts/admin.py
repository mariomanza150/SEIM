from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Permission, Profile, Role, User, UserSession, UserSettings


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "username", "is_active", "is_staff", "is_superuser")
    search_fields = ("email", "username")
    ordering = ("email",)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "secondary_email")
    search_fields = ("user__email", "secondary_email")


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
    list_display = ['user', 'theme', 'font_size', 'profile_public', 'share_analytics']
    list_filter = ['theme', 'font_size', 'profile_public', 'share_analytics']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['user', 'notification_digest_last_sent_at']

    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Appearance', {
            'fields': ('theme', 'font_size', 'high_contrast', 'reduce_motion')
        }),
        ('Notifications', {
            'fields': (
                'email_applications', 'email_documents', 'email_comments', 'email_programs', 'email_system',
                'inapp_applications', 'inapp_documents', 'inapp_comments',
                'notification_digest_frequency', 'email_notification_digest',
                'notification_digest_last_sent_at',
            )
        }),
        ('Privacy', {
            'fields': ('profile_public', 'share_analytics')
        }),
    )


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """Admin interface for user sessions."""
    list_display = ['user', 'device', 'location', 'is_active', 'last_activity']
    list_filter = ['is_active', 'last_activity']
    search_fields = ['user__username', 'user__email', 'device', 'location']
    readonly_fields = ['user', 'session_key', 'user_agent', 'ip_address', 'device', 'location', 'last_activity']

    def has_add_permission(self, request):
        return False  # Sessions are created automatically
