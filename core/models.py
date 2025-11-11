import uuid

from django.db import models

# Create your models here.


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
