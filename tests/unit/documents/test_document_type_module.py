"""Tests for Word MERGEFIELD template prefilling and document-type admin API."""

import io
import zipfile
import xml.etree.ElementTree as ET

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from documents.mailmerge import merge_docx, merge_values_for_application
from documents.models import DocumentType
from exchange.models import Application, ApplicationStatus, ProgramDocumentRequirement
from tests.utils import TestUtils

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def _docx_bytes(
    *, complex_field="FirstName", placeholder="LastName", simple_field="Email"
):
    document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="{W_NS}">
  <w:body>
    <w:p>
      <w:r><w:fldChar w:fldCharType="begin"/></w:r>
      <w:r><w:instrText xml:space="preserve"> MERGEFIELD {complex_field} </w:instrText></w:r>
      <w:r><w:fldChar w:fldCharType="separate"/></w:r>
      <w:r><w:t>«{complex_field}»</w:t></w:r>
      <w:r><w:fldChar w:fldCharType="end"/></w:r>
    </w:p>
    <w:p>
      <w:fldSimple w:instr=" MERGEFIELD {simple_field} ">
        <w:r><w:t>«{simple_field}»</w:t></w:r>
      </w:fldSimple>
    </w:p>
    <w:p>
      <w:r><w:t>Hello {{{{{placeholder}}}}}</w:t></w:r>
    </w:p>
  </w:body>
</w:document>"""
    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""
    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("word/document.xml", document_xml)
    return buf.getvalue()


def _document_text(docx_bytes: bytes) -> str:
    with zipfile.ZipFile(io.BytesIO(docx_bytes)) as zf:
        xml = zf.read("word/document.xml")
    root = ET.fromstring(xml)
    texts = [
        (node.text or "")
        for node in root.iter(f"{{{W_NS}}}t")
    ]
    return "".join(texts)


def _response_bytes(response) -> bytes:
    if hasattr(response, "streaming_content"):
        return b"".join(response.streaming_content)
    return response.content


class MailMergeTests(SimpleTestCase):
    def test_merges_complex_simple_and_placeholder_fields(self):
        raw = _docx_bytes()
        filled = merge_docx(
            raw, {"FirstName": "Ana", "LastName": "Lopez", "Email": "ana@test.com"}
        )
        text = _document_text(filled)
        self.assertIn("Ana", text)
        self.assertIn("Lopez", text)
        self.assertIn("ana@test.com", text)
        self.assertNotIn("MERGEFIELD", text)
        self.assertNotIn("{{LastName}}", text)


class DocumentTypeAdminApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = TestUtils.create_test_user(username="docadmin", role="admin")
        self.student = TestUtils.create_test_user(
            username="docstudent",
            role="student",
            first_name="Ana",
            last_name="Lopez",
        )
        self.program = TestUtils.create_test_program(name="National Mobility")
        app_status, _ = ApplicationStatus.objects.get_or_create(
            name="draft", defaults={"order": 1}
        )
        self.application = Application.objects.create(
            student=self.student, program=self.program, status=app_status
        )
        self.doc_type = DocumentType.objects.create(
            name="Learning Agreement",
            slug="learning_agreement_test",
            instructions="Fill and upload the signed agreement.",
            accepted_extensions="pdf,docx",
            max_file_size_mb=5,
        )

    def test_student_cannot_create_document_type(self):
        self.client.force_authenticate(user=self.student)
        url = reverse("api:documenttype-list")
        response = self.client.post(url, {"name": "Hacked"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_update_instructions_and_requirements(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("api:documenttype-detail", kwargs={"pk": self.doc_type.pk})
        response = self.client.patch(
            url,
            {
                "instructions": "Bring a printed copy.",
                "max_file_size_mb": 8,
                "program_requirements": [
                    {
                        "program": str(self.program.id),
                        "is_required": True,
                        "deadline_days_after_program_start": 10,
                    }
                ],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.doc_type.refresh_from_db()
        self.assertEqual(self.doc_type.instructions, "Bring a printed copy.")
        self.assertEqual(self.doc_type.max_file_size_mb, 8)
        req = ProgramDocumentRequirement.objects.get(
            program=self.program, document_type=self.doc_type
        )
        self.assertEqual(req.deadline_days_after_program_start, 10)
        payload = response.json()
        self.assertEqual(len(payload["program_requirements"]), 1)
        self.assertEqual(
            payload["program_requirements"][0]["deadline_days_after_program_start"],
            10,
        )

    def test_prefilled_template_download_uses_student_data(self):
        self.doc_type.template_file.save(
            "agreement.docx",
            SimpleUploadedFile(
                "agreement.docx",
                _docx_bytes(),
                content_type=(
                    "application/vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),
            ),
            save=True,
        )
        self.client.force_authenticate(user=self.student)
        url = reverse("api:documenttype-download-template", kwargs={"pk": self.doc_type.pk})
        response = self.client.get(url, {"application": str(self.application.id)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        text = _document_text(_response_bytes(response))
        self.assertIn("Ana", text)
        self.assertIn("Lopez", text)
        self.assertIn(self.student.email, text)

    def test_student_cannot_prefill_another_application(self):
        other = TestUtils.create_test_user(username="otherstudent", role="student")
        app_status = ApplicationStatus.objects.get(name="draft")
        other_app = Application.objects.create(
            student=other, program=self.program, status=app_status
        )
        self.doc_type.template_file.save(
            "agreement.docx",
            SimpleUploadedFile("agreement.docx", _docx_bytes()),
            save=True,
        )
        self.client.force_authenticate(user=self.student)
        url = reverse("api:documenttype-download-template", kwargs={"pk": self.doc_type.pk})
        response = self.client.get(url, {"application": str(other_app.id)})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_merge_values_include_program_name(self):
        values = merge_values_for_application(self.application)
        self.assertEqual(values["FirstName"], "Ana")
        self.assertEqual(values["ProgramName"], "National Mobility")
        self.assertEqual(values["Username"], "docstudent")

    def test_merge_fields_catalog(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("api:documenttype-merge-fields")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = {row["name"] for row in response.json()["fields"]}
        self.assertIn("FirstName", names)
        self.assertIn("ProgramStartDate", names)
        self.assertIn("Matricula", names)
