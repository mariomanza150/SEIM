"""Tests for document version history visibility and multi-upload current docs."""

from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile

from core.models import InstitutionFeatureSettings
from documents.models import Document, DocumentType
from documents.services import DocumentService
from documents.visibility import can_view_document_version_history
from tests.utils import APITestCase


class TestDocumentVersionVisibility(APITestCase):
    def setUp(self):
        super().setUp()
        InstitutionFeatureSettings.get_solo()
        self.doc_type = DocumentType.objects.create(
            name="Visibility Type",
            version_history_visibility=DocumentType.VersionHistoryVisibility.INHERIT,
        )

    def test_institution_role_defaults(self):
        student = self.create_user(role="student")
        coordinator = self.create_user(role="coordinator")
        admin = self.create_user(role="admin")
        self.assertFalse(can_view_document_version_history(student, self.doc_type))
        self.assertTrue(can_view_document_version_history(coordinator, self.doc_type))
        self.assertTrue(can_view_document_version_history(admin, self.doc_type))

    def test_master_switch_off_hides_all(self):
        InstitutionFeatureSettings.objects.filter(pk=1).update(
            document_version_history_enabled=False
        )
        admin = self.create_user(role="admin")
        self.assertFalse(can_view_document_version_history(admin, self.doc_type))

    def test_type_hidden_overrides_institution(self):
        self.doc_type.version_history_visibility = (
            DocumentType.VersionHistoryVisibility.HIDDEN
        )
        self.doc_type.save()
        admin = self.create_user(role="admin")
        self.assertFalse(can_view_document_version_history(admin, self.doc_type))

    def test_type_custom_role_override(self):
        self.doc_type.version_history_visibility = (
            DocumentType.VersionHistoryVisibility.CUSTOM
        )
        self.doc_type.version_history_student = True
        self.doc_type.version_history_coordinator = False
        self.doc_type.version_history_admin = True
        self.doc_type.save()
        student = self.create_user(role="student")
        coordinator = self.create_user(role="coordinator")
        self.assertTrue(can_view_document_version_history(student, self.doc_type))
        self.assertFalse(can_view_document_version_history(coordinator, self.doc_type))


class TestDocumentReplaceAndMultiUpload(APITestCase):
    def test_replace_creates_successor_and_checklist_uses_current(self):
        student = self.create_user(role="student")
        app = self.create_application(student=student, status_name="draft")
        doc_type = DocumentType.objects.create(name="Passport Scan")
        old = Document.objects.create(
            application=app,
            type=doc_type,
            file=SimpleUploadedFile("old.pdf", b"%PDF-1.4 old"),
            uploaded_by=student,
        )
        new_file = SimpleUploadedFile(
            "new.pdf", b"%PDF-1.4 new", content_type="application/pdf"
        )
        with patch("documents.services.scan_document_virus.delay"):
            with patch(
                "documents.services.DocumentService.virus_scan", return_value=True
            ):
                with patch(
                    "documents.services.DocumentService.validate_file_type_and_size"
                ):
                    with patch(
                        "documents.services.DocumentService.notify_coordinators_document_replaced"
                    ):
                        new_doc = DocumentService.replace_document(
                            old, new_file, student
                        )
        self.assertEqual(new_doc.supersedes_id, old.id)
        self.assertTrue(DocumentService.is_document_current(new_doc))
        self.assertFalse(DocumentService.is_document_current(old))
        current = list(DocumentService.current_documents(app, doc_type))
        self.assertEqual(len(current), 1)
        self.assertEqual(current[0].id, new_doc.id)

    def test_allows_multiple_counts_current_only(self):
        student = self.create_user(role="student")
        app = self.create_application(student=student, status_name="draft")
        doc_type = DocumentType.objects.create(
            name="Recommendation Letters", allows_multiple=True
        )
        first = Document.objects.create(
            application=app,
            type=doc_type,
            file=SimpleUploadedFile("a.pdf", b"%PDF-1.4 a"),
            uploaded_by=student,
        )
        with patch("documents.services.scan_document_virus.delay"):
            with patch(
                "documents.services.DocumentService.virus_scan", return_value=True
            ):
                with patch(
                    "documents.services.DocumentService.validate_file_type_and_size"
                ):
                    second = DocumentService.upload_document(
                        app,
                        doc_type,
                        SimpleUploadedFile("b.pdf", b"%PDF-1.4 b"),
                        student,
                    )
        self.assertIsNone(second.supersedes_id)
        self.assertEqual(DocumentService.current_documents(app, doc_type).count(), 2)
        tip = DocumentService.current_documents(app, doc_type).filter(pk=first.pk).first()
        self.assertIsNotNone(tip)
        with patch("documents.services.scan_document_virus.delay"):
            with patch(
                "documents.services.DocumentService.virus_scan", return_value=True
            ):
                with patch(
                    "documents.services.DocumentService.validate_file_type_and_size"
                ):
                    with patch(
                        "documents.services.DocumentService.notify_coordinators_document_replaced"
                    ):
                        DocumentService.replace_document(
                            tip,
                            SimpleUploadedFile("a2.pdf", b"%PDF-1.4 a2"),
                            student,
                        )
        self.assertEqual(DocumentService.current_documents(app, doc_type).count(), 2)

    def test_features_api_exposes_history_flags(self):
        admin = self.create_user(role="admin")
        self.authenticate_user(admin)
        response = self.client.get("/api/features/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("document_version_history_enabled", response.data)
        self.assertIn("document_version_history_student", response.data)
        patch_resp = self.client.patch(
            "/api/features/",
            {
                "document_version_history_student": True,
                "document_version_history_enabled": True,
            },
            format="json",
        )
        self.assertEqual(patch_resp.status_code, 200)
        self.assertTrue(patch_resp.data["document_version_history_student"])
