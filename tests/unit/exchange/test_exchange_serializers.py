"""
Unit tests for exchange serializers.
"""

from datetime import date, timedelta
from unittest.mock import Mock, patch

from django.test import TestCase
from django.utils import timezone
from rest_framework import serializers

from accounts.models import Profile, Role, User
from application_forms.models import FormSubmission, FormType
from exchange.models import Application, ApplicationStatus, Program
from exchange.serializers import ApplicationSerializer, ProgramSerializer


class TestProgramSerializer(TestCase):
    """Test cases for ProgramSerializer."""

    def setUp(self):
        self.coordinator_role, _ = Role.objects.get_or_create(name="coordinator")
        self.coordinator = User.objects.create_user(
            username="program-coordinator",
            email="program-coordinator@example.com",
            password="TestPass123!",
        )
        self.coordinator.roles.add(self.coordinator_role)

        self.program = Program.objects.create(
            name='Test Program',
            description='desc',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=365),
            is_active=True
        )
        self.program.coordinators.add(self.coordinator)

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
        self.assertIn("application_open_date", data)
        self.assertIn("application_deadline", data)
        self.assertIn("application_window_open", data)
        self.assertIn("application_window_message", data)
        self.assertIn("coordinators", data)
        self.assertIn("coordinator_details", data)
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
            "application_open_date": "2023-11-01",
            "application_deadline": "2023-12-15",
            "start_date": "2024-01-01",
            "end_date": "2024-06-30",
            "is_active": True,
            "coordinators": [self.coordinator.id],
            "min_gpa": 3.5,
            "required_language": "Spanish",
            "recurring": True,
        }

        serializer = ProgramSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        program = serializer.save()
        self.assertEqual(program.name, "New Program")
        self.assertEqual(program.description, "A new program")
        self.assertEqual(program.application_open_date, date(2023, 11, 1))
        self.assertEqual(program.application_deadline, date(2023, 12, 15))
        self.assertEqual(program.start_date, date(2024, 1, 1))
        self.assertEqual(program.end_date, date(2024, 6, 30))
        self.assertTrue(program.is_active)
        self.assertEqual(list(program.coordinators.values_list("id", flat=True)), [self.coordinator.id])
        self.assertEqual(program.min_gpa, 3.5)
        self.assertEqual(program.required_language, "Spanish")
        self.assertTrue(program.recurring)

    def test_program_serializer_update(self):
        """Test ProgramSerializer update method."""
        program = Program.objects.create(
            name="Original Program",
            description="Original description",
            application_open_date=date(2023, 10, 1),
            application_deadline=date(2023, 12, 1),
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
            "application_deadline": "2023-12-20",
            "coordinators": [self.coordinator.id],
            "min_gpa": 3.5,
        }

        serializer = ProgramSerializer(program, data=data, partial=True)
        self.assertTrue(serializer.is_valid())

        updated_program = serializer.save()
        self.assertEqual(updated_program.name, "Updated Program")
        self.assertEqual(updated_program.description, "Updated description")
        self.assertEqual(updated_program.application_open_date, date(2023, 10, 1))
        self.assertEqual(updated_program.application_deadline, date(2023, 12, 20))
        self.assertEqual(list(updated_program.coordinators.values_list("id", flat=True)), [self.coordinator.id])
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

    def test_program_serializer_rejects_non_coordinator_assignment(self):
        non_coordinator = User.objects.create_user(
            username="not-a-coordinator",
            email="not-a-coordinator@example.com",
            password="TestPass123!",
        )
        data = {
            "name": "Program With Invalid Coordinator",
            "description": "desc",
            "start_date": "2024-01-01",
            "end_date": "2024-06-30",
            "coordinators": [non_coordinator.id],
        }

        serializer = ProgramSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("coordinators", serializer.errors)


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
        self.coordinator_role, _ = Role.objects.get_or_create(name="coordinator")
        self.coordinator = User.objects.create_user(
            username="assigned-coordinator",
            email="assigned-coordinator@example.com",
            password="TestPass123!",
        )
        self.coordinator.roles.add(self.coordinator_role)
        self.program = Program.objects.create(
            name='App Program',
            description='desc',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=365),
            is_active=True
        )
        self.program.coordinators.add(self.coordinator)
        self.form_type = FormType.objects.create(
            name='Application Questions',
            form_type='application',
            schema={
                'properties': {
                    'motivation': {'type': 'string', 'title': 'Motivation'},
                    'academic_goals': {'type': 'string', 'title': 'Academic Goals'},
                },
                'required': ['motivation', 'academic_goals'],
            },
            created_by=self.user,
        )
        self.program_with_form = Program.objects.create(
            name='App Program With Form',
            description='desc',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=365),
            is_active=True,
            application_form=self.form_type,
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
        self.assertEqual(data["program_name"], program.name)
        self.assertEqual(data["status"], "draft")
        self.assertFalse(data["withdrawn"])
        self.assertIn("assigned_coordinator", data)
        self.assertIn("assigned_coordinator_name", data)
        self.assertIn("effective_coordinator", data)
        self.assertIn("dynamic_form_submission", data)
        self.assertIsNone(data["dynamic_form_submission"])

    def test_application_serializer_includes_dynamic_form_submission(self):
        application = Application.objects.create(
            student=self.user,
            program=self.program_with_form,
            status=self.status,
        )
        submission = FormSubmission.objects.create(
            form_type=self.form_type,
            submitted_by=self.user,
            responses={
                'motivation': 'Study abroad experience',
                'academic_goals': 'Research collaboration',
            },
            program=self.program_with_form,
            application=application,
        )

        serializer = ApplicationSerializer(application)
        data = serializer.data

        self.assertIsNotNone(data["dynamic_form_submission"])
        self.assertEqual(data["dynamic_form_submission"]["id"], submission.id)
        self.assertEqual(
            data["dynamic_form_submission"]["responses"]["motivation"],
            'Study abroad experience',
        )

    def test_application_serializer_exposes_assigned_coordinator(self):
        application = Application.objects.create(
            student=self.user,
            program=self.program,
            assigned_coordinator=self.coordinator,
            status=self.status,
        )

        serializer = ApplicationSerializer(application)
        data = serializer.data

        self.assertEqual(data["assigned_coordinator"], self.coordinator.id)
        self.assertEqual(data["assigned_coordinator_name"], self.coordinator.username)
        self.assertIsNotNone(data["effective_coordinator"])
        self.assertEqual(data["effective_coordinator"]["id"], self.coordinator.id)

    @patch('exchange.serializers.ApplicationService.check_eligibility')
    @patch('exchange.serializers.ApplicationService.can_submit_application', return_value=True)
    def test_application_validate_success(self, mock_can_submit, mock_check_elig):
        data = {
            'student': self.user.id,
            'program': self.program.id
        }
        serializer = ApplicationSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_draft_create_skips_eligibility_check(self):
        """Students may save drafts while ineligible; submit still enforces eligibility."""
        profile = Profile.objects.get(user=self.user)
        profile.language = "English"
        profile.language_level = "B2"
        profile.save(update_fields=["language", "language_level"])
        german_program = Program.objects.create(
            name="German-only program",
            description="desc",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=200),
            is_active=True,
            required_language="German",
            min_language_level="B2",
        )
        data = {"program": german_program.id}
        request = Mock()
        request.user = self.user
        request.data = data
        serializer = ApplicationSerializer(data=data, context={"request": request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        application = serializer.save()
        self.assertEqual(application.program, german_program)
        self.assertEqual(application.status.name, "draft")

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
        self.assertIn('program', serializer.errors)

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
        self.assertEqual(app.assigned_coordinator, self.coordinator)

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

    def test_application_serializer_create_rejects_invalid_dynamic_form(self):
        data = {
            "program": self.program_with_form.id,
            "df_motivation": "I want an international experience.",
        }

        request = Mock()
        request.user = self.user
        request.data = data

        serializer = ApplicationSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)

        with self.assertRaises(serializers.ValidationError) as exc:
            serializer.save(student=self.user)

        self.assertIn("dynamic_form", exc.exception.detail)
        self.assertEqual(
            Application.objects.filter(program=self.program_with_form, student=self.user).count(),
            0,
        )

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

    def test_student_cannot_override_assigned_coordinator(self):
        other_coordinator = User.objects.create_user(
            username="other-coordinator",
            email="other-coordinator@example.com",
            password="TestPass123!",
        )
        other_coordinator.roles.add(self.coordinator_role)
        data = {
            "program": self.program.id,
            "assigned_coordinator": other_coordinator.id,
        }

        request = Mock()
        request.user = self.user
        request.data = data

        serializer = ApplicationSerializer(data=data, context={"request": request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        application = serializer.save(student=self.user)
        self.assertEqual(application.assigned_coordinator, self.coordinator)

    def test_coordinator_can_assign_application_coordinator_on_update(self):
        application = Application.objects.create(
            student=self.user,
            program=self.program,
            status=self.status,
        )
        request = Mock()
        request.user = self.coordinator
        request.data = {"assigned_coordinator": self.coordinator.id}

        serializer = ApplicationSerializer(
            application,
            data={"assigned_coordinator": self.coordinator.id},
            context={"request": request},
            partial=True,
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated_application = serializer.save()
        self.assertEqual(updated_application.assigned_coordinator, self.coordinator)

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
