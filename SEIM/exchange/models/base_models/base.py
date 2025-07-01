from django.core.validators import RegexValidator
from django.db import models

from .timestamped_model import TimestampedModel


phone_regex = RegexValidator(
    regex=r"^\+?1?\d{9,15}$",
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
)

passport_regex = RegexValidator(
    regex=r"^[A-Z0-9]{6,12}$",
    message="Passport number must be 6-12 characters with uppercase letters and numbers only.",
)


class Student(TimestampedModel):
    student_id = models.CharField(max_length=50, unique=True)
    phone_number = models.CharField(max_length=15, validators=[phone_regex])
    passport_number = models.CharField(max_length=20, validators=[passport_regex])


class StudentDashboard(TimestampedModel):
    student_id = models.CharField(max_length=50, unique=True)


class File:
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
