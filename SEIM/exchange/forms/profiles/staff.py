# forms/staff_profile_form.py
from django import forms
from django.core.exceptions import ValidationError

from ...models import StaffProfile  # You must define this as BaseProfile + Contact fields
from .base import BaseProfileForm
from ..form_widgets import BootstrapWidgets
from ..form_utils import update_if_not_empty


class StaffProfileForm(BaseProfileForm):
    class Meta(BaseProfileForm.Meta):
        model = StaffProfile
        fields = [
            "university",
            "position",
            "role",
            "office_phone",
        ]
        widgets = {
            "university": BootstrapWidgets.text_input(placeholder="University"),
            "position": BootstrapWidgets.text_input(placeholder="Position"),
            "role": BootstrapWidgets.text_input(placeholder="Role"),
            "office_phone": BootstrapWidgets.text_input(placeholder="Office Phone"),
        }

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