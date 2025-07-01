from django.db import models
from ..base import Option
from .university import University
from .address import Address

class Campus(Option):
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='campuses')

    address = models.ForeignKey(Address, on_delete=models.PROTECT)

    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.university.name}"
