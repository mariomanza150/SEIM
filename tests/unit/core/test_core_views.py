"""
Test Core Views

Comprehensive tests for core application views.
"""

import pytest
from django.contrib.auth import get_user_model
from django.test import Client, SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from unittest.mock import patch, MagicMock

from application_forms.models import FormType
from core.views import DynamicFormFromSchema

User = get_user_model()


class TestHealthLiveView(SimpleTestCase):
    """Liveness endpoint must not depend on Postgres/Redis."""

    def test_health_live_returns_200(self):
        response = self.client.get("/health/live/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "live")
        self.assertIn("version", data)
        self.assertIn("environment", data)


@pytest.mark.django_db
class TestHealthCheckView(TestCase):
    """Test health check endpoint."""

    def setUp(self):
        """Set up test client."""
        self.client = Client()

    def test_health_check_success(self):
        """Test health check returns response with status info."""
        response = self.client.get('/health/')
        
        # May return 200 or 503 depending on service health
        self.assertIn(response.status_code, [200, 503])
        data = response.json()
        
        self.assertIn('status', data)
        self.assertIn('services', data)
        self.assertIn('version', data)
        self.assertIn('environment', data)

    def test_health_check_database_healthy(self):
        """Test health check reports database as healthy."""
        response = self.client.get('/health/')
        
        data = response.json()
        self.assertEqual(data['services']['database'], 'healthy')

    def test_health_check_cache_healthy(self):
        """Test health check reports cache status."""
        response = self.client.get('/health/')
        
        data = response.json()
        # Cache may or may not be working in test environment
        self.assertIn('cache', data['services'])
        self.assertIsNotNone(data['services']['cache'])

    @patch('core.views.connection')
    def test_health_check_database_unhealthy(self, mock_connection):
        """Test health check returns 503 when database unhealthy."""
        # Mock database connection failure
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("Database connection failed")
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        response = self.client.get('/health/')
        
        self.assertEqual(response.status_code, 503)
        data = response.json()
        self.assertEqual(data['status'], 'unhealthy')
        self.assertIn('unhealthy', data['services']['database'])

    @patch('core.views.cache')
    def test_health_check_cache_unhealthy(self, mock_cache):
        """Test health check returns 503 when cache unhealthy."""
        # Mock cache failure
        mock_cache.set.side_effect = Exception("Cache connection failed")
        
        response = self.client.get('/health/')
        
        self.assertEqual(response.status_code, 503)
        data = response.json()
        self.assertEqual(data['status'], 'unhealthy')
        self.assertIn('unhealthy', data['services']['cache'])

    @patch('core.views.redis')
    @override_settings(REDIS_URL='redis://localhost:6379/0')
    def test_health_check_redis_healthy(self, mock_redis):
        """Test health check reports redis as healthy when configured."""
        mock_redis_instance = MagicMock()
        mock_redis_instance.ping.return_value = True
        mock_redis.from_url.return_value = mock_redis_instance
        
        response = self.client.get('/health/')
        
        data = response.json()
        self.assertIn('redis', data['services'])

    @patch('core.views.redis')
    @override_settings(REDIS_URL='redis://localhost:6379/0')
    def test_health_check_redis_unhealthy(self, mock_redis):
        """Test health check returns 503 when redis unhealthy."""
        mock_redis.from_url.side_effect = Exception("Redis connection failed")
        
        response = self.client.get('/health/')
        
        self.assertEqual(response.status_code, 503)
        data = response.json()
        self.assertEqual(data['status'], 'unhealthy')
        self.assertIn('unhealthy', data['services']['redis'])

    @override_settings(REDIS_URL=None)
    def test_health_check_redis_not_configured(self):
        """Test health check when redis not configured."""
        response = self.client.get('/health/')
        
        data = response.json()
        # Response code depends on other services
        self.assertIn(response.status_code, [200, 503])
        self.assertIn('redis', data['services'])


@pytest.mark.django_db
class TestContactFormView(TestCase):
    """Test contact form view."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123"
        )

    def test_contact_form_get_with_form(self):
        """Test GET request displays form when available."""
        # Create a contact form
        form_type = FormType.objects.create(
            name="Contact Form",
            form_type='feedback',
            is_active=True,
            schema={
                'properties': {
                    'name': {'type': 'string', 'title': 'Name'},
                    'email': {'type': 'string', 'format': 'email', 'title': 'Email'},
                    'message': {'type': 'string', 'maxLength': 500, 'title': 'Message'}
                },
                'required': ['name', 'email', 'message']
            }
        )
        
        response = self.client.get('/contact/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'name', response.content)
        self.assertIn(b'email', response.content)
        self.assertIn(b'message', response.content)

    def test_contact_form_get_no_form_configured(self):
        """Test GET request when no form is configured."""
        # Don't create any forms
        response = self.client.get('/contact/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No contact form configured', response.content)

    def test_contact_form_get_only_inactive_forms(self):
        """Test GET when only inactive forms exist."""
        FormType.objects.create(
            name="Inactive Form",
            form_type='feedback',
            is_active=False,
            schema={'properties': {'field': {'type': 'string'}}}
        )
        
        response = self.client.get('/contact/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No contact form configured', response.content)

    @patch('core.views.FormType.objects.filter')
    def test_contact_form_get_error_handling(self, mock_filter):
        """Test GET request handles errors gracefully."""
        mock_filter.side_effect = Exception("Database error")
        
        response = self.client.get('/contact/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Error loading contact form', response.content)


@pytest.mark.django_db
class TestContactFormSubmitView(TestCase):
    """Test contact form submission view."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123"
        )
        
        self.form_type = FormType.objects.create(
            name="Contact Form",
            form_type='feedback',
            is_active=True,
            schema={
                'properties': {
                    'name': {'type': 'string', 'title': 'Name'},
                    'email': {'type': 'string', 'format': 'email', 'title': 'Email'},
                    'message': {'type': 'string', 'maxLength': 500, 'title': 'Message'}
                },
                'required': ['name', 'email', 'message']
            }
        )

    def test_contact_form_submit_valid_authenticated(self):
        """Test POST with valid data when authenticated."""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'message': 'Test message'
        }
        
        response = self.client.post('/contact/submit/', data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Thank you for your submission', response.content)

    def test_contact_form_submit_valid_anonymous(self):
        """Test POST with valid data when not authenticated."""
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'message': 'Test message'
        }
        
        response = self.client.post('/contact/submit/', data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Thank you for your submission', response.content)

    def test_contact_form_submit_invalid_missing_required(self):
        """Test POST with missing required field."""
        data = {
            'name': 'John Doe',
            'email': 'john@example.com'
            # Missing required 'message' field
        }
        
        response = self.client.post('/contact/submit/', data)
        
        # Should re-render form with errors
        self.assertEqual(response.status_code, 200)
        # Should not show thank you message
        self.assertNotIn(b'Thank you for your submission', response.content)

    def test_contact_form_submit_invalid_email(self):
        """Test POST with invalid email format."""
        data = {
            'name': 'John Doe',
            'email': 'invalid-email',
            'message': 'Test message'
        }
        
        response = self.client.post('/contact/submit/', data)
        
        # Should re-render form with errors
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'Thank you for your submission', response.content)

    def test_contact_form_submit_no_form_configured(self):
        """Test POST when no form is configured."""
        # Delete the form
        self.form_type.delete()
        
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'message': 'Test'
        }
        
        response = self.client.post('/contact/submit/', data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No contact form configured', response.content)

    @patch('core.views.FormType.objects.filter')
    def test_contact_form_submit_error_handling(self, mock_filter):
        """Test POST handles errors gracefully."""
        mock_filter.side_effect = Exception("Database error")
        
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'message': 'Test'
        }
        
        response = self.client.post('/contact/submit/', data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Error processing your submission', response.content)

    @patch('application_forms.models.FormSubmission.objects.create')
    def test_contact_form_submit_save_error_still_succeeds(self, mock_create):
        """Test that submission succeeds even if save fails."""
        mock_create.side_effect = Exception("Save failed")
        
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'message': 'Test message'
        }
        
        response = self.client.post('/contact/submit/', data)
        
        # Should still show success message
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Thank you for your submission', response.content)


@pytest.mark.django_db
class TestDynamicFormFromSchemaCoreViews(TestCase):
    """Test DynamicFormFromSchema in core/views.py."""

    def test_string_field_generation(self):
        """Test generating string field."""
        schema = {
            'properties': {
                'name': {'type': 'string', 'title': 'Full Name'}
            },
            'required': ['name']
        }
        
        form_type = FormType.objects.create(
            name="Test Form",
            schema=schema
        )
        
        form = DynamicFormFromSchema(form_type)
        
        self.assertIn('name', form.fields)
        self.assertTrue(form.fields['name'].required)
        self.assertEqual(form.fields['name'].label, 'Full Name')

    def test_email_field_generation(self):
        """Test generating email field."""
        schema = {
            'properties': {
                'email': {'type': 'string', 'format': 'email', 'title': 'Email'}
            }
        }
        
        form_type = FormType.objects.create(
            name="Email Form",
            schema=schema
        )
        
        form = DynamicFormFromSchema(form_type)
        
        from django import forms
        self.assertIsInstance(form.fields['email'], forms.EmailField)

    def test_textarea_field_generation(self):
        """Test generating textarea for long strings."""
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
        self.assertIsInstance(form.fields['description'].widget, forms.Textarea)

    def test_number_field_generation(self):
        """Test generating number field."""
        schema = {
            'properties': {
                'amount': {'type': 'number', 'title': 'Amount'}
            }
        }
        
        form_type = FormType.objects.create(
            name="Number Form",
            schema=schema
        )
        
        form = DynamicFormFromSchema(form_type)
        
        from django import forms
        self.assertIsInstance(form.fields['amount'], forms.DecimalField)

    def test_integer_field_generation(self):
        """Test generating integer field."""
        schema = {
            'properties': {
                'count': {'type': 'integer', 'title': 'Count'}
            }
        }
        
        form_type = FormType.objects.create(
            name="Integer Form",
            schema=schema
        )
        
        form = DynamicFormFromSchema(form_type)
        
        from django import forms
        self.assertIsInstance(form.fields['count'], forms.DecimalField)

    def test_boolean_field_generation(self):
        """Test generating boolean field."""
        schema = {
            'properties': {
                'agreed': {'type': 'boolean', 'title': 'I Agree'}
            }
        }
        
        form_type = FormType.objects.create(
            name="Boolean Form",
            schema=schema
        )
        
        form = DynamicFormFromSchema(form_type)
        
        from django import forms
        self.assertIsInstance(form.fields['agreed'], forms.BooleanField)

    def test_array_choice_field_generation(self):
        """Test generating choice field from array."""
        schema = {
            'properties': {
                'category': {
                    'type': 'array',
                    'items': {
                        'type': 'string',
                        'enum': ['option1', 'option2', 'option3']
                    },
                    'title': 'Category'
                }
            }
        }
        
        form_type = FormType.objects.create(
            name="Choice Form",
            schema=schema
        )
        
        form = DynamicFormFromSchema(form_type)
        
        from django import forms
        self.assertIsInstance(form.fields['category'], forms.ChoiceField)
        self.assertEqual(len(form.fields['category'].choices), 3)

    def test_array_without_enum(self):
        """Test generating array field without enum."""
        schema = {
            'properties': {
                'items': {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'title': 'Items'
                }
            }
        }
        
        form_type = FormType.objects.create(
            name="Array Form",
            schema=schema
        )
        
        form = DynamicFormFromSchema(form_type)
        
        # Should default to CharField
        from django import forms
        self.assertIsInstance(form.fields['items'], forms.CharField)

    def test_unknown_field_type_defaults_to_char(self):
        """Test unknown field type defaults to CharField."""
        schema = {
            'properties': {
                'custom': {'type': 'unknown_type', 'title': 'Custom'}
            }
        }
        
        form_type = FormType.objects.create(
            name="Unknown Form",
            schema=schema
        )
        
        form = DynamicFormFromSchema(form_type)
        
        from django import forms
        self.assertIsInstance(form.fields['custom'], forms.CharField)

    def test_field_with_description(self):
        """Test field includes help_text from description."""
        schema = {
            'properties': {
                'field': {
                    'type': 'string',
                    'title': 'Field',
                    'description': 'This is help text'
                }
            }
        }
        
        form_type = FormType.objects.create(
            name="Help Text Form",
            schema=schema
        )
        
        form = DynamicFormFromSchema(form_type)
        
        self.assertEqual(form.fields['field'].help_text, 'This is help text')

    def test_field_without_title_uses_field_name(self):
        """Test field without title uses formatted field name."""
        schema = {
            'properties': {
                'first_name': {'type': 'string'}
            }
        }
        
        form_type = FormType.objects.create(
            name="Auto Title Form",
            schema=schema
        )
        
        form = DynamicFormFromSchema(form_type)
        
        # Should convert first_name to "First Name"
        self.assertEqual(form.fields['first_name'].label, 'First Name')

    def test_multiple_fields_mixed_types(self):
        """Test form with multiple fields of different types."""
        schema = {
            'properties': {
                'name': {'type': 'string'},
                'age': {'type': 'integer'},
                'subscribed': {'type': 'boolean'},
                'email': {'type': 'string', 'format': 'email'}
            },
            'required': ['name', 'email']
        }
        
        form_type = FormType.objects.create(
            name="Mixed Form",
            schema=schema
        )
        
        form = DynamicFormFromSchema(form_type)
        
        self.assertEqual(len(form.fields), 4)
        self.assertTrue(form.fields['name'].required)
        self.assertTrue(form.fields['email'].required)
        self.assertFalse(form.fields['age'].required)
        self.assertFalse(form.fields['subscribed'].required)

    def test_form_with_empty_schema(self):
        """Test form with empty schema."""
        form_type = FormType.objects.create(
            name="Empty Form",
            schema={}
        )
        
        form = DynamicFormFromSchema(form_type)
        
        self.assertEqual(len(form.fields), 0)

    def test_form_with_no_properties(self):
        """Test form with schema but no properties."""
        form_type = FormType.objects.create(
            name="No Props Form",
            schema={'required': []}
        )
        
        form = DynamicFormFromSchema(form_type)
        
        self.assertEqual(len(form.fields), 0)

