"""
Unit tests for application_forms serializers.
"""

import pytest
from datetime import date, datetime, timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory
from rest_framework.test import APIRequestFactory

from accounts.models import Role
from application_forms.models import FormType, FormSubmission
from application_forms.serializers import (
    FormTypeSerializer,
    FormSubmissionSerializer,
    FormTypeListSerializer,
    FormSubmissionListSerializer
)
from exchange.models import Program, Application, ApplicationStatus

User = get_user_model()


@pytest.mark.django_db
class TestFormTypeSerializer(TestCase):
    """Test FormTypeSerializer."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        
        self.form_type = FormType.objects.create(
            name="Test Form",
            form_type='application',
            description="Test Description",
            schema={
                'properties': {
                    'name': {'type': 'string'},
                    'email': {'type': 'string'}
                },
                'required': ['name']
            },
            ui_schema={'name': {'ui:widget': 'text'}},
            created_by=self.user
        )

    def test_serializer_fields(self):
        """Test serializer includes all expected fields."""
        serializer = FormTypeSerializer(instance=self.form_type)
        data = serializer.data
        
        self.assertIn('id', data)
        self.assertIn('name', data)
        self.assertIn('form_type', data)
        self.assertIn('description', data)
        self.assertIn('schema', data)
        self.assertIn('ui_schema', data)
        self.assertIn('is_active', data)
        self.assertIn('created_by', data)
        self.assertIn('created_by_username', data)
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)
        self.assertIn('field_count', data)
        self.assertIn('required_fields', data)

    def test_created_by_username_field(self):
        """Test created_by_username is populated correctly."""
        serializer = FormTypeSerializer(instance=self.form_type)
        data = serializer.data
        
        self.assertEqual(data['created_by_username'], 'testuser')

    def test_field_count(self):
        """Test field_count is calculated correctly."""
        serializer = FormTypeSerializer(instance=self.form_type)
        data = serializer.data
        
        self.assertEqual(data['field_count'], 2)

    def test_required_fields(self):
        """Test required_fields is populated correctly."""
        serializer = FormTypeSerializer(instance=self.form_type)
        data = serializer.data
        
        self.assertEqual(data['required_fields'], ['name'])

    def test_validate_schema_valid(self):
        """Test schema validation with valid dict."""
        data = {
            'name': 'New Form',
            'form_type': 'application',
            'schema': {'properties': {'field': {'type': 'string'}}}
        }
        
        serializer = FormTypeSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_validate_schema_invalid_non_dict(self):
        """Test schema validation rejects non-dict values."""
        data = {
            'name': 'New Form',
            'form_type': 'application',
            'schema': "not a dict"
        }
        
        serializer = FormTypeSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('schema', serializer.errors)
        self.assertIn('must be a valid JSON object', str(serializer.errors['schema']))

    def test_validate_schema_none_allowed(self):
        """Test schema validation allows None/empty."""
        data = {
            'name': 'New Form',
            'form_type': 'application',
            # schema field is omitted, will use default=dict from model
        }
        
        serializer = FormTypeSerializer(data=data)
        # Schema has a default, so omitted schema should be replaced with {}
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_validate_ui_schema_valid(self):
        """Test ui_schema validation with valid dict."""
        data = {
            'name': 'New Form',
            'form_type': 'application',
            'schema': {},
            'ui_schema': {'field': {'ui:widget': 'text'}}
        }
        
        serializer = FormTypeSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_validate_ui_schema_invalid_non_dict(self):
        """Test ui_schema validation rejects non-dict values."""
        data = {
            'name': 'New Form',
            'form_type': 'application',
            'schema': {},
            'ui_schema': "not a dict"
        }
        
        serializer = FormTypeSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('ui_schema', serializer.errors)
        self.assertIn('must be a valid JSON object', str(serializer.errors['ui_schema']))

    def test_create_form_type(self):
        """Test creating FormType through serializer."""
        data = {
            'name': 'Created Form',
            'form_type': 'custom',  # Changed from 'contact' to valid choice
            'description': 'Created via serializer',
            'schema': {'properties': {'test': {'type': 'string'}}}
        }
        
        serializer = FormTypeSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        form_type = serializer.save(created_by=self.user)
        
        self.assertEqual(form_type.name, 'Created Form')
        self.assertEqual(form_type.form_type, 'custom')

    def test_update_form_type(self):
        """Test updating FormType through serializer."""
        data = {
            'name': 'Updated Form',
            'description': 'Updated description'
        }
        
        serializer = FormTypeSerializer(instance=self.form_type, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated = serializer.save()
        
        self.assertEqual(updated.name, 'Updated Form')
        self.assertEqual(updated.description, 'Updated description')


@pytest.mark.django_db
class TestFormSubmissionSerializer(TestCase):
    """Test FormSubmissionSerializer."""

    def setUp(self):
        """Set up test data."""
        self.student_role, _ = Role.objects.get_or_create(name="student")
        
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.user.roles.add(self.student_role)
        
        self.form_type = FormType.objects.create(
            name="Test Form",
            form_type='application',
            schema={
                'properties': {
                    'name': {'type': 'string'},
                    'email': {'type': 'string'}
                },
                'required': ['name']
            },
            created_by=self.user
        )
        
        self.program = Program.objects.create(
            name="Test Program",
            description="Test",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            is_active=True
        )
        
        self.submission = FormSubmission.objects.create(
            form_type=self.form_type,
            submitted_by=self.user,
            responses={'name': 'John Doe', 'email': 'john@example.com'},
            program=self.program
        )

    def test_serializer_fields(self):
        """Test serializer includes all expected fields."""
        serializer = FormSubmissionSerializer(instance=self.submission)
        data = serializer.data
        
        self.assertIn('id', data)
        self.assertIn('form_type', data)
        self.assertIn('form_type_name', data)
        self.assertIn('submitted_by', data)
        self.assertIn('submitted_by_username', data)
        self.assertIn('responses', data)
        self.assertIn('submitted_at', data)
        self.assertIn('updated_at', data)
        self.assertIn('program', data)
        self.assertIn('program_name', data)
        self.assertIn('application', data)
        self.assertIn('response_count', data)

    def test_form_type_name_field(self):
        """Test form_type_name is populated correctly."""
        serializer = FormSubmissionSerializer(instance=self.submission)
        data = serializer.data
        
        self.assertEqual(data['form_type_name'], 'Test Form')

    def test_submitted_by_username_field(self):
        """Test submitted_by_username is populated correctly."""
        serializer = FormSubmissionSerializer(instance=self.submission)
        data = serializer.data
        
        self.assertEqual(data['submitted_by_username'], 'testuser')

    def test_program_name_field(self):
        """Test program_name is populated correctly."""
        serializer = FormSubmissionSerializer(instance=self.submission)
        data = serializer.data
        
        self.assertEqual(data['program_name'], 'Test Program')

    def test_program_name_field_null(self):
        """Test program_name handles null program."""
        self.submission.program = None
        self.submission.save()
        
        serializer = FormSubmissionSerializer(instance=self.submission)
        data = serializer.data
        
        self.assertIsNone(data['program_name'])

    def test_response_count(self):
        """Test response_count is calculated correctly."""
        serializer = FormSubmissionSerializer(instance=self.submission)
        data = serializer.data
        
        self.assertEqual(data['response_count'], 2)

    def test_validate_responses_valid(self):
        """Test responses validation with valid dict."""
        data = {
            'form_type': self.form_type.id,
            'responses': {'name': 'Jane Doe', 'email': 'jane@example.com'}
        }
        
        serializer = FormSubmissionSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_validate_responses_invalid_non_dict(self):
        """Test responses validation rejects non-dict values."""
        data = {
            'form_type': self.form_type.id,
            'responses': "not a dict"
        }
        
        serializer = FormSubmissionSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('responses', serializer.errors)
        self.assertIn('must be a valid JSON object', str(serializer.errors['responses']))

    def test_validate_required_fields_present(self):
        """Test validation passes when required fields present."""
        data = {
            'form_type': self.form_type.id,
            'responses': {'name': 'Jane Doe', 'email': 'jane@example.com'}
        }
        
        serializer = FormSubmissionSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_validate_responses_partial_payload_allowed_at_serializer(self):
        """Serializer only checks JSON shape; required fields enforced in FormSubmissionService."""
        data = {
            'form_type': self.form_type.id,
            'responses': {'email': 'jane@example.com'}  # Missing schema 'name'
        }

        serializer = FormSubmissionSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_validate_no_required_fields_defined(self):
        """Test validation passes when no required fields defined."""
        form_type_no_required = FormType.objects.create(
            name="No Required Form",
            form_type='application',
            schema={'properties': {'optional': {'type': 'string'}}},
            created_by=self.user
        )
        
        data = {
            'form_type': form_type_no_required.id,
            'responses': {}
        }
        
        serializer = FormSubmissionSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_create_assigns_submitted_by_from_request(self):
        """Test create auto-assigns submitted_by from request user."""
        factory = APIRequestFactory()
        request = factory.post('/fake-url/')
        request.user = self.user
        
        data = {
            'form_type': self.form_type.id,
            'responses': {'name': 'Auto-assigned User'}
        }
        
        serializer = FormSubmissionSerializer(
            data=data,
            context={'request': request}
        )
        self.assertTrue(serializer.is_valid())
        submission = serializer.save()
        
        self.assertEqual(submission.submitted_by, self.user)

    def test_create_without_request_context(self):
        """Test create works without request in context."""
        data = {
            'form_type': self.form_type.id,
            'submitted_by': self.user.id,
            'responses': {'name': 'Manual User'}
        }
        
        serializer = FormSubmissionSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        submission = serializer.save(submitted_by=self.user)
        
        self.assertEqual(submission.submitted_by, self.user)


@pytest.mark.django_db
class TestFormTypeListSerializer(TestCase):
    """Test FormTypeListSerializer."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        
        self.form_type = FormType.objects.create(
            name="Test Form",
            form_type='application',
            description="Test Description",
            schema={'properties': {'field1': {}, 'field2': {}, 'field3': {}}},
            created_by=self.user
        )

    def test_serializer_fields(self):
        """Test lightweight serializer includes only list fields."""
        serializer = FormTypeListSerializer(instance=self.form_type)
        data = serializer.data
        
        expected_fields = ['id', 'name', 'form_type', 'description', 'is_active', 'field_count', 'created_at']
        for field in expected_fields:
            self.assertIn(field, data)
        
        # Should NOT include heavy fields like schema, ui_schema
        self.assertNotIn('schema', data)
        self.assertNotIn('ui_schema', data)

    def test_field_count(self):
        """Test field_count is calculated correctly."""
        serializer = FormTypeListSerializer(instance=self.form_type)
        data = serializer.data
        
        self.assertEqual(data['field_count'], 3)

    def test_all_fields_read_only(self):
        """Test all fields are read-only."""
        serializer = FormTypeListSerializer()
        for field_name in serializer.fields:
            self.assertTrue(serializer.fields[field_name].read_only)


@pytest.mark.django_db
class TestFormSubmissionListSerializer(TestCase):
    """Test FormSubmissionListSerializer."""

    def setUp(self):
        """Set up test data."""
        self.student_role, _ = Role.objects.get_or_create(name="student")
        
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.user.roles.add(self.student_role)
        
        self.form_type = FormType.objects.create(
            name="Test Form",
            form_type='application',
            schema={'properties': {'name': {'type': 'string'}}},
            created_by=self.user
        )
        
        self.program = Program.objects.create(
            name="Test Program",
            description="Test",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            is_active=True
        )
        
        self.submission = FormSubmission.objects.create(
            form_type=self.form_type,
            submitted_by=self.user,
            responses={'name': 'John Doe'},
            program=self.program
        )

    def test_serializer_fields(self):
        """Test lightweight serializer includes only list fields."""
        serializer = FormSubmissionListSerializer(instance=self.submission)
        data = serializer.data
        
        expected_fields = ['id', 'form_type_name', 'submitted_by_username', 'submitted_at', 'program', 'application']
        for field in expected_fields:
            self.assertIn(field, data)
        
        # Should NOT include heavy fields like responses
        self.assertNotIn('responses', data)

    def test_form_type_name(self):
        """Test form_type_name is populated correctly."""
        serializer = FormSubmissionListSerializer(instance=self.submission)
        data = serializer.data
        
        self.assertEqual(data['form_type_name'], 'Test Form')

    def test_submitted_by_username(self):
        """Test submitted_by_username is populated correctly."""
        serializer = FormSubmissionListSerializer(instance=self.submission)
        data = serializer.data
        
        self.assertEqual(data['submitted_by_username'], 'testuser')

    def test_all_fields_read_only(self):
        """Test all fields are read-only."""
        serializer = FormSubmissionListSerializer()
        for field_name in serializer.fields:
            self.assertTrue(serializer.fields[field_name].read_only)

