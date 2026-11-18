"""Data isolation / authz for document APIs (IDOR guards)."""

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status

from documents.models import Document, DocumentType, DocumentValidation
from documents.services import DocumentService
from tests.utils import APITestCase


def _pdf(name="doc.pdf"):
    return SimpleUploadedFile(name, b"%PDF-1.4 isolation", content_type="application/pdf")


class TestDocumentIsolationAPI(APITestCase):
    def setUp(self):
        super().setUp()
        self.owner = self.create_user(
            role="student", username="iso_owner", email="iso_owner@example.com"
        )
        self.other = self.create_user(
            role="student", username="iso_other", email="iso_other@example.com"
        )
        self.coordinator = self.create_user(
            role="coordinator", username="iso_coord", email="iso_coord@example.com"
        )
        self.program = self.create_program()
        self.application = self.create_application(
            student=self.owner, program=self.program, status_name="draft"
        )
        self.doc_type = DocumentType.objects.create(name="isolation_type")
        self.document = Document.objects.create(
            application=self.application,
            type=self.doc_type,
            file=_pdf(),
            uploaded_by=self.owner,
        )

    def test_other_student_list_excludes_foreign_documents(self):
        self.authenticate_user(self.other)
        response = self.client.get(reverse("api:document-list"))
        self.assert_response_success(response)
        results = response.data.get("results", response.data)
        ids = {str(row["id"]) for row in results}
        self.assertNotIn(str(self.document.id), ids)

    def test_other_student_retrieve_is_404(self):
        self.authenticate_user(self.other)
        response = self.client.get(
            reverse("api:document-detail", kwargs={"pk": self.document.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_other_student_cannot_upload_to_foreign_application(self):
        self.authenticate_user(self.other)
        response = self.client.post(
            reverse("api:document-list"),
            {
                "application": str(self.application.id),
                "type": self.doc_type.id,
                "file": _pdf("attack.pdf"),
            },
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        detail = str(response.data)
        self.assertIn("Only the applicant", detail)

    def test_student_cannot_create_document_validation(self):
        self.authenticate_user(self.other)
        response = self.client.post(
            reverse("api:documentvalidation-list"),
            {
                "document": str(self.document.id),
                "result": "valid",
                "details": "forged",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(
            DocumentValidation.objects.filter(
                document=self.document, details="forged"
            ).exists()
        )

    def test_student_cannot_create_resubmission_for_foreign_document(self):
        self.authenticate_user(self.other)
        response = self.client.post(
            reverse("api:documentresubmissionrequest-list"),
            {
                "document": str(self.document.id),
                "reason": "please resubmit",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_cannot_create_resubmission_on_own_document(self):
        # Resubmission is a staff action even when the document is the caller's.
        self.authenticate_user(self.owner)
        response = self.client.post(
            reverse("api:documentresubmissionrequest-list"),
            {
                "document": str(self.document.id),
                "reason": "self request",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_coordinator_can_request_resubmission(self):
        self.authenticate_user(self.coordinator)
        response = self.client.post(
            reverse("api:documentresubmissionrequest-list"),
            {
                "document": str(self.document.id),
                "reason": "missing signature page",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_service_rejects_student_resubmission_request(self):
        with self.assertRaises(ValueError) as ctx:
            DocumentService.request_resubmission(
                self.document, self.owner, "not allowed"
            )
        self.assertIn("Only coordinators or admins", str(ctx.exception))
