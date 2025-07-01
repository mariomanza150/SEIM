"""
Models for documents associated with exchange applications.

This module contains the Document model for file uploads, validation, and status tracking as part of the exchange workflow.
"""

import os

from django.db import models
from django.urls import reverse
from django.utils import timezone

from ..base import Timestamped
from ..utils import document_upload_path


class Document(Timestamped):
    """
    Model for documents uploaded as part of an exchange application.

    Fields:
        exchange (ForeignKey): The related Exchange application.
        title (CharField): Title of the document.
        description (TextField): Description of the document (optional).
        category (CharField): Type/category of the document (see DOCUMENT_TYPES).
        file (FileField): The uploaded file.
        status (CharField): Review status of the document (pending, approved, rejected).
        uploaded_at (DateTimeField): When the document was uploaded.
        reviewed_by (ForeignKey): User who reviewed the document (optional).
        reviewed_at (DateTimeField): When the document was reviewed (optional).
        sha256_hash (CharField): SHA-256 hash for file integrity.
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

    exchange = models.ForeignKey("Exchange", on_delete=models.CASCADE, related_name="documents")

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to=document_upload_path)
    file_size = models.IntegerField(default=0)
    file_hash = models.CharField(max_length=64, blank=True, help_text="SHA-256 hash for integrity verification")
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
        # Defensive fallback for display methods
        category = dict(self.DOCUMENT_TYPES).get(self.category, self.category)
        exchange_pk = getattr(self.exchange, 'pk', str(self.exchange))
        return f"{self.title} ({category}) for Exchange {exchange_pk}"

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
            # Timeline logging and notification can be handled by signals or external services
            return True
        return False

    def reject_document(self, user, reason=""):
        self.status = "REJECTED"
        self.save()
        # Timeline logging can be handled by signals or external services
        return True

    def clean(self):
        """
        Custom validation for the Document model
        """
        super().clean()

        # Validate file size
        if self.file_size <= 0:
            raise ValueError("File size must be greater than zero.")

        # Validate category
        valid_categories = [choice[0] for choice in self.DOCUMENT_TYPES]
        if self.category not in valid_categories:
            raise ValueError(f"Invalid category: {self.category}")

        # Security: Validate file extension and type
        allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx']
        ext = self.get_file_extension()
        if ext not in allowed_extensions:
            raise ValueError(f"File extension {ext} is not allowed.")

        # Optionally, add more security checks here (e.g., MIME type, file scan)

    def save(self, *args, **kwargs):
        """
        Override save method to enforce validation
        """
        self.clean()
        super().save(*args, **kwargs)

    def is_pending(self):
        """
        Check if the document status is pending
        """
        return self.status == "PENDING"

    def is_approved(self):
        """
        Check if the document status is approved
        """
        return self.status == "APPROVED"

    def is_rejected(self):
        """
        Check if the document status is rejected
        """
        return self.status == "REJECTED"
