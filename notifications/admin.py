from django.contrib import admin

from .models import Notification, NotificationPreference, NotificationType


@admin.register(NotificationType)
class NotificationTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("recipient", "title", "notification_type", "is_read", "sent_at")
    search_fields = ("recipient__email", "title", "message")
    list_filter = ("is_read", "notification_type")


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ("user", "type", "enabled")
    search_fields = ("user__email", "type__name")
    list_filter = ("enabled",)
