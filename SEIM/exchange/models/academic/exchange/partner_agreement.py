from django.db import models

from ....timestamp_base import TimestampedModel
from ...config_model import ConfigModel
from ...university import University
from .academic_program import ExchangeProgram

class PartnerAgreement(TimestampedModel):
    home_university = models.ForeignKey(University, on_delete=models.PROTECT, related_name="home_agreements")
    partner_university = models.ForeignKey(University, on_delete=models.PROTECT, related_name="partner_agreements")
    program = models.ForeignKey(ExchangeProgram, on_delete=models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField()
    active = models.BooleanField(default=True)
    quota_limit = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["start_date"]
        indexes = [
            models.Index(fields=["home_university", "partner_university"], name="pa_univ_idx"),
        ]

    def __str__(self):
        return f"{self.home_university.name} ↔ {self.partner_university.name} ({self.program.code})"
