"""
Timeline models for tracking status changes and events in the exchange app.

This module contains the Timeline model for tracking status changes and significant events in the exchange application lifecycle.
"""

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Timeline(models.Model):
    """
    Model for tracking status changes and significant events in the exchange application lifecycle.

    Fields:
        exchange (ForeignKey): The related Exchange application.
        event_type (CharField): The type of event (see EVENT_TYPES).
        description (TextField): Description of the event.
        timestamp (DateTimeField): When the event occurred.
        previous_value (CharField): Previous value (for status changes, etc.).
        new_value (CharField): New value (for status changes, etc.).
        related_document (ForeignKey): Related document (optional).
        related_course (ForeignKey): Related course (optional).
        actor (ForeignKey): User who performed the action (optional).
    """

    # Event types
    EVENT_TYPES = (
        ("STATUS_CHANGE", "Status Change"),
        ("DOCUMENT_UPLOAD", "Document Uploaded"),
        ("DOCUMENT_APPROVED", "Document Approved"),
        ("DOCUMENT_REJECTED", "Document Rejected"),
        ("REVIEW_ADDED", "Review Added"),
        ("COMMENT_ADDED", "Comment Added"),
        ("REMINDER_SENT", "Reminder Sent"),
        ("DEADLINE_CHANGED", "Deadline Changed"),
        ("APPLICATION_EDITED", "Application Edited"),
        ("ASSIGNMENT_CHANGED", "Assignment Changed"),
        ("COURSE_ADDED", "Course Added"),
        ("COURSE_APPROVED", "Course Approved"),
        ("GRADE_ADDED", "Grade Added"),
        ("GRADE_TRANSFERRED", "Grade Transferred"),
        ("MILESTONE", "Milestone Reached"),
        ("OTHER", "Other Event"),
    )

    exchange = models.ForeignKey("Exchange", on_delete=models.CASCADE, related_name="timeline_events")
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    description = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    # Previous and new values (for status changes, etc.)
    previous_value = models.CharField(max_length=255, blank=True, null=True)
    new_value = models.CharField(max_length=255, blank=True, null=True)

    # Related objects (optional)
    related_document = models.ForeignKey(
        "Document",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="timeline_events",
    )

    # Actor who caused this event
    actor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="timeline_actions",
    )

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["event_type", "timestamp"], name="timeline_evt_type_ts_idx"),
        ]

    def __str__(self):
        return f"{self.get_event_type_display()} on {self.timestamp.strftime('%Y-%m-%d')} for Exchange {self.exchange_id}"

    def is_status_change(self):
        return self.event_type == "STATUS_CHANGE"

    def clean(self):
        """
        Custom validation for the Timeline model
        """
        super().clean()

        # Validate event type
        valid_event_types = [choice[0] for choice in self.EVENT_TYPES]
        if self.event_type not in valid_event_types:
            raise ValueError(f"Invalid event type: {self.event_type}")

        # Validate timestamp
        if self.timestamp > timezone.now():
            raise ValueError("Timestamp cannot be in the future.")

    def save(self, *args, **kwargs):
        """
        Override save method to enforce validation
        """
        self.clean()
        super().save(*args, **kwargs)

    def filter_by_event_type(self, event_type):
        """
        Filter timeline events by event type
        """
        return self.objects.filter(event_type=event_type)


class WorkflowLog(models.Model):
    """
    Model for tracking workflow status transitions in the exchange application.
    This provides a dedicated log for status changes with additional information.
    """

    exchange = models.ForeignKey("Exchange", on_delete=models.CASCADE, related_name="workflow_logs")
    from_status = models.CharField(max_length=20)
    to_status = models.CharField(max_length=20)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="workflow_logs",
    )
    comment = models.TextField(blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Workflow transition: {self.from_status} → {self.to_status} ({self.exchange})"

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Workflow Log"
        verbose_name_plural = "Workflow Logs"
        indexes = [
            models.Index(fields=["exchange"]),
            models.Index(fields=["timestamp"]),
        ]
