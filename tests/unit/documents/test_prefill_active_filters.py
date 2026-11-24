"""Tests for DocumentType prefill active filters and auto-inclusion."""

from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import SchoolFaculty, Unidad
from documents.models import DocumentType
from documents.prefill_filters import (
    apply_prefill_active_filters_for_user,
    clear_prefill_active_filters,
    parse_prefill_filter_params,
    prefill_filter_queryset,
    set_prefill_active_filters,
    user_matches_prefill_filters,
)
from tests.utils import TestUtils


class PrefillFilterMatchingTests(TestCase):
    """Unit tests for filter parsing and matching."""

    def setUp(self):
        self.unidad = Unidad.objects.create(name="Campus Alpha", code="alpha")
        self.other_unidad = Unidad.objects.create(name="Campus Beta", code="beta")
        self.school = SchoolFaculty.objects.create(
            name="Sciences", code="sci", unidad=self.unidad
        )
        self.student = TestUtils.create_test_user(
            username="match_stu",
            email="match.stu@example.edu",
            role="student",
            first_name="Match",
            last_name="Student",
        )
        self.student.profile.unidad = self.unidad
        self.student.profile.school = self.school
        self.student.profile.save(update_fields=["unidad", "school"])

    def test_parse_normalizes_domain_and_blank_ids(self):
        parsed = parse_prefill_filter_params(
            {"email_domain": "@Example.EDU", "unidad": "", "school_id": None}
        )
        self.assertEqual(
            parsed,
            {"domain": "example.edu", "unidad_id": None, "school_id": None},
        )

    def test_user_matches_combined_filters(self):
        filters = {
            "domain": "example.edu",
            "unidad_id": str(self.unidad.pk),
            "school_id": str(self.school.pk),
        }
        self.assertTrue(user_matches_prefill_filters(self.student, filters))
        self.assertFalse(
            user_matches_prefill_filters(
                self.student, {**filters, "domain": "other.edu"}
            )
        )
        self.assertEqual(prefill_filter_queryset(filters).count(), 1)

    def test_subdomain_does_not_match_exact_domain(self):
        self.student.email = "match.stu@mail.example.edu"
        self.student.save(update_fields=["email"])
        self.assertFalse(
            user_matches_prefill_filters(
                self.student,
                {"domain": "example.edu", "unidad_id": None, "school_id": None},
            )
        )


class PrefillActiveFiltersApiTests(TestCase):
    """API tests for viewing, setting, and clearing active filters."""

    def setUp(self):
        self.client = APIClient()
        self.admin = TestUtils.create_test_user(
            username="active_admin",
            email="active.admin@example.com",
            role="admin",
        )
        self.coordinator = TestUtils.create_test_user(
            username="active_coord",
            email="active.coord@example.com",
            role="coordinator",
        )
        self.student = TestUtils.create_test_user(
            username="active_stu",
            email="active.stu@example.edu",
            role="student",
            first_name="Active",
            last_name="Student",
        )
        self.unidad = Unidad.objects.create(name="Campus Gamma", code="gamma")
        self.school = SchoolFaculty.objects.create(
            name="Arts", code="arts", unidad=self.unidad
        )
        self.student.profile.unidad = self.unidad
        self.student.profile.school = self.school
        self.student.profile.save(update_fields=["unidad", "school"])
        self.doc_type = DocumentType.objects.create(
            name="Active Filter Form",
            slug="active_filter_form",
        )

    def _url(self):
        return reverse(
            "api:documenttype-prefill-students-active-filters",
            kwargs={"pk": self.doc_type.pk},
        )

    def _confirm_url(self):
        return reverse(
            "api:documenttype-prefill-students-filter-confirm",
            kwargs={"pk": self.doc_type.pk},
        )

    def test_student_gets_403(self):
        self.client.force_authenticate(user=self.student)
        self.assertEqual(
            self.client.get(self._url()).status_code, status.HTTP_403_FORBIDDEN
        )

    def test_get_inactive_by_default(self):
        self.client.force_authenticate(user=self.coordinator)
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.json()
        self.assertFalse(body["active"])
        self.assertIsNone(body["filter"])

    def test_put_sets_active_filters_and_syncs(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.put(
            self._url(),
            {"domain": "example.edu", "unidad_id": str(self.unidad.pk)},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.json()
        self.assertTrue(body["active"])
        self.assertEqual(body["filter"]["domain"], "example.edu")
        self.assertEqual(body["labels"]["unidad"], "Campus Gamma")
        self.assertGreaterEqual(body["added"], 1)
        self.doc_type.refresh_from_db()
        self.assertIsNotNone(self.doc_type.prefill_active_filters)
        self.assertTrue(
            self.doc_type.prefill_students.filter(pk=self.student.pk).exists()
        )

    def test_filter_confirm_persists_active_filters(self):
        self.client.force_authenticate(user=self.coordinator)
        response = self.client.post(
            self._confirm_url(),
            {"domain": "example.edu"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.json()
        self.assertTrue(body["active_filters"]["active"])
        self.doc_type.refresh_from_db()
        self.assertEqual(self.doc_type.prefill_active_filters["domain"], "example.edu")

    def test_clear_stops_auto_include_but_keeps_students(self):
        set_prefill_active_filters(
            self.doc_type,
            {"domain": "example.edu"},
            sync=True,
        )
        self.assertTrue(
            self.doc_type.prefill_students.filter(pk=self.student.pk).exists()
        )
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(self._url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.json()["active"])
        self.doc_type.refresh_from_db()
        self.assertIsNone(self.doc_type.prefill_active_filters)
        self.assertTrue(
            self.doc_type.prefill_students.filter(pk=self.student.pk).exists()
        )


class PrefillActiveFiltersAutoIncludeTests(TransactionTestCase):
    """Auto-include on create/update, idempotency, and manual exclusion."""

    def setUp(self):
        self.unidad = Unidad.objects.create(name="Campus Delta", code="delta")
        self.other_unidad = Unidad.objects.create(name="Campus Epsilon", code="epsilon")
        self.school = SchoolFaculty.objects.create(
            name="Business", code="biz", unidad=self.unidad
        )
        self.doc_type = DocumentType.objects.create(
            name="Auto Include Form",
            slug="auto_include_form",
        )
        set_prefill_active_filters(
            self.doc_type,
            {
                "domain": "example.edu",
                "unidad_id": str(self.unidad.pk),
                "school_id": None,
            },
            sync=True,
        )

    def test_new_matching_student_is_auto_included(self):
        student = TestUtils.create_test_user(
            username="auto_new",
            email="auto.new@example.edu",
            role="student",
            first_name="Auto",
            last_name="New",
        )
        student.profile.unidad = self.unidad
        student.profile.school = self.school
        student.profile.save(update_fields=["unidad", "school"])

        self.assertTrue(self.doc_type.prefill_students.filter(pk=student.pk).exists())

    def test_attribute_change_into_match_auto_includes(self):
        student = TestUtils.create_test_user(
            username="auto_later",
            email="auto.later@other.edu",
            role="student",
            first_name="Auto",
            last_name="Later",
        )
        student.profile.unidad = self.other_unidad
        student.profile.save(update_fields=["unidad"])
        self.assertFalse(self.doc_type.prefill_students.filter(pk=student.pk).exists())

        student.email = "auto.later@example.edu"
        student.save(update_fields=["email"])
        student.profile.unidad = self.unidad
        student.profile.save(update_fields=["unidad"])

        self.assertTrue(self.doc_type.prefill_students.filter(pk=student.pk).exists())

    def test_auto_include_is_idempotent(self):
        student = TestUtils.create_test_user(
            username="auto_idem",
            email="auto.idem@example.edu",
            role="student",
        )
        student.profile.unidad = self.unidad
        student.profile.save(update_fields=["unidad"])
        self.assertEqual(
            self.doc_type.prefill_students.filter(pk=student.pk).count(), 1
        )
        added_again = apply_prefill_active_filters_for_user(student.pk)
        self.assertEqual(added_again, 0)
        self.assertEqual(
            self.doc_type.prefill_students.filter(pk=student.pk).count(), 1
        )

    def test_manual_removal_is_preserved_while_filters_active(self):
        client = APIClient()
        admin = TestUtils.create_test_user(
            username="auto_admin",
            email="auto.admin@example.com",
            role="admin",
        )
        student = TestUtils.create_test_user(
            username="auto_removed",
            email="auto.removed@example.edu",
            role="student",
        )
        student.profile.unidad = self.unidad
        student.profile.save(update_fields=["unidad"])
        self.assertTrue(self.doc_type.prefill_students.filter(pk=student.pk).exists())

        client.force_authenticate(user=admin)
        remove_url = reverse(
            "api:documenttype-prefill-students-remove",
            kwargs={"pk": self.doc_type.pk, "user_id": student.pk},
        )
        response = client.delete(remove_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(self.doc_type.prefill_students.filter(pk=student.pk).exists())
        self.assertTrue(
            self.doc_type.prefill_filter_exclusions.filter(pk=student.pk).exists()
        )

        # Profile save should not re-add while excluded
        student.profile.school = self.school
        student.profile.save(update_fields=["school"])
        self.assertFalse(self.doc_type.prefill_students.filter(pk=student.pk).exists())

        # Manual re-add clears exclusion
        add_url = reverse(
            "api:documenttype-prefill-students",
            kwargs={"pk": self.doc_type.pk},
        )
        add_resp = client.post(add_url, {"user_id": student.pk}, format="json")
        self.assertIn(
            add_resp.status_code, (status.HTTP_200_OK, status.HTTP_201_CREATED)
        )
        self.assertFalse(
            self.doc_type.prefill_filter_exclusions.filter(pk=student.pk).exists()
        )

    def test_clear_keeps_listed_students_and_stops_auto_include(self):
        existing = TestUtils.create_test_user(
            username="auto_keep",
            email="auto.keep@example.edu",
            role="student",
        )
        existing.profile.unidad = self.unidad
        existing.profile.save(update_fields=["unidad"])
        self.assertTrue(self.doc_type.prefill_students.filter(pk=existing.pk).exists())

        clear_prefill_active_filters(self.doc_type)
        self.assertIsNone(self.doc_type.prefill_active_filters)
        self.assertTrue(self.doc_type.prefill_students.filter(pk=existing.pk).exists())

        later = TestUtils.create_test_user(
            username="auto_after_clear",
            email="auto.after@example.edu",
            role="student",
        )
        later.profile.unidad = self.unidad
        later.profile.save(update_fields=["unidad"])
        self.assertFalse(self.doc_type.prefill_students.filter(pk=later.pk).exists())

    def test_non_matching_student_not_included(self):
        outsider = TestUtils.create_test_user(
            username="auto_out",
            email="auto.out@other.edu",
            role="student",
        )
        outsider.profile.unidad = self.other_unidad
        outsider.profile.save(update_fields=["unidad"])
        self.assertFalse(self.doc_type.prefill_students.filter(pk=outsider.pk).exists())
