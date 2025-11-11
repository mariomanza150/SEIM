from django.db import models

from core.models import TimeStampedModel, UUIDModel


class DocumentType(models.Model):
    """Types of documents (e.g., transcript, ID, recommendation letter)."""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)


class Document(UUIDModel, TimeStampedModel):
    """Uploaded document for an application."""

    application = models.ForeignKey("exchange.Application", on_delete=models.CASCADE)
    type = models.ForeignKey(DocumentType, on_delete=models.CASCADE)
    file = models.FileField(upload_to="documents/")
    uploaded_by = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    is_valid = models.BooleanField(default=False)
    validated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['application', 'type'], name='doc_app_type_idx'),
            models.Index(fields=['uploaded_by'], name='doc_uploaded_by_idx'),
            models.Index(fields=['is_valid'], name='doc_is_valid_idx'),
            models.Index(fields=['validated_at'], name='doc_validated_at_idx'),
            models.Index(fields=['-created_at'], name='doc_created_desc_idx'),
        ]
        ordering = ['-created_at']
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'


class DocumentValidation(UUIDModel, TimeStampedModel):
    """Validation record for a document (virus scan, integrity check, etc.)."""

    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    validator = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)
    result = models.CharField(max_length=100)
    details = models.TextField(blank=True)
    validated_at = models.DateTimeField(auto_now_add=True)


class DocumentResubmissionRequest(UUIDModel, TimeStampedModel):
    """Request for a student to resubmit a document."""

    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    requested_by = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    reason = models.TextField()
    resolved = models.BooleanField(default=False)
    requested_at = models.DateTimeField(auto_now_add=True)


class DocumentComment(UUIDModel, TimeStampedModel):
    """Comments on documents, can be internal or visible to students."""

    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    author = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    text = models.TextField()
    is_private = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
