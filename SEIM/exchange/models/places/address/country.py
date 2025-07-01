from django.db import models
from ...base import Option

class Country(Option):
    """Model representing a country."""
    code = models.CharField(max_length=3, unique=True, help_text="ISO 3166-1 alpha-3 country code")
    phone_code = models.CharField(max_length=5, blank=True, help_text="International dialing code")
    
    class Meta:
        verbose_name_plural = "countries"
        ordering = ["name"]

    def __str__(self):
        return self.name
