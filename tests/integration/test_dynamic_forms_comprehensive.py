"""
Comprehensive tests for dynamic forms functionality.

Tests include:
- Form rendering and field generation
- Form validation and submission
- Field visibility and interaction
- API endpoints
- Permission-based access
- Integration with applications
"""

import json
import pytest
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from accounts.models import Role
from application_forms.models import FormType, FormSubmission
from application_forms.services import DynamicFormFromSchema, FormSubmissionService
from exchange.models import Program, Application, ApplicationStatus

User = get_user_model()


@pytest.mark.django_db
class TestDynamicFormRendering(TestCase):
    """Test dynamic form rendering from schema."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_render_text_field(self):
        """Test rendering a text input field."""
        form_type = FormType.objects.create(
            name="Text Form",
            schema={
                'properties': {
                    'first_name': {
                        'type': 'string',
                        'title': 'First Name',
                        'maxLength': 50
                    }
                },
                'required': ['first_name']
            },
            created_by=self.user
        )
        
        form = DynamicFormFromSchema(form_type)
        
        # Check field exists
        self.assertIn('first_name', form.fields)
        
        # Check field is required
        self.assertTrue(form.fields['first_name'].required)
        
        # Check field renders as HTML
        html = str(form)
        self.assertIn('first_name', html)

    def test_render_email_field(self):
        """Test rendering an email input field."""
        form_type = FormType.objects.create(
            name="Email Form",
            schema={
                'properties': {
                    'email': {
                        'type': 'string',
                        'format': 'email',
                        'title': 'Email Address'
                    }
                }
            },
            created_by=self.user
        )
        
        form = DynamicFormFromSchema(form_type)
        
        # Check field exists and is EmailField
        self.assertIn('email', form.fields)
        from django import forms
        self.assertIsInstance(form.fields['email'], forms.EmailField)

    def test_render_date_field(self):
        """Test rendering a date picker field."""
        form_type = FormType.objects.create(
            name="Date Form",
            schema={
                'properties': {
                    'birth_date': {
                        'type': 'string',
                        'format': 'date',
                        'title': 'Date of Birth'
                    }
                }
            },
            created_by=self.user
        )
        
        form = DynamicFormFromSchema(form_type)
        
        # Check field exists and is DateField
        self.assertIn('birth_date', form.fields)
        from django import forms
        self.assertIsInstance(form.fields['birth_date'], forms.DateField)

    def test_render_choice_field(self):
        """Test rendering a dropdown/select field."""
        form_type = FormType.objects.create(
            name="Choice Form",
            schema={
                'properties': {
                    'country': {
                        'type': 'string',
                        'enum': ['USA', 'Canada', 'Mexico'],
                        'title': 'Country'
                    }
                }
            },
            created_by=self.user
        )
        
        form = DynamicFormFromSchema(form_type)
        
        # Check field exists and is ChoiceField
        self.assertIn('country', form.fields)
        from django import forms
        self.assertIsInstance(form.fields['country'], forms.ChoiceField)
        
        # Check choices are set correctly
        choices = [choice[0] for choice in form.fields['country'].choices if choice[0]]
        self.assertEqual(set(choices), {'USA', 'Canada', 'Mexico'})

    def test_render_textarea_field(self):
        """Test rendering a textarea field (via maxLength > 200)."""
        form_type = FormType.objects.create(
            name="Textarea Form",
            schema={
                'properties': {
                    'description': {
                        'type': 'string',
                        'title': 'Description',
                        'maxLength': 500  # maxLength > 200 triggers textarea
                    }
                }
            },
            created_by=self.user
        )
        
        form = DynamicFormFromSchema(form_type)
        
        # Check field exists
        self.assertIn('description', form.fields)
        
        # Check widget is Textarea (triggered by maxLength > 200)
        from django import forms
        self.assertIsInstance(form.fields['description'].widget, forms.Textarea)

    def test_render_number_field(self):
        """Test rendering numeric input fields."""
        form_type = FormType.objects.create(
            name="Number Form",
            schema={
                'properties': {
                    'age': {
                        'type': 'integer',
                        'title': 'Age',
                        'minimum': 18,
                        'maximum': 100
                    }
                }
            },
            created_by=self.user
        )
        
        form = DynamicFormFromSchema(form_type)
        
        # Check field exists and is IntegerField
        self.assertIn('age', form.fields)
        from django import forms
        self.assertIsInstance(form.fields['age'], forms.IntegerField)

    def test_render_boolean_field(self):
        """Test rendering checkbox field."""
        form_type = FormType.objects.create(
            name="Boolean Form",
            schema={
                'properties': {
                    'agree_terms': {
                        'type': 'boolean',
                        'title': 'I agree to terms'
                    }
                }
            },
            created_by=self.user
        )
        
        form = DynamicFormFromSchema(form_type)
        
        # Check field exists and is BooleanField
        self.assertIn('agree_terms', form.fields)
        from django import forms
        self.assertIsInstance(form.fields['agree_terms'], forms.BooleanField)

    def test_render_multiple_fields(self):
        """Test rendering form with multiple field types."""
        form_type = FormType.objects.create(
            name="Complex Form",
            schema={
                'properties': {
                    'name': {'type': 'string', 'title': 'Name'},
                    'email': {'type': 'string', 'format': 'email', 'title': 'Email'},
                    'age': {'type': 'integer', 'title': 'Age'},
                    'country': {'type': 'string', 'enum': ['USA', 'UK'], 'title': 'Country'},
                    'agree': {'type': 'boolean', 'title': 'Agree'}
                },
                'required': ['name', 'email']
            },
            created_by=self.user
        )
        
        form = DynamicFormFromSchema(form_type)
        
        # Check all fields exist
        self.assertEqual(len(form.fields), 5)
        self.assertIn('name', form.fields)
        self.assertIn('email', form.fields)
        self.assertIn('age', form.fields)
        self.assertIn('country', form.fields)
        self.assertIn('agree', form.fields)
        
        # Check required fields
        self.assertTrue(form.fields['name'].required)
        self.assertTrue(form.fields['email'].required)
        self.assertFalse(form.fields['age'].required)

    def test_form_with_no_schema(self):
        """Test form with empty schema."""
        form_type = FormType.objects.create(
            name="Empty Form",
            schema={},
            created_by=self.user
        )
        
        form = DynamicFormFromSchema(form_type)
        
        # Should create form with no fields
        self.assertEqual(len(form.fields), 0)


@pytest.mark.django_db
class TestDynamicFormValidation(TestCase):
    """Test dynamic form validation."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.form_type = FormType.objects.create(
            name="Validation Form",
            schema={
                'properties': {
                    'name': {'type': 'string', 'title': 'Name'},
                    'email': {'type': 'string', 'format': 'email', 'title': 'Email'},
                    'age': {'type': 'integer', 'title': 'Age', 'minimum': 18}
                },
                'required': ['name', 'email']
            },
            created_by=self.user
        )

    def test_valid_form_submission(self):
        """Test valid form data passes validation."""
        form = DynamicFormFromSchema(
            self.form_type,
            data={
                'name': 'John Doe',
                'email': 'john@example.com',
                'age': 25
            }
        )
        
        self.assertTrue(form.is_valid())

    def test_missing_required_field(self):
        """Test missing required field fails validation."""
        form = DynamicFormFromSchema(
            self.form_type,
            data={
                'email': 'john@example.com',
                # Missing required 'name'
            }
        )
        
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_invalid_email_format(self):
        """Test invalid email format fails validation."""
        form = DynamicFormFromSchema(
            self.form_type,
            data={
                'name': 'John Doe',
                'email': 'invalid-email',
                'age': 25
            }
        )
        
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_integer_field_validation(self):
        """Test integer field validates numeric input."""
        form = DynamicFormFromSchema(
            self.form_type,
            data={
                'name': 'John Doe',
                'email': 'john@example.com',
                'age': 'not a number'
            }
        )
        
        self.assertFalse(form.is_valid())
        self.assertIn('age', form.errors)


@pytest.mark.django_db
class TestDynamicFormSubmission(TestCase):
    """Test dynamic form submission workflows."""

    def setUp(self):
        """Set up test data."""
        self.student_role, _ = Role.objects.get_or_create(name="student")
        
        self.user = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='testpass123'
        )
        self.user.roles.add(self.student_role)
        
        self.form_type = FormType.objects.create(
            name="Application Form",
            form_type='application',
            schema={
                'properties': {
                    'motivation': {'type': 'string', 'title': 'Motivation'},
                    'experience': {'type': 'string', 'title': 'Experience'},
                    'gpa': {'type': 'number', 'title': 'GPA', 'minimum': 0, 'maximum': 4}
                },
                'required': ['motivation']
            },
            created_by=self.user
        )
        
        today = date.today()
        self.program = Program.objects.create(
            name="Test Program",
            description="Test",
            start_date=today,
            end_date=today + timedelta(days=365),
            is_active=True,
            application_form=self.form_type
        )

    def test_create_submission(self):
        """Test creating a form submission."""
        responses = {
            'motivation': 'I want to study abroad',
            'experience': '2 years in related field',
            'gpa': 3.5
        }
        
        submission = FormSubmissionService.create_submission(
            form_type=self.form_type,
            submitted_by=self.user,
            responses=responses,
            program=self.program
        )
        
        self.assertIsNotNone(submission)
        self.assertEqual(submission.form_type, self.form_type)
        self.assertEqual(submission.submitted_by, self.user)
        self.assertEqual(submission.responses['motivation'], 'I want to study abroad')

    def test_submission_validation_success(self):
        """Test submission validation with valid data."""
        responses = {
            'motivation': 'Valid motivation',
            'experience': 'Valid experience'
        }
        
        # Should not raise
        FormSubmissionService.validate_responses(self.form_type, responses)

    def test_submission_validation_missing_required(self):
        """Test submission validation fails with missing required field."""
        responses = {
            'experience': 'Experience only'
            # Missing required 'motivation'
        }
        
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            FormSubmissionService.validate_responses(self.form_type, responses)

    def test_get_user_submissions(self):
        """Test retrieving user's submissions."""
        # Create submission
        FormSubmissionService.create_submission(
            form_type=self.form_type,
            submitted_by=self.user,
            responses={'motivation': 'Test'},
            program=self.program
        )
        
        # Get submissions
        submissions = FormSubmissionService.get_user_submissions(
            form_type=self.form_type,
            user=self.user
        )
        
        self.assertEqual(submissions.count(), 1)
        self.assertEqual(submissions.first().submitted_by, self.user)


@pytest.mark.django_db
class TestDynamicFormHTMLRendering(TestCase):
    """Test HTML rendering and visibility of dynamic forms."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.admin_role, _ = Role.objects.get_or_create(name='admin')
        
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.admin.roles.add(self.admin_role)
        
        self.form_type = FormType.objects.create(
            name="Test Application Form",
            form_type='application',
            description="Application form for exchange programs",
            schema={
                'properties': {
                    'full_name': {
                        'type': 'string',
                        'title': 'Full Name',
                        'maxLength': 100
                    },
                    'email': {
                        'type': 'string',
                        'format': 'email',
                        'title': 'Email Address'
                    },
                    'motivation': {
                        'type': 'string',
                        'title': 'Motivation Statement'
                    },
                    'previous_exchanges': {
                        'type': 'integer',
                        'title': 'Previous Exchanges',
                        'minimum': 0
                    }
                },
                'required': ['full_name', 'email', 'motivation']
            },
            ui_schema={
                'motivation': {
                    'ui:widget': 'textarea',
                    'ui:placeholder': 'Describe your motivation...'
                }
            },
            created_by=self.admin
        )

    def test_form_field_visibility_in_html(self):
        """Test that form fields are visible in rendered HTML."""
        form = DynamicFormFromSchema(self.form_type)
        html = form.as_p()
        
        # Check all fields are present in HTML
        self.assertIn('full_name', html)
        self.assertIn('email', html)
        self.assertIn('motivation', html)
        self.assertIn('previous_exchanges', html)
        
        # Check field titles are visible
        self.assertIn('Full Name', html)
        self.assertIn('Email Address', html)
        self.assertIn('Motivation Statement', html)

    def test_required_fields_marked(self):
        """Test that required fields are marked as required in HTML."""
        form = DynamicFormFromSchema(self.form_type)
        html = form.as_p()
        
        # Required fields should have 'required' attribute
        # This is browser-side validation
        self.assertTrue(form.fields['full_name'].required)
        self.assertTrue(form.fields['email'].required)
        self.assertTrue(form.fields['motivation'].required)
        self.assertFalse(form.fields['previous_exchanges'].required)

    def test_textarea_widget_applied(self):
        """Test that textarea widget is applied for long text fields."""
        # Update form_type to have maxLength > 200 for motivation
        self.form_type.schema['properties']['motivation']['maxLength'] = 1000
        self.form_type.save()
        
        form = DynamicFormFromSchema(self.form_type)
        
        # Check motivation field uses Textarea widget
        from django import forms
        self.assertIsInstance(form.fields['motivation'].widget, forms.Textarea)

    def test_form_renders_with_errors(self):
        """Test form renders with validation errors visible."""
        form = DynamicFormFromSchema(
            self.form_type,
            data={
                'email': 'invalid-email',
                # Missing required fields
            }
        )
        
        self.assertFalse(form.is_valid())
        
        # Check errors are accessible
        self.assertIn('full_name', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('motivation', form.errors)
        
        # Render with errors
        html = form.as_p()
        self.assertIn('errorlist', html.lower() or 'ul' in html)


@pytest.mark.django_db
class TestDynamicFormAPIEndpoints(TestCase):
    """Test ViewSet querysets and permissions for dynamic forms."""

    def setUp(self):
        """Set up test data."""
        self.admin_role, _ = Role.objects.get_or_create(name='admin')
        self.student_role, _ = Role.objects.get_or_create(name='student')
        
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.admin.roles.add(self.admin_role)
        
        self.student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='studentpass123'
        )
        self.student.roles.add(self.student_role)
        
        self.active_form = FormType.objects.create(
            name="Active Form",
            form_type='application',
            schema={'properties': {'field1': {'type': 'string'}}},
            created_by=self.admin,
            is_active=True
        )
        
        self.inactive_form = FormType.objects.create(
            name="Inactive Form",
            form_type='survey',
            schema={},
            is_active=False,
            created_by=self.admin
        )

    def test_queryset_filtering_for_student(self):
        """Test that students see only active forms."""
        from application_forms.views import FormTypeViewSet
        from unittest.mock import Mock
        
        # Create mock request with student user
        request = Mock()
        request.user = self.student
        
        viewset = FormTypeViewSet()
        viewset.request = request
        viewset.action = 'list'
        
        queryset = viewset.get_queryset()
        
        # Student should only see active forms
        self.assertIn(self.active_form, queryset)
        self.assertNotIn(self.inactive_form, queryset)

    def test_queryset_filtering_for_admin(self):
        """Test that admins see all forms."""
        from application_forms.views import FormTypeViewSet
        from unittest.mock import Mock
        
        # Create mock request with admin user
        request = Mock()
        request.user = self.admin
        
        viewset = FormTypeViewSet()
        viewset.request = request
        viewset.action = 'list'
        
        queryset = viewset.get_queryset()
        
        # Admin should see both forms
        self.assertIn(self.active_form, queryset)
        self.assertIn(self.inactive_form, queryset)

    def test_form_type_created_by_assignment(self):
        """Test that created_by is assigned on save."""
        new_form = FormType.objects.create(
            name="Created Form",
            form_type='custom',
            schema={},
            created_by=self.admin
        )
        
        self.assertEqual(new_form.created_by, self.admin)

    def test_form_schema_accessible(self):
        """Test that form schema data is accessible."""
        form = self.active_form
        
        self.assertIsNotNone(form.schema)
        self.assertIsInstance(form.schema, dict)
        self.assertIn('properties', form.schema)


@pytest.mark.django_db
class TestDynamicFormWithApplication(TestCase):
    """Test dynamic forms integration with applications."""

    def setUp(self):
        """Set up test data."""
        self.student_role, _ = Role.objects.get_or_create(name="student")
        
        self.student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='testpass123'
        )
        self.student.roles.add(self.student_role)
        
        # Create form type
        self.form_type = FormType.objects.create(
            name="Exchange Application Form",
            form_type='application',
            schema={
                'properties': {
                    'motivation': {
                        'type': 'string',
                        'title': 'Why do you want to participate?'
                    },
                    'academic_goals': {
                        'type': 'string',
                        'title': 'Academic Goals'
                    },
                    'language_proficiency': {
                        'type': 'string',
                        'enum': ['Basic', 'Intermediate', 'Advanced', 'Native'],
                        'title': 'Language Proficiency'
                    }
                },
                'required': ['motivation', 'academic_goals']
            },
            created_by=self.student
        )
        
        # Create program with form
        today = date.today()
        self.program = Program.objects.create(
            name="Exchange Program with Form",
            description="Test program",
            start_date=today,
            end_date=today + timedelta(days=365),
            is_active=True,
            application_form=self.form_type
        )
        
        # Create application
        status, _ = ApplicationStatus.objects.get_or_create(
            name="draft",
            defaults={'order': 1}
        )
        
        self.application = Application.objects.create(
            student=self.student,
            program=self.program,
            status=status
        )

    def test_application_with_dynamic_form(self):
        """Test that program with form requires form submission."""
        # Check program has form
        self.assertIsNotNone(self.application.program.application_form)
        self.assertEqual(
            self.application.program.application_form.name,
            "Exchange Application Form"
        )

    def test_submit_dynamic_form_with_application(self):
        """Test submitting dynamic form data with application."""
        from exchange.services import ApplicationService
        
        form_data = {
            'df_motivation': 'I am passionate about cultural exchange',
            'df_academic_goals': 'Enhance my understanding of international business',
            'df_language_proficiency': 'Intermediate'
        }
        
        submission = ApplicationService.process_dynamic_form_submission(
            application=self.application,
            form_data=form_data,
            user=self.student
        )
        
        self.assertIsNotNone(submission)
        self.assertEqual(submission.application, self.application)
        self.assertEqual(submission.form_type, self.form_type)
        self.assertEqual(
            submission.responses['motivation'],
            'I am passionate about cultural exchange'
        )

    def test_retrieve_dynamic_form_submission(self):
        """Test retrieving existing form submission."""
        from exchange.services import ApplicationService
        
        # Submit form
        form_data = {
            'df_motivation': 'Test motivation',
            'df_academic_goals': 'Test goals'
        }
        
        submission = ApplicationService.process_dynamic_form_submission(
            application=self.application,
            form_data=form_data,
            user=self.student
        )
        
        # Retrieve it
        retrieved = ApplicationService.get_dynamic_form_submission(self.application)
        
        self.assertEqual(retrieved.id, submission.id)
        self.assertEqual(retrieved.responses, submission.responses)

    def test_update_existing_form_submission(self):
        """Test updating an existing form submission."""
        from exchange.services import ApplicationService
        
        # Initial submission
        form_data_1 = {
            'df_motivation': 'Initial motivation',
            'df_academic_goals': 'Initial goals'
        }
        
        submission_1 = ApplicationService.process_dynamic_form_submission(
            application=self.application,
            form_data=form_data_1,
            user=self.student
        )
        
        initial_id = submission_1.id
        
        # Update submission
        form_data_2 = {
            'df_motivation': 'Updated motivation',
            'df_academic_goals': 'Updated goals',
            'df_language_proficiency': 'Advanced'
        }
        
        submission_2 = ApplicationService.process_dynamic_form_submission(
            application=self.application,
            form_data=form_data_2,
            user=self.student
        )
        
        # Should be same submission, updated
        self.assertEqual(submission_2.id, initial_id)
        self.assertEqual(submission_2.responses['motivation'], 'Updated motivation')
        self.assertEqual(submission_2.responses['language_proficiency'], 'Advanced')

    def test_form_submission_without_dynamic_form(self):
        """Test application without dynamic form."""
        from exchange.services import ApplicationService
        
        # Remove form from program
        self.program.application_form = None
        self.program.save()
        
        form_data = {
            'df_some_field': 'Some value'
        }
        
        result = ApplicationService.process_dynamic_form_submission(
            application=self.application,
            form_data=form_data,
            user=self.student
        )
        
        # Should return None
        self.assertIsNone(result)


@pytest.mark.django_db
class TestDynamicFormFieldTypes(TestCase):
    """Test all supported dynamic form field types."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_string_field_type(self):
        """Test string field type renders correctly."""
        form_type = FormType.objects.create(
            name="String Test",
            schema={
                'properties': {
                    'text_field': {'type': 'string', 'title': 'Text Field'}
                }
            },
            created_by=self.user
        )
        
        form = DynamicFormFromSchema(form_type)
        self.assertIn('text_field', form.fields)
        
        from django import forms
        self.assertIsInstance(form.fields['text_field'], forms.CharField)

    def test_number_field_type(self):
        """Test number field type renders correctly."""
        form_type = FormType.objects.create(
            name="Number Test",
            schema={
                'properties': {
                    'score': {'type': 'number', 'title': 'Score'}
                }
            },
            created_by=self.user
        )
        
        form = DynamicFormFromSchema(form_type)
        self.assertIn('score', form.fields)
        
        from django import forms
        self.assertIsInstance(form.fields['score'], (forms.FloatField, forms.DecimalField))

    def test_boolean_field_type(self):
        """Test boolean field type renders correctly."""
        form_type = FormType.objects.create(
            name="Boolean Test",
            schema={
                'properties': {
                    'accept_terms': {'type': 'boolean', 'title': 'Accept Terms'}
                }
            },
            created_by=self.user
        )
        
        form = DynamicFormFromSchema(form_type)
        self.assertIn('accept_terms', form.fields)
        
        from django import forms
        self.assertIsInstance(form.fields['accept_terms'], forms.BooleanField)

    def test_array_field_type(self):
        """Test array field type renders correctly."""
        form_type = FormType.objects.create(
            name="Array Test",
            schema={
                'properties': {
                    'interests': {
                        'type': 'array',
                        'items': {'enum': ['Sports', 'Music', 'Art']},
                        'title': 'Interests'
                    }
                }
            },
            created_by=self.user
        )
        
        form = DynamicFormFromSchema(form_type)
        self.assertIn('interests', form.fields)
        
        # Array fields with enum are MultipleChoiceField
        from django import forms
        self.assertIsInstance(form.fields['interests'], forms.MultipleChoiceField)

    def test_datetime_field_type(self):
        """Test datetime field type renders correctly."""
        form_type = FormType.objects.create(
            name="DateTime Test",
            schema={
                'properties': {
                    'appointment': {
                        'type': 'string',
                        'format': 'datetime',  # Use 'datetime' not 'date-time'
                        'title': 'Appointment'
                    }
                }
            },
            created_by=self.user
        )
        
        form = DynamicFormFromSchema(form_type)
        self.assertIn('appointment', form.fields)
        
        from django import forms
        self.assertIsInstance(form.fields['appointment'], forms.DateTimeField)

    def test_url_field_type(self):
        """Test URL field type renders correctly."""
        form_type = FormType.objects.create(
            name="URL Test",
            schema={
                'properties': {
                    'website': {
                        'type': 'string',
                        'format': 'url',  # Use 'url' not 'uri'
                        'title': 'Website'
                    }
                }
            },
            created_by=self.user
        )
        
        form = DynamicFormFromSchema(form_type)
        self.assertIn('website', form.fields)
        
        from django import forms
        self.assertIsInstance(form.fields['website'], forms.URLField)


@pytest.mark.django_db
class TestDynamicFormPermissions(TestCase):
    """Test permission-based access to dynamic forms at service level."""

    def setUp(self):
        """Set up test data."""
        self.admin_role, _ = Role.objects.get_or_create(name='admin')
        self.student_role, _ = Role.objects.get_or_create(name='student')
        
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.admin.roles.add(self.admin_role)
        
        self.student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='studentpass123'
        )
        self.student.roles.add(self.student_role)
        
        self.active_form = FormType.objects.create(
            name="Active Form",
            form_type='application',
            schema={'properties': {'test': {'type': 'string'}}},
            created_by=self.admin,
            is_active=True
        )
        
        self.inactive_form = FormType.objects.create(
            name="Inactive Form",
            form_type='survey',
            schema={},
            is_active=False,
            created_by=self.admin
        )

    def test_student_queryset_shows_only_active_forms(self):
        """Test student queryset filtering at ViewSet level."""
        from application_forms.views import FormTypeViewSet
        from unittest.mock import Mock
        
        request = Mock()
        request.user = self.student
        
        viewset = FormTypeViewSet()
        viewset.request = request
        
        queryset = viewset.get_queryset()
        
        # Should contain active form
        self.assertIn(self.active_form, queryset)
        # Should NOT contain inactive form
        self.assertNotIn(self.inactive_form, queryset)

    def test_admin_queryset_shows_all_forms(self):
        """Test admin queryset shows all forms."""
        from application_forms.views import FormTypeViewSet
        from unittest.mock import Mock
        
        request = Mock()
        request.user = self.admin
        
        viewset = FormTypeViewSet()
        viewset.request = request
        
        queryset = viewset.get_queryset()
        
        # Should contain both forms
        self.assertIn(self.active_form, queryset)
        self.assertIn(self.inactive_form, queryset)

    def test_form_type_creation_permissions(self):
        """Test form type creation assigns created_by."""
        new_form = FormType.objects.create(
            name="New Test Form",
            form_type='feedback',
            schema={'properties': {'rating': {'type': 'integer'}}},
            created_by=self.student
        )
        
        self.assertEqual(new_form.created_by, self.student)

    def test_active_forms_accessible_to_all(self):
        """Test that active forms are accessible to all authenticated users."""
        # Active forms should be queryable
        active_forms = FormType.objects.filter(is_active=True)
        
        self.assertIn(self.active_form, active_forms)
        self.assertNotIn(self.inactive_form, active_forms)


@pytest.mark.django_db
class TestDynamicFormInteraction(TestCase):
    """Test dynamic form interaction workflows."""

    def setUp(self):
        """Set up test data."""
        self.student_role, _ = Role.objects.get_or_create(name="student")
        
        self.student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='testpass123'
        )
        self.student.roles.add(self.student_role)

    def test_form_submission_creates_timeline_event(self):
        """Test that form submission creates timeline event."""
        from exchange.services import ApplicationService
        from exchange.models import TimelineEvent
        
        # Create form and program
        form_type = FormType.objects.create(
            name="Timeline Test Form",
            form_type='application',
            schema={
                'properties': {
                    'field1': {'type': 'string', 'title': 'Field 1'}
                },
                'required': ['field1']
            },
            created_by=self.student
        )
        
        today = date.today()
        program = Program.objects.create(
            name="Timeline Test Program",
            description="Test",
            start_date=today,
            end_date=today + timedelta(days=365),
            is_active=True,
            application_form=form_type
        )
        
        status, _ = ApplicationStatus.objects.get_or_create(
            name="draft",
            defaults={'order': 1}
        )
        
        application = Application.objects.create(
            student=self.student,
            program=program,
            status=status
        )
        
        # Submit form
        form_data = {
            'df_field1': 'Test value'
        }
        
        ApplicationService.process_dynamic_form_submission(
            application=application,
            form_data=form_data,
            user=self.student
        )
        
        # Check timeline event created
        timeline_events = TimelineEvent.objects.filter(
            application=application,
            event_type='form_submitted'
        )
        
        self.assertEqual(timeline_events.count(), 1)
        self.assertIn('submitted', timeline_events.first().description.lower())

    def test_form_field_prefix_handling(self):
        """Test that df_ prefix is correctly handled."""
        from exchange.services import ApplicationService
        
        form_type = FormType.objects.create(
            name="Prefix Test Form",
            form_type='application',
            schema={
                'properties': {
                    'test_field': {'type': 'string', 'title': 'Test Field'}
                },
                'required': ['test_field']
            },
            created_by=self.student
        )
        
        today = date.today()
        program = Program.objects.create(
            name="Prefix Test Program",
            description="Test",
            start_date=today,
            end_date=today + timedelta(days=365),
            is_active=True,
            application_form=form_type
        )
        
        status, _ = ApplicationStatus.objects.get_or_create(
            name="draft",
            defaults={'order': 1}
        )
        
        application = Application.objects.create(
            student=self.student,
            program=program,
            status=status
        )
        
        # Submit with df_ prefix
        form_data = {
            'df_test_field': 'Test value',
            'non_df_field': 'Should be ignored'
        }
        
        submission = ApplicationService.process_dynamic_form_submission(
            application=application,
            form_data=form_data,
            user=self.student
        )
        
        # Check only df_ prefixed fields are stored (without prefix)
        self.assertIn('test_field', submission.responses)
        self.assertNotIn('non_df_field', submission.responses)
        self.assertNotIn('df_test_field', submission.responses)  # Prefix removed

    def test_form_submission_validation_error(self):
        """Test that invalid form data raises validation error."""
        from exchange.services import ApplicationService
        from django.core.exceptions import ValidationError
        
        form_type = FormType.objects.create(
            name="Validation Test Form",
            form_type='application',
            schema={
                'properties': {
                    'required_field': {'type': 'string', 'title': 'Required Field'}
                },
                'required': ['required_field']
            },
            created_by=self.student
        )
        
        today = date.today()
        program = Program.objects.create(
            name="Validation Test Program",
            description="Test",
            start_date=today,
            end_date=today + timedelta(days=365),
            is_active=True,
            application_form=form_type
        )
        
        status, _ = ApplicationStatus.objects.get_or_create(
            name="draft",
            defaults={'order': 1}
        )
        
        application = Application.objects.create(
            student=self.student,
            program=program,
            status=status
        )
        
        # Submit without required field
        form_data = {
            'df_optional_field': 'Some value'
            # Missing required_field
        }
        
        with self.assertRaises(ValidationError):
            ApplicationService.process_dynamic_form_submission(
                application=application,
                form_data=form_data,
                user=self.student
            )

