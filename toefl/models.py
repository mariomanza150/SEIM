from django.conf import settings
from django.db import models

from core.models import TimeStampedModel, UUIDModel


class PracticeAttempt(UUIDModel, TimeStampedModel):
    """One completed TOEFL Practice session for a SEIM user.

    Does not update ``accounts.Profile.toefl_score`` (official scores only).
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="toefl_practice_attempts",
    )
    external_session_id = models.CharField(max_length=64, unique=True, db_index=True)
    exam_code = models.CharField(max_length=128, blank=True, default="")
    macro_id = models.CharField(max_length=128, blank=True, default="")
    client_ref = models.CharField(max_length=128, blank=True, default="")
    earned = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField(default=0)
    percent = models.FloatField(default=0.0)
    categories = models.JSONField(default=list, blank=True)
    weakest = models.JSONField(default=list, blank=True)
    items = models.JSONField(default=list, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    raw_payload = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-completed_at", "-created_at"]
        indexes = [
            models.Index(fields=["user", "-completed_at"]),
        ]

    def __str__(self):
        return f"{self.user_id} {self.exam_code} {self.percent}%"
