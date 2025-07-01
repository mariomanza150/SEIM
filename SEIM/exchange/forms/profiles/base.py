# forms/base_profile_form.py
from django import forms
from ...models.base import BaseProfile  # Abstract, used for field reuse
from ..form_widgets import BootstrapWidgets
from ..form_utils import update_if_not_empty


class BaseProfileForm(forms.ModelForm):
    """
    Abstract base form for profile models with common User fields.
    """
    first_name = forms.CharField(required=False, widget=BootstrapWidgets.text_input(placeholder="First Name"))
    last_name = forms.CharField(required=False, widget=BootstrapWidgets.text_input(placeholder="Last Name"))
    email = forms.EmailField(required=False, widget=BootstrapWidgets.email_input(placeholder="Email"))

    class Meta:
        model = BaseProfile  # Abstract base model
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields["first_name"].initial = self.instance.user.first_name
            self.fields["last_name"].initial = self.instance.user.last_name
            self.fields["email"].initial = self.instance.user.email

    def save_user_fields(self, user):
        update_if_not_empty(user, "first_name", self.cleaned_data.get("first_name"))
        update_if_not_empty(user, "last_name", self.cleaned_data.get("last_name"))
        update_if_not_empty(user, "email", self.cleaned_data.get("email"))
        user.save()