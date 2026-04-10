"""
Unit tests for new exchange features (October 2025).

Tests for:
1. Program Cloning
2. Enhanced Eligibility Criteria Engine
3. Direct Notification Links (in notifications tests)
"""

from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Profile
from exchange.models import Application, ApplicationStatus, Program
from exchange.services import ApplicationService
from notifications.models import Notification

User = get_user_model()


@pytest.mark.django_db
class TestProgramCloning:
    """Test cases for program cloning feature."""

    @pytest.fixture
    def setup_data(self):
        """Set up test data."""
        # Create admin user
        admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="testpass123"
        )
        admin_user.is_staff = True
        admin_user.save()

        # Create original program
        program = Program.objects.create(
            name="Erasmus 2025",
            description="Exchange program to Europe",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=180),
            is_active=True,
            min_gpa=3.5,
            required_language="English",
            min_language_level="B2",
            min_age=18,
            max_age=30,
            recurring=True,
            auto_reject_ineligible=False
        )

        return {
            'admin_user': admin_user,
            'program': program
        }

    def test_program_clone_creates_copy(self, setup_data):
        """Test that cloning creates a new program with copied fields."""
        client = APIClient()
        admin = setup_data['admin_user']
        program = setup_data['program']

        # Authenticate as admin
        refresh = RefreshToken.for_user(admin)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        # Clone the program
        url = reverse('api:program-clone', kwargs={'pk': program.id})
        response = client.post(url)

        # Verify response
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['status'] == "Program cloned successfully"
        assert 'program' in response.data

        # Verify cloned program exists
        cloned_program_id = response.data['program']['id']
        cloned_program = Program.objects.get(id=cloned_program_id)

        # Verify fields copied correctly
        assert cloned_program.name == f"{program.name} (Copy)"
        assert cloned_program.description == program.description
        assert cloned_program.min_gpa == program.min_gpa
        assert cloned_program.required_language == program.required_language
        assert cloned_program.min_language_level == program.min_language_level
        assert cloned_program.min_age == program.min_age
        assert cloned_program.max_age == program.max_age
        assert cloned_program.recurring == program.recurring

    def test_program_clone_inactive_by_default(self, setup_data):
        """Test that cloned programs start as inactive."""
        client = APIClient()
        admin = setup_data['admin_user']
        program = setup_data['program']

        # Authenticate and clone
        refresh = RefreshToken.for_user(admin)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        url = reverse('api:program-clone', kwargs={'pk': program.id})
        response = client.post(url)

        # Verify cloned program is inactive
        cloned_program_id = response.data['program']['id']
        cloned_program = Program.objects.get(id=cloned_program_id)
        assert cloned_program.is_active is False
        assert program.is_active is True  # Original unchanged

    def test_program_clone_appends_copy_to_name(self, setup_data):
        """Test that cloned program name has (Copy) appended."""
        client = APIClient()
        admin = setup_data['admin_user']
        program = setup_data['program']

        refresh = RefreshToken.for_user(admin)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        url = reverse('api:program-clone', kwargs={'pk': program.id})
        response = client.post(url)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['program']['name'] == f"{program.name} (Copy)"

    def test_program_clone_creates_unique_id(self, setup_data):
        """Test that cloned program has a different UUID."""
        client = APIClient()
        admin = setup_data['admin_user']
        program = setup_data['program']

        refresh = RefreshToken.for_user(admin)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        url = reverse('api:program-clone', kwargs={'pk': program.id})
        response = client.post(url)

        cloned_program_id = response.data['program']['id']
        assert str(cloned_program_id) != str(program.id)

    def test_program_clone_requires_admin(self, setup_data):
        """Test that only admins can clone programs."""
        client = APIClient()
        program = setup_data['program']

        # Create regular user
        user = User.objects.create_user(
            username="student",
            email="student@example.com",
            password="testpass123"
        )

        # Try to clone as regular user
        refresh = RefreshToken.for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        url = reverse('api:program-clone', kwargs={'pk': program.id})
        response = client.post(url)

        # Should be forbidden
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestEnhancedEligibilityCriteria:
    """Test cases for enhanced eligibility validation."""

    @pytest.fixture
    def setup_eligibility_data(self):
        """Set up test data for eligibility checks."""
        # Create student user (profile auto-created by signal)
        student = User.objects.create_user(
            username="student",
            email="student@example.com",
            password="testpass123"
        )

        # Get and update the auto-created profile with eligibility data
        profile = Profile.objects.get(user=student)
        profile.gpa = 3.7
        profile.language = "English"
        profile.language_level = "B2"
        profile.date_of_birth = date(2000, 1, 1)  # 25 years old
        profile.save()

        # Refresh student to clear cached profile
        student.refresh_from_db()

        # Create program with eligibility criteria
        program = Program.objects.create(
            name="Strict Program",
            description="Program with strict requirements",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=180),
            is_active=True,
            min_gpa=3.5,
            required_language="English",
            min_language_level="B2",
            min_age=18,
            max_age=30
        )

        return {
            'student': student,
            'profile': profile,
            'program': program
        }

    def test_eligibility_check_gpa_pass(self, setup_eligibility_data):
        """Test that student with sufficient GPA passes."""
        student = setup_eligibility_data['student']
        program = setup_eligibility_data['program']

        result = ApplicationService.check_eligibility(student, program)

        assert result['eligible'] is True
        assert 'GPA requirement' in str(result.get('checks_passed', []))

    def test_eligibility_check_gpa_fail(self, setup_eligibility_data):
        """Test that student with insufficient GPA fails."""
        student = setup_eligibility_data['student']
        profile = setup_eligibility_data['profile']
        program = setup_eligibility_data['program']

        # Lower student's GPA
        profile.gpa = 3.2
        profile.save()

        with pytest.raises(ValueError) as exc_info:
            ApplicationService.check_eligibility(student, program)

        assert "GPA below program minimum" in str(exc_info.value)
        assert "3.2" in str(exc_info.value)
        assert "3.5" in str(exc_info.value)

    def test_eligibility_check_language_pass(self, setup_eligibility_data):
        """Test that student with correct language passes."""
        student = setup_eligibility_data['student']
        program = setup_eligibility_data['program']

        result = ApplicationService.check_eligibility(student, program)

        assert result['eligible'] is True

    def test_eligibility_check_language_fail(self, setup_eligibility_data):
        """Test that student with wrong language fails."""
        student = setup_eligibility_data['student']
        profile = setup_eligibility_data['profile']
        program = setup_eligibility_data['program']

        # Change student's language
        profile.language = "Spanish"
        profile.save()

        with pytest.raises(ValueError) as exc_info:
            ApplicationService.check_eligibility(student, program)

        assert "Language requirement not met" in str(exc_info.value)
        assert "English" in str(exc_info.value)

    def test_eligibility_check_language_level(self, setup_eligibility_data):
        """Test language proficiency level validation."""
        student = setup_eligibility_data['student']
        profile = setup_eligibility_data['profile']
        program = setup_eligibility_data['program']

        # Student has B2, program requires B2 - should pass
        result = ApplicationService.check_eligibility(student, program)
        assert result['eligible'] is True

        # Lower student's level to B1 - should fail
        profile.language_level = "B1"
        profile.save()
        student.refresh_from_db()  # Refresh to clear cached profile

        with pytest.raises(ValueError) as exc_info:
            ApplicationService.check_eligibility(student, program)

        assert "Language proficiency below requirement" in str(exc_info.value)

    def test_eligibility_check_age_pass(self, setup_eligibility_data):
        """Test that student within age range passes."""
        student = setup_eligibility_data['student']
        program = setup_eligibility_data['program']

        result = ApplicationService.check_eligibility(student, program)

        assert result['eligible'] is True

    def test_eligibility_check_age_too_young(self, setup_eligibility_data):
        """Test that student below minimum age fails."""
        student = setup_eligibility_data['student']
        profile = setup_eligibility_data['profile']
        program = setup_eligibility_data['program']

        # Make student 16 years old
        profile.date_of_birth = date.today() - timedelta(days=365*16)
        profile.save()

        with pytest.raises(ValueError) as exc_info:
            ApplicationService.check_eligibility(student, program)

        assert "Age below minimum requirement" in str(exc_info.value)
        assert "18" in str(exc_info.value)

    def test_eligibility_check_age_too_old(self, setup_eligibility_data):
        """Test that student above maximum age fails."""
        student = setup_eligibility_data['student']
        profile = setup_eligibility_data['profile']
        program = setup_eligibility_data['program']

        # Make student 35 years old
        profile.date_of_birth = date.today() - timedelta(days=365*35)
        profile.save()

        with pytest.raises(ValueError) as exc_info:
            ApplicationService.check_eligibility(student, program)

        assert "Age above maximum requirement" in str(exc_info.value)
        assert "30" in str(exc_info.value)

    def test_eligibility_check_multiple_failures(self, setup_eligibility_data):
        """Test that multiple eligibility issues are reported."""
        student = setup_eligibility_data['student']
        profile = setup_eligibility_data['profile']
        program = setup_eligibility_data['program']

        # Make student fail multiple criteria
        profile.gpa = 3.0  # Too low
        profile.language = "Spanish"  # Wrong language
        profile.date_of_birth = date.today() - timedelta(days=365*35)  # Too old
        profile.save()

        with pytest.raises(ValueError) as exc_info:
            ApplicationService.check_eligibility(student, program)

        error_message = str(exc_info.value)
        assert "GPA below program minimum" in error_message
        assert "Language requirement not met" in error_message
        assert "Age above maximum requirement" in error_message

    def test_eligibility_check_endpoint(self, setup_eligibility_data):
        """Test the check_eligibility API endpoint."""
        client = APIClient()
        student = setup_eligibility_data['student']
        program = setup_eligibility_data['program']

        # Authenticate as student
        refresh = RefreshToken.for_user(student)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        # Check eligibility
        url = reverse('api:program-check-eligibility', kwargs={'pk': program.id})
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['eligible'] is True
        assert 'message' in response.data

    def test_eligibility_check_endpoint_ineligible(self, setup_eligibility_data):
        """Test check_eligibility endpoint with ineligible student."""
        client = APIClient()
        student = setup_eligibility_data['student']
        profile = setup_eligibility_data['profile']
        program = setup_eligibility_data['program']

        # Make student ineligible
        profile.gpa = 2.5
        profile.save()

        # Authenticate and check
        refresh = RefreshToken.for_user(student)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        url = reverse('api:program-check-eligibility', kwargs={'pk': program.id})
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['eligible'] is False
        assert "GPA below program minimum" in response.data['message']
        assert 'program' in response.data

    def test_check_eligibility_application_query_includes_document_rule(
        self, setup_eligibility_data,
    ):
        from documents.models import DocumentType

        client = APIClient()
        student = setup_eligibility_data['student']
        program = setup_eligibility_data['program']
        dt = DocumentType.objects.create(name="ID Scan", description="")
        program.required_document_types.add(dt)
        draft_status, _ = ApplicationStatus.objects.get_or_create(name="draft")
        app = Application.objects.create(
            student=student,
            program=program,
            status=draft_status,
        )
        refresh = RefreshToken.for_user(student)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        url = reverse('api:program-check-eligibility', kwargs={'pk': program.id})
        response = client.get(url, {'application': str(app.id)})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['eligible'] is False
        assert 'Required documents' in response.data['message']
        assert response.data.get('schema_version') == 3
        rule_ids = [r['id'] for r in response.data['rules']]
        assert 'required_documents' in rule_ids


@pytest.mark.django_db
class TestNotificationLinks:
    """Test cases for direct notification links feature."""

    @pytest.fixture
    def setup_notification_data(self):
        """Set up test data for notification tests."""
        # Create users
        student = User.objects.create_user(
            username="student",
            email="student@example.com",
            password="testpass123"
        )
        # Update auto-created profile
        profile = Profile.objects.get(user=student)
        profile.gpa = 3.7
        profile.save()

        # Create program and application
        program = Program.objects.create(
            name="Test Program",
            description="Test",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=180),
            is_active=True
        )

        draft_status = ApplicationStatus.objects.get_or_create(
            name="draft", defaults={'order': 1}
        )[0]

        application = Application.objects.create(
            program=program,
            student=student,
            status=draft_status
        )

        return {
            'student': student,
            'program': program,
            'application': application
        }

    def test_notification_with_action_url(self, setup_notification_data):
        """Test that notifications can include action URLs."""
        student = setup_notification_data['student']
        application = setup_notification_data['application']

        notification = Notification.objects.create(
            recipient=student,
            title="Application Submitted",
            message="Your application has been submitted",
            action_url=f"/applications/{application.id}/",
            action_text="View Application"
        )

        assert notification.action_url == f"/applications/{application.id}/"
        assert notification.action_text == "View Application"

    def test_notification_action_url_in_serializer(self, setup_notification_data):
        """Test that notification serializer includes action URL fields."""
        from notifications.serializers import NotificationSerializer

        student = setup_notification_data['student']
        application = setup_notification_data['application']

        notification = Notification.objects.create(
            recipient=student,
            title="Test Notification",
            message="Test message",
            action_url=f"/applications/{application.id}/",
            action_text="View Now"
        )

        serializer = NotificationSerializer(notification)
        data = serializer.data

        assert 'action_url' in data
        assert 'action_text' in data
        assert data['action_url'] == f"/applications/{application.id}/"
        assert data['action_text'] == "View Now"

    def test_notification_backward_compatible(self, setup_notification_data):
        """Test that notifications without action URLs still work."""
        student = setup_notification_data['student']

        notification = Notification.objects.create(
            recipient=student,
            title="Old Style Notification",
            message="This is an old notification without action URL"
        )

        # Should work fine with null action_url
        assert notification.action_url is None
        assert notification.action_text == "View Details"  # Default

    def test_application_submission_includes_link(self, setup_notification_data):
        """Test that application submission creates notification with link."""
        student = setup_notification_data['student']
        application = setup_notification_data['application']

        # Submit application (this should create notification)
        ApplicationService.submit_application(application, student)

        # Check notification was created with action URL
        notifications = Notification.objects.filter(recipient=student)
        assert notifications.exists()

        notification = notifications.latest('sent_at')
        assert notification.action_url is not None
        assert str(application.id) in notification.action_url
        assert notification.action_text == "View Application"

    def test_status_change_includes_link(self, setup_notification_data):
        """Test that status changes create notifications with links."""
        from accounts.models import Role

        # Create coordinator
        coordinator = User.objects.create_user(
            username="coordinator",
            email="coordinator@example.com",
            password="testpass123"
        )
        coord_role = Role.objects.get_or_create(name="coordinator")[0]
        coordinator.roles.add(coord_role)

        student = setup_notification_data['student']
        application = setup_notification_data['application']

        # First submit the application
        ApplicationService.submit_application(application, student)

        # Clear notifications
        Notification.objects.all().delete()

        # Change status
        ApplicationService.transition_status(application, coordinator, "under_review")

        # Check notification includes action URL
        notifications = Notification.objects.filter(recipient=student)
        assert notifications.exists()

        notification = notifications.latest('sent_at')
        assert notification.action_url is not None
        assert str(application.id) in notification.action_url

