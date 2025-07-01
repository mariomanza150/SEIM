from django.db import models
from .address.country import Country
from ..base_models.config_model import ConfigModel


class University(ConfigModel):
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    code = models.CharField(max_length=50, unique=True)
    is_partner = models.BooleanField(default=True)
    website = models.URLField(blank=True)
    contact_email = models.EmailField(blank=True)
    type = models.CharField(max_length=50, choices=[
        ("PUBLIC", "Public"),
        ("PRIVATE", "Private"),
        ("OTHER", "Other")
    ])

    def __str__(self):
        return f"{self.name} ({self.country.iso_code})"


