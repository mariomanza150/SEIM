from django.db import models
from .base_profile import BaseProfile
from ..places.university import University

class StaffProfile(BaseProfile):
    """
    Profile model for staff
    """

    ROLE_CHOICES = (
        ("COORDINATOR", "Exchange Coordinator"),
        ("MANAGER", "Program Manager"),
        ("ADMIN", "Administrator"),
    )

    university = models.ForeignKey(University, on_delete=models.PROTECT, blank=True, null=True, related_name="staff_profiles")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    position = models.CharField(max_length=255, blank=True, null=True)
    office_phone = models.CharField(max_length=20, blank=True, null=True)

    def is_coordinator(self):
        return self.role == "COORDINATOR"

    def is_manager(self):
        return self.role == "MANAGER"

    def is_admin(self):
        return self.role == "ADMIN"

    def is_staff_role(self):
        return self.role in ["COORDINATOR", "MANAGER", "ADMIN"]
