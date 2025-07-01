"""
User profile forms for the SEIM application.

This module contains forms for managing user profiles including
profile updates and user information management.
"""

from django import forms

from ..models import UserProfile
from .form_utils import update_if_not_empty
from .form_widgets import BootstrapWidgets


class UserProfileForm(forms.ModelForm):
    """
    Form for updating user profile information.

    This form handles both User model fields (first_name, last_name, email)
    and UserProfile model fields, providing a unified interface for
    profile management.
    """

    # User model fields
    first_name = forms.CharField(
        required=False, widget=BootstrapWidgets.text_input(placeholder="First Name")
    )
    last_name = forms.CharField(
        required=False, widget=BootstrapWidgets.text_input(placeholder="Last Name")
    )
    email = forms.EmailField(
        required=False, widget=BootstrapWidgets.email_input(placeholder="Email")
    )

    # Additional profile fields
    student_id = forms.CharField(
        required=False, widget=BootstrapWidgets.text_input(placeholder="Student ID")
    )
    current_program = forms.CharField(
        required=False,
        widget=BootstrapWidgets.text_input(placeholder="Current Program"),
    )
    phone = forms.CharField(
        required=False, widget=BootstrapWidgets.text_input(placeholder="Phone Number")
    )
    date_of_birth = forms.DateField(
        required=False, widget=BootstrapWidgets.date_input()
    )
    gender = forms.ChoiceField(
        required=False,
        choices=UserProfile.GENDER_CHOICES,
        widget=BootstrapWidgets.select(),
    )
    address = forms.CharField(
        required=False, widget=BootstrapWidgets.text_input(placeholder="Street Address")
    )
    city = forms.CharField(
        required=False, widget=BootstrapWidgets.text_input(placeholder="City")
    )
    country = forms.CharField(
        required=False, widget=BootstrapWidgets.text_input(placeholder="Country")
    )

    class Meta:
        model = UserProfile
        fields = ["institution", "department", "position", "office_phone", "student_id"]
        widgets = {
            "institution": BootstrapWidgets.text_input(placeholder="Institution"),
            "department": BootstrapWidgets.text_input(placeholder="Department"),
            "position": BootstrapWidgets.text_input(placeholder="Position"),
            "office_phone": BootstrapWidgets.text_input(placeholder="Office Phone"),
            "student_id": BootstrapWidgets.text_input(placeholder="Student ID"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Pre-populate User model fields if instance exists
        if self.instance and self.instance.user:
            self.fields["first_name"].initial = self.instance.user.first_name
            self.fields["last_name"].initial = self.instance.user.last_name
            self.fields["email"].initial = self.instance.user.email
            self.fields["date_of_birth"].initial = self.instance.date_of_birth
            self.fields["phone"].initial = self.instance.phone
            self.fields["gender"].initial = self.instance.gender
            self.fields["address"].initial = self.instance.address
            self.fields["city"].initial = self.instance.city
            self.fields["country"].initial = self.instance.country
            self.fields["student_id"].initial = self.instance.student_id
            self.fields["current_program"].initial = self.instance.current_program

    def save(self, commit=True):
        """
        Save the profile with proper handling of User model fields.

        This method updates both the UserProfile instance and the
        associated User instance with form data.

        Args:
            commit: Whether to save the instances to the database

        Returns:
            UserProfile: The updated profile instance
        """
        profile = super().save(commit=False)

        # Update profile fields only if they have values
        update_if_not_empty(
            profile, "date_of_birth", self.cleaned_data.get("date_of_birth")
        )
        update_if_not_empty(profile, "phone", self.cleaned_data.get("phone"))
        update_if_not_empty(profile, "gender", self.cleaned_data.get("gender"))
        update_if_not_empty(profile, "address", self.cleaned_data.get("address"))
        update_if_not_empty(profile, "city", self.cleaned_data.get("city"))
        update_if_not_empty(profile, "country", self.cleaned_data.get("country"))
        update_if_not_empty(profile, "student_id", self.cleaned_data.get("student_id"))
        update_if_not_empty(
            profile, "current_program", self.cleaned_data.get("current_program")
        )

        if commit:
            # Update User model fields
            user = profile.user
            update_if_not_empty(user, "first_name", self.cleaned_data.get("first_name"))
            update_if_not_empty(user, "last_name", self.cleaned_data.get("last_name"))
            update_if_not_empty(user, "email", self.cleaned_data.get("email"))
            user.save()

            # Save the profile
            profile.save()

        return profile
