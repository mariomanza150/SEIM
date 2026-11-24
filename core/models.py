import uuid

from django.db import models

# Create your models here.


class EmailDailyUsage(models.Model):
    """Per-day outgoing email send counter in the configured quota timezone."""

    usage_date = models.DateField(unique=True, db_index=True)
    sent_count = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Email daily usage"
        verbose_name_plural = "Email daily usage"
        ordering = ["-usage_date"]

    def __str__(self) -> str:
        return f"{self.usage_date}: {self.sent_count} sent"


class DeferredEmail(models.Model):
    """Persistent outbox for emails deferred by rate/quota limits."""

    PRIORITY_HIGH = "high"
    PRIORITY_NORMAL = "normal"
    PRIORITY_CHOICES = [
        (PRIORITY_HIGH, "High"),
        (PRIORITY_NORMAL, "Normal"),
    ]

    STATUS_PENDING = "pending"
    STATUS_SENDING = "sending"
    STATUS_SENT = "sent"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_SENDING, "Sending"),
        (STATUS_SENT, "Sent"),
        (STATUS_FAILED, "Failed"),
    ]

    priority = models.CharField(
        max_length=16, choices=PRIORITY_CHOICES, default=PRIORITY_NORMAL, db_index=True
    )
    status = models.CharField(
        max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True
    )
    subject = models.CharField(max_length=998, blank=True, default="")
    body = models.TextField(blank=True, default="")
    html_body = models.TextField(blank=True, default="")
    from_email = models.CharField(max_length=254, blank=True, default="")
    to = models.JSONField(default=list, blank=True)
    cc = models.JSONField(default=list, blank=True)
    bcc = models.JSONField(default=list, blank=True)
    reply_to = models.JSONField(default=list, blank=True)
    headers = models.JSONField(default=dict, blank=True)
    attachments = models.JSONField(default=list, blank=True)
    scheduled_for = models.DateTimeField(db_index=True)
    attempts = models.PositiveIntegerField(default=0)
    last_error = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Deferred email"
        verbose_name_plural = "Deferred emails"
        ordering = ["scheduled_for", "created_at"]
        indexes = [
            models.Index(
                fields=["status", "scheduled_for", "priority", "created_at"],
                name="core_defemail_drain_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"DeferredEmail({self.pk}, {self.priority}, {self.status})"

    def clear_sensitive_content(self) -> None:
        """Drop bodies/attachments after successful send (privacy)."""
        self.body = ""
        self.html_body = ""
        self.attachments = []


class UUIDModel(models.Model):
    """
    Abstract base model with UUID primary key.
    Use for all domain models to ensure global uniqueness.
    No domain-specific logic here.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimeStampedModel(models.Model):
    """
    Abstract base model with created/updated timestamps.
    Use for all models that require audit trails.
    No domain-specific logic here.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class InstitutionFeatureSettings(TimeStampedModel):
    """
    Singleton institution feature flags (admin-toggleable).

    Row is always ``pk=1``. Historical scholarship data is kept when flags
    are turned off; surfaces and APIs hide it instead of deleting.
    """

    scholarships_enabled = models.BooleanField(
        default=True,
        help_text=(
            "When false, hide scholarship scoring, ruleset editor, awards, "
            "and cohort exports (data is retained)."
        ),
    )
    document_version_history_enabled = models.BooleanField(
        default=True,
        help_text=(
            "Master switch for application-document version history UI/API. "
            "When false, no role sees prior file versions."
        ),
    )
    document_version_history_student = models.BooleanField(
        default=False,
        help_text="When history is enabled, students may see prior versions.",
    )
    document_version_history_coordinator = models.BooleanField(
        default=True,
        help_text="When history is enabled, coordinators may see prior versions.",
    )
    document_version_history_admin = models.BooleanField(
        default=True,
        help_text="When history is enabled, admins may see prior versions.",
    )

    class Meta:
        verbose_name = "Institution feature settings"
        verbose_name_plural = "Institution feature settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Singleton must not be deleted; reset to defaults instead.
        self.scholarships_enabled = True
        self.document_version_history_enabled = True
        self.document_version_history_student = False
        self.document_version_history_coordinator = True
        self.document_version_history_admin = True
        self.save(
            update_fields=[
                "scholarships_enabled",
                "document_version_history_enabled",
                "document_version_history_student",
                "document_version_history_coordinator",
                "document_version_history_admin",
                "updated_at",
            ]
        )

    def __str__(self):
        return "Institution feature settings"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @classmethod
    def scholarships_are_enabled(cls) -> bool:
        return bool(cls.get_solo().scholarships_enabled)
