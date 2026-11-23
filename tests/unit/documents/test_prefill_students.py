"""Tests for DocumentType.prefill_students allow-list and template downloads."""

from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from documents.mailmerge import merge_docx, merge_values_for_application
from documents.models import DocumentType
from exchange.models import Application, ApplicationStatus
from tests.unit.documents.test_document_type_module import (
    _document_text,
    _docx_bytes,
    _response_bytes,
)
from tests.utils import TestUtils


class PrefillStudentsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = TestUtils.create_test_user(
            username="prefilladmin",
            email="prefill.admin@example.com",
            role="admin",
        )
        self.coordinator = TestUtils.create_test_user(
            username="prefillcoord",
            email="prefill.coord@example.com",
            role="coordinator",
        )
        self.student = TestUtils.create_test_user(
            username="prefillstudent",
            email="prefill.student@example.com",
            role="student",
            first_name="Ana",
            last_name="Lopez",
        )
        self.other_student = TestUtils.create_test_user(
            username="otherprefill",
            email="other.prefill@example.com",
            role="student",
            first_name="Bruno",
            last_name="Diaz",
        )
        self.student.profile.matricula = "A01234567"
        self.student.profile.save(update_fields=["matricula"])
        self.other_student.profile.matricula = "A07654321"
        self.other_student.profile.save(update_fields=["matricula"])
        self.doc_type = DocumentType.objects.create(
            name="Prefill Mobility Form",
            slug="prefill_mobility_form",
        )
        self.doc_type.template_file.save(
            "prefill.docx",
            SimpleUploadedFile("prefill.docx", _docx_bytes()),
            save=True,
        )
        self.program = TestUtils.create_test_program(name="Prefill Mobility Program")
        app_status, _ = ApplicationStatus.objects.get_or_create(
            name="draft", defaults={"order": 1}
        )
        self.application = Application.objects.create(
            student=self.student, program=self.program, status=app_status
        )

    def _download_url(self):
        return reverse(
            "api:documenttype-download-template", kwargs={"pk": self.doc_type.pk}
        )

    def _list_url(self):
        return reverse(
            "api:documenttype-prefill-students", kwargs={"pk": self.doc_type.pk}
        )

    def _remove_url(self, user_id):
        return reverse(
            "api:documenttype-prefill-students-remove",
            kwargs={"pk": self.doc_type.pk, "user_id": user_id},
        )

    def _bulk_url(self):
        return reverse(
            "api:documenttype-prefill-students-bulk", kwargs={"pk": self.doc_type.pk}
        )

    def _my_templates_url(self):
        return reverse("api:documenttype-my-prefill-templates")

    def test_allowed_student_gets_own_values(self):
        self.doc_type.prefill_students.add(self.student)
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self._download_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        text = _document_text(_response_bytes(response))
        self.assertIn("Ana", text)
        self.assertIn("Lopez", text)
        self.assertIn(self.student.email, text)

    def test_unlisted_student_gets_blank_file(self):
        blank = self.doc_type.template_file.open("rb").read()
        self.doc_type.template_file.close()
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self._download_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(_response_bytes(response), blank)

    def test_student_cannot_fetch_another_via_student_param(self):
        self.doc_type.prefill_students.add(self.other_student)
        self.client.force_authenticate(user=self.student)
        response = self.client.get(
            self._download_url(), {"student": str(self.other_student.pk)}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_preview_works_and_writes_audit_entry(self):
        self.doc_type.prefill_students.add(self.student)
        self.client.force_authenticate(user=self.coordinator)
        with mock.patch("documents.views.logger.info") as audit_log:
            response = self.client.get(
                self._download_url(), {"student": str(self.student.pk)}
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        text = _document_text(_response_bytes(response))
        self.assertIn("Ana", text)
        audit_log.assert_called()
        args, kwargs = audit_log.call_args
        self.assertEqual(args[0], "document_template_prefill_preview")
        self.assertEqual(kwargs["extra"]["action"], "prefill_template_preview")
        self.assertEqual(kwargs["extra"]["actor_id"], self.coordinator.pk)
        self.assertEqual(kwargs["extra"]["student_id"], self.student.pk)
        self.assertEqual(kwargs["extra"]["document_type_id"], self.doc_type.pk)

    def test_staff_preview_of_unlisted_student_returns_404(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(
            self._download_url(), {"student": str(self.student.pk)}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_application_merge_has_no_regression(self):
        """?application= download stays byte-for-byte equal to direct merge path."""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(
            self._download_url(), {"application": str(self.application.id)}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        template = self.doc_type.template_file.open("rb").read()
        self.doc_type.template_file.close()
        expected = merge_docx(template, merge_values_for_application(self.application))
        self.assertEqual(_response_bytes(response), expected)

    def test_bulk_add_reports_added_already_not_found(self):
        self.doc_type.prefill_students.add(self.student)
        self.client.force_authenticate(user=self.admin)
        payload = {
            "text": "\n".join(
                [
                    self.student.profile.matricula,
                    self.other_student.email.upper(),
                    "missing.student@example.com",
                    "Z99999999",
                ]
            )
        }
        response = self.client.post(self._bulk_url(), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.json()
        self.assertEqual(body["added"], 1)
        self.assertEqual(body["already_listed"], 1)
        self.assertEqual(
            set(body["not_found"]),
            {"missing.student@example.com", "Z99999999"},
        )
        self.assertTrue(
            self.doc_type.prefill_students.filter(pk=self.other_student.pk).exists()
        )
        # Never creates users
        from django.contrib.auth import get_user_model

        User = get_user_model()
        self.assertFalse(
            User.objects.filter(email__iexact="missing.student@example.com").exists()
        )

    def test_list_endpoints_require_coordinator_or_admin(self):
        self.client.force_authenticate(user=self.student)
        self.assertEqual(
            self.client.get(self._list_url()).status_code, status.HTTP_403_FORBIDDEN
        )
        self.assertEqual(
            self.client.post(
                self._list_url(), {"user_id": self.other_student.pk}, format="json"
            ).status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            self.client.post(
                self._bulk_url(), {"text": self.other_student.email}, format="json"
            ).status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.client.force_authenticate(user=self.coordinator)
        list_resp = self.client.get(self._list_url())
        self.assertEqual(list_resp.status_code, status.HTTP_200_OK)
        add_resp = self.client.post(
            self._list_url(), {"user_id": self.student.pk}, format="json"
        )
        self.assertEqual(add_resp.status_code, status.HTTP_201_CREATED)
        remove_resp = self.client.delete(self._remove_url(self.student.pk))
        self.assertEqual(remove_resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_student_my_prefill_templates_lists_only_own(self):
        other_type = DocumentType.objects.create(
            name="Other Prefill Type", slug="other_prefill_type"
        )
        self.doc_type.prefill_students.add(self.student)
        other_type.prefill_students.add(self.other_student)
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self._my_templates_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = {row["id"] for row in response.json()["results"]}
        self.assertEqual(ids, {self.doc_type.pk})

    def test_student_my_prefill_templates_excludes_types_without_template(self):
        bare = DocumentType.objects.create(
            name="Bare Prefill Type",
            slug="bare_prefill_type",
            submission_mode="download_only",
        )
        self.doc_type.prefill_students.add(self.student)
        bare.prefill_students.add(self.student)
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self._my_templates_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json()["results"]
        ids = {row["id"] for row in results}
        self.assertEqual(ids, {self.doc_type.pk})
        self.assertTrue(all(row.get("has_template") for row in results))

    def test_merge_values_for_student_blanks_program_keys(self):
        from documents.mailmerge import merge_values_for_student

        values = merge_values_for_student(self.student)
        self.assertEqual(values["FirstName"], "Ana")
        self.assertEqual(values["Matricula"], "A01234567")
        self.assertEqual(values["ProgramName"], "")
        self.assertEqual(values["HostInstitution"], "")
        self.assertEqual(values["ApplicationId"], "")


class ApplicationMergeRegressionTests(TestCase):
    """Ensure application merge output matches the pre-refactor field set."""

    def setUp(self):
        self.student = TestUtils.create_test_user(
            username="merge_reg_student",
            email="merge.reg@example.com",
            role="student",
            first_name="Carla",
            last_name="Ruiz",
        )
        self.program = TestUtils.create_test_program(name="Regression Mobility")
        app_status, _ = ApplicationStatus.objects.get_or_create(
            name="draft", defaults={"order": 1}
        )
        self.application = Application.objects.create(
            student=self.student, program=self.program, status=app_status
        )

    def test_application_values_include_program_and_student(self):
        values = merge_values_for_application(self.application)
        self.assertEqual(values["FirstName"], "Carla")
        self.assertEqual(values["ProgramName"], "Regression Mobility")
        self.assertEqual(values["ApplicationId"], str(self.application.id))
        self.assertEqual(values["Username"], "merge_reg_student")
