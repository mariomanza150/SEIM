from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .timestamp_base import TimestampedModel


class Exchange(TimestampedModel):
    STATUS_CHOICES = (
        ("DRAFT", "Draft"),
        ("SUBMITTED", "Submitted"),
        ("UNDER_REVIEW", "Under Review"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
        ("COMPLETED", "Completed"),
    )

    TRANSITIONS = {
        "DRAFT": ["SUBMITTED"],
        "SUBMITTED": ["UNDER_REVIEW", "REJECTED"],
        "UNDER_REVIEW": ["APPROVED", "REJECTED"],
        "APPROVED": ["COMPLETED"],
        "REJECTED": [],
        "COMPLETED": [],
    }

    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="exchanges"
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    passport_number = models.CharField(max_length=50, blank=True)
    student_number = models.CharField(max_length=50)
    # Academic information
    current_university = models.CharField(max_length=255)
    current_program = models.CharField(max_length=255)
    current_year = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)], null=True, blank=True
    )
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)

    # Exchange details
    destination_university = models.CharField(max_length=255)
    destination_country = models.CharField(max_length=100)
    exchange_program = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()

    # Status and workflow
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="DRAFT")
    submission_date = models.DateTimeField(null=True, blank=True)
    review_date = models.DateTimeField(null=True, blank=True)
    decision_date = models.DateTimeField(null=True, blank=True)

    # Additional information
    motivation_letter = models.TextField(blank=True)
    language_proficiency = models.CharField(max_length=100, blank=True)
    special_requirements = models.TextField(blank=True)
    emergency_contact = models.TextField(blank=True)
    home_university = models.CharField(max_length=255, blank=True)
    degree = models.CharField(max_length=255, blank=True)
    major = models.CharField(max_length=255, blank=True)
    academic_year = models.CharField(max_length=50, blank=True)
    current_semester = models.CharField(max_length=50, blank=True)
    host_university = models.CharField(max_length=255, blank=True)
    host_country = models.CharField(max_length=100, blank=True)
    program = models.CharField(max_length=255, blank=True)
    semester = models.CharField(max_length=50, blank=True)
    study_goals = models.TextField(blank=True)
    referral_source = models.CharField(max_length=255, blank=True)

    # Administrative fields
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_exchanges",
    )
    notes = models.TextField(
        blank=True, help_text="Internal notes (not visible to students)"
    )

    class Meta:
        permissions = [
            ("can_review_exchange", "Can review exchange applications"),
            ("can_approve_exchange", "Can approve/reject exchange applications"),
            ("can_view_all_exchanges", "Can view all exchange applications"),
        ]

    def __str__(self):
        return f"{self.student.first_name} {self.student.last_name} - {self.destination_university} ({self.status})"

    def can_submit(self):
        """Check if the application can be submitted."""
        return self.status == "DRAFT" and self.has_required_documents()

    def has_required_documents(self):
        """Check if all required documents are uploaded."""
        required_categories = ["passport", "transcript", "motivation_letter"]
        uploaded_categories = self.documents.values_list("category", flat=True)
        return all(cat in uploaded_categories for cat in required_categories)

    def submit(self):
        """Submit the application for review."""
        if self.can_submit():
            self.status = "SUBMITTED"
            self.submission_date = timezone.now()
            self.save()
            return True
        return False

    def clean(self):
        """Enhanced model validation"""
        # Date validation
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            raise ValidationError("End date must be after start date")

        # Status transition validation
        if self.pk:  # Existing instance
            old_instance = Exchange.objects.get(pk=self.pk)
            if not self.can_transition_to(self.status):
                raise ValidationError(
                    f"Invalid status transition from {old_instance.status} to {self.status}"
                )

    def save(self, *args, **kwargs):
        """Enhanced save with validation"""
        self.full_clean()
        super().save(*args, **kwargs)

    def can_transition_to(self, new_status):
        """
        Check if the exchange can transition to the specified status.

        Args:
            new_status: The target status

        Returns:
            bool: True if transition is allowed, False otherwise
        """
        # Validate that the new status is a valid choice
        valid_statuses = [status[0] for status in self.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return False

        # Check if the transition is allowed based on current status
        if new_status in self.TRANSITIONS.get(self.status, []):
            return True

        return False

    def transition_to(self, new_status, user=None, comment=""):
        """
        Transition the exchange to a new status.

        Args:
            new_status: The target status
            user: The user performing the transition (optional)
            comment: Optional comment for the transition

        Returns:
            bool: True if transition was successful, False otherwise

        Raises:
            ValueError: If transition is not allowed
        """
        if not self.can_transition_to(new_status):
            raise ValueError(f"Cannot transition from {self.status} to {new_status}")

        old_status = self.status
        self.status = new_status

        # Update timestamps based on the transition
        now = timezone.now()
        if new_status == "SUBMITTED":
            self.submission_date = now
        elif new_status in ["APPROVED", "REJECTED"]:
            self.decision_date = now
        self.save()

        # Log the transition in WorkflowLog
        from .timeline import WorkflowLog

        WorkflowLog.objects.create(
            exchange=self,
            from_status=old_status,
            to_status=new_status,
            user=user,
            comment=comment,
        )

        return True
