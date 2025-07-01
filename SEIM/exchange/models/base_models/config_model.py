from django.db import models

class ConfigModel(models.Model):
    name: str = models.CharField(max_length=100, unique=True)
    label: str = models.CharField(max_length=100)
    description: str = models.TextField(blank=True)
    active: bool = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.label