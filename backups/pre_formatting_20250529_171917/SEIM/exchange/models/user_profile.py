"""
User profile model for the exchange app.
Extends the User model to add roles and additional information.
"""

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _


class BaseProfile(models.Model):
    """
    Abstract base class for user profile containing common fields
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.user.username}"


class UserProfile(models.Model):
    """
    Unified user profile model combining student, staff, and contact information
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('', 'Prefer not to say'),
    )

    # Personal information
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    
    # Contact information
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    
    # Academic information
    student_id = models.CharField(max_length=50, blank=True, null=True)
    institution = models.CharField(max_length=255, blank=True, null=True)
    department = models.CharField(max_length=255, blank=True, null=True)
    current_program = models.CharField(max_length=255, blank=True, null=True)
    
    # Staff information
    position = models.CharField(max_length=255, blank=True, null=True)
    office_phone = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} Profile"
    
    def get_profile_completeness(self):
        """Calculate profile completion percentage"""
        required_fields = [
            "user.first_name",
            "user.last_name", 
            "user.email",
            "student_id",
            "department",
            "current_program",
        ]
        comp = 0
        for field in required_fields:
            if "." not in field:
                if getattr(self, field, None):
                    comp += 1
            else:
                obj_field, attr_field = field.split(".")
                obj = getattr(self, obj_field, None)
                if obj and getattr(obj, attr_field, None):
                    comp += 1
        return int((comp / len(required_fields)) * 100) if required_fields else 0


class StudentProfile(BaseProfile):
    """
    Profile model for students
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    student_id = models.CharField(max_length=50, blank=True, null=True)
    institution = models.CharField(max_length=255, blank=True, null=True)
    current_program = models.CharField(max_length=255, blank=True, null=True)

    def get_profile_completeness(self):
        required_fields = [
            "user.first_name",
            "user.last_name",
            "user.email",
            "student_id",
            "department",
            "current_program",
        ]
        comp = 0
        for field in required_fields:
            if getattr(self, field.split(".")[0]):
                if  "." not in field:
                    comp += 1
                else:
                    getattr(getattr(self, field.split(".")[0]), field.split(".")[1], None)
                    comp += 1
        return int((comp / len(required_fields)) * 100) if required_fields else 0


class StaffProfile(BaseProfile):
    """
    Profile model for staff
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="staff_profile")
    
    ROLE_CHOICES = (
        ("COORDINATOR", "Exchange Coordinator"),
        ("MANAGER", "Program Manager"),
        ("ADMIN", "Administrator"),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    position = models.CharField(max_length=255, blank=True, null=True)
    office_phone = models.CharField(max_length=20, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(blank=True, null=True)

    def is_coordinator(self):
        return self.role == "COORDINATOR"

    def is_manager(self):
        return self.role == "MANAGER"

    def is_admin(self):
        return self.role == "ADMIN"

    def is_staff_role(self):
        return self.role in ["COORDINATOR", "MANAGER", "ADMIN"]


class ContactProfile(BaseProfile):
    """
    Profile for additional contact details
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="contact_profile")
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """Create or update the user profile when a user is created or updated"""
    if created:
        UserProfile.objects.create(user=instance)
    else:
        UserProfile.objects.get_or_create(user=instance)
