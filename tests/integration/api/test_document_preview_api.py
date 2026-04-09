"""Tests for GET /api/documents/{id}/preview/ (inline file stream)."""

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from documents.models import Document, DocumentType
from tests.utils import APITestCase


class TestDocumentPreviewAPI(APITestCase):
    def _make_document(self, student):
        program = self.create_program()
        application = self.create_application(student=student, program=program)
        doc_type = DocumentType.objects.create(name="preview_type")
        return Document.objects.create(
            application=application,
            type=doc_type,
            file=SimpleUploadedFile(
                "letter.pdf",
                b"%PDF-1.4 %\xe2\xe3\xcf\xd3 preview",
                content_type="application/pdf",
            ),
            uploaded_by=student,
        )

    def test_student_can_preview_own_document(self):
        student = self.create_user(role="student")
        doc = self._make_document(student)
        self.authenticate_user(student)
        url = reverse("api:document-preview", kwargs={"pk": doc.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/pdf", response.get("Content-Type", ""))
        self.assertIn("inline", response.get("Content-Disposition", ""))

    def test_coordinator_can_preview(self):
        student = self.create_user(role="student")
        coordinator = self.create_user(role="coordinator")
        doc = self._make_document(student)
        self.authenticate_user(coordinator)
        url = reverse("api:document-preview", kwargs={"pk": doc.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_other_student_gets_404(self):
        owner = self.create_user(role="student", username="doc_owner", email="doc_owner@example.com")
        other = self.create_user(role="student", username="doc_other", email="doc_other@example.com")
        doc = self._make_document(owner)
        self.authenticate_user(other)
        url = reverse("api:document-preview", kwargs={"pk": doc.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
