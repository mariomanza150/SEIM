"""Integration tests for GET /api/documents/ query filters."""

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from documents.models import Document, DocumentType
from tests.utils import APITestCase


def _pdf():
    return SimpleUploadedFile("doc.pdf", b"%PDF-1.4 test", content_type="application/pdf")


class TestDocumentsListFiltersAPI(APITestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("api:document-list")

    def test_filter_by_application_and_type(self):
        student = self.create_user(role="student")
        coordinator = self.create_user(role="coordinator")
        program = self.create_program()
        app1 = self.create_application(student=student, program=program, status_name="draft")
        app2 = self.create_application(student=student, program=program, status_name="draft")
        dt1 = DocumentType.objects.create(name="Type A")
        dt2 = DocumentType.objects.create(name="Type B")

        doc1 = Document.objects.create(
            application=app1,
            type=dt1,
            uploaded_by=student,
            is_valid=False,
            file=_pdf(),
        )
        Document.objects.create(
            application=app2,
            type=dt2,
            uploaded_by=student,
            is_valid=True,
            file=_pdf(),
        )

        self.authenticate_user(coordinator)
        r = self.client.get(
            self.url,
            {"application": str(app1.id), "type": dt1.id},
        )
        self.assert_response_success(r)
        results = r.data.get("results", r.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], str(doc1.id))
        self.assertEqual(results[0]["type"]["name"], "Type A")
        self.assertEqual(results[0]["type"]["id"], dt1.id)
        self.assertEqual(results[0]["application"]["id"], str(app1.id))
        self.assertEqual(results[0]["application"]["program_name"], program.name)

    def test_filter_is_valid(self):
        student = self.create_user(role="student")
        coordinator = self.create_user(role="coordinator")
        program = self.create_program()
        app = self.create_application(student=student, program=program, status_name="draft")
        dt = DocumentType.objects.create(name="ID Scan")
        Document.objects.create(
            application=app,
            type=dt,
            uploaded_by=student,
            is_valid=False,
            file=_pdf(),
        )
        Document.objects.create(
            application=app,
            type=dt,
            uploaded_by=student,
            is_valid=True,
            file=_pdf(),
        )

        self.authenticate_user(coordinator)
        r = self.client.get(self.url, {"is_valid": "true", "application": str(app.id)})
        self.assert_response_success(r)
        results = r.data.get("results", r.data)
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0]["is_valid"])
