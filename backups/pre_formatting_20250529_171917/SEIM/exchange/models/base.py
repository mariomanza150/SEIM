from pathlib import Path
import hashlib
import mimetypes
import os
import uuid

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .document import Document
from .timestamp_base import TimestampedModel
from .utils import (
    validate_file_size,
    validate_image_size,
    get_file_hash,
    document_upload_path,
    photo_upload_path,
    get_mime_type,
)

class ConfigModel(models.Model):
    name = models.CharField(max_length=100, unique=True)
    label = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.label


class Institution(ConfigModel):
    pass


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


class StudentProfile(TimestampedModel):
    student_id = models.CharField(max_length=50, unique=True)
    phone_number = models.CharField(max_length=15, validators=[phone_regex])
    passport_number = models.CharField(max_length=20, validators=[passport_regex])


class StudentDashboard(TimestampedModel):
    student_id = models.CharField(max_length=50, unique=True)


class File:
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


def AddStudentProfile(TimestampedModel):
    document = Document.objects.create(document_type="profile", file=models.FileField())
    return document


def AddStudentDashboard(TimestampedModel):
    document = Document.objects.create(
        document_type="dashboard", file=models.FileField()
    )
    return document


def AddStudentProfile(sender, instance, *args, **kwargs):
    print(f"Student profile added: {instance.student_id}")


def AddStudentDashboard(sender, instance, *args, **kwargs):
    print(f"Student dashboard added: {instance.student_id}")

