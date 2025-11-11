"""
Application Forms Services

Business logic for form rendering and submission processing.
"""

from django import forms
from django.core.exceptions import ValidationError

from .models import FormSubmission


class DynamicFormFromSchema(forms.Form):
    """
    Dynamic form class that creates form fields based on a FormType schema.

    This is used to render forms in templates when you have a FormType instance
    and want to create a standard Django form from its schema.
    """

    def __init__(self, form_type, *args, **kwargs):
        """
        Initialize the form with a FormType instance.

        Args:
            form_type: FormType instance with schema definition
        """
        super().__init__(*args, **kwargs)
        self.form_type = form_type
        self._build_fields_from_schema()

    def _build_fields_from_schema(self):
        """Build form fields from the FormType schema."""
        if not self.form_type or not self.form_type.schema:
            return

        schema = self.form_type.schema
        properties = schema.get('properties', {})
        required_fields = schema.get('required', [])

        for field_name, field_config in properties.items():
            field_type = field_config.get('type', 'string')
            field_title = field_config.get('title', field_name)
            field_help = field_config.get('description', '')
            is_required = field_name in required_fields

            # Create appropriate Django form field based on JSON schema type
            if field_type == 'string':
                field_format = field_config.get('format')

                if field_format == 'email':
                    field_class = forms.EmailField
                elif field_format == 'url':
                    field_class = forms.URLField
                elif field_format == 'date':
                    field_class = forms.DateField
                elif field_format == 'datetime':
                    field_class = forms.DateTimeField
                elif field_config.get('enum'):
                    # For enum, use ChoiceField
                    field_class = forms.ChoiceField
                    choices = [(val, val) for val in field_config.get('enum', [])]
                    self.fields[field_name] = field_class(
                        label=field_title,
                        help_text=field_help,
                        required=is_required,
                        choices=choices
                    )
                    continue
                else:
                    # Check for maxLength to determine if we need a textarea
                    max_length = field_config.get('maxLength', 200)
                    if max_length > 200:
                        field_class = forms.CharField
                        self.fields[field_name] = field_class(
                            label=field_title,
                            help_text=field_help,
                            required=is_required,
                            max_length=max_length,
                            widget=forms.Textarea(attrs={'rows': 4})
                        )
                        continue
                    else:
                        field_class = forms.CharField

            elif field_type == 'number' or field_type == 'integer':
                field_class = forms.IntegerField if field_type == 'integer' else forms.FloatField
                min_value = field_config.get('minimum')
                max_value = field_config.get('maximum')
                self.fields[field_name] = field_class(
                    label=field_title,
                    help_text=field_help,
                    required=is_required,
                    min_value=min_value,
                    max_value=max_value
                )
                continue

            elif field_type == 'boolean':
                field_class = forms.BooleanField

            elif field_type == 'array':
                # For arrays, use MultipleChoiceField
                field_class = forms.MultipleChoiceField
                items = field_config.get('items', {})
                choices = [(val, val) for val in items.get('enum', [])]
                self.fields[field_name] = field_class(
                    label=field_title,
                    help_text=field_help,
                    required=is_required,
                    choices=choices
                )
                continue

            else:
                # Default to CharField for unknown types
                field_class = forms.CharField

            # Create the field
            self.fields[field_name] = field_class(
                label=field_title,
                help_text=field_help,
                required=is_required
            )


class FormSubmissionService:
    """
    Service for handling form submission logic.
    """

    @staticmethod
    def create_submission(form_type, submitted_by, responses, program=None, application=None):
        """
        Create a new form submission.

        Args:
            form_type: FormType instance
            submitted_by: User instance
            responses: Dict of form responses
            program: Optional Program instance
            application: Optional Application instance

        Returns:
            FormSubmission instance

        Raises:
            ValidationError: If validation fails
        """
        submission = FormSubmission(
            form_type=form_type,
            submitted_by=submitted_by,
            responses=responses,
            program=program,
            application=application
        )

        # Run model validation
        submission.full_clean()
        submission.save()

        return submission

    @staticmethod
    def validate_responses(form_type, responses):
        """
        Validate form responses against the schema.

        Args:
            form_type: FormType instance
            responses: Dict of responses to validate

        Returns:
            True if valid

        Raises:
            ValidationError: If validation fails
        """
        if not form_type.schema:
            return True

        schema = form_type.schema
        properties = schema.get('properties', {})
        required_fields = schema.get('required', [])

        # Check required fields
        missing_fields = [field for field in required_fields if field not in responses]
        if missing_fields:
            raise ValidationError(f'Missing required fields: {", ".join(missing_fields)}')

        # Validate field types (basic validation)
        for field_name, value in responses.items():
            if field_name not in properties:
                continue  # Allow extra fields

            field_config = properties[field_name]
            field_type = field_config.get('type')

            # Type validation
            if field_type == 'string' and not isinstance(value, str):
                raise ValidationError(f'{field_name} must be a string')
            elif field_type == 'number' and not isinstance(value, (int, float)):
                raise ValidationError(f'{field_name} must be a number')
            elif field_type == 'integer' and not isinstance(value, int):
                raise ValidationError(f'{field_name} must be an integer')
            elif field_type == 'boolean' and not isinstance(value, bool):
                raise ValidationError(f'{field_name} must be a boolean')
            elif field_type == 'array' and not isinstance(value, list):
                raise ValidationError(f'{field_name} must be an array')

        return True

    @staticmethod
    def get_user_submissions(user, form_type=None, program=None):
        """
        Get submissions for a specific user.

        Args:
            user: User instance
            form_type: Optional FormType to filter by
            program: Optional Program to filter by

        Returns:
            QuerySet of FormSubmission instances
        """
        queryset = FormSubmission.objects.filter(submitted_by=user)

        if form_type:
            queryset = queryset.filter(form_type=form_type)

        if program:
            queryset = queryset.filter(program=program)

        return queryset.order_by('-submitted_at')

