"""
Additional tests for Exchange Services to reach 80%+ coverage.

Focuses on uncovered edge cases and scenarios.
"""

import pytest
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from accounts.models import Profile, Role
from application_forms.models import FormType, FormSubmission
from exchange.models import Application, ApplicationStatus, Program, TimelineEvent
from exchange.services import ApplicationService
from grades.models import GradeScale, GradeValue

User = get_user_model()


@pytest.mark.django_db
class TestEligibilityWithGradeScale(TestCase):
    """Test eligibility checking with grade scale conversion."""

    def setUp(self):
        """Set up test data."""
        self.student_role, _ = Role.objects.get_or_create(name="student")
        
        self.student = User.objects.create_user(
            username="student",
            email="student@test.com",
            password="testpass123"
        )
        self.student.roles.add(self.student_role)
        
        # Create grade scale
        self.grade_scale = GradeScale.objects.create(
            name="US GPA",
            code="US_GPA",
            min_value=0.0,
            max_value=4.0,
            passing_value=2.0
        )
        
        # Create grade values
        self.grade_a = GradeValue.objects.create(
            grade_scale=self.grade_scale,
            label="A",
            numeric_value=4.0,
            gpa_equivalent=4.0,
            order=1
        )
        
        self.grade_b = GradeValue.objects.create(
            grade_scale=self.grade_scale,
            label="B",
            numeric_value=3.0,
            gpa_equivalent=3.0,
            order=2
        )
        
        self.grade_c = GradeValue.objects.create(
            grade_scale=self.grade_scale,
            label="C",
            numeric_value=2.0,
            gpa_equivalent=2.0,
            order=3
        )
        
        # Get auto-created profile and update it
        self.profile = self.student.profile
        self.profile.gpa = 3.5
        self.profile.grade_scale = self.grade_scale
        self.profile.save()
        
        # Create program
        today = date.today()
        self.program = Program.objects.create(
            name="GPA Test Program",
            description="Test",
            start_date=today,
            end_date=today + timedelta(days=365),
            is_active=True,
            min_gpa=3.0
        )

    def test_eligibility_with_gpa_equivalent_above_requirement(self):
        """Test eligibility when GPA equivalent is above requirement."""
        # Student has 3.5, program requires 3.0
        ApplicationService.check_eligibility(self.student, self.program)
        # Should not raise - student is eligible

    def test_eligibility_with_gpa_equivalent_below_requirement(self):
        """Test eligibility when GPA equivalent is below requirement."""
        # Use GPA 2.0 which maps to grade C with gpa_equivalent 2.0
        self.profile.gpa = 2.0
        self.profile.save()
        
        self.program.min_gpa = 3.5
        self.program.save()
        
        with self.assertRaises(ValueError) as context:
            ApplicationService.check_eligibility(self.student, self.program)
        
        self.assertIn('GPA below', str(context.exception))

    def test_eligibility_without_grade_scale_direct_comparison(self):
        """Test eligibility uses direct GPA comparison when no grade scale."""
        # Remove grade scale
        self.profile.grade_scale = None
        self.profile.gpa = 2.5
        self.profile.save()
        
        self.program.min_gpa = 3.0
        self.program.save()
        
        with self.assertRaises(ValueError) as context:
            ApplicationService.check_eligibility(self.student, self.program)
        
        # Should use direct comparison
        self.assertIn('GPA below', str(context.exception))


@pytest.mark.django_db
class TestEligibilityLanguageLevel(TestCase):
    """Test language level eligibility checking."""

    def setUp(self):
        """Set up test data."""
        self.student_role, _ = Role.objects.get_or_create(name="student")
        
        self.student = User.objects.create_user(
            username="student",
            email="student@test.com",
            password="testpass123"
        )
        self.student.roles.add(self.student_role)
        
        # Get auto-created profile and update it
        self.profile = self.student.profile
        self.profile.language = "English"
        self.profile.language_level = "B1"
        self.profile.save()
        
        today = date.today()
        self.program = Program.objects.create(
            name="Language Test Program",
            description="Test",
            start_date=today,
            end_date=today + timedelta(days=365),
            is_active=True,
            required_language="English",
            min_language_level="B2"
        )

    def test_eligibility_language_level_below_requirement(self):
        """Test eligibility fails when language level below requirement."""
        # Student has B1, program requires B2
        with self.assertRaises(ValueError) as context:
            ApplicationService.check_eligibility(self.student, self.program)
        
        self.assertIn('Language proficiency below requirement', str(context.exception))

    def test_eligibility_language_level_meets_requirement(self):
        """Test eligibility passes when language level meets requirement."""
        # Update student to B2
        self.profile.language_level = "B2"
        self.profile.save()
        
        # Should not raise
        ApplicationService.check_eligibility(self.student, self.program)

    def test_eligibility_language_level_not_specified(self):
        """Test eligibility fails when language level not specified."""
        # Remove student's language level
        self.profile.language_level = None
        self.profile.save()
        
        with self.assertRaises(ValueError) as context:
            ApplicationService.check_eligibility(self.student, self.program)
        
        self.assertIn('Language proficiency not specified', str(context.exception))


@pytest.mark.django_db
class TestEligibilityAge(TestCase):
    """Test age-based eligibility checking."""

    def setUp(self):
        """Set up test data."""
        self.student_role, _ = Role.objects.get_or_create(name="student")
        
        self.student = User.objects.create_user(
            username="student",
            email="student@test.com",
            password="testpass123"
        )
        self.student.roles.add(self.student_role)
        
        # Get auto-created profile and update it with age (20 years old)
        self.profile = self.student.profile
        self.profile.date_of_birth = date.today() - timedelta(days=365*20)
        self.profile.save()
        
        today = date.today()
        self.program = Program.objects.create(
            name="Age Test Program",
            description="Test",
            start_date=today,
            end_date=today + timedelta(days=365),
            is_active=True,
            min_age=18,
            max_age=25
        )

    def test_eligibility_age_within_range(self):
        """Test eligibility passes when age within range."""
        # Student is 20, program accepts 18-25
        ApplicationService.check_eligibility(self.student, self.program)
        # Should not raise

    def test_eligibility_age_too_young(self):
        """Test eligibility fails when too young."""
        # Set student to 16 years old
        self.profile.date_of_birth = date.today() - timedelta(days=365*16)
        self.profile.save()
        
        with self.assertRaises(ValueError) as context:
            ApplicationService.check_eligibility(self.student, self.program)
        
        self.assertIn('age', str(context.exception).lower())

    def test_eligibility_age_too_old(self):
        """Test eligibility fails when too old."""
        # Set student to 30 years old
        self.profile.date_of_birth = date.today() - timedelta(days=365*30)
        self.profile.save()
        
        with self.assertRaises(ValueError) as context:
            ApplicationService.check_eligibility(self.student, self.program)
        
        self.assertIn('age', str(context.exception).lower())


@pytest.mark.django_db
class TestDynamicFormProcessing(TestCase):
    """Test dynamic form submission processing."""

    def setUp(self):
        """Set up test data."""
        self.student_role, _ = Role.objects.get_or_create(name="student")
        
        self.student = User.objects.create_user(
            username="student",
            email="student@test.com",
            password="testpass123"
        )
        self.student.roles.add(self.student_role)
        
        # Create form type
        self.form_type = FormType.objects.create(
            name="Application Form",
            form_type='application',
            schema={
                'properties': {
                    'motivation': {'type': 'string', 'title': 'Motivation'},
                    'experience': {'type': 'string', 'title': 'Experience'}
                },
                'required': ['motivation']
            }
        )
        
        today = date.today()
        self.program = Program.objects.create(
            name="Form Test Program",
            description="Test",
            start_date=today,
            end_date=today + timedelta(days=365),
            is_active=True,
            application_form=self.form_type
        )
        
        status, _ = ApplicationStatus.objects.get_or_create(
            name="draft",
            defaults={'order': 1}
        )
        
        self.application = Application.objects.create(
            student=self.student,
            program=self.program,
            status=status
        )

    def test_process_dynamic_form_creates_submission(self):
        """Test processing dynamic form creates submission."""
        form_data = {
            'df_motivation': 'I want to study abroad',
            'df_experience': 'Previous internship'
        }
        
        submission = ApplicationService.process_dynamic_form_submission(
            application=self.application,
            form_data=form_data,
            user=self.student
        )
        
        self.assertIsNotNone(submission)
        self.assertEqual(submission.form_type, self.form_type)
        self.assertEqual(submission.responses['motivation'], 'I want to study abroad')
        self.assertEqual(submission.responses['experience'], 'Previous internship')

    def test_process_dynamic_form_updates_existing(self):
        """Test processing dynamic form updates existing submission."""
        # Create initial submission
        form_data1 = {
            'df_motivation': 'Initial motivation',
            'df_experience': 'Initial experience'
        }
        
        submission1 = ApplicationService.process_dynamic_form_submission(
            application=self.application,
            form_data=form_data1,
            user=self.student
        )
        
        # Update with new data
        form_data2 = {
            'df_motivation': 'Updated motivation',
            'df_experience': 'Updated experience'
        }
        
        submission2 = ApplicationService.process_dynamic_form_submission(
            application=self.application,
            form_data=form_data2,
            user=self.student
        )
        
        # Should be same submission, updated
        self.assertEqual(submission1.id, submission2.id)
        submission1.refresh_from_db()
        self.assertEqual(submission1.responses['motivation'], 'Updated motivation')

    def test_process_dynamic_form_creates_timeline_event(self):
        """Test processing dynamic form creates timeline event."""
        form_data = {
            'df_motivation': 'Test motivation'
        }
        
        ApplicationService.process_dynamic_form_submission(
            application=self.application,
            form_data=form_data,
            user=self.student
        )
        
        # Verify timeline event created
        timeline_events = TimelineEvent.objects.filter(
            application=self.application,
            event_type="form_submitted"
        )
        
        self.assertEqual(timeline_events.count(), 1)

    def test_process_dynamic_form_no_form_configured(self):
        """Test processing when program has no dynamic form."""
        # Remove form from program
        self.program.application_form = None
        self.program.save()
        
        form_data = {
            'df_field': 'value'
        }
        
        result = ApplicationService.process_dynamic_form_submission(
            application=self.application,
            form_data=form_data,
            user=self.student
        )
        
        # Should return None
        self.assertIsNone(result)

    def test_process_dynamic_form_no_dynamic_data(self):
        """Test processing when no df_ fields provided."""
        form_data = {
            'regular_field': 'value'  # No df_ prefix
        }
        
        result = ApplicationService.process_dynamic_form_submission(
            application=self.application,
            form_data=form_data,
            user=self.student
        )
        
        # Should return None (no dynamic form data)
        self.assertIsNone(result)

    def test_process_dynamic_form_validation_error(self):
        """Test processing with invalid form data."""
        # Missing required field
        form_data = {
            'df_experience': 'Experience only'
            # Missing required 'motivation'
        }
        
        with self.assertRaises(ValidationError) as context:
            ApplicationService.process_dynamic_form_submission(
                application=self.application,
                form_data=form_data,
                user=self.student
            )
        
        self.assertIn('validation failed', str(context.exception).lower())

    def test_get_dynamic_form_submission_exists(self):
        """Test retrieving existing dynamic form submission."""
        # Create submission
        form_data = {
            'df_motivation': 'Test motivation'
        }
        
        submission = ApplicationService.process_dynamic_form_submission(
            application=self.application,
            form_data=form_data,
            user=self.student
        )
        
        # Retrieve it
        retrieved = ApplicationService.get_dynamic_form_submission(self.application)
        
        self.assertEqual(retrieved.id, submission.id)

    def test_get_dynamic_form_submission_none(self):
        """Test retrieving when no submission exists."""
        result = ApplicationService.get_dynamic_form_submission(self.application)
        
        self.assertIsNone(result)

    def test_get_dynamic_form_submission_no_form_configured(self):
        """Test retrieving submission when program has no form."""
        # Remove form from program
        self.program.application_form = None
        self.program.save()
        
        result = ApplicationService.get_dynamic_form_submission(self.application)
        
        self.assertIsNone(result)


@pytest.mark.django_db
class TestEligibilityEdgeCases(TestCase):
    """Test additional eligibility edge cases."""

    def setUp(self):
        """Set up test data."""
        self.student_role, _ = Role.objects.get_or_create(name="student")
        
        self.student = User.objects.create_user(
            username="student",
            email="student@test.com",
            password="testpass123"
        )
        self.student.roles.add(self.student_role)
        
        # Get auto-created profile
        self.profile = self.student.profile
        
        today = date.today()
        self.program = Program.objects.create(
            name="Test Program",
            description="Test",
            start_date=today,
            end_date=today + timedelta(days=365),
            is_active=True
        )

    def test_eligibility_no_profile(self):
        """Test eligibility check when user has no profile."""
        # Delete profile
        self.profile.delete()
        
        # Should handle gracefully
        try:
            ApplicationService.check_eligibility(self.student, self.program)
        except ValueError:
            # Expected if profile is required
            pass

    def test_eligibility_language_requirement_met(self):
        """Test eligibility passes when language requirement met."""
        self.profile.language = "Spanish"
        self.profile.save()
        
        self.program.required_language = "Spanish"
        self.program.save()
        
        # Should not raise
        ApplicationService.check_eligibility(self.student, self.program)

    def test_eligibility_language_requirement_not_met(self):
        """Test eligibility fails when language requirement not met."""
        self.profile.language = "French"
        self.profile.save()
        
        self.program.required_language = "Spanish"
        self.program.save()
        
        with self.assertRaises(ValueError) as context:
            ApplicationService.check_eligibility(self.student, self.program)
        
        self.assertIn('Language requirement not met', str(context.exception))

    def test_eligibility_language_not_specified(self):
        """Test eligibility when student language not specified."""
        self.profile.language = None
        self.profile.save()
        
        self.program.required_language = "Spanish"
        self.program.save()
        
        with self.assertRaises(ValueError) as context:
            ApplicationService.check_eligibility(self.student, self.program)
        
        self.assertIn('Language requirement not met', str(context.exception))


@pytest.mark.django_db
class TestCanWithdrawApplication(TestCase):
    """Test can_withdraw_application method."""

    def setUp(self):
        """Set up test data."""
        self.student_role, _ = Role.objects.get_or_create(name="student")
        
        self.student = User.objects.create_user(
            username="student",
            email="student@test.com",
            password="testpass123"
        )
        self.student.roles.add(self.student_role)
        
        today = date.today()
        self.program = Program.objects.create(
            name="Test Program",
            description="Test",
            start_date=today,
            end_date=today + timedelta(days=365),
            is_active=True
        )
        
        self.draft_status, _ = ApplicationStatus.objects.get_or_create(
            name="draft",
            defaults={'order': 1}
        )
        
        self.submitted_status, _ = ApplicationStatus.objects.get_or_create(
            name="submitted",
            defaults={'order': 2}
        )

    def test_can_withdraw_draft_application(self):
        """Test can withdraw draft application."""
        application = Application.objects.create(
            student=self.student,
            program=self.program,
            status=self.draft_status
        )
        
        result = ApplicationService.can_withdraw_application(application)
        
        self.assertTrue(result)

    def test_can_withdraw_submitted_application(self):
        """Test can withdraw submitted application."""
        application = Application.objects.create(
            student=self.student,
            program=self.program,
            status=self.submitted_status
        )
        
        result = ApplicationService.can_withdraw_application(application)
        
        self.assertTrue(result)

    def test_cannot_withdraw_already_withdrawn(self):
        """Test cannot withdraw already withdrawn application."""
        application = Application.objects.create(
            student=self.student,
            program=self.program,
            status=self.draft_status,
            withdrawn=True
        )
        
        result = ApplicationService.can_withdraw_application(application)
        
        self.assertFalse(result)


@pytest.mark.django_db
class TestProcessDynamicFormStepVisibleWhen(TestCase):
    """Multi-step save advances over the visible step sequence only."""

    def setUp(self):
        self.student_role, _ = Role.objects.get_or_create(name="student")
        self.student = User.objects.create_user(
            username="vw_student",
            email="vw_student@test.com",
            password="testpass123",
        )
        self.student.roles.add(self.student_role)

        self.form_type = FormType.objects.create(
            name="Visible When Form",
            form_type="application",
            schema={
                "type": "object",
                "properties": {
                    "branch": {"type": "string"},
                    "a": {"type": "string"},
                    "b": {"type": "string"},
                },
                "required": ["branch", "a", "b"],
            },
            step_definitions=[
                {"key": "s1", "title": "One", "field_names": ["branch"]},
                {
                    "key": "s2",
                    "title": "Two",
                    "field_names": ["a"],
                    "visible_when": {"field": "branch", "equals": "extra"},
                },
                {"key": "s3", "title": "Three", "field_names": ["b"]},
            ],
        )
        today = date.today()
        self.program = Program.objects.create(
            name="VW Program",
            description="Test",
            start_date=today,
            end_date=today + timedelta(days=365),
            is_active=True,
            application_form=self.form_type,
        )
        status, _ = ApplicationStatus.objects.get_or_create(
            name="draft",
            defaults={"order": 1},
        )
        self.application = Application.objects.create(
            student=self.student,
            program=self.program,
            status=status,
        )

    def test_advances_s1_to_s3_when_s2_hidden(self):
        ApplicationService.process_dynamic_form_submission(
            application=self.application,
            form_data={
                "df_branch": "skip",
                "dynamic_form_current_step": "s1",
            },
            user=self.student,
        )
        self.application.refresh_from_db()
        self.assertEqual(self.application.dynamic_form_current_step, "s1")

        ApplicationService.process_dynamic_form_submission(
            application=self.application,
            form_data={
                "df_branch": "skip",
                "dynamic_form_current_step": "s1",
            },
            user=self.student,
        )
        self.application.refresh_from_db()
        self.assertEqual(self.application.dynamic_form_current_step, "s3")

    def test_rejects_step_not_visible(self):
        with self.assertRaises(ValidationError):
            ApplicationService.process_dynamic_form_submission(
                application=self.application,
                form_data={
                    "df_a": "x",
                    "dynamic_form_current_step": "s2",
                },
                user=self.student,
            )

