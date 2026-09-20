"""API tests for document validate_document action permissions."""

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from documents.models import Document, DocumentType
from tests.utils import TestUtils


class TestDocumentValidateApi(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.student = TestUtils.create_test_user(username="val_student", role="student")
        self.admin = TestUtils.create_test_user(username="val_admin", role="admin")
        self.coordinator = TestUtils.create_test_user(
            username="val_coord", role="coordinator"
        )
        self.application = TestUtils.create_test_application(student=self.student)
        self.doc_type = DocumentType.objects.create(name="Transcript")
        self.document = Document.objects.create(
            application=self.application,
            type=self.doc_type,
            uploaded_by=self.student,
            file=SimpleUploadedFile("t.pdf", b"%PDF-1.4", content_type="application/pdf"),
        )

    def _url(self):
        return reverse("api:document-validate-document", args=[self.document.id])

    def test_admin_can_mark_document_valid(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self._url(), {"result": "valid"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.document.refresh_from_db()
        self.assertTrue(self.document.is_valid)

    def test_coordinator_can_mark_document_valid(self):
        self.client.force_authenticate(user=self.coordinator)
        response = self.client.post(self._url(), {"result": "valid"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.document.refresh_from_db()
        self.assertTrue(self.document.is_valid)

    def test_student_cannot_validate_document(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post(self._url(), {"result": "valid"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.document.refresh_from_db()
        self.assertFalse(self.document.is_valid)
