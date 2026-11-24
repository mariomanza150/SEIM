"""Regression: form type writes and cross-user submission links."""

import pytest
from rest_framework.test import APIClient

from application_forms.models import FormType
from tests.utils import TestUtils


@pytest.mark.django_db
class TestFormTypeAndSubmissionAcl:
    def setup_method(self):
        self.student_a = TestUtils.create_test_user(
            username="form_acl_a",
            email="form_acl_a@example.com",
            role="student",
        )
        self.student_b = TestUtils.create_test_user(
            username="form_acl_b",
            email="form_acl_b@example.com",
            role="student",
        )
        self.admin = TestUtils.create_test_user(
            username="form_acl_admin",
            email="form_acl_admin@example.com",
            role="admin",
        )
        self.form_type = FormType.objects.create(
            name="ACL Form",
            form_type="application",
            description="acl",
            schema={"type": "object", "properties": {}},
            is_active=True,
            created_by=self.admin,
        )
        self.app_b = TestUtils.create_test_application(student=self.student_b)
        self.client = APIClient()

    def test_student_cannot_create_form_type(self):
        self.client.force_authenticate(user=self.student_a)
        response = self.client.post(
            "/api/application-forms/form-types/",
            {
                "name": "Hijacked Form",
                "form_type": "application",
                "description": "should fail",
                "schema": {"type": "object"},
                "is_active": True,
            },
            format="json",
        )
        assert response.status_code == 403

    def test_student_cannot_link_submission_to_other_application(self):
        self.client.force_authenticate(user=self.student_a)
        response = self.client.post(
            "/api/application-forms/submissions/",
            {
                "form_type": self.form_type.id,
                "responses": {"q": "a"},
                "application": str(self.app_b.id),
            },
            format="json",
        )
        assert response.status_code == 400
        assert "own applications" in str(response.data).lower()

    def test_student_can_link_submission_to_own_application(self):
        app_a = TestUtils.create_test_application(student=self.student_a)
        self.client.force_authenticate(user=self.student_a)
        response = self.client.post(
            "/api/application-forms/submissions/",
            {
                "form_type": self.form_type.id,
                "responses": {"q": "a"},
                "application": str(app_a.id),
            },
            format="json",
        )
        assert response.status_code == 201
        assert str(response.data["application"]) == str(app_a.id)
