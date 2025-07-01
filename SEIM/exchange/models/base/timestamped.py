"""
Base model providing timestamp functionality for all models.
Includes created_at and updated_at fields and utility methods.
"""

from django.db import models
from django.utils import timezone


class Timestamped(models.Model):
    """
    Abstract base model that provides created and modified timestamps.
    Includes utility properties for recency checks.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]
        get_latest_by = "created_at"

    def save(self, *args, **kwargs):
        """
        Override save to update timestamps. Usually not needed with auto_now/auto_now_add,
        but can be extended for custom timestamp logic.
        """
        if not self.id:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super().save(*args, **kwargs)

    @property
    def is_new(self):
        """
        Check if the record was created in the last hour.
        """
        if self.created_at:
            now = timezone.now()
            return (now - self.created_at).total_seconds() < 3600
        return False

    @property
    def recently_updated(self):
        """
        Check if the record was updated in the last 15 minutes.
        """
        if self.updated_at:
            now = timezone.now()
            return (now - self.updated_at).total_seconds() < 900
        return False
