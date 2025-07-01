"""
Authentication forms for the SEIM application.

This module contains forms related to user authentication including
login and registration forms with Bootstrap styling.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from ..models import UserProfile
from .form_widgets import BootstrapWidgets


class LoginForm(AuthenticationForm):
    """
    Custom login form with Bootstrap styling.

    Extends Django's AuthenticationForm with consistent Bootstrap styling
    and custom placeholders for better user experience.
    """

    username = forms.CharField(
        widget=BootstrapWidgets.text_input(placeholder="Username")
    )
    password = forms.CharField(
        widget=BootstrapWidgets.password_input(placeholder="Password")
    )


class RegistrationForm(UserCreationForm):
    """
    Custom registration form with additional fields and Bootstrap styling.

    Extends Django's UserCreationForm to include additional user information
    and create associated UserProfile records automatically.
    """

    email = forms.EmailField(
        required=True, widget=BootstrapWidgets.email_input(placeholder="Email")
    )
    first_name = forms.CharField(
        required=False, widget=BootstrapWidgets.text_input(placeholder="First Name")
    )
    last_name = forms.CharField(
        required=False, widget=BootstrapWidgets.text_input(placeholder="Last Name")
    )
    institution = forms.CharField(
        required=False,
        widget=BootstrapWidgets.text_input(placeholder="Institution/University"),
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Apply Bootstrap styling to password fields
        for fieldname in ["username", "password1", "password2"]:
            self.fields[fieldname].widget.attrs["class"] = "form-control"

    def save(self, commit=True):
        """
        Save the user and create associated UserProfile.

        Args:
            commit: Whether to save the user to the database

        Returns:
            User: The created user instance
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data.get("first_name", "")
        user.last_name = self.cleaned_data.get("last_name", "")

        if commit:
            user.save()
            # Get or update user profile instead of creating a new one
            # (The signal will create it if it doesn't exist)
            profile, created = UserProfile.objects.get_or_create(user=user)
            # Update the profile with form data
            profile.institution = self.cleaned_data.get("institution", "")
            profile.role = "STUDENT"  # Default role
            profile.save()

        return user
