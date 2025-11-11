from unittest import mock

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from documents.models import Document, DocumentResubmissionRequest
from documents.services import DocumentService
from tests.conftest import ApplicationFactory, DocumentTypeFactory, UserFactory


@pytest.mark.django_db
class TestDocumentService:
    def test_validate_file_type_and_size_valid(self):
        file = SimpleUploadedFile(
            "test.pdf", b"%PDF-1.4\n...", content_type="application/pdf"
        )
        file.size = 1024 * 1024  # 1MB
        assert DocumentService.validate_file_type_and_size(file) is True

    def test_validate_file_type_and_size_invalid_type(self):
        file = SimpleUploadedFile(
            "test.exe", b"EXE content", content_type="application/x-msdownload"
        )
        file.size = 1024
        with pytest.raises(ValueError, match="File type not allowed."):
            DocumentService.validate_file_type_and_size(file)

    def test_validate_file_type_and_size_invalid_size(self):
        file = SimpleUploadedFile(
            "test.pdf",
            b"%PDF-1.4\n" + b"0" * (11 * 1024 * 1024),
            content_type="application/pdf",
        )
        file.size = 11 * 1024 * 1024  # 11MB
        with pytest.raises(ValueError, match="File size exceeds maximum allowed."):
            DocumentService.validate_file_type_and_size(file)

    def test_virus_scan_stub(self):
        file = SimpleUploadedFile(
            "test.pdf", b"PDF content", content_type="application/pdf"
        )
        assert DocumentService.virus_scan(file) is True

    @mock.patch("documents.services.scan_document_virus.delay")
    def test_upload_document_success(self, mock_scan):
        user = UserFactory()
        application = ApplicationFactory()
        doc_type = DocumentTypeFactory()
        file = SimpleUploadedFile(
            "test.pdf", b"%PDF-1.4\n...", content_type="application/pdf"
        )
        file.size = 1024
        document = DocumentService.upload_document(application, doc_type, file, user)
        assert Document.objects.filter(id=document.id).exists()
        mock_scan.assert_called_once()

    def test_upload_document_invalid_file(self):
        user = UserFactory()
        application = ApplicationFactory()
        doc_type = DocumentTypeFactory()
        file = SimpleUploadedFile(
            "test.exe", b"EXE content", content_type="application/x-msdownload"
        )
        file.size = 1024
        with pytest.raises(ValueError):
            DocumentService.upload_document(application, doc_type, file, user)

    def test_validate_document_valid(self):
        user = UserFactory()
        application = ApplicationFactory()
        doc_type = DocumentTypeFactory()
        file = SimpleUploadedFile(
            "test.pdf", b"%PDF-1.4\n...", content_type="application/pdf"
        )
        file.size = 1024
        document = Document.objects.create(
            application=application, type=doc_type, file=file, uploaded_by=user
        )
        validation = DocumentService.validate_document(
            document, user, "valid", "All good"
        )
        document.refresh_from_db()
        assert document.is_valid is True
        assert document.validated_at is not None
        assert validation.result == "valid"

    def test_validate_document_invalid(self):
        user = UserFactory()
        application = ApplicationFactory()
        doc_type = DocumentTypeFactory()
        file = SimpleUploadedFile(
            "test.pdf", b"%PDF-1.4\n...", content_type="application/pdf"
        )
        file.size = 1024
        document = Document.objects.create(
            application=application, type=doc_type, file=file, uploaded_by=user
        )
        validation = DocumentService.validate_document(
            document, user, "invalid", "Corrupt"
        )
        document.refresh_from_db()
        assert document.is_valid is False
        assert document.validated_at is not None
        assert validation.result == "invalid"

    def test_can_request_resubmission_true(self):
        user = UserFactory()
        application = ApplicationFactory()
        doc_type = DocumentTypeFactory()
        file = SimpleUploadedFile(
            "test.pdf", b"%PDF-1.4\n...", content_type="application/pdf"
        )
        file.size = 1024
        document = Document.objects.create(
            application=application, type=doc_type, file=file, uploaded_by=user
        )
        assert DocumentService.can_request_resubmission(document) is True

    def test_can_request_resubmission_false(self):
        user = UserFactory()
        application = ApplicationFactory()
        doc_type = DocumentTypeFactory()
        file = SimpleUploadedFile(
            "test.pdf", b"%PDF-1.4\n...", content_type="application/pdf"
        )
        file.size = 1024
        document = Document.objects.create(
            application=application, type=doc_type, file=file, uploaded_by=user
        )
        for _ in range(DocumentService.MAX_RESUBMISSIONS):
            DocumentResubmissionRequest.objects.create(
                document=document, requested_by=user, reason="Test"
            )
        assert DocumentService.can_request_resubmission(document) is False

    @mock.patch("documents.services.NotificationService.send_notification")
    def test_request_resubmission_success(self, mock_notify):
        user = UserFactory()
        application = ApplicationFactory()
        doc_type = DocumentTypeFactory()
        file = SimpleUploadedFile(
            "test.pdf", b"%PDF-1.4\n...", content_type="application/pdf"
        )
        file.size = 1024
        document = Document.objects.create(
            application=application, type=doc_type, file=file, uploaded_by=user
        )
        req = DocumentService.request_resubmission(document, user, "Reason")
        assert DocumentResubmissionRequest.objects.filter(id=req.id).exists()
        mock_notify.assert_called_once()

    def test_request_resubmission_limit(self):
        user = UserFactory()
        application = ApplicationFactory()
        doc_type = DocumentTypeFactory()
        file = SimpleUploadedFile(
            "test.pdf", b"%PDF-1.4\n...", content_type="application/pdf"
        )
        file.size = 1024
        document = Document.objects.create(
            application=application, type=doc_type, file=file, uploaded_by=user
        )
        for _ in range(DocumentService.MAX_RESUBMISSIONS):
            DocumentResubmissionRequest.objects.create(
                document=document, requested_by=user, reason="Test"
            )
        with pytest.raises(
            ValueError, match="Maximum number of resubmissions reached."
        ):
            DocumentService.request_resubmission(document, user, "Reason")
