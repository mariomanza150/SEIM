"""
Application Forms Services

Business logic for form rendering and submission processing.
"""

from django import forms
from django.core.exceptions import ValidationError

from .models import FormSubmission
from .visibility import field_effective_visible


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
    def _is_missing_or_empty(field_config, value):
        if value is None:
            return True
        field_type = field_config.get('type', 'string')
        if field_type == 'boolean':
            return False
        if field_type == 'array':
            return not isinstance(value, list) or len(value) == 0
        if field_type in ('number', 'integer'):
            return value == ''
        if isinstance(value, str):
            return value.strip() == ''
        return False

    @staticmethod
    def _validate_response_field_type(field_name, field_config, value):
        field_type = field_config.get('type')

        if field_type == 'string' and not isinstance(value, str):
            raise ValidationError(f'{field_name} must be a string')
        if field_type == 'number' and not isinstance(value, (int, float)):
            raise ValidationError(f'{field_name} must be a number')
        if field_type == 'integer' and not isinstance(value, int):
            raise ValidationError(f'{field_name} must be an integer')
        if field_type == 'boolean' and not isinstance(value, bool):
            raise ValidationError(f'{field_name} must be a boolean')
        if field_type == 'array' and not isinstance(value, list):
            raise ValidationError(f'{field_name} must be an array')

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
    def validate_responses(form_type, responses, *, visibility_context=None):
        """
        Validate form responses against the schema.

        Args:
            form_type: FormType instance
            responses: Dict of responses to validate
            visibility_context: Optional dict (program_id, has_assigned_coordinator) for rules

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
        vctx = visibility_context

        missing_fields = []
        for field in required_fields:
            if field not in properties:
                continue
            if not field_effective_visible(form_type, field, responses, vctx):
                continue
            if field not in responses or FormSubmissionService._is_missing_or_empty(
                properties[field], responses[field]
            ):
                missing_fields.append(field)
        if missing_fields:
            raise ValidationError(f'Missing required fields: {", ".join(missing_fields)}')

        for field_name, value in responses.items():
            if field_name not in properties:
                continue

            field_config = properties[field_name]
            if not field_effective_visible(form_type, field_name, responses, vctx):
                continue
            FormSubmissionService._validate_response_field_type(field_name, field_config, value)

        return True

    @staticmethod
    def validate_step_patch(
        form_type,
        patch_dict,
        step_field_names,
        *,
        merged_responses=None,
        visibility_context=None,
    ):
        """
        Validate a partial update for one step: keys must belong to the step, types must match,
        and schema-required fields for that step must be present in patch_dict with non-empty values.
        ``merged_responses`` is the full response object (existing + patch) for visibility rules.
        """
        if not form_type.schema:
            return True

        schema = form_type.schema
        properties = schema.get('properties', {})
        required_fields = set(schema.get('required', []))
        step_set = set(step_field_names)
        merged = merged_responses if merged_responses is not None else patch_dict
        vctx = visibility_context

        for field_name in patch_dict:
            if field_name not in step_set:
                raise ValidationError(f'Field "{field_name}" is not part of this step.')
            if field_name not in properties:
                raise ValidationError(f'Unknown field "{field_name}".')

        for field_name, value in patch_dict.items():
            field_config = properties[field_name]
            if field_effective_visible(form_type, field_name, merged, vctx):
                FormSubmissionService._validate_response_field_type(field_name, field_config, value)

        step_required = []
        for f in step_field_names:
            if f not in required_fields or f not in properties:
                continue
            if not field_effective_visible(form_type, f, merged, vctx):
                continue
            step_required.append(f)
        missing = []
        for field_name in step_required:
            if field_name not in patch_dict:
                missing.append(field_name)
                continue
            if FormSubmissionService._is_missing_or_empty(properties[field_name], patch_dict[field_name]):
                missing.append(field_name)
        if missing:
            raise ValidationError(f'Missing required fields for this step: {", ".join(missing)}')

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

