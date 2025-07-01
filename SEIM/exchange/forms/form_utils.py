"""
Utility functions for SEIM forms.

This module contains helper functions and utilities that can be used
across multiple forms to reduce code duplication and improve maintainability.
"""

from django import forms


def update_if_not_empty(instance, attr, new_value):
    """
    Update an instance attribute only if the new value is not empty.

    Args:
        instance: The model instance to update
        attr: The attribute name to update
        new_value: The new value to set (if not empty)
    """
    if new_value not in [None, "", [], {}]:
        setattr(instance, attr, new_value)


def apply_bootstrap_styling(form_instance, excluded_fields=None):
    """
    Apply Bootstrap styling to all fields in a form.

    Args:
        form_instance: The form instance to style
        excluded_fields: List of field names to exclude from styling
    """
    excluded_fields = excluded_fields or []

    for field_name, field in form_instance.fields.items():
        if field_name not in excluded_fields:
            # Add Bootstrap classes based on widget type
            widget = field.widget
            if isinstance(widget, forms.TextInput):
                widget.attrs.update({"class": "form-control"})
            elif isinstance(widget, forms.EmailInput):
                widget.attrs.update({"class": "form-control"})
            elif isinstance(widget, forms.PasswordInput):
                widget.attrs.update({"class": "form-control"})
            elif isinstance(widget, forms.Textarea):
                widget.attrs.update({"class": "form-control"})
            elif isinstance(widget, forms.Select):
                widget.attrs.update({"class": "form-select"})
            elif isinstance(widget, forms.NumberInput):
                widget.attrs.update({"class": "form-control"})
            elif isinstance(widget, forms.DateInput):
                widget.attrs.update({"class": "form-control"})


def validate_word_count(text, min_words=0, max_words=None, field_name="text"):
    """
    Validate that text meets word count requirements.

    Args:
        text: The text to validate
        min_words: Minimum required word count
        max_words: Maximum allowed word count (optional)
        field_name: Name of the field for error messages

    Returns:
        The validated text

    Raises:
        ValidationError: If word count requirements are not met
    """
    if not text:
        word_count = 0
    else:
        word_count = len(text.split())

    if min_words > 0 and word_count < min_words:
        raise forms.ValidationError(
            f"{field_name.title()} must be at least {min_words} words. " f"Current count: {word_count} words."
        )

    if max_words and word_count > max_words:
        raise forms.ValidationError(
            f"{field_name.title()} must be no more than {max_words} words. " f"Current count: {word_count} words."
        )

    return text


def validate_date_range(start_date, end_date, start_field="start_date", end_field="end_date"):
    """
    Validate that end date is after start date.

    Args:
        start_date: The start date
        end_date: The end date
        start_field: Name of start date field for error messages
        end_field: Name of end date field for error messages

    Raises:
        ValidationError: If end date is not after start date
    """
    if start_date and end_date and end_date <= start_date:
        raise forms.ValidationError(
            f'{end_field.replace("_", " ").title()} must be after {start_field.replace("_", " ").title()}.'
        )


def populate_user_fields(form_instance, user, field_mapping=None):
    """
    Populate form fields with user data.

    Args:
        form_instance: The form instance to populate
        user: The user object
        field_mapping: Optional dict mapping form fields to user attributes
    """
    if not user:
        return

    # Default field mapping
    default_mapping = {
        "first_name": "first_name",
        "last_name": "last_name",
        "email": "email",
        "contact_email": "email",
        "username": "username",
    }

    field_mapping = field_mapping or default_mapping

    for form_field, user_attr in field_mapping.items():
        if form_field in form_instance.fields:
            value = getattr(user, user_attr, None)
            if value:
                form_instance.fields[form_field].initial = value
