"""Unit tests for Phase 4 document deadlines and Solicitud PDF."""

from datetime import date, timedelta
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone

from documents.models import DocumentType
from documents.pdf_generation import render_solicitud_participacion_pdf
from documents.services import DocumentService
from exchange.models import Application, ApplicationStatus, Program, ProgramDocumentRequirement


class DocumentDeadlineTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="deadline_student",
            email="deadline@example.com",
            password="TestPass123!",
        )
        today = timezone.localdate()
        self.program = Program.objects.create(
            name="Deadline Program",
            description="Test",
            start_date=today + timedelta(days=60),
            end_date=today + timedelta(days=180),
            application_deadline=today + timedelta(days=30),
            is_active=True,
        )
        status, _ = ApplicationStatus.objects.get_or_create(
            name="draft", defaults={"order": 1}
        )
        self.application = Application.objects.create(
            student=self.user, program=self.program, status=status
        )
        self.doc_type = DocumentType.objects.create(
            name="Kardex Test",
            slug="kardex_test",
            submission_mode=DocumentType.SubmissionMode.UPLOAD,
            accepted_extensions="pdf",
        )
        self.requirement = ProgramDocumentRequirement.objects.create(
            program=self.program,
            document_type=self.doc_type,
            is_required=True,
            deadline=today - timedelta(days=1),
            sort_order=10,
        )

    def test_checklist_marks_overdue(self):
        summary = DocumentService.build_application_document_checklist(self.application)
        self.assertEqual(summary["required_count"], 1)
        item = summary["items"][0]
        self.assertTrue(item["is_overdue"])
        self.assertEqual(item["deadline"], self.requirement.deadline.isoformat())
        self.assertEqual(item["status"], "missing")

    def test_relative_deadline_days_before_program(self):
        self.requirement.deadline = None
        self.requirement.deadline_days_before_program_deadline = 10
        self.requirement.save()
        expected = self.program.application_deadline - timedelta(days=10)
        self.assertEqual(self.requirement.resolve_deadline(), expected)

    def test_upload_blocked_when_overdue(self):
        pdf = SimpleUploadedFile(
            "late.pdf", b"%PDF-1.4\n", content_type="application/pdf"
        )
        with patch("documents.services.scan_document_virus") as mock_scan:
            mock_scan.delay = MagicMock()
            with self.assertRaises(ValueError) as ctx:
                DocumentService.upload_document(
                    self.application, self.doc_type, pdf, self.user
                )
        self.assertIn("deadline", str(ctx.exception).lower())

    def test_upload_allowed_before_deadline(self):
        self.requirement.deadline = timezone.localdate() + timedelta(days=5)
        self.requirement.save()
        pdf = SimpleUploadedFile(
            "ok.pdf", b"%PDF-1.4\n", content_type="application/pdf"
        )
        with patch("documents.services.scan_document_virus") as mock_scan:
            mock_scan.delay = MagicMock()
            with patch.object(DocumentService, "virus_scan", return_value=True):
                # virus_scan not called in upload_document; mime check uses magic/mimetypes
                doc = DocumentService.upload_document(
                    self.application, self.doc_type, pdf, self.user
                )
        self.assertIsNotNone(doc.id)

    def test_instructions_only_counts_complete(self):
        instr = DocumentType.objects.create(
            name="Reglamento",
            slug="reglamento_test",
            submission_mode=DocumentType.SubmissionMode.INSTRUCTIONS_ONLY,
        )
        ProgramDocumentRequirement.objects.create(
            program=self.program,
            document_type=instr,
            is_required=True,
            sort_order=20,
        )
        # Approve the upload type first
        self.requirement.deadline = timezone.localdate() + timedelta(days=5)
        self.requirement.save()
        from documents.models import Document

        Document.objects.create(
            application=self.application,
            type=self.doc_type,
            file=SimpleUploadedFile("a.pdf", b"%PDF-1.4\n", content_type="application/pdf"),
            uploaded_by=self.user,
            is_valid=True,
        )
        summary = DocumentService.build_application_document_checklist(self.application)
        self.assertTrue(summary["complete"])
        statuses = {i["slug"]: i["status"] for i in summary["items"]}
        self.assertEqual(statuses["reglamento_test"], "n_a")


class SolicitudPdfTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="pdf_student",
            email="pdf@example.com",
            password="TestPass123!",
            first_name="Ana",
            last_name="Lopez",
        )
        today = date.today()
        self.program = Program.objects.create(
            name="Movilidad Nacional",
            description="Test",
            start_date=today + timedelta(days=60),
            end_date=today + timedelta(days=180),
            is_active=True,
        )
        status, _ = ApplicationStatus.objects.get_or_create(
            name="draft", defaults={"order": 1}
        )
        self.application = Application.objects.create(
            student=self.user, program=self.program, status=status
        )

    def test_render_solicitud_pdf_bytes(self):
        pdf = render_solicitud_participacion_pdf(self.application)
        self.assertTrue(pdf.startswith(b"%PDF"))
        self.assertGreater(len(pdf), 200)
        # Graceful when host FKs absent / null
        self.assertIn(b"Solicitud", pdf)
