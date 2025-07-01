"""
Timeline models for tracking status changes and events in the exchange app.
"""

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Timeline(models.Model):
    """
    Model for tracking status changes and significant events in the exchange application lifecycle
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

    exchange = models.ForeignKey(
        "Exchange", on_delete=models.CASCADE, related_name="timeline_events"
    )
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
    related_review = models.ForeignKey(
        "Review",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="timeline_events",
    )
    related_comment = models.ForeignKey(
        "Comment",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="timeline_events",
    )
    related_course = models.ForeignKey(
        "Course",
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
        related_name="timeline_events",
    )
    is_system_generated = models.BooleanField(default=False)

    # Additional data as JSON
    additional_data = models.JSONField(blank=True, null=True)

    @classmethod
    def log_status_change(cls, exchange, previous_status, new_status, actor=None):
        """
        Log a status change event
        """
        return cls.objects.create(
            exchange=exchange,
            event_type="STATUS_CHANGE",
            description=f"Application status changed from {previous_status} to {new_status}",
            previous_value=previous_status,
            new_value=new_status,
            actor=actor,
            is_system_generated=actor is None,
        )

    @classmethod
    def log_document_upload(cls, document, actor):
        """
        Log a document upload event
        """
        return cls.objects.create(
            exchange=document.exchange,
            event_type="DOCUMENT_UPLOAD",
            description=f"Document uploaded: {document.get_document_type_display()}",
            related_document=document,
            actor=actor,
            new_value=f"Version {document.version}",
        )

    @classmethod
    def log_document_status_change(cls, document, previous_status, actor):
        """
        Log a document status change event
        """
        event_type = (
            "DOCUMENT_APPROVED"
            if document.status == "APPROVED"
            else "DOCUMENT_REJECTED"
        )
        return cls.objects.create(
            exchange=document.exchange,
            event_type=event_type,
            description=f"Document {document.get_document_type_display()} was {document.get_status_display().lower()}",
            related_document=document,
            actor=actor,
            previous_value=previous_status,
            new_value=document.status,
        )

    @classmethod
    def log_review_added(cls, review):
        """
        Log a review added event
        """
        return cls.objects.create(
            exchange=review.exchange,
            event_type="REVIEW_ADDED",
            description=f"{review.get_review_type_display()} completed with decision: {review.get_decision_display()}",
            related_review=review,
            actor=review.reviewer,
            new_value=review.decision,
        )

    @classmethod
    def log_milestone(cls, exchange, milestone_name, actor=None, additional_data=None):
        """
        Log a milestone event
        """
        return cls.objects.create(
            exchange=exchange,
            event_type="MILESTONE",
            description=f"Milestone reached: {milestone_name}",
            actor=actor,
            is_system_generated=actor is None,
            additional_data=additional_data,
        )

    def __str__(self):
        return f"{self.get_event_type_display()} - {self.exchange.application_id} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Timeline Event"
        verbose_name_plural = "Timeline Events"
        indexes = [
            models.Index(fields=["exchange", "event_type"]),
            models.Index(fields=["timestamp"]),
        ]


class WorkflowLog(models.Model):
    """
    Model for tracking workflow status transitions in the exchange application.
    This provides a dedicated log for status changes with additional information.
    """

    exchange = models.ForeignKey(
        "Exchange", on_delete=models.CASCADE, related_name="workflow_logs"
    )
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
