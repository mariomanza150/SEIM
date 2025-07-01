"""
Course and Grade models for the exchange app.

This module contains the Course model for tracking courses at the host institution and their equivalence at the home university.
"""

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Course(models.Model):
    """
    Model for tracking courses at the host institution.

    Fields:
        exchange (ForeignKey): The related Exchange application.
        course_code (CharField): Code of the course at the host university.
        course_name (CharField): Name of the course at the host university.
        host_university (CharField): Name of the host university.
        department (CharField): Department offering the course.
        credits (DecimalField): Number of credits for the course.
        hours_per_week (PositiveSmallIntegerField): Weekly hours (optional).
        description (TextField): Course description (optional).
        home_course_code (CharField): Equivalent course code at home university (optional).
        home_course_name (CharField): Equivalent course name at home university (optional).
        home_credits (DecimalField): Credits at home university (optional).
        status (CharField): Status of the course in the exchange process.
        approved_by (ForeignKey): User who approved the course (optional).
    """

    # Course status choices
    STATUS_CHOICES = (
        ("PLANNED", "Planned"),
        ("APPROVED", "Approved in Learning Agreement"),
        ("ENROLLED", "Enrolled"),
        ("IN_PROGRESS", "In Progress"),
        ("COMPLETED", "Completed"),
        ("DROPPED", "Dropped"),
        ("REPLACED", "Replaced"),
    )

    exchange = models.ForeignKey("Exchange", on_delete=models.CASCADE, related_name="courses")

    # Course information
    course_code = models.CharField(max_length=20)
    course_name = models.CharField(max_length=255)
    host_university = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    credits = models.DecimalField(max_digits=5, decimal_places=2)
    hours_per_week = models.PositiveSmallIntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    # Equivalence at home university
    home_course_code = models.CharField(max_length=20, blank=True, null=True)
    home_course_name = models.CharField(max_length=255, blank=True, null=True)
    home_credits = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PLANNED",
        help_text="Status of the course in the exchange process.",
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="approved_courses",
        help_text="User who approved the course (optional).",
    )
    approved_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["course_code"]
        indexes = [
            models.Index(fields=["status", "course_code"], name="course_status_code_idx"),
        ]

    def __str__(self):
        return f"{self.course_code} - {self.course_name} ({self.host_university})"

    def clean(self):
        """
        Custom validation for the Course model.
        Ensures logical consistency and provides specific error messages.
        """
        super().clean()
        if self.credits is None or self.credits <= 0:
            raise ValueError("Credits must be greater than zero.")
        if self.hours_per_week is not None and self.hours_per_week <= 0:
            raise ValueError("Hours per week must be greater than zero.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def is_approved(self) -> bool:
        return self.status == "APPROVED"

    def is_completed(self) -> bool:
        return self.status == "COMPLETED"

    def is_in_progress(self) -> bool:
        return self.status == "IN_PROGRESS"

    def is_planned(self) -> bool:
        return self.status == "PLANNED"


class Grade(models.Model):
    """
    Model for recording grades for completed courses
    """

    # Grade status choices
    STATUS_CHOICES = (
        ("PROVISIONAL", "Provisional"),
        ("OFFICIAL", "Official"),
        ("TRANSFERRED", "Transferred to Home University"),
    )

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="grades")

    # Grade information
    host_grade = models.CharField(max_length=10)
    host_grade_description = models.CharField(max_length=255, blank=True, null=True)
    converted_grade = models.CharField(max_length=10, blank=True, null=True)

    # Metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PROVISIONAL")
    date_received = models.DateField()
    date_processed = models.DateField(blank=True, null=True)

    # Documents
    grade_document = models.ForeignKey(
        "Document",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="grades",
    )

    # Processing information
    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="processed_grades",
    )
    notes = models.TextField(blank=True, null=True)

    def transfer_to_home_university(self, user) -> None:
        """Mark grade as transferred to home university"""
        self.status = "TRANSFERRED"
        self.processed_by = user
        self.date_processed = timezone.now().date()
        self.save()

    def __str__(self):
        return f"{self.course.course_code} - {self.host_grade}"

    class Meta:
        ordering = ["course", "date_received"]
        verbose_name = "Grade"
        verbose_name_plural = "Grades"
