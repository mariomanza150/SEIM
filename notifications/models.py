from django.db import models

from core.models import TimeStampedModel, UUIDModel


class NotificationType(models.Model):
    """Types of notifications (e.g., status change, comment, reminder)."""

    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Notification(UUIDModel, TimeStampedModel):
    """Notification instance sent to a user."""

    recipient = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name='notifications', null=True, blank=True, default=None)
    title = models.CharField(max_length=255, null=True, blank=True, default="Untitled")
    message = models.TextField(null=True, blank=True, default="")
    notification_type = models.CharField(max_length=50, choices=[
        ('in_app', 'In-App'),
        ('email', 'Email'),
        ('both', 'Both'),
    ], default='in_app', null=True, blank=True)
    category = models.CharField(
        max_length=20,
        choices=[
            ('info', 'Information'),
            ('success', 'Success'),
            ('warning', 'Warning'),
            ('error', 'Error'),
        ],
        default='info',
        help_text="Category for styling and priority"
    )
    is_read = models.BooleanField(default=False)
    action_url = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Direct link to the related resource (e.g., application detail page)"
    )
    action_text = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default="View Details",
        help_text="Text for the action button/link"
    )
    data = models.JSONField(default=dict, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['recipient', 'is_read'], name='notif_recipient_read_idx'),
            models.Index(fields=['recipient', '-sent_at'], name='notif_recipient_sent_idx'),
            models.Index(fields=['notification_type'], name='notif_type_idx'),
            models.Index(fields=['category'], name='notif_category_idx'),
            models.Index(fields=['-sent_at'], name='notif_sent_desc_idx'),
        ]
        ordering = ['-sent_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return f"{self.title} - {self.recipient.username if self.recipient else 'None'}"


class NotificationPreference(UUIDModel, TimeStampedModel):
    """User preferences for notification types (email, in-app, etc.)."""

    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    type = models.ForeignKey(NotificationType, on_delete=models.CASCADE)
    enabled = models.BooleanField(default=True)


class Reminder(UUIDModel, TimeStampedModel):
    """Reminder for events like deadlines."""
    
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name='reminders')
    event_type = models.CharField(
        max_length=50,
        choices=[
            ('application_deadline', 'Application Deadline'),
            ('document_deadline', 'Document Deadline'),
            ('program_start', 'Program Start'),
            ('program_end', 'Program End'),
            ('custom', 'Custom Reminder'),
        ],
        help_text="Type of event to remind about"
    )
    event_id = models.UUIDField(
        help_text="ID of the related object (Program, Application, etc.)"
    )
    event_title = models.CharField(
        max_length=255,
        help_text="Title/description of the event"
    )
    remind_at = models.DateTimeField(
        help_text="When to send the reminder"
    )
    sent = models.BooleanField(
        default=False,
        help_text="Whether the reminder has been sent"
    )
    notification = models.ForeignKey(
        Notification,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Notification created when reminder was sent"
    )
    
    class Meta:
        ordering = ['remind_at']
        verbose_name = 'Reminder'
        verbose_name_plural = 'Reminders'
        indexes = [
            models.Index(fields=['user', 'sent'], name='reminder_user_sent_idx'),
            models.Index(fields=['remind_at', 'sent'], name='reminder_time_sent_idx'),
            models.Index(fields=['event_type', 'event_id'], name='reminder_event_idx'),
        ]
    
    def __str__(self):
        return f"{self.event_title} - {self.user.username} ({self.remind_at})"


class NotificationRoutingOverride(UUIDModel, TimeStampedModel):
    """
    Admin-configurable overrides for mapping event keys to ``NotificationService.settings_category``.

    Initially used for Reminder ``event_type`` routing; can be extended to other keys.
    """

    KIND_REMINDER_EVENT_TYPE = "reminder_event_type"
    KIND_TRANSACTIONAL_ROUTE_KEY = "transactional_route_key"
    KIND_CHOICES = [
        (KIND_REMINDER_EVENT_TYPE, "Reminder event type"),
        (KIND_TRANSACTIONAL_ROUTE_KEY, "Transactional route key"),
    ]

    SETTINGS_CATEGORY_APPLICATIONS = "applications"
    SETTINGS_CATEGORY_DOCUMENTS = "documents"
    SETTINGS_CATEGORY_COMMENTS = "comments"
    SETTINGS_CATEGORY_PROGRAMS = "programs"
    SETTINGS_CATEGORY_SYSTEM = "system"
    SETTINGS_CATEGORY_UNGATED = "ungated"
    SETTINGS_CATEGORY_CHOICES = [
        (SETTINGS_CATEGORY_APPLICATIONS, "Applications"),
        (SETTINGS_CATEGORY_DOCUMENTS, "Documents"),
        (SETTINGS_CATEGORY_COMMENTS, "Comments"),
        (SETTINGS_CATEGORY_PROGRAMS, "Programs"),
        (SETTINGS_CATEGORY_SYSTEM, "System"),
        (SETTINGS_CATEGORY_UNGATED, "Ungated (ignore UserSettings groups)"),
    ]

    kind = models.CharField(max_length=64, choices=KIND_CHOICES)
    key = models.CharField(
        max_length=128,
        help_text="For reminder routing: the Reminder.event_type string.",
    )
    settings_category = models.CharField(
        max_length=32,
        choices=SETTINGS_CATEGORY_CHOICES,
        help_text=(
            "Which UserSettings notification group gates delivery for this key. "
            "Use Ungated to bypass group toggles (settings_category=None)."
        ),
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["kind", "key"],
                name="uniq_notification_routing_override_kind_key",
            )
        ]
        indexes = [
            models.Index(fields=["kind", "key"], name="notif_route_override_kind_key"),
            # Keep index names <= backend max identifier length (e.g., Oracle 30 chars).
            models.Index(fields=["kind", "is_active"], name="notif_route_ovr_kind_act"),
        ]

    def __str__(self) -> str:
        return f"{self.kind}:{self.key} → {self.settings_category}"
