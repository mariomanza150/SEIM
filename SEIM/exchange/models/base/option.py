from django.db import models

class Option(models.Model):
    """
    Abstract base model for selectable options (e.g., dropdowns, enums).
    """
    name: str = models.CharField(max_length=100, unique=True)
    label: str = models.CharField(max_length=100)
    description: str = models.TextField(blank=True)
    active: bool = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.label
