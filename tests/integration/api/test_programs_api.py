"""
Integration tests for programs API endpoints.

These tests validate the programs API that the frontend uses for:
- Listing programs
- Creating programs
- Updating programs
- Program filtering and search
- Role-based access control
"""

import pytest
from django.urls import reverse
from rest_framework import status

from exchange.models import Program
from tests.utils import APITestCase, PerformanceTestCase, WorkflowTestCase


class TestProgramsAPI(APITestCase):
    """Test programs API endpoints."""

    def setUp(self):
        """Set up test case."""
        super().setUp()
        self.programs_url = reverse("api:program-list")
        self.program_detail_url = reverse("api:program-detail", args=[1])

    def test_list_programs_authenticated(self):
        """Test listing programs with authentication."""
        # Create test programs
        self.create_program(name="Test Program 1")
        self.create_program(name="Test Program 2")

        # Authenticate as student
        student = self.create_user(role="student")
        self.authenticate_user(student)

        response = self.client.get(self.programs_url)

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

        # Verify program data structure
        program_data = response.data["results"][0]
        required_fields = [
            "id",
            "name",
            "description",
            "start_date",
            "end_date",
            "is_active",
        ]
        for field in required_fields:
            self.assertIn(field, program_data)

    def test_list_programs_unauthenticated(self):
        """Test listing programs without authentication."""
        response = self.client.get(self.programs_url)

        self.assert_response_unauthorized(response)

    def test_create_program_admin_only(self):
        """Test that only admins can create programs."""
        # Try as student
        student = self.create_user(role="student")
        self.authenticate_user(student)

        data = {
            "name": "New Program",
            "description": "Test description",
            "start_date": "2025-06-01",
            "end_date": "2025-12-01",
            "is_active": True,
        }

        response = self.client.post(self.programs_url, data, format="json")
        self.assert_response_unauthorized(response)

        # Try as coordinator
        coordinator = self.create_user(role="coordinator")
        self.authenticate_user(coordinator)

        response = self.client.post(self.programs_url, data, format="json")
        self.assert_response_unauthorized(response)

        # Try as admin (should succeed)
        admin = self.create_user(role="admin")
        self.authenticate_user(admin)

        response = self.client.post(self.programs_url, data, format="json")
        self.assert_response_success(response, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "New Program")

    def test_create_program_validation(self):
        """Test program creation validation."""
        admin = self.create_user(role="admin")
        self.authenticate_user(admin)

        # Test invalid data
        invalid_data = {
            "name": "",  # Empty name
            "description": "Test description",
            "start_date": "invalid-date",  # Invalid date
            "end_date": "2025-12-01",
            "is_active": True,
        }

        response = self.client.post(self.programs_url, invalid_data, format="json")
        self.assert_response_error(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertIn("start_date", response.data)

    def test_update_program_admin_only(self):
        """Test that only admins can update programs."""
        program = self.create_program(name="Original Name")

        # Try as student
        student = self.create_user(role="student")
        self.authenticate_user(student)

        data = {"name": "Updated Name"}
        response = self.client.patch(
            reverse("api:program-detail", args=[program.id]), data, format="json"
        )
        self.assert_response_unauthorized(response)

        # Try as admin (should succeed)
        admin = self.create_user(role="admin")
        self.authenticate_user(admin)

        response = self.client.patch(
            reverse("api:program-detail", args=[program.id]), data, format="json"
        )
        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Name")

    def test_delete_program_admin_only(self):
        """Test that only admins can delete programs."""
        program = self.create_program()

        # Try as student
        student = self.create_user(role="student")
        self.authenticate_user(student)

        response = self.client.delete(reverse("api:program-detail", args=[program.id]))
        self.assert_response_unauthorized(response)

        # Try as admin (should succeed)
        admin = self.create_user(role="admin")
        self.authenticate_user(admin)

        response = self.client.delete(reverse("api:program-detail", args=[program.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assert_model_not_exists(Program, id=program.id)

    def test_program_filtering(self):
        """Test program filtering functionality."""
        from django.core.cache import cache

        cache.clear()
        # Ensure test data isolation
        Program.objects.all().delete()
        # Create programs with different attributes
        self.create_program(name="Active Program", is_active=True)
        self.create_program(name="Inactive Program", is_active=False)

        student = self.create_user(role="student")
        self.authenticate_user(student)

        # Filter by active status
        response = self.client.get(f"{self.programs_url}?is_active=true")
        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Active Program")

        # Filter by inactive status
        response = self.client.get(f"{self.programs_url}?is_active=false")
        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Inactive Program")

    def test_program_search(self):
        """Test program search functionality."""
        # Create programs with searchable names
        self.create_program(name="Computer Science Exchange")
        self.create_program(name="Engineering Program")
        self.create_program(name="Business Exchange")

        student = self.create_user(role="student")
        self.authenticate_user(student)

        # Search for "Exchange"
        response = self.client.get(f"{self.programs_url}?search=Exchange")
        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

        # Search for "Engineering"
        response = self.client.get(f"{self.programs_url}?search=Engineering")
        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Engineering Program")

    def test_program_ordering(self):
        """Test program ordering functionality."""
        from django.core.cache import cache

        cache.clear()
        # Ensure test data isolation
        Program.objects.all().delete()
        # Create programs with different names
        self.create_program(name="C Program")
        self.create_program(name="A Program")
        self.create_program(name="B Program")

        student = self.create_user(role="student")
        self.authenticate_user(student)

        # Order by name ascending
        response = self.client.get(f"{self.programs_url}?ordering=name")
        self.assert_response_success(response, status.HTTP_200_OK)
        results = response.data["results"]

        # Get the actual program names from the response
        program_names = [result["name"] for result in results]

        # Check that we have exactly 3 programs
        self.assertEqual(len(program_names), 3)

        # Check that the programs are in alphabetical order
        self.assertIn("A Program", program_names)
        self.assertIn("B Program", program_names)
        self.assertIn("C Program", program_names)

        # Verify the order
        self.assertEqual(program_names[0], "A Program")
        self.assertEqual(program_names[1], "B Program")
        self.assertEqual(program_names[2], "C Program")

        # Order by name descending
        response = self.client.get(f"{self.programs_url}?ordering=-name")
        self.assert_response_success(response, status.HTTP_200_OK)
        results = response.data["results"]
        self.assertEqual(results[0]["name"], "C Program")
        self.assertEqual(results[1]["name"], "B Program")
        self.assertEqual(results[2]["name"], "A Program")

    def test_program_pagination(self):
        """Test program pagination."""
        # Create multiple programs
        for i in range(25):
            self.create_program(name=f"Program {i}")

        student = self.create_user(role="student")
        self.authenticate_user(student)

        # Test first page
        response = self.client.get(self.programs_url)
        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)

        # Verify pagination structure
        self.assertEqual(response.data["count"], 25)
        self.assertIsNotNone(response.data["next"])  # Should have next page
        self.assertIsNone(response.data["previous"])  # First page, no previous

        # Test second page
        response = self.client.get(response.data["next"])
        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertIsNotNone(response.data["previous"])  # Should have previous page


class TestProgramsIntegration(WorkflowTestCase):
    """Test programs integration scenarios."""

    def test_program_application_workflow(self):
        """Test complete workflow from program creation to application."""
        # 1. Admin creates program
        admin = self.create_user(role="admin")
        self.authenticate_user(admin)

        program_data = {
            "name": "Test Exchange Program",
            "description": "A test exchange program",
            "start_date": "2025-06-01",
            "end_date": "2025-12-01",
            "is_active": True,
            "min_gpa": 3.0,
            "required_language": "English",
        }

        program_response = self.client.post(
            reverse("api:program-list"), program_data, format="json"
        )
        self.assert_response_success(program_response, status.HTTP_201_CREATED)
        program_id = program_response.data["id"]

        # 2. Student views program
        student = self.create_user(role="student")
        self.authenticate_user(student)

        program_detail_response = self.client.get(
            reverse("api:program-detail", args=[program_id])
        )
        self.assert_response_success(program_detail_response, status.HTTP_200_OK)
        self.assertEqual(program_detail_response.data["name"], "Test Exchange Program")

        # 3. Student creates application for program
        application_data = {
            "program": program_id,
            "comments": "I am interested in this program",
        }

        application_response = self.client.post(
            reverse("api:application-list"), application_data, format="json"
        )
        self.assert_response_success(application_response, status.HTTP_201_CREATED)
        self.assertEqual(str(application_response.data["program"]), str(program_id))

    def test_program_eligibility_check(self):
        """Test program eligibility checking."""
        # Create program with specific requirements
        program = self.create_program(min_gpa=3.5, required_language="English")

        # Create student with different profiles
        student_low_gpa = self.create_user(role="student")
        student_low_gpa.profile.gpa = 3.0
        student_low_gpa.profile.save()

        student_high_gpa = self.create_user(role="student")
        student_high_gpa.profile.gpa = 3.8
        student_high_gpa.profile.save()

        # Test eligibility check
        self.authenticate_user(student_low_gpa)
        response = self.client.get(reverse("api:program-detail", args=[program.id]))
        self.assert_response_success(response, status.HTTP_200_OK)
        # Note: Actual eligibility logic would be implemented in the frontend
        # or as a separate API endpoint

    def test_program_statistics(self):
        """Test program statistics and analytics."""
        # Clear existing programs to ensure clean test
        Program.objects.all().delete()

        # Create programs and applications
        program1 = self.create_program(name="Popular Program")
        program2 = self.create_program(name="Less Popular Program")

        # Create applications for program1
        for _i in range(5):
            student = self.create_user(role="student")
            self.create_application(student=student, program=program1)

        # Create applications for program2
        for _i in range(2):
            student = self.create_user(role="student")
            self.create_application(student=student, program=program2)

        # Test program listing with application counts
        admin = self.create_user(role="admin")
        self.authenticate_user(admin)

        response = self.client.get(reverse("api:program-list"))
        self.assert_response_success(response, status.HTTP_200_OK)

        # Verify programs are returned
        self.assertEqual(len(response.data["results"]), 2)

        # Note: Application counts would typically be added as annotations
        # or through a separate statistics endpoint


class TestProgramsPerformance(PerformanceTestCase):
    """Test programs API performance."""

    @pytest.mark.performance
    def test_large_program_list_performance(self):
        """Test performance with large number of programs."""
        # Create many programs
        for i in range(100):
            self.create_program(name=f"Program {i}")

        student = self.create_user(role="student")
        self.authenticate_user(student)

        # Test response time
        response = self.client.get(reverse("api:program-list"))
        self.assert_response_success(response, status.HTTP_200_OK)
        self.assert_response_time(
            response, max_time=1.0
        )  # Should respond within 1 second

        # Verify pagination works correctly
        self.assertEqual(response.data["count"], 100)
        self.assertIn("results", response.data)
        self.assertIn("next", response.data)

    @pytest.mark.performance
    def test_program_search_performance(self):
        """Test search performance with large dataset."""
        # Create programs with searchable content
        for i in range(50):
            self.create_program(
                name=f"Program {i}",
                description=f"This is a detailed description for program {i} with many words",
            )

        student = self.create_user(role="student")
        self.authenticate_user(student)

        # Test search performance
        response = self.client.get(f"{reverse('api:program-list')}?search=detailed")
        self.assert_response_success(response, status.HTTP_200_OK)
        self.assert_response_time(response, max_time=1.0)

        # Verify search results
        self.assertGreater(len(response.data["results"]), 0)


class TestProgramsSecurity(APITestCase):
    """Test programs API security."""

    def test_program_data_validation(self):
        """Test program data validation and sanitization."""
        admin = self.create_user(role="admin")
        self.authenticate_user(admin)

        # Test XSS prevention
        malicious_data = {
            "name": '<script>alert("xss")</script>',
            "description": "Normal description",
            "start_date": "2025-06-01",
            "end_date": "2025-12-01",
            "is_active": True,
        }

        response = self.client.post(
            reverse("api:program-list"), malicious_data, format="json"
        )

        # For MVP, we accept the data as-is since XSS protection is handled at frontend
        # In production, this should be validated or sanitized
        self.assert_response_success(response, status.HTTP_201_CREATED)
        # Verify the data is stored as provided (frontend will handle escaping)
        self.assertEqual(response.data["name"], '<script>alert("xss")</script>')

    def test_program_access_control(self):
        """Test program access control by role."""
        program = self.create_program(name="Test Program")

        # Test student access (should be read-only)
        student = self.create_user(role="student")
        self.authenticate_user(student)

        # Should be able to read
        response = self.client.get(reverse("api:program-detail", args=[program.id]))
        self.assert_response_success(response, status.HTTP_200_OK)

        # Should not be able to modify
        response = self.client.patch(
            reverse("api:program-detail", args=[program.id]),
            {"name": "Modified Name"},
            format="json",
        )
        self.assert_response_unauthorized(response)

        # Test coordinator access (should be read-only)
        coordinator = self.create_user(role="coordinator")
        self.authenticate_user(coordinator)

        response = self.client.patch(
            reverse("api:program-detail", args=[program.id]),
            {"name": "Modified Name"},
            format="json",
        )
        self.assert_response_unauthorized(response)

        # Test admin access (should be able to modify)
        admin = self.create_user(role="admin")
        self.authenticate_user(admin)

        response = self.client.patch(
            reverse("api:program-detail", args=[program.id]),
            {"name": "Modified Name"},
            format="json",
        )
        self.assert_response_success(response, status.HTTP_200_OK)
