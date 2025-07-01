from django.db import models
from ...config_model import ConfigModel

class ProgramRequirements(ConfigModel):
    DURATION_UNITS = (
        ('WEEKS', 'Weeks'),
        ('MONTHS', 'Months'),
        ('SEMESTERS', 'Semesters'),
        ('YEARS', 'Years'),
    )

    # Duration and Timing
    min_duration = models.PositiveIntegerField(help_text="Minimum duration")
    max_duration = models.PositiveIntegerField(help_text="Maximum duration")
    duration_unit = models.CharField(max_length=20, choices=DURATION_UNITS)

    # Requirements
    min_gpa = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Minimum GPA required"
    )
    language_requirements = models.JSONField(
        default=dict,
        help_text="Language requirements (e.g., {'english': 'TOEFL 90+', 'german': 'B2'})"
    )
    eligible_degrees = models.JSONField(
        default=list,
        help_text="List of eligible degree programs"
    )
    eligible_years = models.JSONField(
        default=list,
        help_text="List of eligible academic years (e.g., [2, 3, 4])"
    )
    student_semesters_remaining_after_exchange = models.JSONField(
        default=list,
        help_text="Minimum semesters a student must have after the exchange in their host university"
    )
