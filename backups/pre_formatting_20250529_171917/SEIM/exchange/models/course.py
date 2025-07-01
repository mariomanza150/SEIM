"""
Course and Grade models for the exchange app.
"""

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Course(models.Model):
    """
    Model for tracking courses at the host institution
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

    exchange = models.ForeignKey(
        "Exchange", on_delete=models.CASCADE, related_name="courses"
    )

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
    home_credits = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )

    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PLANNED")
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="approved_courses",
    )
    approved_at = models.DateTimeField(blank=True, null=True)

    # Term information
    term = models.CharField(max_length=100, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    # Notes
    notes = models.TextField(blank=True, null=True)

    def approve(self, user):
        """Approve course for learning agreement"""
        self.status = "APPROVED"
        self.approved_by = user
        self.approved_at = timezone.now()
        self.save()

    def __str__(self):
        return (
            f"{self.course_code}: {self.course_name} ({self.exchange.application_id})"
        )

    class Meta:
        ordering = ["exchange", "course_code"]
        verbose_name = "Course"
        verbose_name_plural = "Courses"


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
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="PROVISIONAL"
    )
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

    def transfer_to_home_university(self, user):
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
