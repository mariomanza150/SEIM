from django.db import models

from ...base import Timestamped
from ...base import Option
from ...places.university import University
from .exchange_program import ExchangeProgram

class PartnerAgreement(Option, Timestamped):
    home_university = models.ForeignKey(University, on_delete=models.PROTECT, related_name="home_agreements")
    partner_university = models.ForeignKey(University, on_delete=models.PROTECT, related_name="partner_agreements")
    program = models.ForeignKey(ExchangeProgram, on_delete=models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField()

    quota_limit = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["start_date"]
        indexes = [
            models.Index(fields=["home_university", "partner_university"], name="pa_univ_idx"),
        ]

    def __str__(self):
        return f"{self.home_university.name} ↔ {self.partner_university.name} ({self.program.code})"
