"""
Bulk Action models for tracking bulk operations on exchanges
"""

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

# Comment out the problematic import
# from .exchange_program.exchange import Exchange

User = get_user_model()


class BulkAction(models.Model):
    """
    Track bulk actions performed on exchanges.
    """
    class ActionType(models.TextChoices):
        APPROVE = "APPROVE", "Bulk Approve"
        REJECT = "REJECT", "Bulk Reject"
        STATUS_UPDATE = "STATUS_UPDATE", "Status Update"
        ASSIGN = "ASSIGN", "Bulk Assign"
        DELETE = "DELETE", "Bulk Delete"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"
        CANCELLED = "CANCELLED", "Cancelled"

    # Basic Information
    action_type = models.CharField(max_length=20, choices=ActionType.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    performed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bulk_actions")
    performed_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Action Details
    comment = models.TextField(blank=True, help_text="Comment or reason for the bulk action")
    target_status = models.CharField(max_length=50, blank=True, help_text="Target status for status updates")
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_bulk_actions",
        help_text="User assigned to for bulk assignment actions",
    )

    # Results
    total_items = models.PositiveIntegerField(default=0)
    successful_items = models.PositiveIntegerField(default=0)
    failed_items = models.PositiveIntegerField(default=0)

    # Additional metadata
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional action metadata")
    error_details = models.TextField(blank=True, help_text="Detailed error information if action failed")

    class Meta:
        ordering = ["-performed_at"]
        verbose_name = "Bulk Action"
        verbose_name_plural = "Bulk Actions"
        indexes = [
            models.Index(fields=["action_type", "performed_at"]),
            models.Index(fields=["performed_by", "performed_at"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.get_action_type_display()} by {self.performed_by.get_full_name() or self.performed_by.username} on {self.performed_at.strftime('%Y-%m-%d %H:%M')}"

    def clean(self):
        super().clean()
        if self.status not in self.Status.values:
            raise ValueError(f"Invalid status: {self.status}")
        if self.action_type not in self.ActionType.values:
            raise ValueError(f"Invalid action type: {self.action_type}")

    @property
    def success_rate(self):
        """Calculate success rate as percentage."""
        if self.total_items == 0:
            return 0
        return round((self.successful_items / self.total_items) * 100, 1)

    @property
    def duration(self):
        """Calculate duration of the bulk action."""
        if not self.completed_at:
            return None
        return self.completed_at - self.performed_at

    def mark_completed(self):
        """Mark the bulk action as completed."""
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        self.save(update_fields=["status", "completed_at"])

    def mark_failed(self, error_message=""):
        """Mark the bulk action as failed."""
        self.status = self.Status.FAILED
        self.completed_at = timezone.now()
        if error_message:
            self.error_details = error_message
        self.save(update_fields=["status", "completed_at", "error_details"])

    def add_metadata(self, key, value):
        """Add metadata to the bulk action."""
        if not isinstance(self.metadata, dict):
            self.metadata = {}
        self.metadata[key] = value
        self.save(update_fields=["metadata"])


class BulkActionItem(models.Model):
    """
    Individual items in a bulk action.
    """
    class ItemStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"
        SKIPPED = "SKIPPED", "Skipped"

    bulk_action = models.ForeignKey(BulkAction, on_delete=models.CASCADE, related_name="items")
    exchange = models.ForeignKey('exchange.Exchange', on_delete=models.CASCADE, related_name="bulk_action_items")
    status = models.CharField(max_length=20, choices=ItemStatus.choices, default=ItemStatus.PENDING)
    processed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    # Store original and new values for auditing
    original_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["id"]
        verbose_name = "Bulk Action Item"
        verbose_name_plural = "Bulk Action Items"
        indexes = [
            models.Index(fields=["bulk_action", "status"]),
            models.Index(fields=["exchange"]),
        ]
        unique_together = ["bulk_action", "exchange"]

    def __str__(self):
        return f"Bulk Action Item #{self.id} - Exchange #{self.exchange.id}"

    def clean(self):
        super().clean()
        if self.status not in self.ItemStatus.values:
            raise ValueError(f"Invalid item status: {self.status}")

    def mark_success(self, new_values=None):
        """Mark this item as successfully processed."""
        self.status = self.ItemStatus.SUCCESS
        self.processed_at = timezone.now()
        if new_values:
            self.new_values = new_values
        self.save(update_fields=["status", "processed_at", "new_values"])

    def mark_failed(self, error_message):
        """Mark this item as failed."""
        self.status = self.ItemStatus.FAILED
        self.processed_at = timezone.now()
        self.error_message = error_message
        self.save(update_fields=["status", "processed_at", "error_message"])

    def mark_skipped(self, reason=""):
        """Mark this item as skipped."""
        self.status = self.ItemStatus.SKIPPED
        self.processed_at = timezone.now()
        if reason:
            self.error_message = reason
        self.save(update_fields=["status", "processed_at", "error_message"])


class BulkActionLog(models.Model):
    """
    Detailed logging for bulk actions.
    """
    class LogLevel(models.TextChoices):
        DEBUG = "DEBUG", "Debug"
        INFO = "INFO", "Info"
        WARNING = "WARNING", "Warning"
        ERROR = "ERROR", "Error"
        CRITICAL = "CRITICAL", "Critical"

    bulk_action = models.ForeignKey(BulkAction, on_delete=models.CASCADE, related_name="logs")
    timestamp = models.DateTimeField(auto_now_add=True)
    level = models.CharField(max_length=10, choices=LogLevel.choices, default=LogLevel.INFO)
    message = models.TextField()
    details = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["timestamp"]
        verbose_name = "Bulk Action Log"
        verbose_name_plural = "Bulk Action Logs"
        indexes = [
            models.Index(fields=["bulk_action", "timestamp"]),
            models.Index(fields=["level"]),
        ]

    def __str__(self):
        return f"{self.level} - {self.message[:50]}..."

    @classmethod
    def log(cls, bulk_action, level, message, details=None):
        """Convenience method to create log entries."""
        return cls.objects.create(bulk_action=bulk_action, level=level, message=message, details=details or {})
