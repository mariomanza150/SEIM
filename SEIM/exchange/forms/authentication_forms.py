"""
Authentication forms for the SEIM application.

This module contains forms related to user authentication including
login and registration forms with Bootstrap styling.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re

from ..models import UserProfile
from .form_widgets import BootstrapWidgets


class LoginForm(AuthenticationForm):
    """
    Custom login form with Bootstrap styling and remember me functionality.
    """

    username = forms.CharField(widget=BootstrapWidgets.text_input(placeholder="Username"))
    password = forms.CharField(widget=BootstrapWidgets.password_input(placeholder="Password"))
    remember_me = forms.BooleanField(required=False)


class RegistrationForm(UserCreationForm):
    """
    Custom registration form with additional fields and enhanced validation.

    Extends Django's UserCreationForm to include additional user information
    and create associated UserProfile records automatically.
    """

    email = forms.EmailField(
        required=True,
        widget=BootstrapWidgets.email_input(placeholder="Email")
    )
    first_name = forms.CharField(
        required=True,
        widget=BootstrapWidgets.text_input(placeholder="First Name")
    )
    last_name = forms.CharField(
        required=True,
        widget=BootstrapWidgets.text_input(placeholder="Last Name")
    )
    institution = forms.CharField(
        required=True,
        widget=BootstrapWidgets.text_input(placeholder="Institution/University")
    )
    department = forms.CharField(
        required=False,
        widget=BootstrapWidgets.text_input(placeholder="Department")
    )
    password1 = forms.CharField(
        widget=BootstrapWidgets.password_input(placeholder="Password"),
        help_text="Password must include at least 8 characters with letters, numbers and symbols."
    )
    password2 = forms.CharField(
        widget=BootstrapWidgets.password_input(placeholder="Confirm Password")
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget = BootstrapWidgets.text_input(placeholder="Username")
        self.fields['username'].help_text = "Letters, digits and @.+-_ only. Maximum 150 characters."

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'[A-Za-z]', password):
            raise ValidationError("Password must contain at least one letter.")
        if not re.search(r'[0-9]', password):
            raise ValidationError("Password must contain at least one number.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError("Password must contain at least one symbol.")
        return password

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()
            # Create the associated profile with student role
            UserProfile.objects.create(
                user=user,
                role='STUDENT',
                institution=self.cleaned_data.get('institution', ''),
                department=self.cleaned_data.get('department', '')
            )
        return user
