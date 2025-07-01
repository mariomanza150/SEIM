from django.db import models
from ...base import Option
from .state import State
from .country import Country

class City(Option):
    """Model representing a city within a state/province."""
    state = models.ForeignKey(State, on_delete=models.PROTECT, related_name='cities')
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "cities"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}, {self.state.name}, {self.country.name}"
