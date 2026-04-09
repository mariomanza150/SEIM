"""
Unit tests for application submission workflow.
"""

from datetime import date

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Role
from exchange.models import (
    Application,
    ApplicationStatus,
    Comment,
    Program,
    TimelineEvent,
)
from exchange.services import ApplicationService

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.unit
@pytest.mark.workflow
class TestApplicationSubmissionWorkflow:
    """Test application submission and workflow transitions."""

    def setup_method(self):
        """Set up test data."""
        self.client = APIClient()

        # Create users with different roles
        self.student = User.objects.create_user(
            username="student",
            email="student@university.edu",
            password="testpass123",
        )

        # Set up student profile with eligibility data
        student_profile = self.student.profile
        student_profile.gpa = 3.5
        student_profile.language = "English"
        student_profile.language_level = "B2"
        student_profile.date_of_birth = date(2000, 1, 1)  # 25 years old
        student_profile.save()

        self.coordinator = User.objects.create_user(
            username="coordinator",
            email="coordinator@university.edu",
            password="testpass123",
        )

        self.admin = User.objects.create_user(
            username="admin",
            email="admin@university.edu",
            password="testpass123",
            is_staff=True,
        )

        # Create roles (use lowercase to match permission checks)
        student_role, _ = Role.objects.get_or_create(name="student")
        coordinator_role, _ = Role.objects.get_or_create(name="coordinator")
        admin_role, _ = Role.objects.get_or_create(name="admin")

        # Assign roles
        self.student.roles.add(student_role)
        self.coordinator.roles.add(coordinator_role)
        self.admin.roles.add(admin_role)

        # Create application statuses
        self.draft_status, _ = ApplicationStatus.objects.get_or_create(
            name="draft", defaults={"order": 1}
        )
        self.submitted_status, _ = ApplicationStatus.objects.get_or_create(
            name="submitted", defaults={"order": 2}
        )
        self.under_review_status, _ = ApplicationStatus.objects.get_or_create(
            name="under_review", defaults={"order": 3}
        )
        self.approved_status, _ = ApplicationStatus.objects.get_or_create(
            name="approved", defaults={"order": 4}
        )
        self.rejected_status, _ = ApplicationStatus.objects.get_or_create(
            name="rejected", defaults={"order": 5}
        )

        # Create test program with eligibility criteria matching student profile
        self.program = Program.objects.create(
            name="Test Exchange Program",
            description="A test exchange program",
            start_date=date(2025, 9, 1),
            end_date=date(2026, 1, 31),
            min_gpa=3.0,
            required_language="English",
            min_language_level="B1",  # Student has B2, which is higher
            min_age=18,
            max_age=30,
            is_active=True,
        )

    def test_application_creation_by_student(self):
        """Test that students can create applications."""
        refresh = RefreshToken.for_user(self.student)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        data = {
            "program": self.program.id,
        }

        response = self.client.post("/api/applications/", data)
        assert response.status_code == status.HTTP_201_CREATED

        application = Application.objects.get(id=response.data["id"])
        assert application.student == self.student
        assert application.program == self.program
        assert application.status == self.draft_status

    def test_application_submission_workflow(self):
        """Test the complete application submission workflow."""
        # Create application in draft status
        application = Application.objects.create(
            student=self.student,
            program=self.program,
            status=self.draft_status,
        )

        # Submit application
        refresh = RefreshToken.for_user(self.student)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        data = {"status": "submitted"}
        response = self.client.patch(f"/api/applications/{application.id}/", data)
        assert response.status_code == status.HTTP_200_OK

        application.refresh_from_db()
        assert application.status == self.submitted_status
        assert application.submitted_at is not None

    def test_coordinator_can_review_application(self):
        """Test that coordinators can change application status to under review."""
        application = Application.objects.create(
            student=self.student,
            program=self.program,
            status=self.submitted_status,
        )

        refresh = RefreshToken.for_user(self.coordinator)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        data = {"status": "under_review"}
        response = self.client.patch(f"/api/applications/{application.id}/", data)
        assert response.status_code == status.HTTP_200_OK

        application.refresh_from_db()
        assert application.status == self.under_review_status

    def test_admin_can_approve_reject_application(self):
        """Test that admins can approve or reject applications."""
        application = Application.objects.create(
            student=self.student,
            program=self.program,
            status=self.under_review_status,
        )

        refresh = RefreshToken.for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        # Test approval
        data = {"status": "approved"}
        response = self.client.patch(f"/api/applications/{application.id}/", data)
        assert response.status_code == status.HTTP_200_OK

        application.refresh_from_db()
        assert application.status == self.approved_status

        # Test rejection
        data = {"status": "rejected"}
        response = self.client.patch(f"/api/applications/{application.id}/", data)
        assert response.status_code == status.HTTP_200_OK

        application.refresh_from_db()
        assert application.status == self.rejected_status

    def test_student_cannot_modify_submitted_application(self):
        """Test that students cannot modify applications after submission."""
        application = Application.objects.create(
            student=self.student,
            program=self.program,
            status=self.submitted_status,
        )

        refresh = RefreshToken.for_user(self.student)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        # Try to change status back to draft
        data = {"status": "draft"}
        response = self.client.patch(f"/api/applications/{application.id}/", data)
        # Expect 400 (Bad Request - validation error) not 403 (Permission denied)
        # Permission allows students to update their own applications, but service layer blocks invalid status transitions
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "permission" in response.data[0].lower() or "transition" in response.data[0].lower()

    def test_application_withdrawal(self):
        """Test that students can withdraw their applications."""
        application = Application.objects.create(
            student=self.student,
            program=self.program,
            status=self.submitted_status,
        )

        refresh = RefreshToken.for_user(self.student)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        data = {"withdrawn": True}
        response = self.client.patch(f"/api/applications/{application.id}/", data)
        assert response.status_code == status.HTTP_200_OK

        application.refresh_from_db()
        assert application.withdrawn is True

    def test_timeline_event_creation_on_status_change(self):
        """Test that timeline events are created when application status changes."""
        application = Application.objects.create(
            student=self.student,
            program=self.program,
            status=self.draft_status,
        )

        initial_event_count = TimelineEvent.objects.filter(application=application).count()

        # Change status
        refresh = RefreshToken.for_user(self.coordinator)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        data = {"status": "submitted"}
        response = self.client.patch(f"/api/applications/{application.id}/", data)
        assert response.status_code == status.HTTP_200_OK

        # Check that timeline event was created
        final_event_count = TimelineEvent.objects.filter(application=application).count()
        assert final_event_count > initial_event_count

    def test_comment_creation_on_application(self):
        """Test that comments can be added to applications."""
        application = Application.objects.create(
            student=self.student,
            program=self.program,
            status=self.under_review_status,
        )

        refresh = RefreshToken.for_user(self.coordinator)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        comment_data = {
            "application": application.id,
            "text": "This application looks good, but needs more details.",
            "is_private": False,
        }

        response = self.client.post("/api/comments/", comment_data)
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.data}")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["author_name"] == self.coordinator.username
        assert response.data["author_role"] == "coordinator"

        comment = Comment.objects.get(id=response.data["id"])
        assert comment.application == application
        assert comment.author == self.coordinator
        assert comment.text == comment_data["text"]
        assert comment.is_private == comment_data["is_private"]


@pytest.mark.django_db
@pytest.mark.unit
@pytest.mark.models
class TestApplicationService:
    """Test ApplicationService business logic."""

    def setup_method(self):
        """Set up test data."""
        self.student = User.objects.create_user(
            username="student",
            email="student@university.edu",
            password="testpass123",
        )

        self.program = Program.objects.create(
            name="Test Program",
            description="Test Description",
            start_date=date(2025, 9, 1),
            end_date=date(2026, 1, 31),
            is_active=True,
        )

        self.draft_status, _ = ApplicationStatus.objects.get_or_create(
            name="draft", defaults={"order": 1}
        )
        self.submitted_status, _ = ApplicationStatus.objects.get_or_create(
            name="submitted", defaults={"order": 2}
        )

    def test_can_submit_application(self):
        """Test application submission validation."""
        application = Application.objects.create(
            student=self.student,
            program=self.program,
            status=self.draft_status,
        )

        # Should be able to submit (no active application exists)
        assert ApplicationService.can_submit_application(self.student, self.program) is True

        # Should not be able to submit (active application exists)
        application.status = self.submitted_status
        application.save()
        assert ApplicationService.can_submit_application(self.student, self.program) is False

    def test_can_withdraw_application(self):
        """Test application withdrawal validation."""
        application = Application.objects.create(
            student=self.student,
            program=self.program,
            status=self.submitted_status,
        )

        # Should be able to withdraw submitted application
        assert ApplicationService.can_withdraw_application(application) is True

        # Should not be able to withdraw withdrawn application
        application.withdrawn = True
        application.save()
        assert ApplicationService.can_withdraw_application(application) is False

    def test_get_application_status_history(self):
        """Test retrieving application status history."""
        application = Application.objects.create(
            student=self.student,
            program=self.program,
            status=self.draft_status,
        )

        # Create timeline events
        TimelineEvent.objects.create(
            application=application,
            event_type="created",
            description="Application created",
            created_by=self.student,
        )

        TimelineEvent.objects.create(
            application=application,
            event_type="status_changed",
            description="Status changed to submitted",
            created_by=self.student,
        )

        history = ApplicationService.get_status_history(application)
        assert len(history) == 2
        assert history[0].event_type == "created"
        assert history[1].event_type == "status_changed"
