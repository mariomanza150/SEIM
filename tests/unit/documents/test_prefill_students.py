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


class PrefillStudentsFilterBulkTests(TestCase):
    """Filter preview/confirm bulk-add for DocumentType.prefill_students."""

    def setUp(self):
        from accounts.models import SchoolFaculty, Unidad

        self.client = APIClient()
        self.admin = TestUtils.create_test_user(
            username="filteradmin",
            email="filter.admin@example.com",
            role="admin",
        )
        self.coordinator = TestUtils.create_test_user(
            username="filtercoord",
            email="filter.coord@example.com",
            role="coordinator",
        )
        self.unidad_a = Unidad.objects.create(name="Campus North", code="north")
        self.unidad_b = Unidad.objects.create(name="Campus South", code="south")
        self.school_a = SchoolFaculty.objects.create(
            name="Engineering", code="eng", unidad=self.unidad_a
        )
        self.school_b = SchoolFaculty.objects.create(
            name="Medicine", code="med", unidad=self.unidad_b
        )

        self.student_a = TestUtils.create_test_user(
            username="filterstu_a",
            email="ana.filter@example.edu",
            role="student",
            first_name="Ana",
            last_name="Filter",
        )
        self.student_b = TestUtils.create_test_user(
            username="filterstu_b",
            email="bruno.filter@example.edu",
            role="student",
            first_name="Bruno",
            last_name="Filter",
        )
        self.student_other_domain = TestUtils.create_test_user(
            username="filterstu_other",
            email="carla.filter@other.edu",
            role="student",
            first_name="Carla",
            last_name="Filter",
        )
        self.student_subdomain = TestUtils.create_test_user(
            username="filterstu_sub",
            email="diego.filter@mail.example.edu",
            role="student",
            first_name="Diego",
            last_name="Filter",
        )
        self.inactive_student = TestUtils.create_test_user(
            username="filterstu_inactive",
            email="eva.filter@example.edu",
            role="student",
            first_name="Eva",
            last_name="Filter",
        )
        self.inactive_student.is_active = False
        self.inactive_student.save(update_fields=["is_active"])
        self.non_student = TestUtils.create_test_user(
            username="filterstaff",
            email="staff.filter@example.edu",
            role="coordinator",
            first_name="Staff",
            last_name="Filter",
        )

        for user, unidad, school in (
            (self.student_a, self.unidad_a, self.school_a),
            (self.student_b, self.unidad_a, self.school_a),
            (self.student_other_domain, self.unidad_b, self.school_b),
            (self.student_subdomain, self.unidad_a, self.school_a),
            (self.inactive_student, self.unidad_a, self.school_a),
        ):
            user.profile.unidad = unidad
            user.profile.school = school
            user.profile.save(update_fields=["unidad", "school"])

        self.doc_type = DocumentType.objects.create(
            name="Filter Prefill Form",
            slug="filter_prefill_form",
        )

    def _options_url(self):
        return reverse(
            "api:documenttype-prefill-students-filter-options",
            kwargs={"pk": self.doc_type.pk},
        )

    def _preview_url(self):
        return reverse(
            "api:documenttype-prefill-students-filter-preview",
            kwargs={"pk": self.doc_type.pk},
        )

    def _confirm_url(self):
        return reverse(
            "api:documenttype-prefill-students-filter-confirm",
            kwargs={"pk": self.doc_type.pk},
        )

    def test_student_gets_403_on_filter_endpoints(self):
        self.client.force_authenticate(user=self.student_a)
        self.assertEqual(
            self.client.get(self._options_url()).status_code, status.HTTP_403_FORBIDDEN
        )
        self.assertEqual(
            self.client.post(self._preview_url(), {}, format="json").status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            self.client.post(self._confirm_url(), {}, format="json").status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_filter_options_lists_unidad_school_and_domains(self):
        self.client.force_authenticate(user=self.coordinator)
        response = self.client.get(self._options_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.json()
        unidad_ids = {row["id"] for row in body["unidades"]}
        school_ids = {row["id"] for row in body["schools"]}
        self.assertIn(str(self.unidad_a.pk), unidad_ids)
        self.assertIn(str(self.school_a.pk), school_ids)
        self.assertIn("example.edu", body["domains"])
        self.assertIn("other.edu", body["domains"])
        self.assertIn("mail.example.edu", body["domains"])

    def test_preview_all_excludes_inactive_and_non_students(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self._preview_url(), {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.json()
        # Four active students only (a, b, other_domain, subdomain)
        self.assertEqual(body["matched"], 4)
        self.assertEqual(body["new_count"], 4)
        self.assertEqual(body["already_listed"], 0)
        sample_emails = {row["email"].lower() for row in body["samples"]}
        self.assertNotIn(self.inactive_student.email.lower(), sample_emails)
        self.assertNotIn(self.non_student.email.lower(), sample_emails)

    def test_domain_filter_exact_host_no_subdomains(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            self._preview_url(), {"domain": "Example.EDU"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.json()
        # ana + bruno + inactive excluded → 2; subdomain mail.example.edu excluded
        self.assertEqual(body["matched"], 2)
        self.assertEqual(body["new_count"], 2)
        emails = {row["email"].lower() for row in body["samples"]}
        self.assertIn(self.student_a.email.lower(), emails)
        self.assertNotIn(self.student_subdomain.email.lower(), emails)

    def test_unidad_and_school_filters(self):
        self.client.force_authenticate(user=self.coordinator)
        unidad_resp = self.client.post(
            self._preview_url(),
            {"unidad_id": str(self.unidad_b.pk)},
            format="json",
        )
        self.assertEqual(unidad_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(unidad_resp.json()["matched"], 1)
        self.assertEqual(
            unidad_resp.json()["samples"][0]["email"].lower(),
            self.student_other_domain.email.lower(),
        )

        school_resp = self.client.post(
            self._preview_url(),
            {"school_id": str(self.school_a.pk)},
            format="json",
        )
        self.assertEqual(school_resp.status_code, status.HTTP_200_OK)
        # student_a, student_b, student_subdomain (inactive excluded)
        self.assertEqual(school_resp.json()["matched"], 3)

    def test_confirm_matches_preview_and_is_idempotent(self):
        self.doc_type.prefill_students.add(self.student_a)
        self.client.force_authenticate(user=self.admin)
        filters = {"domain": "example.edu", "unidad_id": str(self.unidad_a.pk)}
        preview = self.client.post(self._preview_url(), filters, format="json")
        self.assertEqual(preview.status_code, status.HTTP_200_OK)
        preview_body = preview.json()
        self.assertEqual(preview_body["matched"], 2)
        self.assertEqual(preview_body["new_count"], 1)
        self.assertEqual(preview_body["already_listed"], 1)

        with mock.patch("documents.views.logger.info") as audit_log:
            confirm = self.client.post(self._confirm_url(), filters, format="json")
        self.assertEqual(confirm.status_code, status.HTTP_200_OK)
        confirm_body = confirm.json()
        self.assertEqual(confirm_body["matched"], preview_body["matched"])
        self.assertEqual(confirm_body["added"], preview_body["new_count"])
        self.assertEqual(confirm_body["already_listed"], preview_body["already_listed"])
        self.assertTrue(
            self.doc_type.prefill_students.filter(pk=self.student_b.pk).exists()
        )
        audit_log.assert_called()
        args, kwargs = audit_log.call_args
        self.assertEqual(args[0], "document_template_prefill_bulk_add")
        self.assertEqual(kwargs["extra"]["added"], 1)
        self.assertEqual(kwargs["extra"]["actor_id"], self.admin.pk)

        # Idempotent second confirm
        again = self.client.post(self._confirm_url(), filters, format="json")
        self.assertEqual(again.status_code, status.HTTP_200_OK)
        self.assertEqual(again.json()["added"], 0)
        self.assertEqual(again.json()["already_listed"], 2)
        self.assertEqual(
            self.doc_type.prefill_students.filter(
                pk__in=[self.student_a.pk, self.student_b.pk]
            ).count(),
            2,
        )

    def test_combined_filters_and_empty_add_all(self):
        self.client.force_authenticate(user=self.coordinator)
        combined = self.client.post(
            self._preview_url(),
            {
                "domain": "example.edu",
                "unidad_id": str(self.unidad_a.pk),
                "school_id": str(self.school_a.pk),
            },
            format="json",
        )
        self.assertEqual(combined.status_code, status.HTTP_200_OK)
        self.assertEqual(combined.json()["matched"], 2)

        confirm_all = self.client.post(self._confirm_url(), {}, format="json")
        self.assertEqual(confirm_all.status_code, status.HTTP_200_OK)
        self.assertEqual(confirm_all.json()["added"], 4)
        self.assertEqual(self.doc_type.prefill_students.count(), 4)


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
