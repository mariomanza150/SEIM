from django.db import models
from ....timestamp_base import TimestampedModel

class FundingType(TimestampedModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_recurring = models.BooleanField(default=False)

    def __str__(self):
        return self.name
