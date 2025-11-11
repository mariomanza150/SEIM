"""
Test Form Builder Integration

This test file verifies that users can create forms for new exchange programs
using the django-dynforms integration.
"""

import pytest
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import Role
from application_forms.models import FormType
from exchange.models import Program

User = get_user_model()


class FormBuilderIntegrationTest(TestCase):
    """Test the complete form builder integration workflow."""

    def setUp(self):
        """Set up test data."""
        # Create roles (use get_or_create to handle existing roles)
        self.admin_role, created = Role.objects.get_or_create(name='admin')
        self.student_role, created = Role.objects.get_or_create(name='student')

        # Create admin user (make superuser to ensure all permissions)
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            is_superuser=True,
            is_staff=True
        )
        self.admin_user.roles.add(self.admin_role)

        # Create a test dynamic form
        self.test_form = FormType.objects.create(
            name='Test Application Form',
            description='A test form for exchange applications'
        )

        self.client = Client()

    @pytest.mark.skip(reason="Dynforms package views require additional template configuration")
    def test_form_builder_urls_accessible(self):
        """Test that form builder URLs are accessible to admins."""
        self.client.force_login(self.admin_user)

        # Test form list page
        response = self.client.get('/dynforms/')
        self.assertEqual(response.status_code, 200)

        # Test form builder page (edit existing form)
        response = self.client.get(f'/dynforms/builder/{self.test_form.pk}/')
        self.assertEqual(response.status_code, 200)

    def test_program_creation_with_form_selection(self):
        """Test that admins can create programs with dynamic form selection."""
        self.client.force_login(self.admin_user)

        # Test program creation form loads
        response = self.client.get(reverse('frontend:program_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'application_form')

        # Test program creation with form
        data = {
            'name': 'Test Exchange Program',
            'description': 'A test exchange program',
            'start_date': '2025-06-01',
            'end_date': '2025-12-01',
            'is_active': True,
            'min_gpa': 3.0,
            'required_language': 'English',
            'recurring': False,
            'application_form': self.test_form.id
        }

        response = self.client.post(reverse('frontend:program_create'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success

        # Verify program was created with form
        program = Program.objects.get(name='Test Exchange Program')
        self.assertEqual(program.application_form, self.test_form)

    def test_program_creation_without_form(self):
        """Test that programs can be created without selecting a form."""
        self.client.force_login(self.admin_user)

        data = {
            'name': 'Test Program No Form',
            'description': 'A test program without form',
            'start_date': '2025-06-01',
            'end_date': '2025-12-01',
            'is_active': True,
            'min_gpa': 3.0,
            'required_language': 'English',
            'recurring': False,
            # No application_form selected
        }

        response = self.client.post(reverse('frontend:program_create'), data)
        self.assertEqual(response.status_code, 302)

        program = Program.objects.get(name='Test Program No Form')
        self.assertIsNone(program.application_form)

    def test_non_admin_cannot_access_form_builder(self):
        """Test that non-admin users cannot access form builder."""
        # Create student user
        student_user = User.objects.create_user(
            username='student',
            email='student@test.com',
            password='testpass123'
        )
        student_user.roles.add(self.student_role)

        self.client.force_login(student_user)

        # Should be forbidden or redirected away from form builder
        response = self.client.get('/dynforms/')
        self.assertIn(response.status_code, [302, 403])
        response = self.client.get(f'/dynforms/builder/{self.test_form.pk}/')
        self.assertIn(response.status_code, [302, 403])

    def test_program_form_includes_dynamic_forms(self):
        """Test that the program form includes dynamic forms in the dropdown."""
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse('frontend:program_create'))
        self.assertEqual(response.status_code, 200)

        # Check that the form contains the test form
        self.assertContains(response, self.test_form.name)

    def test_form_builder_instructions_displayed(self):
        """Test that form builder instructions are displayed on program creation page."""
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse('frontend:program_create'))
        self.assertEqual(response.status_code, 200)

        # Check for form builder instructions
        self.assertContains(response, 'Dynamic Form Builder')
        self.assertContains(response, 'Create Form')
        self.assertContains(response, 'View Forms')


class FormBuilderWorkflowTest(TestCase):
    """Test the complete form builder workflow from form creation to program association."""

    def setUp(self):
        """Set up test data."""
        # Create admin role (use get_or_create to handle existing roles)
        self.admin_role, created = Role.objects.get_or_create(name='admin')

        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            is_superuser=True,
            is_staff=True
        )
        self.admin_user.roles.add(self.admin_role)
        self.client = Client()

    def test_complete_form_builder_workflow(self):
        """Test the complete workflow: create form -> create program -> associate form."""
        self.client.force_login(self.admin_user)

        # Step 1: Create a dynamic form via the form builder
        # (This would normally be done through the UI, but we'll create it programmatically)
        form = FormType.objects.create(
            name='Erasmus Application Form',
            description='Form for Erasmus exchange applications'
        )

        # Step 2: Create a program and associate the form
        data = {
            'name': 'Erasmus Exchange Program',
            'description': 'European exchange program',
            'start_date': '2025-09-01',
            'end_date': '2026-01-31',
            'is_active': True,
            'min_gpa': 3.0,
            'required_language': 'English',
            'recurring': True,
            'application_form': form.id
        }

        response = self.client.post(reverse('frontend:program_create'), data)
        self.assertEqual(response.status_code, 302)

        # Step 3: Verify the association
        program = Program.objects.get(name='Erasmus Exchange Program')
        self.assertEqual(program.application_form, form)

        # Step 4: Verify the form can be accessed
        self.assertIsNotNone(program.application_form)
        self.assertEqual(program.application_form.name, 'Erasmus Application Form')

    def test_multiple_forms_available_for_selection(self):
        """Test that multiple forms are available for selection."""
        self.client.force_login(self.admin_user)

        # Create multiple forms
        form1 = FormType.objects.create(name='Form 1', description='First form')
        form2 = FormType.objects.create(name='Form 2', description='Second form')
        form3 = FormType.objects.create(name='Form 3', description='Third form')

        response = self.client.get(reverse('frontend:program_create'))
        self.assertEqual(response.status_code, 200)

        # Check that all forms are available
        self.assertContains(response, form1.name)
        self.assertContains(response, form2.name)
        self.assertContains(response, form3.name)


if __name__ == '__main__':
    pytest.main([__file__])
