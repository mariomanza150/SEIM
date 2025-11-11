from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from core.models import TimeStampedModel, UUIDModel


class GradeScale(UUIDModel, TimeStampedModel):
    """Represents a grading system used by an institution or country."""

    name = models.CharField(
        max_length=255,
        help_text="Display name of the grading scale (e.g., 'US GPA 4.0 Scale')"
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique code for the scale (e.g., 'US_GPA_4', 'ECTS')"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the grading scale"
    )
    country = models.CharField(
        max_length=100,
        blank=True,
        help_text="Country or region where this scale is used"
    )
    min_value = models.FloatField(
        help_text="Minimum possible grade value in this scale"
    )
    max_value = models.FloatField(
        help_text="Maximum possible grade value in this scale"
    )
    passing_value = models.FloatField(
        help_text="Minimum grade value required to pass"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this scale is currently in use"
    )
    is_reverse_scale = models.BooleanField(
        default=False,
        help_text="True if lower values are better (e.g., German scale 1.0-5.0)"
    )

    class Meta:
        ordering = ['country', 'name']
        verbose_name = 'Grade Scale'
        verbose_name_plural = 'Grade Scales'
        indexes = [
            models.Index(fields=['code'], name='grade_scale_code_idx'),
            models.Index(fields=['is_active'], name='grade_scale_active_idx'),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"

    def clean(self):
        """Validate grade scale data."""
        if self.min_value >= self.max_value:
            raise ValidationError({
                'max_value': 'Maximum value must be greater than minimum value.'
            })
        if self.passing_value < self.min_value or self.passing_value > self.max_value:
            raise ValidationError({
                'passing_value': 'Passing value must be between min and max values.'
            })


class GradeValue(UUIDModel, TimeStampedModel):
    """Individual grade values within a scale with their numeric equivalents."""

    grade_scale = models.ForeignKey(
        GradeScale,
        on_delete=models.CASCADE,
        related_name='grade_values',
        help_text="The grade scale this value belongs to"
    )
    label = models.CharField(
        max_length=50,
        help_text="Grade label (e.g., 'A', '1.0', 'First Class')"
    )
    numeric_value = models.FloatField(
        help_text="Numeric representation within the scale"
    )
    gpa_equivalent = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(4.0)],
        help_text="Normalized 4.0 GPA equivalent for cross-scale comparison"
    )
    min_percentage = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Minimum percentage for this grade (optional)"
    )
    max_percentage = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Maximum percentage for this grade (optional)"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of what this grade represents"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order within the scale"
    )
    is_passing = models.BooleanField(
        default=True,
        help_text="Whether this grade is considered passing"
    )

    class Meta:
        ordering = ['grade_scale', 'order']
        verbose_name = 'Grade Value'
        verbose_name_plural = 'Grade Values'
        unique_together = [['grade_scale', 'label'], ['grade_scale', 'numeric_value']]
        indexes = [
            models.Index(fields=['grade_scale', 'gpa_equivalent'], name='grade_val_gpa_idx'),
            models.Index(fields=['grade_scale', 'numeric_value'], name='grade_val_num_idx'),
        ]

    def __str__(self):
        return f"{self.grade_scale.code}: {self.label} ({self.gpa_equivalent} GPA)"

    def clean(self):
        """Validate grade value data."""
        if self.grade_scale:
            if self.numeric_value < self.grade_scale.min_value or \
               self.numeric_value > self.grade_scale.max_value:
                raise ValidationError({
                    'numeric_value': f'Value must be between {self.grade_scale.min_value} '
                                   f'and {self.grade_scale.max_value} for this scale.'
                })

        if self.min_percentage is not None and self.max_percentage is not None:
            if self.min_percentage >= self.max_percentage:
                raise ValidationError({
                    'max_percentage': 'Maximum percentage must be greater than minimum percentage.'
                })


class GradeTranslation(UUIDModel, TimeStampedModel):
    """Direct translation mappings between specific grades in different scales."""

    source_grade = models.ForeignKey(
        GradeValue,
        on_delete=models.CASCADE,
        related_name='translations_from',
        help_text="Source grade value"
    )
    target_grade = models.ForeignKey(
        GradeValue,
        on_delete=models.CASCADE,
        related_name='translations_to',
        help_text="Target grade value"
    )
    confidence = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Confidence level of this translation (0.0-1.0)"
    )
    notes = models.TextField(
        blank=True,
        help_text="Translation notes or rationale"
    )
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who created this translation mapping"
    )

    class Meta:
        verbose_name = 'Grade Translation'
        verbose_name_plural = 'Grade Translations'
        unique_together = [['source_grade', 'target_grade']]
        indexes = [
            models.Index(fields=['source_grade'], name='grade_trans_src_idx'),
            models.Index(fields=['target_grade'], name='grade_trans_tgt_idx'),
        ]

    def __str__(self):
        return f"{self.source_grade.label} ({self.source_grade.grade_scale.code}) → " \
               f"{self.target_grade.label} ({self.target_grade.grade_scale.code})"

    def clean(self):
        """Validate translation mapping."""
        if self.source_grade and self.target_grade:
            if self.source_grade.grade_scale == self.target_grade.grade_scale:
                raise ValidationError(
                    'Source and target grades must be from different scales.'
                )
