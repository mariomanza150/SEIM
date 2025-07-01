
# forms/student_profile_form.py
from django import forms
from django.core.exceptions import ValidationError
from datetime import date

from ...models import StudentProfile
from .base import BaseProfileForm
from ..form_widgets import BootstrapWidgets
from ..form_utils import update_if_not_empty


class StudentProfileForm(BaseProfileForm):
    class Meta(BaseProfileForm.Meta):
        model = StudentProfile
        fields = [
            "student_id",
            "institution",
            "degree",
            "academic_level",
            "university",
            "date_of_birth",
            "gender",
            "phone",
            "address",
            "city",
            "country",
        ]
        widgets = {
            "student_id": BootstrapWidgets.text_input(placeholder="Student ID"),
            "institution": BootstrapWidgets.text_input(placeholder="Institution"),
            "degree": BootstrapWidgets.text_input(placeholder="Degree"),
            "academic_level": BootstrapWidgets.text_input(placeholder="Academic Level"),
            "university": BootstrapWidgets.text_input(placeholder="University"),
            "date_of_birth": BootstrapWidgets.date_input(),
            "gender": BootstrapWidgets.select(),
            "phone": BootstrapWidgets.text_input(placeholder="Phone"),
            "address": BootstrapWidgets.text_input(placeholder="Address"),
            "city": BootstrapWidgets.text_input(placeholder="City"),
            "country": BootstrapWidgets.text_input(placeholder="Country"),
        }

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get("date_of_birth")
        if dob and dob > date.today():
            raise ValidationError("Date of birth cannot be in the future.")
        return dob

    def clean(self):
        cleaned_data = super().clean()
        if any([cleaned_data.get("address"), cleaned_data.get("city"), cleaned_data.get("country")]) and not all([
            cleaned_data.get("address"), cleaned_data.get("city"), cleaned_data.get("country")
        ]):
            raise ValidationError("Address, city, and country must all be filled together.")
        return cleaned_data

    def save(self, commit=True):
        profile = super().save(commit=False)
        for field in self.Meta.fields:
            update_if_not_empty(profile, field, self.cleaned_data.get(field))
        if commit:
            self.save_user_fields(profile.user)
            profile.save()
        return profile
