from django.db import models
from ..base_models.timestamped_model import TimestampedModel

class NotificationType(TimestampedModel):
    name = models.CharField(max_length=100)
    template_key = models.CharField(max_length=100)

    def __str__(self):
        return self.name
