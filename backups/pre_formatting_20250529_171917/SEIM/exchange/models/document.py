"""
Models for documents associated with exchange applications
"""

import os
from django.db import models
from django.urls import reverse
from django.utils import timezone
from .timestamp_base import TimestampedModel
from .utils import document_upload_path


class Document(TimestampedModel):
    """
    Model for documents uploaded as part of an exchange application
    """

    DOCUMENT_TYPES = (
        ("passport", "Passport Copy"),
        ("transcript", "Academic Transcript"),
        ("language_cert", "Language Certificate"),
        ("motivation_letter", "Motivation Letter"),
        ("recommendation", "Recommendation Letter"),
        ("cv", "Curriculum Vitae"),
        ("photo", "ID Photo"),
        ("acceptance_letter", "Acceptance Letter"),
        ("learning_agreement", "Learning Agreement"),
        ("health_insurance", "Health Insurance"),
        ("visa", "Visa/Residence Permit"),
        ("housing_proof", "Housing Proof"),
        ("financial_support", "Financial Support Proof"),
        ("grade_sheet", "Grade Sheet"),
        ("progress_report", "Progress Report"),
        ("other", "Other Document"),
    )

    STATUS_CHOICES = (
        ("PENDING", "Pending Review"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    )

    exchange = models.ForeignKey(
        "Exchange", on_delete=models.CASCADE, related_name="documents"
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to=document_upload_path)
    file_size = models.IntegerField(default=0)
    file_hash = models.CharField(
        max_length=64, blank=True, help_text="SHA-256 hash for integrity verification"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_documents",
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    version = models.IntegerField(default=1)
    supersedes = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="superseded_by",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-uploaded_at"]
        permissions = [
            ("can_verify_documents", "Can verify documents"),
        ]

    def __str__(self):
        return f"{self.get_category_display()} - {self.exchange}"

    def get_absolute_url(self):
        return reverse(
            "exchange:document-detail",
            kwargs={"pk": self.exchange.pk, "doc_id": self.pk},
        )

    def get_filename(self):
        return os.path.basename(self.file.name)

    def get_file_extension(self):
        return os.path.splitext(self.file.name)[1].lower()

    def get_human_readable_size(self):
        size = self.file_size
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"

    def verify_document(self, user):
        if not self.verified:
            self.verified = True
            self.verified_by = user
            self.verified_at = timezone.now()
            self.status = "APPROVED"
            self.save()

            from .timeline import Timeline
            Timeline.log_document_status_change(
                document=self, previous_status="PENDING", actor=user
            )

            from ..services.notification import NotificationService
            NotificationService.send_document_verification_notification(self, user)
            return True
        return False

    def reject_document(self, user, reason=""):
        previous_status = self.status
        self.status = "REJECTED"
        self.save()

        from .timeline import Timeline
        Timeline.log_document_status_change(
            document=self, previous_status=previous_status, actor=user
        )

        return True

    def save(self, *args, **kwargs):
        if self.pk is None and self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)

