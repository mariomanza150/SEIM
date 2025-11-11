from django.db import models

from core.models import TimeStampedModel, UUIDModel


class Program(UUIDModel, TimeStampedModel):
    """Represents an exchange program (e.g., Erasmus, semester abroad)."""

    name = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    min_gpa = models.FloatField(
        null=True, blank=True, help_text="Minimum GPA required for eligibility."
    )
    required_language = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        help_text="Required language for eligibility.",
    )
    min_language_level = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        choices=[
            ('A1', 'Beginner (A1)'),
            ('A2', 'Elementary (A2)'),
            ('B1', 'Intermediate (B1)'),
            ('B2', 'Upper Intermediate (B2)'),
            ('C1', 'Advanced (C1)'),
            ('C2', 'Proficient (C2)'),
        ],
        help_text="Minimum language proficiency level (CEFR scale)."
    )
    max_age = models.PositiveIntegerField(
        null=True, blank=True, help_text="Maximum age for eligibility."
    )
    min_age = models.PositiveIntegerField(
        null=True, blank=True, help_text="Minimum age for eligibility."
    )
    auto_reject_ineligible = models.BooleanField(
        default=False,
        help_text="Automatically reject applications that don't meet eligibility criteria."
    )
    recurring = models.BooleanField(
        default=False, help_text="Is this program recurring (e.g., every semester)?"
    )
    # Link to dynamic form created via django-dynforms
    application_form = models.ForeignKey(
        'application_forms.FormType',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Dynamic application form for this program"
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.end_date and self.start_date and self.end_date <= self.start_date:
            raise ValidationError({"end_date": "End date must be after start date."})


class Application(UUIDModel, TimeStampedModel):
    """Student application for a program. No user logic here; delegates to accounts.User."""

    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    student = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    status = models.ForeignKey("ApplicationStatus", on_delete=models.PROTECT)
    submitted_at = models.DateTimeField(null=True, blank=True)
    withdrawn = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['student', 'status'], name='app_student_status_idx'),
            models.Index(fields=['program', 'status'], name='app_program_status_idx'),
            models.Index(fields=['student', 'withdrawn'], name='app_student_withdrawn_idx'),
            models.Index(fields=['submitted_at'], name='app_submitted_idx'),
            models.Index(fields=['-created_at'], name='app_created_desc_idx'),
        ]
        ordering = ['-created_at']
        verbose_name = 'Application'
        verbose_name_plural = 'Applications'

    def __str__(self):
        return f"{self.student} - {self.program}"


class ApplicationStatus(models.Model):
    """Status for application workflow (draft, submitted, under_review, etc.)."""

    name = models.CharField(max_length=50, unique=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["order"]


class Comment(UUIDModel, TimeStampedModel):
    """Comments on applications, can be internal or visible to students."""

    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    author = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    text = models.TextField()
    is_private = models.BooleanField(default=False)

    def __str__(self):
        return f"Comment by {self.author} on {self.application}"


class TimelineEvent(UUIDModel, TimeStampedModel):
    """Tracks status changes and key events for an application."""

    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=100)
    description = models.TextField()
    created_by = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True
    )

    def __str__(self):
        return f"{self.event_type} - {self.description}"
