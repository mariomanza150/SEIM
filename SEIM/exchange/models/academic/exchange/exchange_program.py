"""Exchange Program model for managing different exchange programs."""
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

from ...base import Timestamped
from .program_requirements import ProgramRequirements
from .funding import FundingType


class ExchangeProgram(Timestamped):
    """
    Model to represent different exchange programs available to students.
    """
    
    PROGRAM_TYPES = (
        ('BILATERAL', 'Bilateral Agreement'),
        ('ERASMUS', 'Erasmus+'),
        ('GLOBAL', 'Global Exchange'),
        ('SUMMER', 'Summer Program'),
        ('RESEARCH', 'Research Exchange'),
        ('INTERNSHIP', 'Internship Program'),
    )
    
    DURATION_UNITS = (
        ('WEEKS', 'Weeks'),
        ('MONTHS', 'Months'),
        ('SEMESTERS', 'Semesters'),
        ('YEARS', 'Years'),
    )
    
    # Basic Information
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=50, unique=True, help_text="Program identification code")
    program_type = models.CharField(max_length=20, choices=PROGRAM_TYPES)
    description = models.TextField()
    
    # Partner Information
    partner_universities = models.JSONField(
        default=list,
        help_text="List of partner universities and their details"
    )
    countries = models.JSONField(
        default=list,
        help_text="List of countries covered by this program"
    )
    
    # Duration and timing are now handled through program_requirements
    
    # Application Period
    application_start_date = models.DateField(null=True, blank=True)
    application_end_date = models.DateField(null=True, blank=True)
    
    # Requirements (now composed)
    program_requirements = models.ForeignKey(
        ProgramRequirements,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Requirements for this program"
    )
    
    # Financial Information
    funding_types = models.ManyToManyField(
        FundingType,
        blank=True,
        related_name='exchange_programs',
        help_text="Available funding types for this program"
    )
    funding_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Monthly funding amount if available"
    )
    funding_currency = models.CharField(max_length=3, default='EUR')
    
    # Administrative
    coordinator = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='coordinated_programs'
    )
    max_participants = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum number of participants per period"
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    priority_order = models.PositiveIntegerField(
        default=0,
        help_text="Display order priority (lower numbers appear first)"
    )
    
    # Documents Required
    required_documents = models.JSONField(
        default=list,
        help_text="List of required document types for this program"
    )
    
    # Additional Information
    website_url = models.URLField(blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    additional_info = models.TextField(blank=True)
    
    class Meta:
        ordering = ['priority_order', 'name']
        indexes = [
            models.Index(fields=['is_active', 'program_type']),
            models.Index(fields=['application_start_date', 'application_end_date']),
        ]
        
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def clean(self):
        """Validate the exchange program data."""
        super().clean()
        
        # Validate duration through program_requirements if it exists
        if self.program_requirements:
            reqs = self.program_requirements
            if reqs.min_duration and reqs.max_duration:
                if reqs.min_duration > reqs.max_duration:
                    raise ValidationError("Minimum duration cannot be greater than maximum duration in program requirements.")
        
        # Validate application dates
        if self.application_start_date and self.application_end_date:
            if self.application_start_date >= self.application_end_date:
                raise ValidationError("Application start date must be before end date.")
    
    def is_application_open(self):
        """Check if applications are currently open for this program."""
        if not self.is_active:
            return False
            
        if not self.application_start_date or not self.application_end_date:
            return True  # Always open if no dates specified
            
        today = timezone.now().date()
        return self.application_start_date <= today <= self.application_end_date
    
    def get_available_slots(self):
        """Get the number of available slots for this program."""
        if not self.max_participants:
            return None  # Unlimited
            
        # Count current participants
        current_count = self.exchange_set.filter(
            status__in=['APPROVED', 'UNDER_REVIEW', 'SUBMITTED']
        ).count()
        
        return max(0, self.max_participants - current_count)
    
    def is_student_eligible(self, student_profile):
        """
        Check if a student meets the eligibility criteria.
        
        Args:
            student_profile: Dictionary with student information
                {
                    'gpa': Decimal,
                    'degree': str,
                    'year': int,
                    'languages': dict,
                    'semesters_remaining': int
                }
        """
        if not self.program_requirements:
            return True, "No specific requirements"
            
        reqs = self.program_requirements
        
        # Check GPA
        if reqs.min_gpa and student_profile.get('gpa', 0) < reqs.min_gpa:
            return False, "GPA requirement not met"
        
        # Check degree
        if reqs.eligible_degrees and student_profile.get('degree') not in reqs.eligible_degrees:
            return False, "Degree program not eligible"
        
        # Check year
        if reqs.eligible_years and student_profile.get('year') not in reqs.eligible_years:
            return False, "Academic year not eligible"
        
        # Check semesters remaining
        semesters_remaining = student_profile.get('semesters_remaining')
        if reqs.student_semesters_remaining_after_exchange and semesters_remaining:
            min_required = min(reqs.student_semesters_remaining_after_exchange) if reqs.student_semesters_remaining_after_exchange else 0
            if semesters_remaining < min_required:
                return False, f"Must have at least {min_required} semesters remaining after exchange"
        
        # Check language requirements
        if reqs.language_requirements and isinstance(reqs.language_requirements, dict):
            student_languages = student_profile.get('languages', {})
            for lang, requirement in reqs.language_requirements.items():
                if lang not in student_languages:
                    return False, f"Missing {lang} language requirement: {requirement}"
        
        return True, "Eligible"
    
    def get_required_documents_display(self):
        """Get a formatted list of required documents."""
        return ', '.join(self.required_documents) if self.required_documents else 'None specified'
    
    def get_partner_universities_by_country(self):
        """Group partner universities by country."""
        grouped = {}
        for uni in self.partner_universities:
            country = uni.get('country', 'Unknown')
            if country not in grouped:
                grouped[country] = []
            grouped[country].append(uni)
        return grouped
    
    def has_funding(self):
        """Check if this program has any funding available."""
        return self.funding_types.exists() or (self.funding_amount and self.funding_amount > 0)
    
    def get_duration_display(self):
        """Get a formatted duration display from program requirements."""
        if not self.program_requirements:
            return "Duration not specified"
        
        reqs = self.program_requirements
        if reqs.min_duration == reqs.max_duration:
            return f"{reqs.min_duration} {reqs.get_duration_unit_display()}"
        return f"{reqs.min_duration}-{reqs.max_duration} {reqs.get_duration_unit_display()}"
