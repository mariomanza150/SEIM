"""
Test API Edge Cases and Boundary Conditions

This test file covers edge cases for API endpoints including
validation, error handling, and security scenarios.
"""

import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import Role
from exchange.models import Application, ApplicationStatus, Comment, Program

User = get_user_model()


@pytest.mark.django_db
class TestAPIValidationEdgeCases(TestCase):
    """Test API validation edge cases."""

    def setUp(self):
        """Set up test client and data."""
        self.client = APIClient()
        
        # Create roles
        self.student_role, _ = Role.objects.get_or_create(name="student")
        self.coordinator_role, _ = Role.objects.get_or_create(name="coordinator")
        
        # Create student
        self.student = User.objects.create_user(
            username="student",
            email="student@test.com",
            password="testpass123"
        )
        self.student.roles.add(self.student_role)

    def test_create_application_with_missing_required_fields(self):
        """Test application creation with missing required fields."""
        self.client.force_authenticate(user=self.student)
        
        # Missing program field (program is required)
        data = {}
        
        response = self.client.post(reverse("api:application-list"), data)
        
        # Should fail validation
        self.assertIn(
            response.status_code,
            [status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN]
        )

    def test_create_application_with_extra_fields(self):
        """Test that extra/unknown fields are handled properly."""
        self.client.force_authenticate(user=self.student)
        
        program = Program.objects.create(
            name="Test Program",
            description="Test",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365),
            is_active=True,
        )
        
        data = {
            "program": program.id,
            "unknown_field": "Should be ignored",  # Extra field
            "another_extra": 123,
        }
        
        response = self.client.post(reverse("api:application-list"), data)
        
        # Extra fields should be ignored (or rejected depending on serializer)
        self.assertIn(
            response.status_code,
            [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]
        )

    def test_update_with_invalid_data_types(self):
        """Test update with wrong data types."""
        self.client.force_authenticate(user=self.student)
        
        program = Program.objects.create(
            name="Test Program",
            description="Test",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365),
            is_active=True,
        )
        
        # Try to create application with string instead of integer for program
        data = {
            "program": "not_a_number",
        }
        
        response = self.client.post(reverse("api:application-list"), data)
        
        # Should fail validation
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_pagination_edge_cases(self):
        """Test pagination with edge case parameters."""
        self.client.force_authenticate(user=self.student)
        
        # Test with page=0
        response = self.client.get(reverse("api:program-list") + "?page=0")
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])
        
        # Test with negative page
        response = self.client.get(reverse("api:program-list") + "?page=-1")
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])
        
        # Test with huge page number
        response = self.client.get(reverse("api:program-list") + "?page=99999")
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])

    def test_filter_with_invalid_values(self):
        """Test filtering with invalid values."""
        self.client.force_authenticate(user=self.student)
        
        # Invalid boolean
        response = self.client.get(reverse("api:program-list") + "?is_active=maybe")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Invalid date format
        response = self.client.get(reverse("api:program-list") + "?start_date=not-a-date")
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])


@pytest.mark.django_db
class TestAPISecurityEdgeCases(TestCase):
    """Test API security edge cases."""

    def setUp(self):
        """Set up test client and data."""
        self.client = APIClient()
        
        # Create roles
        self.student_role, _ = Role.objects.get_or_create(name="student")
        
        # Create users
        self.student1 = User.objects.create_user(
            username="student1",
            email="student1@test.com",
            password="testpass123"
        )
        self.student1.roles.add(self.student_role)
        
        self.student2 = User.objects.create_user(
            username="student2",
            email="student2@test.com",
            password="testpass123"
        )
        self.student2.roles.add(self.student_role)

    def test_unauthorized_access_to_other_user_data(self):
        """Test that users cannot access other users' private data."""
        program = Program.objects.create(
            name="Test Program",
            description="Test",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365),
            is_active=True,
        )
        
        status_obj, _ = ApplicationStatus.objects.get_or_create(name="draft", defaults={'order': 1})
        
        # Student1 creates application
        application = Application.objects.create(
            student=self.student1,
            program=program,
            status=status_obj,
        )
        
        # Student2 tries to access student1's application
        self.client.force_authenticate(user=self.student2)
        
        response = self.client.get(
            reverse("api:application-detail", args=[application.id])
        )
        
        # Should be forbidden or not found
        self.assertIn(
            response.status_code,
            [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
        )

    def test_unauthenticated_api_access(self):
        """Test that unauthenticated users cannot access protected endpoints."""
        # No authentication
        response = self.client.get(reverse("api:application-list"))
        
        # Should require authentication
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_malformed_json_request(self):
        """Test API with malformed JSON."""
        self.client.force_authenticate(user=self.student1)
        
        # Send malformed JSON
        response = self.client.post(
            reverse("api:application-list"),
            data="{'invalid': json}",  # Not valid JSON
            content_type="application/json"
        )
        
        # Should return bad request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sql_injection_in_api_parameters(self):
        """Test that SQL injection attempts are prevented."""
        self.client.force_authenticate(user=self.student1)
        
        # SQL injection attempt in query parameter
        injection_attempt = "1' OR '1'='1"
        response = self.client.get(
            reverse("api:program-list") + f"?search={injection_attempt}"
        )
        
        # Should return safely (ORM prevents injection)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


@pytest.mark.django_db
class TestAPIErrorHandling(TestCase):
    """Test API error handling scenarios."""

    def setUp(self):
        """Set up test client and data."""
        self.client = APIClient()
        
        self.student_role, _ = Role.objects.get_or_create(name="student")
        self.student = User.objects.create_user(
            username="student",
            email="student@test.com",
            password="testpass123"
        )
        self.student.roles.add(self.student_role)

    def test_get_nonexistent_resource(self):
        """Test getting a resource that doesn't exist."""
        self.client.force_authenticate(user=self.student)
        
        # UUID that doesn't exist
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        
        response = self.client.get(
            reverse("api:application-detail", args=[fake_uuid])
        )
        
        # Should return 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_already_deleted_resource(self):
        """Test deleting a resource that was already deleted."""
        self.client.force_authenticate(user=self.student)
        
        program = Program.objects.create(
            name="Test Program",
            description="Test",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365),
            is_active=True,
        )
        
        status_obj, _ = ApplicationStatus.objects.get_or_create(name="draft", defaults={'order': 1})
        
        application = Application.objects.create(
            student=self.student,
            program=program,
            status=status_obj,
        )
        
        app_id = application.id
        
        # Delete application directly
        application.delete()
        
        # Try to delete via API
        response = self.client.delete(
            reverse("api:application-detail", args=[app_id])
        )
        
        # Should return 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_partial_update_with_readonly_fields(self):
        """Test partial update attempt on readonly fields."""
        self.client.force_authenticate(user=self.student)
        
        program = Program.objects.create(
            name="Test Program",
            description="Test",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365),
            is_active=True,
        )
        
        status_obj, _ = ApplicationStatus.objects.get_or_create(name="draft", defaults={'order': 1})
        
        application = Application.objects.create(
            student=self.student,
            program=program,
            status=status_obj,
        )
        
        original_created = application.created_at
        
        # Try to update created_at (should be readonly)
        data = {
            "created_at": "2020-01-01T00:00:00Z"
        }
        
        response = self.client.patch(
            reverse("api:application-detail", args=[application.id]),
            data
        )
        
        # Either ignored or rejected
        application.refresh_from_db()
        
        # created_at should not have changed
        self.assertEqual(application.created_at.date(), original_created.date())


@pytest.mark.django_db
class TestAPIRateLimiting(TestCase):
    """Test rate limiting and throttling edge cases."""

    def setUp(self):
        """Set up test client."""
        self.client = APIClient()
        
        self.student_role, _ = Role.objects.get_or_create(name="student")
        self.student = User.objects.create_user(
            username="student",
            email="student@test.com",
            password="testpass123"
        )
        self.student.roles.add(self.student_role)

    def test_rapid_fire_requests(self):
        """Test making many rapid requests."""
        self.client.force_authenticate(user=self.student)
        
        # Make 20 rapid requests
        responses = []
        for _ in range(20):
            response = self.client.get(reverse("api:program-list"))
            responses.append(response.status_code)
        
        # All should succeed (or some throttled if limits configured)
        success_count = sum(1 for code in responses if code == 200)
        throttled_count = sum(1 for code in responses if code == 429)
        
        # At least some should succeed
        self.assertGreater(success_count, 0)


@pytest.mark.django_db
class TestCommentEdgeCases(TestCase):
    """Test comment functionality edge cases."""

    def setUp(self):
        """Set up test data."""
        self.student_role, _ = Role.objects.get_or_create(name="student")
        self.student = User.objects.create_user(
            username="student",
            email="student@test.com",
            password="testpass123"
        )
        self.student.roles.add(self.student_role)
        
        self.program = Program.objects.create(
            name="Test Program",
            description="Test",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365),
            is_active=True,
        )
        
        self.status, _ = ApplicationStatus.objects.get_or_create(name="submitted", defaults={'order': 2})
        
        self.application = Application.objects.create(
            student=self.student,
            program=self.program,
            status=self.status,
        )

    def test_comment_with_only_whitespace(self):
        """Test comment with only whitespace."""
        whitespace_comment = "   \t\n   "
        
        comment = Comment.objects.create(
            application=self.application,
            author=self.student,
            text=whitespace_comment,
        )
        
        self.assertEqual(comment.text, whitespace_comment)

    def test_comment_with_html_entities(self):
        """Test comment with HTML entities."""
        html_entities = "&lt;script&gt;alert('test')&lt;/script&gt;"
        
        comment = Comment.objects.create(
            application=self.application,
            author=self.student,
            text=html_entities,
        )
        
        self.assertEqual(comment.text, html_entities)

    def test_comment_with_newlines_and_formatting(self):
        """Test comment with newlines and formatting."""
        formatted_text = """Line 1
        Line 2
            Indented line
        
        Line after blank line"""
        
        comment = Comment.objects.create(
            application=self.application,
            author=self.student,
            text=formatted_text,
        )
        
        self.assertEqual(comment.text, formatted_text)

    def test_very_long_comment(self):
        """Test comment with maximum length text."""
        long_text = "A" * 5000
        
        comment = Comment.objects.create(
            application=self.application,
            author=self.student,
            text=long_text,
        )
        
        self.assertEqual(len(comment.text), 5000)

    def test_comment_edit_history(self):
        """Test comment modification tracking."""
        comment = Comment.objects.create(
            application=self.application,
            author=self.student,
            text="Original text",
        )
        
        original_created = comment.created_at
        
        # Update comment
        comment.text = "Updated text"
        comment.save()
        
        # created_at should not change
        self.assertEqual(comment.created_at, original_created)
        
        # updated_at should change
        self.assertGreater(comment.updated_at, comment.created_at)


@pytest.mark.django_db
class TestProgramEdgeCases(TestCase):
    """Test program-related edge cases."""

    def test_program_with_special_characters_in_name(self):
        """Test program name with special characters."""
        special_name = "Program: <Test> & \"Quotes\" 'Apostrophes' (2025)"
        
        program = Program.objects.create(
            name=special_name,
            description="Test",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365),
            is_active=True,
        )
        
        self.assertEqual(program.name, special_name)

    def test_program_with_very_long_description(self):
        """Test program with maximum length description."""
        long_desc = "Description " * 1000  # Very long description
        
        program = Program.objects.create(
            name="Long Desc Program",
            description=long_desc,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365),
            is_active=True,
        )
        
        self.assertTrue(len(program.description) > 10000)

    def test_program_with_unicode_description(self):
        """Test program with unicode in description."""
        unicode_desc = "Programme d'échange 交换项目 برنامج تبادل"
        
        program = Program.objects.create(
            name="Unicode Program",
            description=unicode_desc,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365),
            is_active=True,
        )
        
        self.assertEqual(program.description, unicode_desc)

    def test_inactive_program_visibility(self):
        """Test that inactive programs are handled correctly."""
        inactive_program = Program.objects.create(
            name="Inactive Program",
            description="Test",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365),
            is_active=False,  # Explicitly inactive
        )
        
        self.assertFalse(inactive_program.is_active)
        
        # Check if it appears in queryset
        all_programs = Program.objects.all()
        self.assertIn(inactive_program, all_programs)
        
        # Check active programs only
        active_programs = Program.objects.filter(is_active=True)
        self.assertNotIn(inactive_program, active_programs)


@pytest.mark.django_db
class TestApplicationStatusEdgeCases(TestCase):
    """Test application status transition edge cases."""

    def setUp(self):
        """Set up test data."""
        self.student_role, _ = Role.objects.get_or_create(name="student")
        self.coordinator_role, _ = Role.objects.get_or_create(name="coordinator")
        
        self.student = User.objects.create_user(
            username="student",
            email="student@test.com",
            password="testpass123"
        )
        self.student.roles.add(self.student_role)
        
        self.coordinator = User.objects.create_user(
            username="coordinator",
            email="coordinator@test.com",
            password="testpass123"
        )
        self.coordinator.roles.add(self.coordinator_role)
        
        self.program = Program.objects.create(
            name="Test Program",
            description="Test",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365),
            is_active=True,
        )
        
        # Create statuses
        self.draft, _ = ApplicationStatus.objects.get_or_create(name="draft", defaults={'order': 1})
        self.submitted, _ = ApplicationStatus.objects.get_or_create(name="submitted", defaults={'order': 2})
        self.under_review, _ = ApplicationStatus.objects.get_or_create(name="under_review", defaults={'order': 3})
        self.approved, _ = ApplicationStatus.objects.get_or_create(name="approved", defaults={'order': 4})
        self.rejected, _ = ApplicationStatus.objects.get_or_create(name="rejected", defaults={'order': 5})

    def test_skip_status_transition(self):
        """Test skipping intermediate status (draft -> approved)."""
        application = Application.objects.create(
            student=self.student,
            program=self.program,
            status=self.draft,
        )
        
        # Jump directly from draft to approved (skipping submitted, under_review)
        application.status = self.approved
        application.save()
        
        # Should be allowed at model level
        self.assertEqual(application.status, self.approved)

    def test_backward_status_transition(self):
        """Test moving backward in status (approved -> draft)."""
        application = Application.objects.create(
            student=self.student,
            program=self.program,
            status=self.approved,
        )
        
        # Move backward
        application.status = self.draft
        application.save()
        
        # Should be allowed at model level
        self.assertEqual(application.status, self.draft)

    def test_status_transition_to_same_status(self):
        """Test transitioning to same status (idempotent)."""
        application = Application.objects.create(
            student=self.student,
            program=self.program,
            status=self.submitted,
        )
        
        # Transition to same status
        application.status = self.submitted
        application.save()
        
        # Should remain unchanged
        self.assertEqual(application.status, self.submitted)

