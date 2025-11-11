"""
Application Forms Models

This module provides custom form type and submission tracking models
that work alongside the official django-dynforms package.

Note: This app is separate from the 'dynforms' package to avoid namespace conflicts.
The official django-dynforms package provides the form builder UI, while this app
provides custom models for tracking form definitions and submissions specific to
SEIM's exchange program workflow.
"""

import json

from django.core.exceptions import ValidationError
from django.db import models


class FormType(models.Model):
    """
    Defines the structure and configuration of a dynamic form.

    This model stores custom form schemas for exchange program applications,
    surveys, feedback forms, etc. It works alongside the official django-dynforms
    package by providing additional metadata and program-specific features.
    """
    FORM_TYPE_CHOICES = [
        ('application', 'Exchange Application'),
        ('survey', 'Survey'),
        ('feedback', 'Feedback'),
        ('custom', 'Custom Form'),
    ]

    name = models.CharField(
        max_length=200,
        help_text="Display name for the form"
    )
    form_type = models.CharField(
        max_length=50,
        choices=FORM_TYPE_CHOICES,
        default='application',
        help_text="The purpose/type of this form"
    )
    description = models.TextField(
        blank=True,
        help_text="Optional description of the form"
    )
    schema = models.JSONField(
        help_text="JSON schema defining field structure",
        default=dict,
        blank=True
    )
    ui_schema = models.JSONField(
        help_text="UI schema for form rendering (optional)",
        default=dict,
        blank=True
    )

    # Meta fields
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_application_forms'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Application Form Type'
        verbose_name_plural = 'Application Form Types'
        app_label = 'application_forms'

    def __str__(self):
        return f"{self.name} ({self.get_form_type_display()})"

    def clean(self):
        """Validate the form schema"""
        if self.schema:
            try:
                # Basic validation to ensure it's valid JSON
                json.dumps(self.schema)
            except (TypeError, ValueError) as e:
                raise ValidationError(f'Invalid JSON schema: {str(e)}')

    def get_field_count(self):
        """Return the number of fields in the form schema"""
        if not self.schema:
            return 0
        properties = self.schema.get('properties', {})
        return len(properties)

    def get_required_fields(self):
        """Return list of required field names"""
        if not self.schema:
            return []
        return self.schema.get('required', [])


class FormSubmission(models.Model):
    """
    Stores individual form submissions with responses.

    This model captures user responses to custom forms and links them
    to exchange programs and applications for tracking and analysis.
    """
    form_type = models.ForeignKey(
        FormType,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    submitted_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='application_form_submissions'
    )

    # Store responses as JSON
    responses = models.JSONField(
        help_text="JSON object containing the form responses",
        default=dict
    )

    # Meta fields
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Optional: link to exchange programs and applications
    program = models.ForeignKey(
        'exchange.Program',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='form_submissions'
    )
    application = models.ForeignKey(
        'exchange.Application',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='form_submissions',
        help_text="Link to the exchange application this form is part of"
    )

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Form Submission'
        verbose_name_plural = 'Form Submissions'
        app_label = 'application_forms'

    def __str__(self):
        return f"{self.form_type.name} - {self.submitted_by} ({self.submitted_at.date()})"

    def clean(self):
        """Validate the responses against the form schema"""
        if self.responses:
            try:
                json.dumps(self.responses)
            except (TypeError, ValueError) as e:
                raise ValidationError(f'Invalid JSON responses: {str(e)}')

        # Validate required fields if schema exists
        if self.form_type and self.form_type.schema:
            required_fields = self.form_type.get_required_fields()
            missing_fields = [field for field in required_fields if field not in self.responses]
            if missing_fields:
                raise ValidationError(
                    f'Missing required fields: {", ".join(missing_fields)}'
                )

    def get_response_count(self):
        """Return the number of fields with responses"""
        if not self.responses:
            return 0
        return len(self.responses)


# Utility validators for reuse
def validate_json_schema(value):
    """Validator for JSON schema fields"""
    try:
        if isinstance(value, str):
            json.loads(value)
        elif isinstance(value, dict):
            json.dumps(value)
        else:
            raise ValidationError('Schema must be a valid JSON object or string')
    except (TypeError, ValueError) as e:
        raise ValidationError(f'Invalid JSON: {str(e)}')


def validate_form_response(value):
    """Validator for form response data"""
    try:
        if isinstance(value, str):
            data = json.loads(value)
        elif isinstance(value, dict):
            data = value
        else:
            raise ValidationError('Response must be a valid JSON object or string')

        if not isinstance(data, dict):
            raise ValidationError('Form response must be a JSON object')
    except (TypeError, ValueError) as e:
        raise ValidationError(f'Invalid JSON response: {str(e)}')

