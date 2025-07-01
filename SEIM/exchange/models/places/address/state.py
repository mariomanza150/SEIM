from django.db import models
from ...base import Option
from .country import Country

class State(Option):
    """Model representing a state/province/region within a country."""
    country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name='states')
    code = models.CharField(max_length=10, help_text="State/province code")
    
    class Meta:
        ordering = ["name"]
        unique_together = [['country', 'code']]

    def __str__(self):
        return f"{self.name}, {self.country.name}"
