"""
Tests for documents services.
"""
# Create a mock magic module for tests
import sys
from datetime import date
from unittest.mock import MagicMock, patch

sys.modules['magic'] = MagicMock()

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from documents.models import (
    Document,
    DocumentResubmissionRequest,
    DocumentType,
    DocumentValidation,
)
from documents.services import DocumentService
from exchange.models import Application, ApplicationStatus, Program

User = get_user_model()


class TestDocumentService(TestCase):
    """Test the DocumentService."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

        self.program = Program.objects.create(
            name="Test Program",
            description="Test program description",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 30),
            is_active=True
        )

        # Create ApplicationStatus
        self.application_status, _ = ApplicationStatus.objects.get_or_create(
            name="draft",
            defaults={"order": 1}
        )

        self.application = Application.objects.create(
            student=self.user,
            program=self.program,
            status=self.application_status
        )

        self.document_type = DocumentType.objects.create(
            name="transcript",
            description="Academic transcript"
        )

    def test_validate_file_type_and_size_success(self):
        """Test successful file type and size validation."""
        # Create a mock file
        file_content = b"Test file content"
        uploaded_file = SimpleUploadedFile(
            "test.pdf",
            file_content,
            content_type="application/pdf"
        )
        uploaded_file.size = 1024  # 1KB

        # Create a mock magic module
        mock_magic_module = MagicMock()
        mock_magic_module.from_buffer = MagicMock(return_value="application/pdf")

        with patch('documents.services.MAGIC_AVAILABLE', True):
            with patch('documents.services.magic', mock_magic_module):
                result = DocumentService.validate_file_type_and_size(uploaded_file)

                self.assertTrue(result)

    def test_validate_file_type_and_size_invalid_type(self):
        """Test file validation with invalid type."""
        file_content = b"Test file content"
        uploaded_file = SimpleUploadedFile(
            "test.txt",
            file_content,
            content_type="text/plain"
        )
        uploaded_file.size = 1024

        with patch('documents.services.MAGIC_AVAILABLE', True):
            with patch('magic.from_buffer') as mock_magic:
                mock_magic.return_value = "text/plain"

                with self.assertRaises(ValueError, msg="File type not allowed."):
                    DocumentService.validate_file_type_and_size(uploaded_file)

    def test_validate_file_type_and_size_too_large(self):
        """Test file validation with file too large."""
        file_content = b"x" * (DocumentService.MAX_FILE_SIZE_MB * 1024 * 1024 + 1000)
        uploaded_file = SimpleUploadedFile(
            "large.pdf",
            file_content,
            content_type="application/pdf"
        )
        uploaded_file.size = DocumentService.MAX_FILE_SIZE_MB * 1024 * 1024 + 1000

        with patch('documents.services.MAGIC_AVAILABLE', True):
            with patch('magic.from_buffer') as mock_magic:
                mock_magic.return_value = "application/pdf"

                with self.assertRaises(ValueError, msg="File size exceeds maximum allowed."):
                    DocumentService.validate_file_type_and_size(uploaded_file)

    def test_virus_scan_clean(self):
        """Test virus scan with clean file."""
        file_content = b"Test file content"
        uploaded_file = SimpleUploadedFile(
            "test.pdf",
            file_content,
            content_type="application/pdf"
        )

        result = DocumentService.virus_scan(uploaded_file)

        self.assertTrue(result)

    def test_upload_document_success(self):
        """Test successful document upload."""
        file_content = b"Test file content"
        uploaded_file = SimpleUploadedFile(
            "test.pdf",
            file_content,
            content_type="application/pdf"
        )
        uploaded_file.size = 1024

        # Create a mock magic module
        mock_magic_module = MagicMock()
        mock_magic_module.from_buffer = MagicMock(return_value="application/pdf")

        with patch('documents.services.MAGIC_AVAILABLE', True):
            with patch('documents.services.magic', mock_magic_module):
                with patch('documents.services.scan_document_virus.delay'):
                    result = DocumentService.upload_document(
                        self.application,
                        self.document_type,
                        uploaded_file,
                        self.user
                    )

                    self.assertIsInstance(result, Document)
                    self.assertEqual(result.application, self.application)
                    self.assertEqual(result.type, self.document_type)
                    self.assertEqual(result.uploaded_by, self.user)

    def test_upload_document_invalid_file(self):
        """Test document upload with invalid file."""
        file_content = b"Test file content"
        uploaded_file = SimpleUploadedFile(
            "test.txt",
            file_content,
            content_type="text/plain"
        )
        uploaded_file.size = 1024

        with patch('documents.services.MAGIC_AVAILABLE', True):
            with patch('magic.from_buffer') as mock_magic:
                mock_magic.return_value = "text/plain"

                with self.assertRaises(ValueError, msg="File type not allowed."):
                    DocumentService.upload_document(
                        self.application,
                        self.document_type,
                        uploaded_file,
                        self.user
                    )

    def test_validate_document_success(self):
        """Test successful document validation."""
        document = Document.objects.create(
            application=self.application,
            type=self.document_type,
            uploaded_by=self.user
        )

        with patch("notifications.services.NotificationService.send_notification") as mock_notify:
            result = DocumentService.validate_document(
                document,
                self.user,
                "valid",
                "Document is valid",
            )

        mock_notify.assert_not_called()

        self.assertIsInstance(result, DocumentValidation)
        self.assertEqual(result.document, document)
        self.assertEqual(result.validator, self.user)
        self.assertEqual(result.result, "valid")

        document.refresh_from_db()
        self.assertTrue(document.is_valid)
        self.assertIsNotNone(document.validated_at)

    def test_validate_document_invalid(self):
        """Test document validation with invalid result."""
        document = Document.objects.create(
            application=self.application,
            type=self.document_type,
            uploaded_by=self.user
        )

        with patch("notifications.services.NotificationService.send_notification") as mock_notify:
            DocumentService.validate_document(
                document,
                self.user,
                "invalid",
                "Document is invalid",
            )

        mock_notify.assert_called_once()

        document.refresh_from_db()
        self.assertFalse(document.is_valid)

    def test_can_request_resubmission_under_limit(self):
        """Test resubmission request under limit."""
        document = Document.objects.create(
            application=self.application,
            type=self.document_type,
            uploaded_by=self.user
        )

        result = DocumentService.can_request_resubmission(document)

        self.assertTrue(result)

    def test_can_request_resubmission_at_limit(self):
        """Test resubmission request at limit."""
        document = Document.objects.create(
            application=self.application,
            type=self.document_type,
            uploaded_by=self.user
        )

        # Create maximum number of resubmission requests
        for i in range(DocumentService.MAX_RESUBMISSIONS):
            DocumentResubmissionRequest.objects.create(
                document=document,
                requested_by=self.user,
                reason=f"Request {i+1}"
            )

        result = DocumentService.can_request_resubmission(document)

        self.assertFalse(result)

    def test_request_resubmission_success(self):
        """Test successful resubmission request."""
        document = Document.objects.create(
            application=self.application,
            type=self.document_type,
            uploaded_by=self.user
        )

        with patch('documents.services.NotificationService.send_notification'):
            result = DocumentService.request_resubmission(
                document,
                self.user,
                "Document needs to be updated"
            )

            self.assertIsInstance(result, DocumentResubmissionRequest)
            self.assertEqual(result.document, document)
            self.assertEqual(result.requested_by, self.user)
            self.assertEqual(result.reason, "Document needs to be updated")

    def test_request_resubmission_over_limit(self):
        """Test resubmission request over limit."""
        document = Document.objects.create(
            application=self.application,
            type=self.document_type,
            uploaded_by=self.user
        )

        # Create maximum number of resubmission requests
        for i in range(DocumentService.MAX_RESUBMISSIONS):
            DocumentResubmissionRequest.objects.create(
                document=document,
                requested_by=self.user,
                reason=f"Request {i+1}"
            )

        with self.assertRaises(ValueError, msg="Maximum number of resubmissions reached."):
            DocumentService.request_resubmission(
                document,
                self.user,
                "Another request"
            )

    def test_can_replace_document_draft_status(self):
        """Test document replacement when application is in draft status."""
        # Set application to draft status
        draft_status, _ = ApplicationStatus.objects.get_or_create(name="draft", defaults={"order": 1})
        self.application.status = draft_status
        self.application.save()

        document = Document.objects.create(
            application=self.application,
            type=self.document_type,
            uploaded_by=self.user
        )

        result = DocumentService.can_replace_document(document, self.user)

        self.assertTrue(result)

    def test_can_replace_document_with_pending_request(self):
        """Test document replacement with pending resubmission request."""
        # Set application to submitted status
        submitted_status, _ = ApplicationStatus.objects.get_or_create(name="submitted", defaults={"order": 2})
        self.application.status = submitted_status
        self.application.save()

        document = Document.objects.create(
            application=self.application,
            type=self.document_type,
            uploaded_by=self.user
        )

        # Create a pending resubmission request
        DocumentResubmissionRequest.objects.create(
            document=document,
            requested_by=self.user,
            reason="Update needed",
            resolved=False
        )

        result = DocumentService.can_replace_document(document, self.user)

        self.assertTrue(result)

    def test_can_replace_document_no_pending_request(self):
        """Test document replacement without pending resubmission request."""
        # Set application to submitted status
        submitted_status, _ = ApplicationStatus.objects.get_or_create(name="submitted", defaults={"order": 2})
        self.application.status = submitted_status
        self.application.save()

        document = Document.objects.create(
            application=self.application,
            type=self.document_type,
            uploaded_by=self.user
        )

        result = DocumentService.can_replace_document(document, self.user)

        self.assertFalse(result)

    def test_can_replace_document_admin_override(self):
        """Test document replacement with admin override."""
        # Set application to submitted status
        submitted_status, _ = ApplicationStatus.objects.get_or_create(name="submitted", defaults={"order": 2})
        self.application.status = submitted_status
        self.application.save()

        document = Document.objects.create(
            application=self.application,
            type=self.document_type,
            uploaded_by=self.user
        )

        # Create admin user
        admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="testpass123"
        )
        # Assign admin role to user
        from accounts.models import Role
        admin_role, _ = Role.objects.get_or_create(name="admin")
        admin_user.roles.add(admin_role)
        admin_user.save()
        result = DocumentService.can_replace_document(document, admin_user)
        self.assertTrue(result)
