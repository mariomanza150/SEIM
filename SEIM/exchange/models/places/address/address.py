from django.db import models
from .city import City
from .state import State
from .country import Country

class Address(models.Model):
    """
    Stores a postal address with references to city, state, and country.
    """
    line_1 = models.CharField(max_length=100)
    line_2 = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=8)
    city = models.ForeignKey(City, on_delete=models.PROTECT)
    state = models.ForeignKey(State, on_delete=models.PROTECT)
    country = models.ForeignKey(Country, on_delete=models.PROTECT)

    class Meta:
        ordering = ["city", "line_1"]
        verbose_name = "Address"
        verbose_name_plural = "Addresses"

    def __str__(self):
        return f"{self.line_1}, {self.line_2}, {self.city}, {self.state}, {self.country} {self.postal_code}"
