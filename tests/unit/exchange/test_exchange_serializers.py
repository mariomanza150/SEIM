"""
Unit tests for exchange serializers.
"""

from datetime import date, timedelta
from unittest.mock import Mock, patch

from django.test import TestCase
from django.utils import timezone
from rest_framework import serializers

from accounts.models import Role, User
from exchange.models import Application, ApplicationStatus, Program
from exchange.serializers import ApplicationSerializer, ProgramSerializer


class TestProgramSerializer(TestCase):
    """Test cases for ProgramSerializer."""

    def setUp(self):
        self.program = Program.objects.create(
            name='Test Program',
            description='desc',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=365),
            is_active=True
        )

    def test_program_serialize(self):
        serializer = ProgramSerializer(self.program)
        data = serializer.data
        self.assertEqual(data['name'], 'Test Program')
        self.assertTrue(data['is_active'])

    def test_program_create(self):
        data = {
            'name': 'New Program',
            'description': 'desc',
            'start_date': timezone.now().date(),
            'end_date': timezone.now().date() + timedelta(days=100),
            'is_active': False
        }
        serializer = ProgramSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        program = serializer.save()
        self.assertEqual(program.name, 'New Program')
        self.assertFalse(program.is_active)

    def test_program_serializer_fields(self):
        """Test that ProgramSerializer includes all required fields."""
        program = Program.objects.create(
            name="Test Program",
            description="A test program",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 30),
            is_active=True,
            min_gpa=3.0,
            required_language="English",
            recurring=False,
        )

        serializer = ProgramSerializer(program)
        data = serializer.data

        self.assertIn("id", data)
        self.assertIn("name", data)
        self.assertIn("description", data)
        self.assertIn("start_date", data)
        self.assertIn("end_date", data)
        self.assertIn("is_active", data)
        self.assertIn("min_gpa", data)
        self.assertIn("required_language", data)
        self.assertIn("recurring", data)
        self.assertEqual(data["name"], "Test Program")
        self.assertEqual(data["description"], "A test program")
        self.assertTrue(data["is_active"])
        self.assertEqual(data["min_gpa"], 3.0)
        self.assertEqual(data["required_language"], "English")
        self.assertFalse(data["recurring"])

    def test_program_serializer_create(self):
        """Test ProgramSerializer create method."""
        data = {
            "name": "New Program",
            "description": "A new program",
            "start_date": "2024-01-01",
            "end_date": "2024-06-30",
            "is_active": True,
            "min_gpa": 3.5,
            "required_language": "Spanish",
            "recurring": True,
        }

        serializer = ProgramSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        program = serializer.save()
        self.assertEqual(program.name, "New Program")
        self.assertEqual(program.description, "A new program")
        self.assertEqual(program.start_date, date(2024, 1, 1))
        self.assertEqual(program.end_date, date(2024, 6, 30))
        self.assertTrue(program.is_active)
        self.assertEqual(program.min_gpa, 3.5)
        self.assertEqual(program.required_language, "Spanish")
        self.assertTrue(program.recurring)

    def test_program_serializer_update(self):
        """Test ProgramSerializer update method."""
        program = Program.objects.create(
            name="Original Program",
            description="Original description",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 30),
            is_active=True,
            min_gpa=3.0,
            required_language="English",
            recurring=False,
        )

        data = {
            "name": "Updated Program",
            "description": "Updated description",
            "min_gpa": 3.5,
        }

        serializer = ProgramSerializer(program, data=data, partial=True)
        self.assertTrue(serializer.is_valid())

        updated_program = serializer.save()
        self.assertEqual(updated_program.name, "Updated Program")
        self.assertEqual(updated_program.description, "Updated description")
        self.assertEqual(updated_program.min_gpa, 3.5)
        # Other fields should remain unchanged
        self.assertEqual(updated_program.start_date, date(2024, 1, 1))
        self.assertEqual(updated_program.end_date, date(2024, 6, 30))
        self.assertTrue(updated_program.is_active)
        self.assertEqual(updated_program.required_language, "English")
        self.assertFalse(updated_program.recurring)

    def test_program_serializer_validation(self):
        """Test ProgramSerializer validation."""
        # Test with invalid data
        data = {
            "name": "",  # Empty name should be invalid
            "description": "",  # Empty description should be invalid
            "start_date": "2024-06-30",  # Start date after end date
            "end_date": "2024-01-01",
        }

        serializer = ProgramSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)
        self.assertIn('description', serializer.errors)


class TestApplicationSerializer(TestCase):
    """Test cases for ApplicationSerializer."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='appuser',
            email='appuser@example.com',
            password='TestPass123!'
        )
        # Ensure user has 'student' role
        student_role, _ = Role.objects.get_or_create(name='student')
        self.user.roles.add(student_role)
        self.program = Program.objects.create(
            name='App Program',
            description='desc',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=365),
            is_active=True
        )
        self.status, _ = ApplicationStatus.objects.get_or_create(name='draft', defaults={'order': 1})

    def test_application_serializer_fields(self):
        """Test that ApplicationSerializer includes all required fields."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        program = Program.objects.create(
            name="Test Program",
            description="A test program",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 30),
            is_active=True,
        )
        status, _ = ApplicationStatus.objects.get_or_create(name="draft", defaults={"order": 1})
        application = Application.objects.create(
            student=user,
            program=program,
            status=status,
        )

        serializer = ApplicationSerializer(application)
        data = serializer.data

        self.assertIn("id", data)
        self.assertIn("student", data)
        self.assertIn("program", data)
        self.assertIn("status", data)
        self.assertIn("submitted_at", data)
        self.assertIn("withdrawn", data)
        self.assertEqual(data["student"], user.id)
        self.assertEqual(data["program"], program.id)
        self.assertEqual(data["status"], "draft")
        self.assertFalse(data["withdrawn"])

    @patch('exchange.serializers.ApplicationService.check_eligibility')
    @patch('exchange.serializers.ApplicationService.can_submit_application', return_value=True)
    def test_application_validate_success(self, mock_can_submit, mock_check_elig):
        data = {
            'student': self.user.id,
            'program': self.program.id
        }
        serializer = ApplicationSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_application_validate_duplicate(self):
        # Create an existing application with status 'submitted' to trigger duplicate validation
        submitted_status, _ = ApplicationStatus.objects.get_or_create(name='submitted', defaults={'order': 2})
        Application.objects.create(student=self.user, program=self.program, status=submitted_status)
        data = {
            'program': self.program.id
        }
        # Create mock request with user
        request = Mock()
        request.user = self.user
        request.data = data
        serializer = ApplicationSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

    def test_application_create_default_status(self):
        data = {
            'program': self.program.id
        }
        # Create mock request with user
        request = Mock()
        request.user = self.user
        request.data = data
        serializer = ApplicationSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        app = serializer.save(student=self.user)
        self.assertEqual(app.status.name, 'draft')

    @patch('exchange.serializers.ApplicationService.transition_status')
    def test_application_update_status_transition(self, mock_transition):
        app = Application.objects.create(student=self.user, program=self.program, status=self.status)
        request = Mock()
        request.user = self.user
        request.data = {'status': 'submitted'}
        serializer = ApplicationSerializer(app, data={'program': self.program.id}, context={'request': request}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        mock_transition.assert_called_once()

    @patch('exchange.serializers.ApplicationService.transition_status', side_effect=ValueError('Invalid transition'))
    def test_application_update_status_transition_error(self, mock_transition):
        app = Application.objects.create(student=self.user, program=self.program, status=self.status)
        request = Mock()
        request.user = self.user
        request.data = {'status': 'submitted'}
        serializer = ApplicationSerializer(app, data={'program': self.program.id}, context={'request': request}, partial=True)
        serializer.is_valid(raise_exception=True)
        with self.assertRaises(serializers.ValidationError):
            serializer.save()

    def test_application_serializer_create(self):
        """Test ApplicationSerializer create method."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        program = Program.objects.create(
            name="Test Program",
            description="A test program",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 30),
            is_active=True,
        )
        status, _ = ApplicationStatus.objects.get_or_create(name="draft", defaults={"order": 1})

        data = {
            "program": program.id,
        }

        # Create mock request with user
        request = Mock()
        request.user = user
        request.data = data
        serializer = ApplicationSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid())

        application = serializer.save(student=user)
        self.assertEqual(application.student, user)
        self.assertEqual(application.program, program)
        self.assertEqual(application.status, status)  # Should default to draft

    def test_application_serializer_update(self):
        """Test ApplicationSerializer update method."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        program = Program.objects.create(
            name="Test Program",
            description="A test program",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 30),
            is_active=True,
        )
        status, _ = ApplicationStatus.objects.get_or_create(name="draft", defaults={"order": 1})
        application = Application.objects.create(
            student=user,
            program=program,
            status=status,
        )

        data = {
            "withdrawn": True,
        }

        serializer = ApplicationSerializer(application, data=data, partial=True)
        self.assertTrue(serializer.is_valid())

        updated_application = serializer.save()
        self.assertTrue(updated_application.withdrawn)

    def test_application_serializer_validation(self):
        """Test ApplicationSerializer validation."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        Program.objects.create(
            name="Test Program",
            description="A test program",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 30),
            is_active=True,
        )

        # Test with missing required fields
        data = {
            "student": user.id,
            # Missing program
        }

        serializer = ApplicationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('program', serializer.errors)

    def test_application_serializer_read_only_fields(self):
        """Test that certain fields are read-only."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        program = Program.objects.create(
            name="Test Program",
            description="A test program",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 30),
            is_active=True,
        )
        status, _ = ApplicationStatus.objects.get_or_create(name="draft", defaults={"order": 1})
        application = Application.objects.create(
            student=user,
            program=program,
            status=status,
        )

        # submitted_at should be read-only and not change after update
        original_submitted_at = application.submitted_at
        data = {"submitted_at": "2024-01-01T00:00:00Z"}
        serializer = ApplicationSerializer(application, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_application = serializer.save()
        self.assertEqual(updated_application.submitted_at, original_submitted_at)
