import json

from django import forms
from django.core.exceptions import ValidationError

from ..models import Exchange, FormStep, FormSubmission


class DynamicForm(forms.Form):
    """Dynamically generated form based on FormStep configuration"""

    def __init__(self, *args, **kwargs):
        self.step = kwargs.pop("step")
        self.exchange = kwargs.pop("exchange", None)
        super().__init__(*args, **kwargs)

        # Build fields based on step configuration
        for field_config in self.step.fields:
            field_type = field_config.get("type", "text")
            field_name = field_config.get("name")
            field_label = field_config.get("label", field_name)
            required = field_config.get("required", False)

            # Create appropriate field based on type
            if field_type == "text":
                field = forms.CharField(
                    label=field_label,
                    required=required,
                    max_length=field_config.get("max_length", 255),
                )
            elif field_type == "email":
                field = forms.EmailField(label=field_label, required=required)
            elif field_type == "date":
                field = forms.DateField(
                    label=field_label,
                    required=required,
                    widget=forms.DateInput(attrs={"type": "date"}),
                )
            elif field_type == "choice":
                choices = [(c["value"], c["label"]) for c in field_config.get("choices", [])]
                field = forms.ChoiceField(label=field_label, required=required, choices=choices)
            elif field_type == "textarea":
                field = forms.CharField(
                    label=field_label,
                    required=required,
                    widget=forms.Textarea(attrs={"rows": field_config.get("rows", 4)}),
                )
            elif field_type == "file":
                field = forms.FileField(
                    label=field_label,
                    required=required,
                    help_text=field_config.get("help_text", ""),
                )
            elif field_type == "boolean":
                field = forms.BooleanField(
                    label=field_label,
                    required=False,  # Checkboxes are typically not required
                )
            else:
                continue  # Skip unknown field types

            # Add help text if provided
            if "help_text" in field_config:
                field.help_text = field_config["help_text"]

            # Add CSS classes
            if "css_class" in field_config:
                field.widget.attrs["class"] = field_config["css_class"]

            self.fields[field_name] = field


class FormService:
    """Service for handling multi-step forms"""

    @staticmethod
    def get_form_steps(active_only=True):
        """Get all form steps"""
        steps = FormStep.objects.all()
        if active_only:
            steps = steps.filter(is_active=True)
        return steps.order_by("order")

    @staticmethod
    def get_current_step(exchange):
        """Get the current step for an exchange"""
        # Find the first incomplete step
        steps = FormService.get_form_steps()

        for step in steps:
            submission = FormSubmission.objects.filter(exchange=exchange, step=step).first()

            if not submission or not submission.is_complete:
                return step

        # All steps complete, return last step
        return steps.last()

    @staticmethod
    def get_step_progress(exchange):
        """Get progress information for all steps"""
        steps = FormService.get_form_steps()
        progress = []

        for step in steps:
            submission = FormSubmission.objects.filter(exchange=exchange, step=step).first()

            progress.append(
                {
                    "step": step,
                    "is_complete": submission.is_complete if submission else False,
                    "data": submission.data if submission else {},
                }
            )

        return progress

    @staticmethod
    def save_step_data(exchange, step, data, is_complete=False):
        """Save data for a form step"""
        submission, created = FormSubmission.objects.get_or_create(exchange=exchange, step=step, defaults={"data": {}})

        # Update data
        submission.data.update(data)
        submission.is_complete = is_complete
        submission.save()

        # Update exchange fields if mapped
        FormService._update_exchange_fields(exchange, step, data)

        return submission

    @staticmethod
    def _update_exchange_fields(exchange, step, data):
        """Update exchange model fields based on form data"""
        # Map form fields to exchange model fields
        field_mapping = {
            "first_name": "first_name",
            "last_name": "last_name",
            "email": "email",
            "phone": "phone",
            "date_of_birth": "date_of_birth",
            "university": "university",
            "program": "program",
            "destination_university": "destination_university",
            "destination_country": "destination_country",
            "start_date": "start_date",
            "end_date": "end_date",
        }

        updated = False
        for form_field, model_field in field_mapping.items():
            if form_field in data:
                setattr(exchange, model_field, data[form_field])
                updated = True

        if updated:
            exchange.save()

    @staticmethod
    def validate_step(exchange, step, data):
        """Validate data for a specific step"""
        form = DynamicForm(data=data, step=step, exchange=exchange)
        return form.is_valid(), form.errors

    @staticmethod
    def get_next_step(current_step):
        """Get the next step after current step"""
        return FormStep.objects.filter(order__gt=current_step.order, is_active=True).order_by("order").first()

    @staticmethod
    def get_previous_step(current_step):
        """Get the previous step before current step"""
        return FormStep.objects.filter(order__lt=current_step.order, is_active=True).order_by("-order").first()

    @staticmethod
    def is_form_complete(exchange):
        """Check if all form steps are complete"""
        steps = FormService.get_form_steps()

        for step in steps:
            submission = FormSubmission.objects.filter(exchange=exchange, step=step).first()

            if not submission or not submission.is_complete:
                return False

        return True

    @staticmethod
    def create_default_steps():
        """Create default form steps for initial setup"""
        default_steps = [
            {
                "name": "personal_info",
                "title": "Personal Information",
                "description": "Basic personal details",
                "order": 1,
                "fields": [
                    {
                        "name": "first_name",
                        "type": "text",
                        "label": "First Name",
                        "required": True,
                    },
                    {
                        "name": "last_name",
                        "type": "text",
                        "label": "Last Name",
                        "required": True,
                    },
                    {
                        "name": "email",
                        "type": "email",
                        "label": "Email",
                        "required": True,
                    },
                    {
                        "name": "phone",
                        "type": "text",
                        "label": "Phone Number",
                        "required": False,
                    },
                    {
                        "name": "date_of_birth",
                        "type": "date",
                        "label": "Date of Birth",
                        "required": True,
                    },
                ],
            },
            {
                "name": "academic_info",
                "title": "Academic Information",
                "description": "Current academic status",
                "order": 2,
                "fields": [
                    {
                        "name": "university",
                        "type": "text",
                        "label": "Current University",
                        "required": True,
                    },
                    {
                        "name": "program",
                        "type": "text",
                        "label": "Study Program",
                        "required": True,
                    },
                    {
                        "name": "current_semester",
                        "type": "text",
                        "label": "Current Semester",
                        "required": True,
                    },
                    {
                        "name": "academic_year",
                        "type": "text",
                        "label": "Academic Year",
                        "required": True,
                    },
                ],
            },
            {
                "name": "exchange_details",
                "title": "Exchange Details",
                "description": "Information about your exchange",
                "order": 3,
                "fields": [
                    {
                        "name": "destination_university",
                        "type": "text",
                        "label": "Destination University",
                        "required": True,
                    },
                    {
                        "name": "destination_country",
                        "type": "text",
                        "label": "Destination Country",
                        "required": True,
                    },
                    {
                        "name": "start_date",
                        "type": "date",
                        "label": "Start Date",
                        "required": True,
                    },
                    {
                        "name": "end_date",
                        "type": "date",
                        "label": "End Date",
                        "required": True,
                    },
                ],
            },
            {
                "name": "documents",
                "title": "Document Upload",
                "description": "Upload required documents",
                "order": 4,
                "fields": [
                    {
                        "name": "passport",
                        "type": "file",
                        "label": "Passport",
                        "required": True,
                        "help_text": "Upload a scan of your passport",
                    },
                    {
                        "name": "transcript",
                        "type": "file",
                        "label": "Academic Transcript",
                        "required": True,
                        "help_text": "Upload your latest academic transcript",
                    },
                    {
                        "name": "motivation_letter",
                        "type": "file",
                        "label": "Motivation Letter",
                        "required": True,
                        "help_text": "Upload your motivation letter",
                    },
                ],
            },
        ]

        for step_data in default_steps:
            FormStep.objects.get_or_create(name=step_data["name"], defaults=step_data)
