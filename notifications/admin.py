from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Notification,
    NotificationPreference,
    NotificationRoutingOverride,
    NotificationType,
    Reminder,
)


@admin.register(NotificationType)
class NotificationTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("recipient", "title", "category", "notification_type", "is_read", "sent_at")
    search_fields = ("recipient__email", "title", "message")
    list_filter = ("is_read", "notification_type", "category", "sent_at")
    readonly_fields = ("sent_at", "created_at", "updated_at")
    
    fieldsets = (
        (None, {
            "fields": ("recipient", "title", "message", "category", "notification_type")
        }),
        ("Action", {
            "fields": ("action_url", "action_text"),
            "classes": ("collapse",)
        }),
        ("Status", {
            "fields": ("is_read", "sent_at")
        }),
        ("Data", {
            "fields": ("data",),
            "classes": ("collapse",)
        }),
    )


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ("user", "type", "enabled")
    search_fields = ("user__email", "type__name")
    list_filter = ("enabled",)


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    """Admin interface for Reminder model."""
    
    list_display = ("event_title", "user", "event_type", "remind_at", "sent_status", "created_at")
    search_fields = ("event_title", "user__username", "user__email")
    list_filter = ("sent", "event_type", "remind_at")
    readonly_fields = ("created_at", "updated_at", "notification")
    date_hierarchy = "remind_at"
    
    fieldsets = (
        (None, {
            "fields": ("user", "event_type", "event_id", "event_title")
        }),
        ("Reminder", {
            "fields": ("remind_at", "sent", "notification")
        }),
        ("Audit", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def sent_status(self, obj):
        """Show sent status with icon."""
        if obj.sent:
            return format_html(
                '<span style="color: green;">✓ Sent</span>'
            )
        else:
            from django.utils import timezone
            if obj.remind_at <= timezone.now():
                return format_html(
                    '<span style="color: red;">⚠ Overdue</span>'
                )
            else:
                return format_html(
                    '<span style="color: orange;">⏳ Pending</span>'
                )
    
    sent_status.short_description = "Status"


@admin.register(NotificationRoutingOverride)
class NotificationRoutingOverrideAdmin(admin.ModelAdmin):
    list_display = ("kind", "key", "settings_category", "is_active", "updated_at")
    list_filter = ("kind", "settings_category", "is_active")
    search_fields = ("key",)
    ordering = ("kind", "key")
