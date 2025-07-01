"""
Common form widget configurations for SEIM forms.

This module provides reusable widget configurations with Bootstrap styling
to maintain consistency across all forms in the application.
"""

from django import forms


class BootstrapWidgets:
    """
    Collection of pre-configured Bootstrap-styled widgets for forms.
    """

    @staticmethod
    def text_input(placeholder="", **kwargs):
        """Bootstrap-styled text input widget."""
        attrs = {
            "class": "form-control",
            "placeholder": placeholder,
        }
        attrs.update(kwargs)
        return forms.TextInput(attrs=attrs)

    @staticmethod
    def email_input(placeholder="Email", **kwargs):
        """Bootstrap-styled email input widget."""
        attrs = {
            "class": "form-control",
            "placeholder": placeholder,
        }
        attrs.update(kwargs)
        return forms.EmailInput(attrs=attrs)

    @staticmethod
    def password_input(placeholder="Password", **kwargs):
        """Bootstrap-styled password input widget."""
        attrs = {
            "class": "form-control",
            "placeholder": placeholder,
        }
        attrs.update(kwargs)
        return forms.PasswordInput(attrs=attrs)

    @staticmethod
    def textarea(placeholder="", rows=3, **kwargs):
        """Bootstrap-styled textarea widget."""
        attrs = {
            "class": "form-control",
            "placeholder": placeholder,
            "rows": rows,
        }
        attrs.update(kwargs)
        return forms.Textarea(attrs=attrs)

    @staticmethod
    def select(**kwargs):
        """Bootstrap-styled select widget."""
        attrs = {
            "class": "form-select",
        }
        attrs.update(kwargs)
        return forms.Select(attrs=attrs)

    @staticmethod
    def date_input(**kwargs):
        """Bootstrap-styled date input widget."""
        attrs = {
            "class": "form-control",
            "type": "date",
        }
        attrs.update(kwargs)
        return forms.DateInput(attrs=attrs)

    @staticmethod
    def number_input(step="1", min_val=None, max_val=None, **kwargs):
        """Bootstrap-styled number input widget."""
        attrs = {
            "class": "form-control",
            "step": step,
        }
        if min_val is not None:
            attrs["min"] = str(min_val)
        if max_val is not None:
            attrs["max"] = str(max_val)
        attrs.update(kwargs)
        return forms.NumberInput(attrs=attrs)


# Commonly used widget configurations
COMMON_WIDGETS = {
    "text": BootstrapWidgets.text_input,
    "email": BootstrapWidgets.email_input,
    "password": BootstrapWidgets.password_input,
    "textarea": BootstrapWidgets.textarea,
    "select": BootstrapWidgets.select,
    "date": BootstrapWidgets.date_input,
    "number": BootstrapWidgets.number_input,
}
