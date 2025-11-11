from django import forms

from .models import Program


class ProgramForm(forms.ModelForm):
    # Add proper widgets for better UX
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        help_text="Start date of the exchange program"
    )

    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        help_text="End date of the exchange program"
    )

    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Name of the exchange program"
    )

    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        help_text="Detailed description of the program"
    )

    min_gpa = forms.FloatField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.0', 'max': '4.0'}),
        required=False,
        help_text="Minimum GPA required for eligibility"
    )

    required_language = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
        help_text="Required language for eligibility"
    )

    is_active = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        required=False,
        initial=True,
        help_text="Whether this program is currently active"
    )

    recurring = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        required=False,
        initial=False,
        help_text="Is this program recurring (e.g., every semester)?"
    )

    application_form = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Select a dynamic application form for this program (optional)"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Import here to avoid circular imports
        try:
            from application_forms.models import FormType
            self.fields['application_form'].queryset = FormType.objects.filter(
                is_active=True,
                form_type__in=['application', 'custom']
            )
        except ImportError:
            # If application_forms is not available, hide the field
            del self.fields['application_form']
        except Exception as e:
            # If there's any other error, log it but hide the field
            print(f"Error loading application forms: {e}")
            if 'application_form' in self.fields:
                del self.fields['application_form']

    class Meta:
        model = Program
        fields = [
            'name', 'description', 'start_date', 'end_date', 'is_active',
            'min_gpa', 'required_language', 'recurring', 'application_form'
        ]
