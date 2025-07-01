
# forms/contact_profile_form.py
from django import forms
from ...models import ContactProfile
from ..form_widgets import BootstrapWidgets
from ..form_utils import update_if_not_empty


class ContactProfileForm(forms.ModelForm):
    class Meta:
        model = ContactProfile
        fields = [
            "university",
            "position",
            "phone",
            "office_phone",
            "address",
            "city",
            "country",
        ]
        widgets = {
            "university": BootstrapWidgets.text_input(placeholder="University"),
            "position": BootstrapWidgets.text_input(placeholder="Position"),
            "phone": BootstrapWidgets.text_input(placeholder="Phone"),
            "office_phone": BootstrapWidgets.text_input(placeholder="Office Phone"),
            "address": BootstrapWidgets.text_input(placeholder="Address"),
            "city": BootstrapWidgets.text_input(placeholder="City"),
            "country": BootstrapWidgets.text_input(placeholder="Country"),
        }

    def clean(self):
        cleaned_data = super().clean()
        if any([cleaned_data.get("address"), cleaned_data.get("city"), cleaned_data.get("country")]) and not all([
            cleaned_data.get("address"), cleaned_data.get("city"), cleaned_data.get("country")
        ]):
            raise forms.ValidationError("Address, city, and country must all be filled together.")
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        for field in self.Meta.fields:
            update_if_not_empty(instance, field, self.cleaned_data.get(field))
        if commit:
            instance.save()
        return instance
