from django.db import models
from ..base import BaseProfile
from ..places.university import University

class StudentProfile(BaseProfile):
    """
    Profile model for students
    """
    GENDER_CHOICES = (
        ("M", "Male"),
        ("F", "Female"),
        ("O", "Other"),
        ("", "Prefer not to say"),
    )

    # Personal information
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    middle_name = models.CharField(max_length=60, blank=True, null=True)
    last_mothers_name = models.CharField(max_length=60, blank=True, null=True)
    
    # Contact information
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    # Academic information
    academic_level = models.CharField(max_length=255, blank=True, null=True)
    university = models.ForeignKey(University, on_delete=models.PROTECT, blank=True, null=True, related_name="student_profiles")
    institution = models.CharField(max_length=255, blank=True, null=True)
    degree = models.CharField(max_length=255, blank=True, null=True)

    student_id = models.CharField(max_length=50, blank=True, null=True)

    def get_profile_completeness(self):
        required_fields = [
            "user.first_name",
            "user.last_name",
            "user.email",
            "student_id",
            "institution",
            "degree",
        ]
        comp = 0
        for field in required_fields:
            if getattr(self, field.split(".")[0]):
                if "." not in field:
                    comp += 1
                else:
                    getattr(getattr(self, field.split(".")[0]), field.split(".")[1], None)
                    comp += 1
        return int((comp / len(required_fields)) * 100) if required_fields else 0