"""Regression: only staff may create/update document validations."""

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from documents.models import Document, DocumentType
from tests.utils import TestUtils


@pytest.mark.django_db
class TestDocumentValidationWriteAcl:
    def setup_method(self):
        self.student_a = TestUtils.create_test_user(
            username="val_acl_a",
            email="val_acl_a@example.com",
            role="student",
        )
        self.student_b = TestUtils.create_test_user(
            username="val_acl_b",
            email="val_acl_b@example.com",
            role="student",
        )
        self.coordinator = TestUtils.create_test_user(
            username="val_acl_coord",
            email="val_acl_coord@example.com",
            role="coordinator",
        )
        self.app_b = TestUtils.create_test_application(student=self.student_b)
        doc_type, _ = DocumentType.objects.get_or_create(name="acl_transcript")
        self.document = Document.objects.create(
            application=self.app_b,
            type=doc_type,
            uploaded_by=self.student_b,
            file=SimpleUploadedFile(
                "sample.pdf", b"%PDF-1.4", content_type="application/pdf"
            ),
        )
        self.client = APIClient()

    def test_student_cannot_create_validation_on_other_document(self):
        self.client.force_authenticate(user=self.student_a)
        response = self.client.post(
            "/api/document-validations/",
            {
                "document": str(self.document.id),
                "result": "valid",
                "details": "should be forbidden",
            },
            format="json",
        )
        assert response.status_code == 403

    def test_student_cannot_create_validation_on_own_document(self):
        self.client.force_authenticate(user=self.student_b)
        response = self.client.post(
            "/api/document-validations/",
            {
                "document": str(self.document.id),
                "result": "valid",
                "details": "students cannot self-validate",
            },
            format="json",
        )
        assert response.status_code == 403

    def test_coordinator_can_create_validation(self):
        self.client.force_authenticate(user=self.coordinator)
        response = self.client.post(
            "/api/document-validations/",
            {
                "document": str(self.document.id),
                "result": "valid",
                "details": "staff review",
            },
            format="json",
        )
        assert response.status_code == 201
        assert response.data["result"] == "valid"

    def test_student_cannot_create_resubmission_request(self):
        self.client.force_authenticate(user=self.student_a)
        response = self.client.post(
            "/api/document-resubmissions/",
            {
                "document": str(self.document.id),
                "reason": "should be forbidden",
            },
            format="json",
        )
        assert response.status_code == 403
