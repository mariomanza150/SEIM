"""
Bulk Action models for tracking bulk operations on exchanges
"""

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from .exchange import Exchange


class BulkAction(models.Model):
    """Track bulk actions performed on exchanges"""

    ACTION_TYPES = [
        ("APPROVE", "Bulk Approve"),
        ("REJECT", "Bulk Reject"),
        ("STATUS_UPDATE", "Status Update"),
        ("ASSIGN", "Bulk Assign"),
        ("DELETE", "Bulk Delete"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("IN_PROGRESS", "In Progress"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
        ("CANCELLED", "Cancelled"),
    ]

    # Basic Information
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    performed_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bulk_actions"
    )
    performed_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Action Details
    comment = models.TextField(
        blank=True, help_text="Comment or reason for the bulk action"
    )
    target_status = models.CharField(
        max_length=50, blank=True, help_text="Target status for status updates"
    )
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
    metadata = models.JSONField(
        default=dict, blank=True, help_text="Additional action metadata"
    )
    error_details = models.TextField(
        blank=True, help_text="Detailed error information if action failed"
    )

    class Meta:
        ordering = ["-performed_at"]
        indexes = [
            models.Index(fields=["action_type", "performed_at"]),
            models.Index(fields=["performed_by", "performed_at"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.get_action_type_display()} by {self.performed_by.get_full_name() or self.performed_by.username} on {self.performed_at.strftime('%Y-%m-%d %H:%M')}"

    @property
    def success_rate(self):
        """Calculate success rate as percentage"""
        if self.total_items == 0:
            return 0
        return round((self.successful_items / self.total_items) * 100, 1)

    @property
    def duration(self):
        """Calculate duration of the bulk action"""
        if not self.completed_at:
            return None
        return self.completed_at - self.performed_at

    def mark_completed(self):
        """Mark the bulk action as completed"""
        self.status = "COMPLETED"
        self.completed_at = timezone.now()
        self.save(update_fields=["status", "completed_at"])

    def mark_failed(self, error_message=""):
        """Mark the bulk action as failed"""
        self.status = "FAILED"
        self.completed_at = timezone.now()
        if error_message:
            self.error_details = error_message
        self.save(update_fields=["status", "completed_at", "error_details"])

    def add_metadata(self, key, value):
        """Add metadata to the bulk action"""
        if not isinstance(self.metadata, dict):
            self.metadata = {}
        self.metadata[key] = value
        self.save(update_fields=["metadata"])


class BulkActionItem(models.Model):
    """Individual items in a bulk action"""

    ITEM_STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
        ("SKIPPED", "Skipped"),
    ]

    bulk_action = models.ForeignKey(
        BulkAction, on_delete=models.CASCADE, related_name="items"
    )
    exchange = models.ForeignKey(
        Exchange, on_delete=models.CASCADE, related_name="bulk_action_items"
    )

    status = models.CharField(
        max_length=20, choices=ITEM_STATUS_CHOICES, default="PENDING"
    )
    processed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    # Store original and new values for auditing
    original_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["id"]
        indexes = [
            models.Index(fields=["bulk_action", "status"]),
            models.Index(fields=["exchange"]),
        ]
        unique_together = ["bulk_action", "exchange"]

    def __str__(self):
        return f"Bulk Action Item #{self.id} - Exchange #{self.exchange.id}"

    def mark_success(self, new_values=None):
        """Mark this item as successfully processed"""
        self.status = "SUCCESS"
        self.processed_at = timezone.now()
        if new_values:
            self.new_values = new_values
        self.save(update_fields=["status", "processed_at", "new_values"])

    def mark_failed(self, error_message):
        """Mark this item as failed"""
        self.status = "FAILED"
        self.processed_at = timezone.now()
        self.error_message = error_message
        self.save(update_fields=["status", "processed_at", "error_message"])

    def mark_skipped(self, reason=""):
        """Mark this item as skipped"""
        self.status = "SKIPPED"
        self.processed_at = timezone.now()
        if reason:
            self.error_message = reason
        self.save(update_fields=["status", "processed_at", "error_message"])


class BulkActionLog(models.Model):
    """Detailed logging for bulk actions"""

    LOG_LEVELS = [
        ("DEBUG", "Debug"),
        ("INFO", "Info"),
        ("WARNING", "Warning"),
        ("ERROR", "Error"),
        ("CRITICAL", "Critical"),
    ]

    bulk_action = models.ForeignKey(
        BulkAction, on_delete=models.CASCADE, related_name="logs"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    level = models.CharField(max_length=10, choices=LOG_LEVELS, default="INFO")
    message = models.TextField()
    details = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["timestamp"]
        indexes = [
            models.Index(fields=["bulk_action", "timestamp"]),
            models.Index(fields=["level"]),
        ]

    def __str__(self):
        return f"{self.level} - {self.message[:50]}..."

    @classmethod
    def log(cls, bulk_action, level, message, details=None):
        """Convenience method to create log entries"""
        return cls.objects.create(
            bulk_action=bulk_action, level=level, message=message, details=details or {}
        )
