from django.db import models
from ..base import Option
from .campus import Campus
from .university import University
from .address import Address
from ..profiles.contact_profile import ContactProfile

class Institution(Option):
    main_contact = models.ForeignKey(ContactProfile, on_delete=models.PROTECT)
    campus = models.ForeignKey(Campus, on_delete=models.PROTECT)
    university = models.ForeignKey(University, on_delete=models.PROTECT)
    
    address = models.ForeignKey(Address, on_delete=models.PROTECT)

    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.university.name}"
