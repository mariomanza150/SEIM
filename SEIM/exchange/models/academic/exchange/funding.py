from django.db import models
from ...base import Timestamped

class FundingType(Timestamped):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_recurring = models.BooleanField(default=False)

    def __str__(self):
        return self.name
