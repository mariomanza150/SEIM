from django.db import models

from core.models import TimeStampedModel, UUIDModel


class Report(UUIDModel, TimeStampedModel):
    """Analytics report definition (e.g., applications by status, program stats)."""

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True
    )

    def __str__(self):
        return self.name


class Metric(UUIDModel, TimeStampedModel):
    """Individual metric tracked for analytics (e.g., count, average, etc.)."""

    name = models.CharField(max_length=100)
    value = models.FloatField()
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="metrics")
    calculated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}: {self.value}"


class DashboardConfig(UUIDModel, TimeStampedModel):
    """User or admin dashboard configuration (widgets, filters, etc.)."""

    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    config = models.JSONField()

    def __str__(self):
        return f"Dashboard config for {self.user.username}"
