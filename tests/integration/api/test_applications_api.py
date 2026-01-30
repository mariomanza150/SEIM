"""
Integration tests for applications API endpoints.

These tests validate the applications API that the frontend uses for:
- Creating applications
- Submitting applications
- Application workflow transitions
- Role-based access control
- Application filtering and search
"""

import pytest
from django.urls import reverse
from rest_framework import status

from exchange.models import ApplicationStatus
from tests.utils import APITestCase, PerformanceTestCase, WorkflowTestCase


class TestApplicationsAPI(APITestCase):
    """Test applications API endpoints."""

    def setUp(self):
        """Set up test case."""
        super().setUp()
        self.applications_url = reverse("api:application-list")
        self.application_detail_url = reverse("api:application-detail", args=[1])

    def test_create_application_student(self):
        """Test that students can create applications."""
        student = self.create_user(role="student")
        program = self.create_program()
        self.authenticate_user(student)

        data = {"program": program.id}

        response = self.client.post(self.applications_url, data, format="json")

        if response.status_code != 201:
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.data}")

        self.assert_response_success(response, status.HTTP_201_CREATED)
        self.assertEqual(response.data["program"], program.id)
        self.assertEqual(response.data["student"], student.id)
        self.assertEqual(response.data["status"], "draft")

    def test_create_application_other_roles(self):
        """Test that coordinators and admins can also create applications (on behalf of students)."""
        program = self.create_program()

        # Try as coordinator (should succeed)
        coordinator = self.create_user(role="coordinator")
        self.authenticate_user(coordinator)

        data = {"program": program.id}

        response = self.client.post(self.applications_url, data, format="json")
        self.assertEqual(response.status_code, 201)

        # Try as admin (should succeed)
        admin = self.create_user(role="admin")
        self.authenticate_user(admin)

        response = self.client.post(self.applications_url, data, format="json")
        self.assertEqual(response.status_code, 201)

    def test_list_applications_student(self):
        """Test that students can only see their own applications."""
        student1 = self.create_user(role="student")
        student2 = self.create_user(role="student")
        program = self.create_program()

        # Create applications for both students
        app1 = self.create_application(student=student1, program=program)
        self.create_application(student=student2, program=program)

        # Authenticate as student1
        self.authenticate_user(student1)

        response = self.client.get(self.applications_url)

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], str(app1.id))

    def test_list_applications_coordinator(self):
        """Test that coordinators can see all applications."""
        student1 = self.create_user(role="student")
        student2 = self.create_user(role="student")
        program = self.create_program()

        # Create applications for both students
        app1 = self.create_application(student=student1, program=program)
        app2 = self.create_application(student=student2, program=program)

        # Authenticate as coordinator
        coordinator = self.create_user(role="coordinator")
        self.authenticate_user(coordinator)

        response = self.client.get(self.applications_url)

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        application_ids = [app["id"] for app in response.data["results"]]
        self.assertIn(str(app1.id), application_ids)
        self.assertIn(str(app2.id), application_ids)

    def test_list_applications_admin(self):
        """Test that admins can see all applications."""
        student1 = self.create_user(role="student")
        student2 = self.create_user(role="student")
        program = self.create_program()

        # Create applications for both students
        app1 = self.create_application(student=student1, program=program)
        app2 = self.create_application(student=student2, program=program)

        # Authenticate as admin
        admin = self.create_user(role="admin")
        self.authenticate_user(admin)

        response = self.client.get(self.applications_url)

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        application_ids = [app["id"] for app in response.data["results"]]
        self.assertIn(str(app1.id), application_ids)
        self.assertIn(str(app2.id), application_ids)

    def test_update_application_student_own(self):
        """Test that students can update their own applications."""
        student = self.create_user(role="student")
        application = self.create_application(student=student)
        self.authenticate_user(student)

        data = {"status": "submitted"}

        response = self.client.patch(
            reverse("api:application-detail", args=[application.id]),
            data,
            format="json",
        )

        self.assert_response_success(response, status.HTTP_200_OK)
        # Note: comments are handled separately via Comment model

    def test_update_application_student_other(self):
        """Test that students cannot update other students' applications."""
        student1 = self.create_user(role="student")
        student2 = self.create_user(role="student")
        application = self.create_application(student=student1)

        self.authenticate_user(student2)

        data = {"status": "submitted"}

        response = self.client.patch(
            reverse("api:application-detail", args=[application.id]),
            data,
            format="json",
        )
        if response.status_code not in [401, 403]:
            print(f"Response status: {response.status_code}")
            print(f"Response data: {getattr(response, 'data', None)}")
        self.assertEqual(response.status_code, 404)

    def test_update_application_coordinator(self):
        """Test that coordinators can update applications."""
        student = self.create_user(role="student")
        application = self.create_application(student=student)

        coordinator = self.create_user(role="coordinator")
        self.authenticate_user(coordinator)

        data = {"status": "under_review"}

        response = self.client.patch(
            reverse("api:application-detail", args=[application.id]),
            data,
            format="json",
        )

        self.assert_response_success(response, status.HTTP_200_OK)
        # Note: comments are handled separately via Comment model

    def test_submit_application(self):
        """Test application submission workflow."""
        student = self.create_user(role="student")
        application = self.create_application(student=student, status_name="draft")
        self.authenticate_user(student)

        # Submit application
        response = self.client.post(
            reverse("api:application-submit", args=[application.id])
        )

        self.assert_response_success(response, status.HTTP_200_OK)

        # Verify application status changed
        application.refresh_from_db()
        self.assertEqual(application.status.name, "submitted")
        self.assertIsNotNone(application.submitted_at)

    def test_submit_application_wrong_status(self):
        """Test that applications cannot be submitted from wrong status."""
        student = self.create_user(role="student")
        application = self.create_application(student=student, status_name="submitted")
        self.authenticate_user(student)

        # Try to submit already submitted application
        response = self.client.post(
            reverse("api:application-submit", args=[application.id])
        )

        self.assert_response_error(response, status.HTTP_400_BAD_REQUEST)

    def test_withdraw_application(self):
        """Test application withdrawal workflow."""
        student = self.create_user(role="student")
        application = self.create_application(student=student, status_name="draft")
        self.authenticate_user(student)

        # Withdraw application
        response = self.client.post(
            reverse("api:application-withdraw", args=[application.id])
        )
        if response.status_code != 200:
            print(f"Response status: {response.status_code}")
            print(f"Response data: {getattr(response, 'data', None)}")
        self.assert_response_success(response, status.HTTP_200_OK)

        # Verify application status changed
        application.refresh_from_db()
        self.assertEqual(application.status.name, "withdrawn")

    def test_application_filtering(self):
        """Test application filtering functionality."""
        student = self.create_user(role="student")
        program1 = self.create_program(name="Program 1")
        program2 = self.create_program(name="Program 2")

        # Create applications with different statuses
        draft_app = self.create_application(
            student=student, program=program1, status_name="draft"
        )
        self.create_application(
            student=student, program=program2, status_name="submitted"
        )

        self.authenticate_user(student)

        # Filter by status (use status ID)
        draft_status = ApplicationStatus.objects.get(name="draft")
        response = self.client.get(f"{self.applications_url}?status={draft_status.id}")
        if response.status_code != 200:
            print(f"Response status: {response.status_code}")
            print(f"Response data: {getattr(response, 'data', None)}")
        self.assert_response_success(response, status.HTTP_200_OK)
        
        # Verify our draft application is in the results
        draft_app_ids = [app["id"] for app in response.data["results"]]
        self.assertIn(str(draft_app.id), draft_app_ids)
        
        # Verify the draft application has correct status
        our_draft_app = next((app for app in response.data["results"] if app["id"] == str(draft_app.id)), None)
        self.assertIsNotNone(our_draft_app)
        self.assertEqual(our_draft_app["status"], "draft")

        # Filter by program
        response = self.client.get(f"{self.applications_url}?program={program1.id}")
        self.assert_response_success(response, status.HTTP_200_OK)
        
        # Verify our application is in program1 results
        program1_app_ids = [app["id"] for app in response.data["results"]]
        self.assertIn(str(draft_app.id), program1_app_ids)
        
        # Verify the application belongs to program1
        our_program1_app = next((app for app in response.data["results"] if app["id"] == str(draft_app.id)), None)
        self.assertIsNotNone(our_program1_app)
        self.assertEqual(our_program1_app["program"], program1.id)

    def test_application_search(self):
        """Test application search functionality."""
        student = self.create_user(role="student")
        program1 = self.create_program(name="Computer Science Program")
        program2 = self.create_program(name="Engineering Program")

        # Create applications for different programs
        app1 = self.create_application(student=student, program=program1)
        app2 = self.create_application(student=student, program=program2)

        self.authenticate_user(student)

        # Search by program name
        response = self.client.get(f"{self.applications_url}?search=Computer Science")
        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], str(app1.id))

        # Search by comments
        response = self.client.get(f"{self.applications_url}?search=engineering")
        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], str(app2.id))


class TestApplicationsIntegration(WorkflowTestCase):
    """Test applications integration scenarios."""

    def test_complete_application_workflow(self):
        """Test complete application workflow from creation to completion."""
        # 1. Student creates application
        student = self.create_user(role="student")
        program = self.create_program()
        self.authenticate_user(student)

        application_data = {"program": program.id}

        create_response = self.client.post(
            reverse("api:application-list"), application_data, format="json"
        )
        self.assert_response_success(create_response, status.HTTP_201_CREATED)
        application_id = create_response.data["id"]

        # 2. Student submits application
        submit_response = self.client.post(
            reverse("api:application-submit", args=[application_id])
        )
        self.assert_response_success(submit_response, status.HTTP_200_OK)

        # 3. Coordinator reviews application
        coordinator = self.create_user(role="coordinator")
        self.authenticate_user(coordinator)

        # Add comment
        comment_data = {
            "application": application_id,
            "text": "Application looks good",
            "is_private": False,
            "author": coordinator.id,
        }

        comment_response = self.client.post(
            reverse("api:comment-list"), comment_data, format="json"
        )
        if comment_response.status_code != 201:
            print(f"Response status: {comment_response.status_code}")
            print(f"Response data: {getattr(comment_response, 'data', None)}")
        self.assert_response_success(comment_response, status.HTTP_201_CREATED)

        # 4. Admin approves application
        admin = self.create_user(role="admin")
        self.authenticate_user(admin)

        # Update status to approved
        update_data = {"status": "approved"}
        update_response = self.client.patch(
            reverse("api:application-detail", args=[application_id]),
            update_data,
            format="json",
        )
        self.assert_response_success(update_response, status.HTTP_200_OK)

        # 5. Verify final state
        final_response = self.client.get(
            reverse("api:application-detail", args=[application_id])
        )
        self.assert_response_success(final_response, status.HTTP_200_OK)
        self.assertEqual(final_response.data["status"], "approved")

    def test_application_with_documents(self):
        """Test application workflow with document uploads."""
        # 1. Create application
        student = self.create_user(role="student")
        program = self.create_program()
        application = self.create_application(student=student, program=program)

        # 2. Upload documents
        self.authenticate_user(student)

        # Create test file
        from django.core.files.uploadedfile import SimpleUploadedFile

        test_file = SimpleUploadedFile(
            "test_document.pdf",
            b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<< /Type /Catalog >>\nendobj\n",  # Minimal valid PDF header
            content_type="application/pdf",
        )

        # For document upload
        from documents.models import DocumentType

        doc_type = DocumentType.objects.create(name="Transcript")
        document_data = {
            "application": application.id,
            "file": test_file,
            "file_name": "test_document.pdf",
            "file_type": "application/pdf",
            "is_required": True,
            "type": doc_type.id,
            "uploaded_by": student.id,
        }

        document_response = self.client.post(
            reverse("api:document-list"), document_data, format="multipart"
        )
        if document_response.status_code != 201:
            print(f"Response status: {document_response.status_code}")
            print(f"Response data: {getattr(document_response, 'data', None)}")
        self.assert_response_success(document_response, status.HTTP_201_CREATED)

        # 3. Submit application
        submit_response = self.client.post(
            reverse("api:application-submit", args=[application.id])
        )
        self.assert_response_success(submit_response, status.HTTP_200_OK)

        # 4. Verify application has documents
        application_response = self.client.get(
            reverse("api:application-detail", args=[application.id])
        )
        self.assert_response_success(application_response, status.HTTP_200_OK)
        # Note: Document details would be included in the response if configured

    def test_application_notifications(self):
        """Test that notifications are sent during application workflow."""
        # This test would verify that notifications are sent
        # when applications are submitted, reviewed, approved, etc.
        # For now, we'll test the basic workflow

        student = self.create_user(role="student")
        program = self.create_program()
        application = self.create_application(student=student, program=program)

        self.authenticate_user(student)

        # Submit application (should trigger notification)
        response = self.client.post(
            reverse("api:application-submit", args=[application.id])
        )
        self.assert_response_success(response, status.HTTP_200_OK)

        # Verify application was submitted
        application.refresh_from_db()
        self.assertEqual(application.status.name, "submitted")
        # Note: Notification verification would require checking the notification system


class TestApplicationsPerformance(PerformanceTestCase):
    """Test applications API performance."""

    @pytest.mark.performance
    def test_large_application_list_performance(self):
        """Test performance with large number of applications."""
        # Create many applications
        student = self.create_user(role="student")
        program = self.create_program()

        for _i in range(50):
            self.create_application(student=student, program=program)

        self.authenticate_user(student)

        # Test response time
        response = self.client.get(reverse("api:application-list"))
        self.assert_response_success(response, status.HTTP_200_OK)
        self.assert_response_time(response, max_time=1.0)

        # Verify pagination works correctly
        self.assertEqual(response.data["count"], 50)
        self.assertIn("results", response.data)
        self.assertIn("next", response.data)

    @pytest.mark.performance
    def test_application_search_performance(self):
        """Test search performance with large dataset."""
        # Create applications with searchable content
        student = self.create_user(role="student")
        self.create_program()

        for i in range(100):
            self.create_application(
                student=student,
                status_name="draft",
                program=self.create_program(name=f"Detailed application {i}"),
            )

        self.authenticate_user(student)

        # Test search performance
        response = self.client.get(f"{reverse('api:application-list')}?search=Detailed")
        if response.status_code != 200:
            print(f"Response status: {response.status_code}")
            print(f"Response data: {getattr(response, 'data', None)}")
        self.assert_response_success(response, status.HTTP_200_OK)
        self.assert_response_time(response, max_time=1.0)

        # Verify search results
        self.assertGreater(len(response.data["results"]), 0)


class TestApplicationsSecurity(APITestCase):
    """Test applications API security."""

    def test_application_data_validation(self):
        """Test application data validation and sanitization."""
        student = self.create_user(role="student")
        program = self.create_program()
        self.authenticate_user(student)

        # Test XSS prevention in program name (since comments are separate)
        malicious_data = {"program": program.id, "status": "submitted"}

        response = self.client.post(
            reverse("api:application-list"), malicious_data, format="json"
        )

        # Should accept valid data
        self.assert_response_success(response, status.HTTP_201_CREATED)

        # Test XSS prevention in comments via Comment model
        application_id = response.data["id"]
        comment_data = {
            "application": application_id,
            "text": '<script>alert("xss")</script>',
            "is_private": False,
        }

        comment_response = self.client.post(
            reverse("api:comment-list"), comment_data, format="json"
        )

        # Should either reject the data or sanitize it
        if comment_response.status_code == status.HTTP_201_CREATED:
            # If accepted, verify it's sanitized
            self.assertNotIn("<script>", comment_response.data["text"])
        else:
            # If rejected, verify it's due to validation
            self.assert_response_error(comment_response, status.HTTP_400_BAD_REQUEST)

    def test_application_access_control(self):
        """Test application access control by role."""
        student1 = self.create_user(role="student")
        student2 = self.create_user(role="student")
        application = self.create_application(student=student1)

        # Test student2 cannot access student1's application
        self.authenticate_user(student2)

        response = self.client.get(
            reverse("api:application-detail", args=[application.id])
        )
        if response.status_code not in [401, 403]:
            print(f"Response status: {response.status_code}")
            print(f"Response data: {getattr(response, 'data', None)}")
        self.assertEqual(response.status_code, 404)

        # Test coordinator can access
        coordinator = self.create_user(role="coordinator")
        self.authenticate_user(coordinator)

        response = self.client.get(
            reverse("api:application-detail", args=[application.id])
        )
        self.assert_response_success(response, status.HTTP_200_OK)

        # Test admin can access
        admin = self.create_user(role="admin")
        self.authenticate_user(admin)

        response = self.client.get(
            reverse("api:application-detail", args=[application.id])
        )
        self.assert_response_success(response, status.HTTP_200_OK)

    def test_application_status_transitions(self):
        """Test that only authorized users can change application status."""
        student = self.create_user(role="student")
        application = self.create_application(student=student, status_name="submitted")

        # Test student cannot change status to approved
        self.authenticate_user(student)

        data = {"status": "approved"}
        response = self.client.patch(
            reverse("api:application-detail", args=[application.id]),
            data,
            format="json",
        )
        if response.status_code not in [401, 403]:
            print(f"Response status: {response.status_code}")
            print(f"Response data: {getattr(response, 'data', None)}")
        self.assertEqual(response.status_code, 400)

        # Test coordinator can change status
        coordinator = self.create_user(role="coordinator")
        self.authenticate_user(coordinator)

        response = self.client.patch(
            reverse("api:application-detail", args=[application.id]),
            data,
            format="json",
        )
        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "approved")
