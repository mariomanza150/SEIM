"""Tests for DocumentType.SubmissionMode.DOWNLOAD_ONLY."""

from datetime import timedelta
from pathlib import Path

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from cms.cgri_samples import official_sample_path, samples_dir
from documents.models import DocumentType
from documents.services import DocumentService
from exchange.models import Application, ApplicationStatus, ProgramDocumentRequirement
from tests.unit.documents.test_document_type_module import (
    _document_text,
    _docx_bytes,
    _response_bytes,
)
from tests.utils import TestUtils


class DownloadOnlyModeTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.student = TestUtils.create_test_user(
            username="dlonly_student",
            email="dlonly.student@example.com",
            role="student",
            first_name="Ana",
            last_name="Lopez",
        )
        self.other = TestUtils.create_test_user(
            username="dlonly_other",
            email="dlonly.other@example.com",
            role="student",
            first_name="Bruno",
            last_name="Diaz",
        )
        self.program = TestUtils.create_test_program(name="Download Only Mobility")
        app_status, _ = ApplicationStatus.objects.get_or_create(
            name="draft", defaults={"order": 1}
        )
        self.application = Application.objects.create(
            student=self.student, program=self.program, status=app_status
        )
        self.doc_type = DocumentType.objects.create(
            name="Guide Packet",
            slug="guide_packet_dl_only",
            submission_mode=DocumentType.SubmissionMode.DOWNLOAD_ONLY,
        )
        self.doc_type.template_file.save(
            "guide.docx",
            SimpleUploadedFile("guide.docx", _docx_bytes()),
            save=True,
        )
        self.requirement = ProgramDocumentRequirement.objects.create(
            program=self.program,
            document_type=self.doc_type,
            is_required=True,
            sort_order=10,
            deadline=timezone.localdate() - timedelta(days=1),
        )

    def test_download_only_not_counted_missing_or_pending(self):
        summary = DocumentService.build_application_document_checklist(self.application)
        self.assertTrue(summary["complete"])
        self.assertEqual(summary["required_count"], 1)
        self.assertEqual(summary["approved_count"], 1)
        item = summary["items"][0]
        self.assertEqual(item["status"], "n_a")
        self.assertEqual(item["submission_mode"], "download_only")
        self.assertFalse(item["is_overdue"])

    def test_upload_to_download_only_returns_400(self):
        self.client.force_authenticate(user=self.student)
        url = reverse("api:document-list")
        pdf = SimpleUploadedFile(
            "attempt.pdf", b"%PDF-1.4\n", content_type="application/pdf"
        )
        response = self.client.post(
            url,
            {
                "application": str(self.application.id),
                "type": self.doc_type.pk,
                "file": pdf,
            },
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        detail = response.json().get("detail") or response.json().get("file") or ""
        if isinstance(detail, list):
            detail = " ".join(str(part) for part in detail)
        self.assertIn("download-only", str(detail).lower())

    def test_listed_student_gets_prefilled_file(self):
        self.doc_type.prefill_students.add(self.student)
        self.client.force_authenticate(user=self.student)
        url = reverse(
            "api:documenttype-download-template", kwargs={"pk": self.doc_type.pk}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        text = _document_text(_response_bytes(response))
        self.assertIn("Ana", text)
        self.assertIn("Lopez", text)
        self.assertIn(self.student.email, text)

    def test_unlisted_student_gets_blank_file(self):
        blank = self.doc_type.template_file.open("rb").read()
        self.doc_type.template_file.close()
        self.client.force_authenticate(user=self.other)
        url = reverse(
            "api:documenttype-download-template", kwargs={"pk": self.doc_type.pk}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(_response_bytes(response), blank)

    def test_official_form_served_as_exact_bytes(self):
        if (
            not samples_dir().is_dir()
            or official_sample_path("carta_compromiso") is None
        ):
            pytest.skip("SAMPLES/ carta_compromiso not present")
        sample = official_sample_path("carta_compromiso").read_bytes()
        official = DocumentType.objects.create(
            name="Official Commitment Letter",
            slug="carta_compromiso_dl_only_test",
            submission_mode=DocumentType.SubmissionMode.DOWNLOAD_ONLY,
        )
        official.template_file.save(
            "FS-CC_Carta_Compromiso.docx",
            SimpleUploadedFile(
                "FS-CC_Carta_Compromiso.docx",
                sample,
                content_type=(
                    "application/vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),
            ),
            save=True,
        )
        official.prefill_students.add(self.student)
        self.client.force_authenticate(user=self.student)
        url = reverse("api:documenttype-download-template", kwargs={"pk": official.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, sample)
        # Prefill listing must not rewrite official blank forms.
        self.assertEqual(Path(official.template_file.name).name.endswith(".docx"), True)
