from django.db import models
from ..places.university import University

class ContactProfile(models.Model):
    """
    Profile for additional contact details
    """

    university = models.ForeignKey(University, on_delete=models.PROTECT, blank=True, null=True, related_name="contact_profiles")
    position = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    office_phone = models.CharField(max_length=20, blank=True, null=True)

    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
