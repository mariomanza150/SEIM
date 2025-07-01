from django.db import models
from .base_profile import BaseProfile

class Logged(models.Model):
    """
    Abstract base model for tracking creator and updater profiles.
    """
    created_by = models.ForeignKey(BaseProfile, on_delete=models.PROTECT, related_name="logged_created_set")
    updated_by = models.ForeignKey(BaseProfile, on_delete=models.PROTECT, related_name="logged_updated_set")

    class Meta:
        abstract = True
