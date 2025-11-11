from django.db import models

from core.models import TimeStampedModel, UUIDModel


class Plugin(UUIDModel, TimeStampedModel):
    """Registered plugin for custom workflows or integrations."""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    enabled = models.BooleanField(default=True)


class PluginConfig(UUIDModel, TimeStampedModel):
    """Configuration for a plugin instance."""

    plugin = models.ForeignKey(Plugin, on_delete=models.CASCADE)
    config = models.JSONField()
    created_by = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True
    )
