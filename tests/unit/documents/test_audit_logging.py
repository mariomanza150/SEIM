"""caplog tests for seim.audit document type / upload events."""

import logging

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from documents.models import DocumentType
from tests.utils import TestUtils


class DocumentAuditLoggingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Ensure prior dictConfig(settings.LOGGING) did not leave the logger disabled.
        self.audit_logger = logging.getLogger("seim.audit")
        self.audit_logger.disabled = False
        self.audit_logger.setLevel(logging.INFO)
        self.admin = TestUtils.create_test_user(
            username="auditadmin",
            email="audit.admin@example.edu",
            role="admin",
        )
        self.student = TestUtils.create_test_user(
            username="auditstudent",
            email="audit.student@example.edu",
            role="student",
        )
        self.program = TestUtils.create_test_program(name="Audit Mobility Program")
        self.application = TestUtils.create_test_application(
            student=self.student, program=self.program
        )
        self.doc_type = DocumentType.objects.create(
            name="Audit Passport",
            slug="audit_passport",
            submission_mode="upload",
            accepted_extensions="pdf",
            max_file_size_mb=5,
        )

    def test_document_type_update_emits_audit(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("api:documenttype-detail", kwargs={"pk": self.doc_type.pk})
        with self.assertLogs("seim.audit", level="INFO") as caplog:
            response = self.client.patch(url, {"description": "updated"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            any("document_type_update" in line for line in caplog.output),
            caplog.output,
        )

    def test_template_upload_emits_audit(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse(
            "api:documenttype-upload-template", kwargs={"pk": self.doc_type.pk}
        )
        upload = SimpleUploadedFile(
            "template.docx",
            b"PK\x03\x04fake-docx",
            content_type=(
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ),
        )
        with self.assertLogs("seim.audit", level="INFO") as caplog:
            response = self.client.post(
                url, {"template_file": upload}, format="multipart"
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            any("document_type_template_upload" in line for line in caplog.output),
            caplog.output,
        )

    def test_document_upload_success_emits_audit(self):
        self.client.force_authenticate(user=self.student)
        url = reverse("api:document-list")
        upload = SimpleUploadedFile(
            "passport.pdf", b"%PDF-1.4 audit", content_type="application/pdf"
        )
        with self.assertLogs("seim.audit", level="INFO") as caplog:
            response = self.client.post(
                url,
                {
                    "application": str(self.application.pk),
                    "type": str(self.doc_type.pk),
                    "file": upload,
                },
                format="multipart",
            )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertTrue(
            any("document_upload" in line for line in caplog.output),
            caplog.output,
        )

    def test_document_upload_rejection_emits_warning(self):
        self.client.force_authenticate(user=self.student)
        url = reverse("api:document-list")
        # Missing file → serializer validation failure → 400 + audit warning
        with self.assertLogs("seim.audit", level="WARNING") as caplog:
            response = self.client.post(
                url,
                {
                    "application": str(self.application.pk),
                    "type": str(self.doc_type.pk),
                },
                format="multipart",
            )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(
            any("document_upload_rejected" in line for line in caplog.output),
            caplog.output,
        )
