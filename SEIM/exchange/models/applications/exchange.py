"""
Enhanced Exchange model with FSM workflow support.

This module contains the Exchange model, which represents a student exchange application and manages its workflow using a finite state machine (FSM).
"""
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django_fsm import FSMField, transition, can_proceed

from ..base_models.timestamped_model import TimestampedModel


class Exchange(TimestampedModel):
    """
    Main model for student exchange applications with state machine workflow.

    Fields:
        student (ForeignKey): The student applying for the exchange.
        exchange_program (ForeignKey): The selected exchange program.
        current_university (CharField): Student's current university.
        host_university (CharField): Destination university for exchange.
        destination_country (CharField): Country of the host university.
        current_program (CharField): Student's current academic program.
        current_year (PositiveIntegerField): Student's current year of study.
        gpa (DecimalField): Student's GPA.
        degree (CharField): Student's degree.
        major (CharField): Student's major.
        program (CharField): Academic program for the exchange.
        academic_year (CharField): Academic year for the exchange.
        current_semester (CharField): Current semester of the student.
        start_date (DateField): Exchange start date.
        end_date (DateField): Exchange end date.
        motivation_letter (TextField): Student's motivation for the exchange.
        study_goals (TextField): Academic goals for the exchange.
        special_requirements (TextField): Any special requirements or accommodations needed.
        referral_source (CharField): How the student learned about the program.
        status (FSMField): Current status of the application (see STATUS_CHOICES).
    """
    
    # Status choices with additional CANCELLED state
    STATUS_CHOICES = (
        ("DRAFT", "Draft"),
        ("SUBMITTED", "Submitted"),
        ("UNDER_REVIEW", "Under Review"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    )

    # Core fields
    student = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="exchanges",
        help_text="Student applying for the exchange"
    )
    
    # Exchange program reference
    exchange_program = models.ForeignKey(
        'ExchangeProgram', 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        help_text="Selected exchange program"
    )
    
    # University Information
    current_university = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        help_text="Student's current university"
    )
    host_university = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        help_text="Destination university for exchange"
    )
    destination_country = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="Country of the host university"
    )
    
    # Academic Information
    current_program = models.CharField(max_length=255, blank=True, null=True)
    current_year = models.PositiveIntegerField(blank=True, null=True)
    gpa = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        blank=True, 
        null=True,
        help_text="Current GPA"
    )
    degree = models.CharField(max_length=255, blank=True, null=True)
    major = models.CharField(max_length=255, blank=True, null=True)
    program = models.CharField(max_length=255, blank=True, null=True)
    academic_year = models.CharField(max_length=50, blank=True, null=True)
    current_semester = models.CharField(max_length=50, blank=True, null=True)
    
    # Exchange Period
    start_date = models.DateField(
        null=True, 
        blank=True,
        help_text="Exchange start date"
    )
    end_date = models.DateField(
        null=True, 
        blank=True,
        help_text="Exchange end date"
    )
    
    # Application Details
    motivation_letter = models.TextField(
        blank=True, 
        null=True,
        help_text="Student's motivation for the exchange"
    )
    study_goals = models.TextField(
        blank=True, 
        null=True,
        help_text="Academic goals for the exchange"
    )
    special_requirements = models.TextField(
        blank=True, 
        null=True,
        help_text="Any special requirements or accommodations needed"
    )
    referral_source = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        help_text="How the student learned about the program"
    )
    
    # Status management with FSM
    status = FSMField(
        default="DRAFT",
        choices=STATUS_CHOICES,
        help_text="Current status of the application"
    )
    
    # Timeline tracking
    submission_date = models.DateTimeField(null=True, blank=True)
    review_date = models.DateTimeField(null=True, blank=True)
    decision_date = models.DateTimeField(null=True, blank=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    
    # Administrative fields
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_exchanges",
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_exchanges",
    )
    notes = models.TextField(
        blank=True, 
        help_text="Internal notes (not visible to students)"
    )
    rejection_reason = models.TextField(
        blank=True,
        help_text="Reason for rejection (if applicable)"
    )
    
    # Language proficiency
    language_proficiencies = models.JSONField(
        default=dict,
        blank=True,
        help_text="Language proficiency scores/certificates"
    )
    
    # Emergency contact
    emergency_contact_name = models.CharField(max_length=255, blank=True)
    emergency_contact_phone = models.CharField(max_length=50, blank=True)
    emergency_contact_relationship = models.CharField(max_length=100, blank=True)
    
    class Meta:
        permissions = [
            ("can_review_exchange", "Can review exchange applications"),
            ("can_approve_exchange", "Can approve/reject exchange applications"),
            ("can_view_all_exchanges", "Can view all exchange applications"),
            ("can_cancel_exchange", "Can cancel exchange applications"),
        ]
        ordering = ["-submission_date", "-created_at"]
        indexes = [
            models.Index(fields=["status", "submission_date"], name="exchange_status_submission_idx"),
            models.Index(fields=["student", "status"], name="exchange_student_status_idx"),
            models.Index(fields=["exchange_program", "status"], name="exchange_program_status_idx"),
        ]

    def __str__(self):
        # Defensive fallback for display methods
        status = dict(self.STATUS_CHOICES).get(self.status, self.status)
        student = getattr(self.student, 'username', str(self.student))
        return f"Exchange Application for {student} ({status})"

    # FSM Transitions
    
    @transition(field=status, source='DRAFT', target='SUBMITTED')
    def submit(self, user=None):
        """Submit the exchange application for review."""
        if not self.has_required_documents():
            raise ValidationError("Cannot submit without all required documents.")
        self.submission_date = timezone.now()
        # Log the transition
        self._log_transition('DRAFT', 'SUBMITTED', user, "Application submitted")
    
    @transition(field=status, source='SUBMITTED', target='UNDER_REVIEW')
    def start_review(self, user=None):
        """Start the review process."""
        self.review_date = timezone.now()
        if user:
            self.reviewed_by = user
        self._log_transition('SUBMITTED', 'UNDER_REVIEW', user, "Review started")
    
    @transition(field=status, source=['SUBMITTED', 'UNDER_REVIEW'], target='APPROVED')
    def approve(self, user=None, comment=""):
        """Approve the exchange application."""
        self.decision_date = timezone.now()
        if user:
            self.approved_by = user
        self._log_transition(self.status, 'APPROVED', user, comment or "Application approved")
    
    @transition(field=status, source=['SUBMITTED', 'UNDER_REVIEW'], target='REJECTED')
    def reject(self, user=None, reason=""):
        """Reject the exchange application."""
        self.decision_date = timezone.now()
        self.rejection_reason = reason
        self._log_transition(self.status, 'REJECTED', user, reason or "Application rejected")
    
    @transition(field=status, source='APPROVED', target='COMPLETED')
    def complete(self, user=None):
        """Mark the exchange as completed."""
        self.completion_date = timezone.now()
        self._log_transition('APPROVED', 'COMPLETED', user, "Exchange completed")
    
    @transition(field=status, source=['DRAFT', 'SUBMITTED', 'UNDER_REVIEW', 'APPROVED'], target='CANCELLED')
    def cancel(self, user=None, reason=""):
        """Cancel the exchange application."""
        self._log_transition(self.status, 'CANCELLED', user, reason or "Application cancelled")
    
    def _log_transition(self, from_status, to_status, user, comment):
        """Log workflow transitions."""
        # Timeline logging can be handled by signals or external services
        pass
    
    # Validation methods
    
    def has_required_documents(self):
        """Check if all required documents are uploaded."""
        # Defensive: Only check if documents attribute exists
        if hasattr(self, 'documents'):
            if self.exchange_program and hasattr(self.exchange_program, 'required_documents') and self.exchange_program.required_documents:
                required_categories = self.exchange_program.required_documents
            else:
                required_categories = ["passport", "transcript", "motivation_letter"]
            uploaded_categories = self.documents.filter(is_deleted=False).values_list("category", flat=True)
            return all(cat in uploaded_categories for cat in required_categories)
        return False
    
    def get_missing_documents(self):
        """Get list of missing required documents."""
        if hasattr(self, 'documents'):
            if self.exchange_program and hasattr(self.exchange_program, 'required_documents') and self.exchange_program.required_documents:
                required_categories = self.exchange_program.required_documents
            else:
                required_categories = ["passport", "transcript", "motivation_letter"]
            uploaded_categories = set(self.documents.filter(is_deleted=False).values_list("category", flat=True))
            return [cat for cat in required_categories if cat not in uploaded_categories]
        return []
    
    def can_be_edited(self):
        """Check if the application can be edited by the student."""
        return self.status in ['DRAFT', 'SUBMITTED']
    
    def get_available_transitions(self):
        """Get list of available status transitions."""
        if hasattr(self, 'get_available_status_transitions'):
            return [
                {
                    'name': t.name,
                    'source': t.source,
                    'target': t.target,
                    'available': can_proceed(getattr(self, t.name))
                }
                for t in self.get_available_status_transitions()
            ]
        return []
    
    def clean(self):
        """
        Enhanced model validation for Exchange.
        """
        super().clean()
        # Validate dates
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            raise ValidationError("End date must be after start date.")
        # Validate exchange program selection
        if self.exchange_program and hasattr(self.exchange_program, 'is_active') and not self.exchange_program.is_active:
            raise ValidationError("Selected exchange program is not active.")
        # Check if student is eligible for the program
        if self.exchange_program and self.gpa and hasattr(self.exchange_program, 'is_student_eligible'):
            student_profile = {
                'gpa': self.gpa,
                'degree': self.degree,
                'year': self.current_year,
                'languages': self.language_proficiencies
            }
            eligible, reason = self.exchange_program.is_student_eligible(student_profile)
            if not eligible:
                raise ValidationError(f"Not eligible for this program: {reason}")
    
    def save(self, *args, **kwargs):
        """
        Enhanced save with validation.
        """
        if not kwargs.pop('skip_validation', False):
            self.full_clean()
        super().save(*args, **kwargs)
    
    # Helper methods for status checking (backward compatibility)
    
    def is_completed(self):
        """Check if the exchange application is completed."""
        return self.status == "COMPLETED"
    
    def is_under_review(self):
        """Check if the exchange application is under review."""
        return self.status == "UNDER_REVIEW"
    
    def is_approved(self):
        """Check if the exchange application is approved."""
        return self.status == "APPROVED"
    
    def is_rejected(self):
        """Check if the exchange application is rejected."""
        return self.status == "REJECTED"
    
    def is_cancelled(self):
        """Check if the exchange application is cancelled."""
        return self.status == "CANCELLED"
    
    def get_status_display_class(self):
        """Get CSS class for status display."""
        status_classes = {
            'DRAFT': 'secondary',
            'SUBMITTED': 'info',
            'UNDER_REVIEW': 'warning',
            'APPROVED': 'success',
            'REJECTED': 'danger',
            'COMPLETED': 'primary',
            'CANCELLED': 'dark'
        }
        return status_classes.get(self.status, 'secondary')
    
    def get_progress_percentage(self):
        """Calculate application progress percentage."""
        progress_map = {
            'DRAFT': 20,
            'SUBMITTED': 40,
            'UNDER_REVIEW': 60,
            'APPROVED': 80,
            'COMPLETED': 100,
            'REJECTED': 100,
            'CANCELLED': 100
        }
        return progress_map.get(self.status, 0)
    
    def get_timeline_events(self):
        """Get all timeline events for this exchange."""
        events = []
        
        # Add creation event
        events.append({
            'date': self.created_at,
            'event': 'Application created',
            'type': 'info'
        })
        
        # Add submission event
        if self.submission_date:
            events.append({
                'date': self.submission_date,
                'event': 'Application submitted',
                'type': 'primary'
            })
        
        # Add review event
        if self.review_date:
            events.append({
                'date': self.review_date,
                'event': 'Review started',
                'type': 'warning'
            })
        
        # Add decision event
        if self.decision_date:
            event_type = 'success' if self.status == 'APPROVED' else 'danger'
            event_text = 'Application approved' if self.status == 'APPROVED' else 'Application rejected'
            events.append({
                'date': self.decision_date,
                'event': event_text,
                'type': event_type
            })
        
        # Add completion event
        if self.completion_date:
            events.append({
                'date': self.completion_date,
                'event': 'Exchange completed',
                'type': 'success'
            })
        
        # Sort by date
        events.sort(key=lambda x: x['date'])
        
        return events
    
    # Backward compatibility methods
    
    def can_transition_to(self, new_status):
        """Check if transition to new status is allowed (backward compatibility)."""
        # Map old transition check to FSM
        transition_map = {
            ('DRAFT', 'SUBMITTED'): self.submit,
            ('SUBMITTED', 'UNDER_REVIEW'): self.start_review,
            ('SUBMITTED', 'APPROVED'): self.approve,
            ('SUBMITTED', 'REJECTED'): self.reject,
            ('UNDER_REVIEW', 'APPROVED'): self.approve,
            ('UNDER_REVIEW', 'REJECTED'): self.reject,
            ('APPROVED', 'COMPLETED'): self.complete,
        }
        
        key = (self.status, new_status)
        if key in transition_map:
            return can_proceed(transition_map[key])
        
        # Check cancel transition
        if new_status == 'CANCELLED' and self.status in ['DRAFT', 'SUBMITTED', 'UNDER_REVIEW', 'APPROVED']:
            return can_proceed(self.cancel)
        
        return False
    
    def transition_to(self, new_status, user=None, comment=""):
        """Transition to new status (backward compatibility wrapper)."""
        # Map to FSM transitions
        if self.status == 'DRAFT' and new_status == 'SUBMITTED':
            self.submit(user=user)
        elif self.status == 'SUBMITTED' and new_status == 'UNDER_REVIEW':
            self.start_review(user=user)
        elif new_status == 'APPROVED':
            self.approve(user=user, comment=comment)
        elif new_status == 'REJECTED':
            self.reject(user=user, reason=comment)
        elif self.status == 'APPROVED' and new_status == 'COMPLETED':
            self.complete(user=user)
        elif new_status == 'CANCELLED':
            self.cancel(user=user, reason=comment)
        else:
            raise ValueError(f"Cannot transition from {self.status} to {new_status}")
        
        self.save(skip_validation=True)
        return True
