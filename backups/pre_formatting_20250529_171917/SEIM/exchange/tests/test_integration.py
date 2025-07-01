"""
Integration tests for Exchange workflows
"""

import json
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from exchange.models import Document, Exchange, UserProfile


class ExchangeWorkflowIntegrationTest(TestCase):
    """Integration tests for complete exchange workflows"""

    def setUp(self):
        self.client = Client()

        # Create users
        self.student = User.objects.create_user(
            username="student", email="student@test.com", password="testpass123"
        )
        self.student_profile = UserProfile.objects.create(
            user=self.student, role="STUDENT"
        )

        self.coordinator = User.objects.create_user(
            username="coordinator", email="coordinator@test.com", password="testpass123"
        )
        self.coordinator_profile = UserProfile.objects.create(
            user=self.coordinator, role="COORDINATOR"
        )

    def test_complete_exchange_workflow(self):
        """Test complete workflow from creation to approval"""
        # Step 1: Student creates draft exchange
        self.client.login(username="student", password="testpass123")

        create_data = {
            "first_name": "Test",
            "last_name": "Student",
            "email": "test@test.com",
            "phone_number": "+1234567890",
            "academic_level": "BACHELOR",
            "current_university": "Test University",
            "host_university": "Host University",
            "host_country": "Germany",
            "start_date": (timezone.now().date() + timedelta(days=90)).isoformat(),
            "end_date": (timezone.now().date() + timedelta(days=180)).isoformat(),
            "action": "save_draft",
        }

        response = self.client.post(reverse("exchange:create-exchange"), create_data)
        exchange = Exchange.objects.get(student=self.student)
        self.assertEqual(exchange.status, "DRAFT")

        # Step 2: Student uploads documents
        document_file = SimpleUploadedFile(
            "test_document.pdf", b"file_content", content_type="application/pdf"
        )

        upload_response = self.client.post(
            reverse("exchange:document-upload"),
            {
                "exchange": exchange.id,
                "category": "TRANSCRIPT",
                "file": document_file,
                "description": "Test transcript",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(upload_response.status_code, 200)
        self.assertEqual(Document.objects.filter(exchange=exchange).count(), 1)

        # Step 3: Student submits exchange
        submit_response = self.client.post(
            reverse("exchange:exchange-submit", args=[exchange.id]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        exchange.refresh_from_db()
        self.assertEqual(exchange.status, "SUBMITTED")

        # Step 4: Coordinator starts review
        self.client.logout()
        self.client.login(username="coordinator", password="testpass123")

        review_response = self.client.post(
            reverse("exchange:exchange-review", args=[exchange.id]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        exchange.refresh_from_db()
        self.assertEqual(exchange.status, "UNDER_REVIEW")

        # Step 5: Coordinator approves exchange
        approve_response = self.client.post(
            reverse("exchange:exchange-approve", args=[exchange.id]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        exchange.refresh_from_db()
        self.assertEqual(exchange.status, "APPROVED")

        # Verify notifications were created
        student_notifications = Notification.objects.filter(user=self.student)
        self.assertTrue(student_notifications.exists())
        self.assertTrue(
            any(n.title.lower().contains("approved") for n in student_notifications)
        )

    def test_rejection_workflow(self):
        """Test exchange rejection workflow"""
        # Create and submit exchange
        self.client.login(username="student", password="testpass123")

        exchange = Exchange.objects.create(
            student=self.student,
            first_name="Test",
            last_name="Student",
            status="SUBMITTED",
        )

        # Coordinator reviews and rejects
        self.client.logout()
        self.client.login(username="coordinator", password="testpass123")

        # Start review
        self.client.post(
            reverse("exchange:exchange-review", args=[exchange.id]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        # Reject with reason
        reject_data = {"reason": "Incomplete documentation"}
        reject_response = self.client.post(
            reverse("exchange:exchange-reject", args=[exchange.id]),
            data=json.dumps(reject_data),
            content_type="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        exchange.refresh_from_db()
        self.assertEqual(exchange.status, "REJECTED")

        # Verify student was notified
        notifications = Notification.objects.filter(
            user=self.student, title__icontains="rejected"
        )
        self.assertTrue(notifications.exists())

    def test_document_management_workflow(self):
        """Test document upload, review, and deletion workflow"""
        # Create exchange
        exchange = Exchange.objects.create(
            student=self.student, first_name="Test", last_name="Student", status="DRAFT"
        )

        self.client.login(username="student", password="testpass123")

        # Upload multiple documents
        document_types = ["TRANSCRIPT", "LANGUAGE_CERT", "MOTIVATION"]

        for doc_type in document_types:
            file_content = f"{doc_type} content".encode()
            document_file = SimpleUploadedFile(
                f"{doc_type.lower()}.pdf", file_content, content_type="application/pdf"
            )

            response = self.client.post(
                reverse("exchange:document-upload"),
                {"exchange": exchange.id, "category": doc_type, "file": document_file},
                HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            )

            self.assertEqual(response.status_code, 200)

        # Verify all documents uploaded
        documents = Document.objects.filter(exchange=exchange)
        self.assertEqual(documents.count(), 3)

        # Delete one document
        doc_to_delete = documents.first()
        delete_response = self.client.delete(
            reverse("exchange:document-delete", args=[doc_to_delete.id]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(delete_response.status_code, 200)
        self.assertEqual(Document.objects.filter(exchange=exchange).count(), 2)

    def test_notification_workflow(self):
        """Test notification creation and management"""
        # Create exchange
        exchange = Exchange.objects.create(
            student=self.student,
            first_name="Test",
            last_name="Student",
            status="SUBMITTED",
        )

        # Login as coordinator
        self.client.login(username="coordinator", password="testpass123")

        # Perform actions that trigger notifications
        actions = [
            ("exchange:exchange-review", "UNDER_REVIEW"),
            ("exchange:exchange-approve", "APPROVED"),
        ]

        for url_name, expected_status in actions:
            response = self.client.post(
                reverse(url_name, args=[exchange.id]),
                HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            )

            exchange.refresh_from_db()
            self.assertEqual(exchange.status, expected_status)

        # Check student notifications
        notifications = Notification.objects.filter(user=self.student)
        self.assertGreaterEqual(notifications.count(), 2)

        # Test marking notification as read
        self.client.logout()
        self.client.login(username="student", password="testpass123")

        notification = notifications.first()
        read_response = self.client.post(
            reverse("exchange:notification-read", args=[notification.id]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        notification.refresh_from_db()
        self.assertTrue(notification.is_read)

    def test_filter_and_search_workflow(self):
        """Test filtering and searching exchanges"""
        # Create multiple exchanges with different statuses
        statuses = ["DRAFT", "SUBMITTED", "UNDER_REVIEW", "APPROVED", "REJECTED"]

        for i, status in enumerate(statuses):
            Exchange.objects.create(
                student=self.student,
                first_name=f"Test{i}",
                last_name="Student",
                status=status,
                host_country="Germany" if i % 2 == 0 else "France",
            )

        self.client.login(username="coordinator", password="testpass123")

        # Test status filter
        response = self.client.get(
            reverse("exchange:exchange-list"), {"status": "APPROVED"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test3")  # Approved exchange
        self.assertNotContains(response, "Test0")  # Draft exchange

        # Test country filter
        response = self.client.get(
            reverse("exchange:exchange-list"), {"country": "Germany"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test0")
        self.assertContains(response, "Test2")
        self.assertNotContains(response, "Test1")

    def test_permission_workflow(self):
        """Test permission checks throughout the workflow"""
        # Create another student
        other_student = User.objects.create_user(
            username="otherstudent", email="other@test.com", password="testpass123"
        )
        UserProfile.objects.create(user=other_student, role="STUDENT")

        # Create exchange for first student
        exchange = Exchange.objects.create(
            student=self.student, first_name="Test", last_name="Student", status="DRAFT"
        )

        # Try to access as other student
        self.client.login(username="otherstudent", password="testpass123")

        # Should not be able to view
        response = self.client.get(
            reverse("exchange:exchange-detail", args=[exchange.id])
        )
        self.assertEqual(response.status_code, 403)

        # Should not be able to edit
        response = self.client.get(
            reverse("exchange:exchange-edit", args=[exchange.id])
        )
        self.assertEqual(response.status_code, 403)

        # Should not be able to submit
        response = self.client.post(
            reverse("exchange:exchange-submit", args=[exchange.id]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 403)

    def test_ajax_error_handling(self):
        """Test AJAX error responses"""
        self.client.login(username="student", password="testpass123")

        # Try to submit non-existent exchange
        response = self.client.post(
            reverse("exchange:exchange-submit", args=[9999]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 404)

        # Try to upload document without required fields
        response = self.client.post(
            reverse("exchange:document-upload"),
            {},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertIn("error", response_data)
