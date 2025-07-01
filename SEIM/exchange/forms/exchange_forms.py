"""
Fixed Exchange application forms for the SEIM application.

This module contains the corrected ExchangeForm with proper field mapping,
validation, and user data pre-population.
"""

from datetime import date

from django import forms
from django.core.exceptions import ValidationError

from ..models import Exchange
from .form_choices import COUNTRY_CHOICES


class ExchangeForm(forms.ModelForm):
    """
    Fixed ExchangeForm with proper field mapping to Exchange model.

    This form directly maps to Exchange model fields and handles
    proper validation, field mapping, and user data pre-population.
    """

    class Meta:
        model = Exchange
        fields = [
            "gpa",
            "exchange_program",
            "current_university",
            "current_program",
            "host_university",
            "current_year",
            "motivation_letter",
            "end_date",
            "special_requirements",
            "destination_country",
        ]

        widgets = {
            "gpa": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "max": "4.0",
                    "placeholder": "GPA (0.0 - 4.0)",
                }
            ),
            "host_university": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Host University",
                    "list": "universities",
                }
            ),
            "destination_country": forms.Select(attrs={"class": "form-select"}),
            "exchange_program": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Exchange Program",
                    "list": "programs",
                }
            ),
            "start_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "end_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "motivation_letter": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 6,
                    "placeholder": "Statement of Purpose (minimum 200 words)",
                }
            ),
            "special_requirements": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Any special requirements or accommodations needed",
                }
            ),
        }

        labels = {
            "gpa": "Current GPA",
            "host_university": "Host University *",
            "destination_country": "Host Country *",
            "exchange_program": "Exchange Program *",
            "start_date": "Start Date *",
            "end_date": "End Date *",
            "motivation_letter": "Statement of Purpose *",
            "special_requirements": "Special Requirements",
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Set country choices
        self.fields["destination_country"].choices = COUNTRY_CHOICES

        # Set current year choices
        self.fields["current_year"].choices = [("", "Choose year...")] + [(i, f"Year {i}") for i in range(1, 6)]

        # Pre-populate from user and profile if creating new exchange
        if not self.instance.pk and self.user:
            # Populate from user profile if it exists
            if hasattr(self.user, "profile"):
                profile = self.user.profile
                self.fields["current_university"].initial = getattr(profile, "institution", "")

        # Make required fields clearly marked
        required_fields = [
            "gpa",
            "host_university",
            "destination_country",
            "exchange_program",
            "start_date",
            "end_date",
            "motivation_letter",
        ]

        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True

    def clean_motivation_letter(self):
        """Validate that motivation letter has minimum word count."""
        motivation = self.cleaned_data.get("motivation_letter", "")
        if motivation:
            word_count = len(motivation.split())
            if word_count < 200:
                raise ValidationError(
                    f"Statement of purpose must be at least 200 words. " f"Current count: {word_count} words."
                )
        return motivation

    def clean_gpa(self):
        """Validate GPA is within acceptable range."""
        gpa = self.cleaned_data.get("gpa")
        if gpa is not None:
            if gpa < 0 or gpa > 4.0:
                raise ValidationError("GPA must be between 0.0 and 4.0")
        return gpa

    def clean(self):
        """Additional form validation for date ranges and field consistency."""
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        # Validate date range
        if start_date and end_date:
            if end_date <= start_date:
                raise ValidationError("End date must be after start date.")

            # Check that start date is not in the past
            if start_date < date.today():
                raise ValidationError("Start date cannot be in the past.")

            # Check reasonable duration (not more than 2 years)
            duration = (end_date - start_date).days
            if duration > 730:  # 2 years
                raise ValidationError("Exchange duration cannot exceed 2 years.")

        return cleaned_data

    def save(self, commit=True):
        exchange = super().save(commit=False)

        # Set the student to the current user
        if self.user:
            exchange.student = self.user

        if commit:
            exchange.save()

        return exchange
