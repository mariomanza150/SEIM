from datetime import timedelta

from django.core.files.base import ContentFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import Profile, Role, User
from documents.models import Document, DocumentType
from documents.services import DocumentService
from exchange.models import ApplicationStatus, Program


class TestDocumentChecklistAPI(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.student_role, _ = Role.objects.get_or_create(name="student")
        self.coordinator_role, _ = Role.objects.get_or_create(name="coordinator")
        self.student = User.objects.create_user(
            username="doc-check-student",
            email="doc-check-student@example.com",
            password="testpass123",
        )
        self.student.roles.add(self.student_role)
        Profile.objects.get_or_create(user=self.student)
        self.coordinator = User.objects.create_user(
            username="doc-check-coord",
            email="doc-check-coord@example.com",
            password="testpass123",
        )
        self.coordinator.roles.add(self.coordinator_role)
        self.client.force_authenticate(user=self.student)

        self.doc_type = DocumentType.objects.create(
            name="Official Transcript",
            description="Sealed transcript",
        )
        self.program = Program.objects.create(
            name="Doc Check Program",
            description="Requires documents",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=120),
            is_active=True,
        )
        self.program.required_document_types.add(self.doc_type)
        self.draft_status, _ = ApplicationStatus.objects.get_or_create(
            name="draft",
            defaults={"order": 1},
        )
        ApplicationStatus.objects.get_or_create(
            name="submitted",
            defaults={"order": 2},
        )

    def test_detail_includes_document_checklist(self):
        from exchange.models import Application

        app = Application.objects.create(
            program=self.program,
            student=self.student,
            status=self.draft_status,
        )
        response = self.client.get(reverse("api:application-detail", args=[app.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        checklist = response.data["document_checklist"]
        self.assertEqual(checklist["required_count"], 1)
        self.assertEqual(checklist["approved_count"], 0)
        self.assertFalse(checklist["complete"])
        self.assertEqual(checklist["items"][0]["status"], "missing")
        self.assertEqual(checklist["items"][0]["name"], "Official Transcript")

    def test_submit_blocked_until_required_document_approved(self):
        from exchange.models import Application

        app = Application.objects.create(
            program=self.program,
            student=self.student,
            status=self.draft_status,
        )
        submit = self.client.post(
            reverse("api:application-submit", args=[app.id]),
            {},
            format="json",
        )
        self.assertEqual(submit.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Required documents", submit.data["error"])

        doc = Document.objects.create(
            application=app,
            type=self.doc_type,
            file=ContentFile(b"%PDF-1.4 minimal", name="test.pdf"),
            uploaded_by=self.student,
            is_valid=False,
        )
        DocumentService.validate_document(doc, self.coordinator, "valid", "")
        submit_ok = self.client.post(
            reverse("api:application-submit", args=[app.id]),
            {},
            format="json",
        )
        self.assertEqual(submit_ok.status_code, status.HTTP_200_OK)

    def test_list_excludes_document_checklist_payload(self):
        from exchange.models import Application

        Application.objects.create(
            program=self.program,
            student=self.student,
            status=self.draft_status,
        )
        response = self.client.get(reverse("api:application-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payload = response.data
        rows = payload["results"] if isinstance(payload, dict) and "results" in payload else payload
        row = rows[0]
        self.assertIsNone(row.get("document_checklist"))
