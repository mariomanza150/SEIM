from django.db import models
from ..base_models.config_model import ConfigModel
from .university import University
from .address import City, State, Country

class Campus(ConfigModel):
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='campuses')

    address = models.TextField(blank=True)
    city = models.ForeignKey(City, on_delete=models.PROTECT)
    state = models.ForeignKey(State, on_delete=models.PROTECT)
    country = models.ForeignKey(Country, on_delete=models.PROTECT)

    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.university.name}"
