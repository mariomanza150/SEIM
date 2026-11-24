"""Integration: prefill active filters persist, sync, clear, and auto-include."""

from django.test import TransactionTestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import Unidad
from documents.models import DocumentType
from tests.utils import TestUtils


class PrefillActiveFiltersIntegrationTests(TransactionTestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = TestUtils.create_test_user(
            username="int_prefill_admin",
            email="int.prefill.admin@example.com",
            role="admin",
        )
        self.unidad = Unidad.objects.create(name="Campus Integration", code="intcamp")
        self.doc_type = DocumentType.objects.create(
            name="Integration Prefill Form",
            slug="integration_prefill_form",
        )
        self.existing = TestUtils.create_test_user(
            username="int_prefill_existing",
            email="int.existing@example.edu",
            role="student",
            first_name="Existing",
            last_name="Student",
        )
        self.existing.profile.unidad = self.unidad
        self.existing.profile.save(update_fields=["unidad"])

    def _active_url(self):
        return reverse(
            "api:documenttype-prefill-students-active-filters",
            kwargs={"pk": self.doc_type.pk},
        )

    def test_put_clear_and_auto_include_new_student(self):
        self.client.force_authenticate(user=self.admin)
        put_resp = self.client.put(
            self._active_url(),
            {"domain": "example.edu", "unidad_id": str(self.unidad.pk)},
            format="json",
        )
        self.assertEqual(put_resp.status_code, status.HTTP_200_OK)
        self.assertTrue(put_resp.json()["active"])
        self.assertTrue(
            self.doc_type.prefill_students.filter(pk=self.existing.pk).exists()
        )

        new_student = TestUtils.create_test_user(
            username="int_prefill_new",
            email="int.new@example.edu",
            role="student",
            first_name="New",
            last_name="Student",
        )
        new_student.profile.unidad = self.unidad
        new_student.profile.save(update_fields=["unidad"])
        self.assertTrue(
            self.doc_type.prefill_students.filter(pk=new_student.pk).exists()
        )

        clear_resp = self.client.delete(self._active_url())
        self.assertEqual(clear_resp.status_code, status.HTTP_200_OK)
        self.assertFalse(clear_resp.json()["active"])
        self.assertTrue(
            self.doc_type.prefill_students.filter(pk=new_student.pk).exists()
        )

        after_clear = TestUtils.create_test_user(
            username="int_prefill_after",
            email="int.after@example.edu",
            role="student",
        )
        after_clear.profile.unidad = self.unidad
        after_clear.profile.save(update_fields=["unidad"])
        self.assertFalse(
            self.doc_type.prefill_students.filter(pk=after_clear.pk).exists()
        )
