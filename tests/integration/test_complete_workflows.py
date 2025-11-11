"""
Integration tests for complete user workflows.

Tests end-to-end scenarios including:
- Student registration and application submission
- Document upload and validation
- Notification delivery
- Grade translation workflows
"""

import pytest
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse

from accounts.models import Role, Profile
from application_forms.models import FormType, FormSubmission
from documents.models import Document
from exchange.models import Program, Application, ApplicationStatus
from grades.models import GradeScale, GradeValue, GradeTranslation
from notifications.models import Notification, NotificationPreference, NotificationType

User = get_user_model()


@pytest.mark.django_db
class TestStudentApplicationWorkflow(TestCase):
    """Test complete workflow from registration to application submission."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        
        # Create roles
        self.student_role, _ = Role.objects.get_or_create(name="student")
        self.coordinator_role, _ = Role.objects.get_or_create(name="coordinator")
        
        # Create application statuses
        self.draft_status, _ = ApplicationStatus.objects.get_or_create(
            name="draft",
            defaults={'order': 1}
        )
        self.submitted_status, _ = ApplicationStatus.objects.get_or_create(
            name="submitted",
            defaults={'order': 2}
        )
        self.approved_status, _ = ApplicationStatus.objects.get_or_create(
            name="approved",
            defaults={'order': 3}
        )
        
        # Create program
        today = date.today()
        self.program = Program.objects.create(
            name="Exchange Program 2025",
            description="Test exchange program",
            start_date=today + timedelta(days=30),
            end_date=today + timedelta(days=365),
            is_active=True,
            min_gpa=3.0
        )

    def test_complete_student_workflow(self):
        """Test full workflow: registration -> application -> submission."""
        # Step 1: Student registers
        register_data = {
            'username': 'newstudent',
            'email': 'newstudent@university.edu',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'first_name': 'New',
            'last_name': 'Student'
        }
        
        # Note: Using direct user creation since we don't have registration API
        student = User.objects.create_user(
            username=register_data['username'],
            email=register_data['email'],
            password=register_data['password'],
            first_name=register_data['first_name'],
            last_name=register_data['last_name']
        )
        student.roles.add(self.student_role)
        
        # Update profile with required info
        profile = student.profile
        profile.gpa = 3.5
        profile.save()
        
        # Step 2: Student logs in and creates draft application
        self.client.force_login(student)
        
        # Create draft application
        application = Application.objects.create(
            student=student,
            program=self.program,
            status=self.draft_status
        )
        
        self.assertEqual(application.status, self.draft_status)
        self.assertEqual(application.student, student)
        
        # Step 3: Submit application
        from exchange.services import ApplicationService
        
        # Check eligibility
        ApplicationService.check_eligibility(student, self.program)
        
        # Submit application
        ApplicationService.submit_application(application, student)
        
        application.refresh_from_db()
        self.assertEqual(application.status.name, "submitted")
        
        # Step 4: Verify notification was created
        notifications = Notification.objects.filter(recipient=student)
        self.assertGreater(notifications.count(), 0)

    def test_application_workflow_with_documents(self):
        """Test application workflow including document upload."""
        # Create student
        student = User.objects.create_user(
            username='docstudent',
            email='docstudent@university.edu',
            password='TestPass123!'
        )
        student.roles.add(self.student_role)
        
        # Update profile
        profile = student.profile
        profile.gpa = 3.7
        profile.save()
        
        # Create application
        application = Application.objects.create(
            student=student,
            program=self.program,
            status=self.draft_status
        )
        
        # Upload document
        file_content = b'Test document content'
        uploaded_file = SimpleUploadedFile(
            "transcript.pdf",
            file_content,
            content_type="application/pdf"
        )
        
        document = Document.objects.create(
            application=application,
            document_type='transcript',
            file=uploaded_file,
            uploaded_by=student
        )
        
        self.assertEqual(document.application, application)
        self.assertEqual(document.uploaded_by, student)
        
        # Submit application
        from exchange.services import ApplicationService
        ApplicationService.submit_application(application, student)
        
        application.refresh_from_db()
        self.assertEqual(application.status.name, "submitted")

    def test_application_rejection_ineligible_gpa(self):
        """Test that ineligible student cannot submit application."""
        # Create student with low GPA
        student = User.objects.create_user(
            username='lowgpa',
            email='lowgpa@university.edu',
            password='TestPass123!'
        )
        student.roles.add(self.student_role)
        
        # Update profile with GPA below minimum
        profile = student.profile
        profile.gpa = 2.5  # Below program minimum of 3.0
        profile.save()
        
        # Try to create application
        application = Application.objects.create(
            student=student,
            program=self.program,
            status=self.draft_status
        )
        
        # Try to submit - should raise ValueError
        from exchange.services import ApplicationService
        
        with self.assertRaises(ValueError) as context:
            ApplicationService.submit_application(application, student)
        
        self.assertIn('GPA below', str(context.exception))


@pytest.mark.django_db
class TestCoordinatorWorkflow(TestCase):
    """Test coordinator workflow for reviewing applications."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        
        # Create roles
        self.student_role, _ = Role.objects.get_or_create(name="student")
        self.coordinator_role, _ = Role.objects.get_or_create(name="coordinator")
        
        # Create statuses
        self.draft_status, _ = ApplicationStatus.objects.get_or_create(
            name="draft",
            defaults={'order': 1}
        )
        self.submitted_status, _ = ApplicationStatus.objects.get_or_create(
            name="submitted",
            defaults={'order': 2}
        )
        self.approved_status, _ = ApplicationStatus.objects.get_or_create(
            name="approved",
            defaults={'order': 3}
        )
        
        # Create coordinator
        self.coordinator = User.objects.create_user(
            username='coordinator1',
            email='coordinator@university.edu',
            password='CoordPass123!'
        )
        self.coordinator.roles.add(self.coordinator_role)
        
        # Create student
        self.student = User.objects.create_user(
            username='applicant',
            email='applicant@university.edu',
            password='StudentPass123!'
        )
        self.student.roles.add(self.student_role)
        self.student.profile.gpa = 3.5
        self.student.profile.save()
        
        # Create program
        today = date.today()
        self.program = Program.objects.create(
            name="Test Program",
            description="Test",
            start_date=today,
            end_date=today + timedelta(days=365),
            is_active=True
        )
        
        # Create submitted application
        self.application = Application.objects.create(
            student=self.student,
            program=self.program,
            status=self.submitted_status
        )

    def test_coordinator_approves_application(self):
        """Test coordinator approving an application."""
        self.client.force_login(self.coordinator)
        
        # Approve application
        from exchange.services import ApplicationService
        
        ApplicationService.transition_status(
            self.application,
            self.coordinator,
            "approved"
        )
        
        self.application.refresh_from_db()
        self.assertEqual(self.application.status.name, "approved")
        
        # Verify notification sent to student
        notifications = Notification.objects.filter(recipient=self.student)
        self.assertGreater(notifications.count(), 0)

    def test_coordinator_adds_comment(self):
        """Test coordinator adding comments to application."""
        self.client.force_login(self.coordinator)
        
        # Add comment
        from exchange.services import ApplicationService
        
        comment = ApplicationService.add_comment(
            self.application,
            self.coordinator,
            "Application looks good, approving.",
            is_private=False
        )
        
        self.assertEqual(comment.author, self.coordinator)
        self.assertEqual(comment.application, self.application)

    def test_student_cannot_approve_application(self):
        """Test that students cannot approve their own applications."""
        self.client.force_login(self.student)
        
        # Try to approve - should raise ValueError
        from exchange.services import ApplicationService
        
        with self.assertRaises(ValueError) as context:
            ApplicationService.transition_status(
                self.application,
                self.student,
                "approved"
            )
        
        self.assertIn('not authorized', str(context.exception).lower())


@pytest.mark.django_db
class TestGradeTranslationWorkflow(TestCase):
    """Test grade translation workflow."""

    def setUp(self):
        """Set up test data."""
        # Create grade scales
        self.us_scale = GradeScale.objects.create(
            name="US GPA",
            code="US_GPA",
            min_value=0.0,
            max_value=4.0,
            passing_value=2.0
        )
        
        self.german_scale = GradeScale.objects.create(
            name="German Scale",
            code="DE_SCALE",
            min_value=1.0,
            max_value=6.0,
            passing_value=4.0
        )
        
        # Create US grades
        GradeValue.objects.create(
            grade_scale=self.us_scale,
            label="A",
            numeric_value=4.0,
            gpa_equivalent=4.0,
            order=1
        )
        
        GradeValue.objects.create(
            grade_scale=self.us_scale,
            label="B",
            numeric_value=3.0,
            gpa_equivalent=3.0,
            order=2
        )
        
        # Create German grades
        GradeValue.objects.create(
            grade_scale=self.german_scale,
            label="1 (sehr gut)",
            numeric_value=1.0,
            gpa_equivalent=4.0,
            order=1
        )
        
        GradeValue.objects.create(
            grade_scale=self.german_scale,
            label="2 (gut)",
            numeric_value=2.0,
            gpa_equivalent=3.0,
            order=2
        )

    def test_grade_translation_workflow(self):
        """Test translating grades between scales."""
        from grades.services import GradeTranslationService
        
        # Get German grade "1"
        german_grade = GradeValue.objects.get(
            grade_scale=self.german_scale,
            numeric_value=1.0
        )
        
        # Create translation first (simulate existing translation)
        from grades.models import GradeTranslation
        us_a = GradeValue.objects.get(
            grade_scale=self.us_scale,
            numeric_value=4.0
        )
        
        GradeTranslation.objects.create(
            source_grade=german_grade,
            target_grade=us_a,
            confidence_score=1.0,
            translation_method='direct'
        )
        
        # Translate to US scale using the service (uses IDs not objects)
        us_equivalent = GradeTranslationService.translate_grade(
            source_grade_value_id=str(german_grade.id),
            target_scale_id=str(self.us_scale.id)
        )
        
        self.assertIsNotNone(us_equivalent)
        self.assertEqual(us_equivalent.gpa_equivalent, 4.0)

    def test_gpa_conversion_workflow(self):
        """Test GPA conversion between scales."""
        from grades.services import GradeTranslationService
        
        # Test that GPA equivalents work across scales
        # Get US grade B (3.0)
        us_b = GradeValue.objects.get(
            grade_scale=self.us_scale,
            numeric_value=3.0
        )
        
        # Its GPA equivalent should be accessible
        self.assertEqual(us_b.gpa_equivalent, 3.0)
        
        # German grade 2 should have same GPA equivalent
        german_2 = GradeValue.objects.get(
            grade_scale=self.german_scale,
            numeric_value=2.0
        )
        
        self.assertEqual(german_2.gpa_equivalent, 3.0)


@pytest.mark.django_db
class TestNotificationWorkflow(TestCase):
    """Test notification delivery workflow."""

    def setUp(self):
        """Set up test data."""
        self.student = User.objects.create_user(
            username='notifstudent',
            email='notif@university.edu',
            password='TestPass123!'
        )
        
        # Create notification types
        self.email_type, _ = NotificationType.objects.get_or_create(
            name='email'
        )
        
        self.sms_type, _ = NotificationType.objects.get_or_create(
            name='sms'
        )

    def test_notification_delivery_workflow(self):
        """Test that notifications are created and delivered."""
        from notifications.services import NotificationService
        
        # Send notification
        notification = NotificationService.send_notification(
            user=self.student,
            title="Test Notification",
            message="This is a test message",
            notification_type=self.email_type
        )
        
        self.assertIsNotNone(notification)
        self.assertEqual(notification.recipient, self.student)
        self.assertFalse(notification.is_read)

    def test_notification_preference_workflow(self):
        """Test notification preferences are respected."""
        from notifications.services import NotificationService
        
        # Disable email notifications
        NotificationService.set_preference(
            user=self.student,
            notification_type=self.email_type,
            enabled=False
        )
        
        # Check preference
        is_enabled = NotificationService.is_enabled(
            self.student,
            self.email_type
        )
        
        self.assertFalse(is_enabled)

    def test_mark_notification_as_read(self):
        """Test marking notifications as read."""
        from notifications.services import NotificationService
        
        # Create notification
        notification = NotificationService.send_notification(
            user=self.student,
            title="Test",
            message="Test message",
            notification_type=self.email_type
        )
        
        # Mark as read
        NotificationService.mark_notification_as_read(notification.id)
        
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)


@pytest.mark.django_db
class TestDynamicFormWorkflow(TestCase):
    """Test dynamic form submission workflow."""

    def setUp(self):
        """Set up test data."""
        self.student_role, _ = Role.objects.get_or_create(name="student")
        
        self.student = User.objects.create_user(
            username='formstudent',
            email='form@university.edu',
            password='TestPass123!'
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
            },
            created_by=self.student
        )
        
        # Create program with form
        today = date.today()
        self.program = Program.objects.create(
            name="Form Test Program",
            description="Test",
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

    def test_dynamic_form_submission_workflow(self):
        """Test submitting dynamic form with application."""
        from exchange.services import ApplicationService
        
        # Submit form
        form_data = {
            'df_motivation': 'I am passionate about international education',
            'df_experience': 'Previous exchange program participation'
        }
        
        submission = ApplicationService.process_dynamic_form_submission(
            application=self.application,
            form_data=form_data,
            user=self.student
        )
        
        self.assertIsNotNone(submission)
        self.assertEqual(submission.form_type, self.form_type)
        self.assertEqual(submission.responses['motivation'], form_data['df_motivation'])

    def test_dynamic_form_update_workflow(self):
        """Test updating existing form submission."""
        from exchange.services import ApplicationService
        
        # Initial submission
        form_data1 = {
            'df_motivation': 'Initial motivation'
        }
        
        submission1 = ApplicationService.process_dynamic_form_submission(
            application=self.application,
            form_data=form_data1,
            user=self.student
        )
        
        # Update submission
        form_data2 = {
            'df_motivation': 'Updated motivation',
            'df_experience': 'Added experience'
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

