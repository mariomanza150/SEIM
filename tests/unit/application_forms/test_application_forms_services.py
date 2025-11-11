"""
Test Application Forms Services

Comprehensive tests for form rendering and submission processing.
"""

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from accounts.models import Role
from application_forms.models import FormSubmission, FormType
from application_forms.services import DynamicFormFromSchema, FormSubmissionService
from exchange.models import Application, ApplicationStatus, Program

User = get_user_model()


@pytest.mark.django_db
class TestDynamicFormFromSchema(TestCase):
    """Test dynamic form generation from JSON schema."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123"
        )

    def test_empty_schema(self):
        """Test form with empty schema."""
        form_type = FormType.objects.create(
            name="Empty Form",
            form_type='custom',
            schema={}
        )
        
        form = DynamicFormFromSchema(form_type)
        
        # Should create form with no fields
        self.assertEqual(len(form.fields), 0)

    def test_string_field(self):
        """Test creating string field."""
        schema = {
            'properties': {
                'name': {
                    'type': 'string',
                    'title': 'Full Name',
                    'description': 'Enter your full name'
                }
            },
            'required': ['name']
        }
        
        form_type = FormType.objects.create(
            name="String Form",
            form_type='custom',
            schema=schema
        )
        
        form = DynamicFormFromSchema(form_type)
        
        self.assertIn('name', form.fields)
        self.assertEqual(form.fields['name'].label, 'Full Name')
        self.assertEqual(form.fields['name'].help_text, 'Enter your full name')
        self.assertTrue(form.fields['name'].required)

    def test_email_field(self):
        """Test creating email field."""
        schema = {
            'properties': {
                'email': {
                    'type': 'string',
                    'format': 'email',
                    'title': 'Email Address'
                }
            }
        }
        
        form_type = FormType.objects.create(
            name="Email Form",
            schema=schema
        )
        
        form = DynamicFormFromSchema(form_type)
        
        self.assertIn('email', form.fields)
        from django import forms
        self.assertIsInstance(form.fields['email'], forms.EmailField)

    def test_url_field(self):
        """Test creating URL field."""
        schema = {
            'properties': {
                'website': {
                    'type': 'string',
                    'format': 'url',
                    'title': 'Website'
                }
            }
        }
        
        form_type = FormType.objects.create(
            name="URL Form",
            schema=schema
        )
        
        form = DynamicFormFromSchema(form_type)
        
        from django import forms
        self.assertIsInstance(form.fields['website'], forms.URLField)

    def test_date_field(self):
        """Test creating date field."""
        schema = {
            'properties': {
                'birthdate': {
                    'type': 'string',
                    'format': 'date',
                    'title': 'Birth Date'
                }
            }
        }
        
        form_type = FormType.objects.create(
            name="Date Form",
            schema=schema
        )
        
        form = DynamicFormFromSchema(form_type)
        
        from django import forms
        self.assertIsInstance(form.fields['birthdate'], forms.DateField)

    def test_datetime_field(self):
        """Test creating datetime field."""
        schema = {
            'properties': {
                'appointment': {
                    'type': 'string',
                    'format': 'datetime',
                    'title': 'Appointment Time'
                }
            }
        }
        
        form_type = FormType.objects.create(
            name="DateTime Form",
            schema=schema
        )
        
        form = DynamicFormFromSchema(form_type)
        
        from django import forms
        self.assertIsInstance(form.fields['appointment'], forms.DateTimeField)

    def test_enum_field(self):
        """Test creating choice field from enum."""
        schema = {
            'properties': {
                'status': {
                    'type': 'string',
                    'enum': ['draft', 'submitted', 'approved'],
                    'title': 'Status'
                }
            }
        }
        
        form_type = FormType.objects.create(
            name="Enum Form",
            schema=schema
        )
        
        form = DynamicFormFromSchema(form_type)
        
        from django import forms
        self.assertIsInstance(form.fields['status'], forms.ChoiceField)
        self.assertEqual(len(form.fields['status'].choices), 3)

    def test_textarea_field(self):
        """Test creating textarea for long text."""
        schema = {
            'properties': {
                'description': {
                    'type': 'string',
                    'maxLength': 500,
                    'title': 'Description'
                }
            }
        }
        
        form_type = FormType.objects.create(
            name="Textarea Form",
            schema=schema
        )
        
        form = DynamicFormFromSchema(form_type)
        
        from django import forms
        self.assertIsInstance(form.fields['description'], forms.CharField)
        self.assertIsInstance(form.fields['description'].widget, forms.Textarea)

    def test_integer_field(self):
        """Test creating integer field."""
        schema = {
            'properties': {
                'age': {
                    'type': 'integer',
                    'minimum': 18,
                    'maximum': 100,
                    'title': 'Age'
                }
            }
        }
        
        form_type = FormType.objects.create(
            name="Integer Form",
            schema=schema
        )
        
        form = DynamicFormFromSchema(form_type)
        
        from django import forms
        self.assertIsInstance(form.fields['age'], forms.IntegerField)
        self.assertEqual(form.fields['age'].min_value, 18)
        self.assertEqual(form.fields['age'].max_value, 100)

    def test_number_field(self):
        """Test creating float number field."""
        schema = {
            'properties': {
                'gpa': {
                    'type': 'number',
                    'minimum': 0.0,
                    'maximum': 4.0,
                    'title': 'GPA'
                }
            }
        }
        
        form_type = FormType.objects.create(
            name="Number Form",
            schema=schema
        )
        
        form = DynamicFormFromSchema(form_type)
        
        from django import forms
        self.assertIsInstance(form.fields['gpa'], forms.FloatField)

    def test_boolean_field(self):
        """Test creating boolean field."""
        schema = {
            'properties': {
                'agreed': {
                    'type': 'boolean',
                    'title': 'I Agree'
                }
            }
        }
        
        form_type = FormType.objects.create(
            name="Boolean Form",
            schema=schema
        )
        
        form = DynamicFormFromSchema(form_type)
        
        from django import forms
        self.assertIsInstance(form.fields['agreed'], forms.BooleanField)

    def test_array_field(self):
        """Test creating multiple choice field from array."""
        schema = {
            'properties': {
                'interests': {
                    'type': 'array',
                    'items': {
                        'enum': ['sports', 'music', 'art', 'science']
                    },
                    'title': 'Interests'
                }
            }
        }
        
        form_type = FormType.objects.create(
            name="Array Form",
            schema=schema
        )
        
        form = DynamicFormFromSchema(form_type)
        
        from django import forms
        self.assertIsInstance(form.fields['interests'], forms.MultipleChoiceField)
        self.assertEqual(len(form.fields['interests'].choices), 4)

    def test_multiple_fields(self):
        """Test form with multiple fields of different types."""
        schema = {
            'properties': {
                'name': {'type': 'string', 'title': 'Name'},
                'email': {'type': 'string', 'format': 'email', 'title': 'Email'},
                'age': {'type': 'integer', 'title': 'Age'},
                'active': {'type': 'boolean', 'title': 'Active'}
            },
            'required': ['name', 'email']
        }
        
        form_type = FormType.objects.create(
            name="Multi Form",
            schema=schema
        )
        
        form = DynamicFormFromSchema(form_type)
        
        self.assertEqual(len(form.fields), 4)
        self.assertTrue(form.fields['name'].required)
        self.assertTrue(form.fields['email'].required)
        self.assertFalse(form.fields['age'].required)

    def test_none_form_type(self):
        """Test handling None form_type."""
        form = DynamicFormFromSchema(None)
        self.assertEqual(len(form.fields), 0)

    def test_form_type_without_schema(self):
        """Test form type with empty schema."""
        form_type = FormType.objects.create(
            name="No Schema",
            schema={}  # Empty dict, not None
        )
        
        form = DynamicFormFromSchema(form_type)
        self.assertEqual(len(form.fields), 0)


@pytest.mark.django_db
class TestFormSubmissionService(TestCase):
    """Test form submission service methods."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123"
        )
        
        self.schema = {
            'properties': {
                'name': {
                    'type': 'string',
                    'title': 'Name'
                },
                'email': {
                    'type': 'string',
                    'format': 'email',
                    'title': 'Email'
                },
                'age': {
                    'type': 'integer',
                    'title': 'Age'
                }
            },
            'required': ['name', 'email']
        }
        
        self.form_type = FormType.objects.create(
            name="Test Form",
            form_type='custom',
            schema=self.schema
        )

    def test_create_submission_success(self):
        """Test successful submission creation."""
        responses = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'age': 25
        }
        
        submission = FormSubmissionService.create_submission(
            form_type=self.form_type,
            submitted_by=self.user,
            responses=responses
        )
        
        self.assertIsNotNone(submission.id)
        self.assertEqual(submission.form_type, self.form_type)
        self.assertEqual(submission.submitted_by, self.user)
        self.assertEqual(submission.responses['name'], 'John Doe')

    def test_create_submission_with_program(self):
        """Test submission creation with program link."""
        program = Program.objects.create(
            name="Test Program",
            description="Test",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365),
            is_active=True
        )
        
        responses = {'name': 'John Doe', 'email': 'john@example.com'}
        
        submission = FormSubmissionService.create_submission(
            form_type=self.form_type,
            submitted_by=self.user,
            responses=responses,
            program=program
        )
        
        self.assertEqual(submission.program, program)

    def test_create_submission_with_application(self):
        """Test submission creation with application link."""
        student_role, _ = Role.objects.get_or_create(name="student")
        self.user.roles.add(student_role)
        
        program = Program.objects.create(
            name="Test Program",
            description="Test",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365),
            is_active=True
        )
        
        status, _ = ApplicationStatus.objects.get_or_create(
            name="draft",
            defaults={'order': 1}
        )
        
        application = Application.objects.create(
            student=self.user,
            program=program,
            status=status
        )
        
        responses = {'name': 'John Doe', 'email': 'john@example.com'}
        
        submission = FormSubmissionService.create_submission(
            form_type=self.form_type,
            submitted_by=self.user,
            responses=responses,
            application=application
        )
        
        self.assertEqual(submission.application, application)

    def test_validate_responses_success(self):
        """Test successful response validation."""
        responses = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'age': 25
        }
        
        result = FormSubmissionService.validate_responses(
            form_type=self.form_type,
            responses=responses
        )
        
        self.assertTrue(result)

    def test_validate_responses_missing_required(self):
        """Test validation failure for missing required fields."""
        responses = {
            'name': 'John Doe'
            # Missing required 'email' field
        }
        
        with self.assertRaises(ValidationError) as context:
            FormSubmissionService.validate_responses(
                form_type=self.form_type,
                responses=responses
            )
        
        self.assertIn('email', str(context.exception))

    def test_validate_responses_wrong_type_string(self):
        """Test validation failure for wrong type (string)."""
        responses = {
            'name': 123,  # Should be string
            'email': 'john@example.com'
        }
        
        with self.assertRaises(ValidationError) as context:
            FormSubmissionService.validate_responses(
                form_type=self.form_type,
                responses=responses
            )
        
        self.assertIn('string', str(context.exception).lower())

    def test_validate_responses_wrong_type_integer(self):
        """Test validation failure for wrong type (integer)."""
        responses = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'age': 'twenty-five'  # Should be integer
        }
        
        with self.assertRaises(ValidationError) as context:
            FormSubmissionService.validate_responses(
                form_type=self.form_type,
                responses=responses
            )
        
        self.assertIn('integer', str(context.exception).lower())

    def test_validate_responses_number_type(self):
        """Test validation for number type."""
        schema = {
            'properties': {
                'gpa': {'type': 'number'}
            }
        }
        form_type = FormType.objects.create(
            name="Number Form",
            schema=schema
        )
        
        # Should fail with string
        with self.assertRaises(ValidationError):
            FormSubmissionService.validate_responses(
                form_type=form_type,
                responses={'gpa': 'three point five'}
            )

    def test_validate_responses_boolean_type(self):
        """Test validation for boolean type."""
        schema = {
            'properties': {
                'agreed': {'type': 'boolean'}
            }
        }
        form_type = FormType.objects.create(
            name="Bool Form",
            schema=schema
        )
        
        # Should fail with non-boolean
        with self.assertRaises(ValidationError):
            FormSubmissionService.validate_responses(
                form_type=form_type,
                responses={'agreed': 'yes'}
            )

    def test_validate_responses_array_type(self):
        """Test validation for array type."""
        schema = {
            'properties': {
                'tags': {'type': 'array'}
            }
        }
        form_type = FormType.objects.create(
            name="Array Form",
            schema=schema
        )
        
        # Should fail with non-array
        with self.assertRaises(ValidationError):
            FormSubmissionService.validate_responses(
                form_type=form_type,
                responses={'tags': 'tag1,tag2'}
            )

    def test_validate_responses_extra_fields_allowed(self):
        """Test that extra fields are allowed."""
        responses = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'extra_field': 'Extra data'
        }
        
        # Should not raise error
        result = FormSubmissionService.validate_responses(
            form_type=self.form_type,
            responses=responses
        )
        
        self.assertTrue(result)

    def test_validate_responses_no_schema(self):
        """Test validation with form type having empty schema."""
        form_type = FormType.objects.create(
            name="No Schema",
            schema={}  # Empty dict, not None
        )
        
        responses = {'anything': 'goes'}
        
        result = FormSubmissionService.validate_responses(
            form_type=form_type,
            responses=responses
        )
        
        self.assertTrue(result)

    def test_get_user_submissions_all(self):
        """Test getting all submissions for a user."""
        responses1 = {'name': 'John', 'email': 'john@example.com'}
        responses2 = {'name': 'Jane', 'email': 'jane@example.com'}
        
        FormSubmissionService.create_submission(
            form_type=self.form_type,
            submitted_by=self.user,
            responses=responses1
        )
        
        FormSubmissionService.create_submission(
            form_type=self.form_type,
            submitted_by=self.user,
            responses=responses2
        )
        
        submissions = FormSubmissionService.get_user_submissions(self.user)
        
        self.assertEqual(submissions.count(), 2)

    def test_get_user_submissions_filtered_by_form_type(self):
        """Test getting submissions filtered by form type."""
        form_type2 = FormType.objects.create(
            name="Another Form",
            schema={'properties': {'field': {'type': 'string'}}}
        )
        
        FormSubmissionService.create_submission(
            form_type=self.form_type,
            submitted_by=self.user,
            responses={'name': 'John', 'email': 'john@example.com'}
        )
        
        FormSubmissionService.create_submission(
            form_type=form_type2,
            submitted_by=self.user,
            responses={'field': 'value'}
        )
        
        submissions = FormSubmissionService.get_user_submissions(
            self.user,
            form_type=self.form_type
        )
        
        self.assertEqual(submissions.count(), 1)
        self.assertEqual(submissions.first().form_type, self.form_type)

    def test_get_user_submissions_filtered_by_program(self):
        """Test getting submissions filtered by program."""
        program1 = Program.objects.create(
            name="Program 1",
            description="Test",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365),
            is_active=True
        )
        
        program2 = Program.objects.create(
            name="Program 2",
            description="Test",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365),
            is_active=True
        )
        
        FormSubmissionService.create_submission(
            form_type=self.form_type,
            submitted_by=self.user,
            responses={'name': 'John', 'email': 'john@example.com'},
            program=program1
        )
        
        FormSubmissionService.create_submission(
            form_type=self.form_type,
            submitted_by=self.user,
            responses={'name': 'Jane', 'email': 'jane@example.com'},
            program=program2
        )
        
        submissions = FormSubmissionService.get_user_submissions(
            self.user,
            program=program1
        )
        
        self.assertEqual(submissions.count(), 1)
        self.assertEqual(submissions.first().program, program1)

    def test_get_user_submissions_ordering(self):
        """Test submissions are ordered by submitted_at descending."""
        import time
        
        submission1 = FormSubmissionService.create_submission(
            form_type=self.form_type,
            submitted_by=self.user,
            responses={'name': 'First', 'email': 'first@example.com'}
        )
        
        time.sleep(0.01)  # Small delay to ensure different timestamps
        
        submission2 = FormSubmissionService.create_submission(
            form_type=self.form_type,
            submitted_by=self.user,
            responses={'name': 'Second', 'email': 'second@example.com'}
        )
        
        submissions = FormSubmissionService.get_user_submissions(self.user)
        
        # Most recent should be first
        self.assertEqual(submissions.first().id, submission2.id)
        self.assertEqual(submissions.last().id, submission1.id)

    def test_get_user_submissions_different_users(self):
        """Test that submissions are filtered by user."""
        user2 = User.objects.create_user(
            username="user2",
            email="user2@test.com",
            password="testpass123"
        )
        
        FormSubmissionService.create_submission(
            form_type=self.form_type,
            submitted_by=self.user,
            responses={'name': 'User1', 'email': 'user1@example.com'}
        )
        
        FormSubmissionService.create_submission(
            form_type=self.form_type,
            submitted_by=user2,
            responses={'name': 'User2', 'email': 'user2@example.com'}
        )
        
        submissions = FormSubmissionService.get_user_submissions(self.user)
        
        self.assertEqual(submissions.count(), 1)
        self.assertEqual(submissions.first().submitted_by, self.user)

