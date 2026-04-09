"""Tests for FormStepTemplate and apply_step_template_to_form_type."""

import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from application_forms.models import FormStepTemplate, FormType
from application_forms.step_template_service import apply_step_template_to_form_type
from tests.utils import TestUtils


@pytest.mark.django_db
class TestApplyStepTemplateService:
    def test_happy_path_merges_schema_and_step(self):
        ft = FormType.objects.create(
            name="Base",
            form_type="application",
            schema={"type": "object", "properties": {"a": {"type": "string"}}, "required": []},
            step_definitions=[],
        )
        tpl = FormStepTemplate.objects.create(
            name="Extra step",
            step_title="Documents",
            default_step_key="docs",
            schema_properties={"b": {"type": "string", "title": "B"}},
            required_field_names=["b"],
            ui_schema_fragment={"b": {"ui:placeholder": "x"}},
        )
        apply_step_template_to_form_type(ft, tpl)
        ft.refresh_from_db()
        assert "b" in (ft.schema.get("properties") or {})
        assert "b" in (ft.schema.get("required") or [])
        assert len(ft.step_definitions) == 1
        assert ft.step_definitions[0]["key"] == "docs"
        assert ft.step_definitions[0]["field_names"] == ["b"]
        assert ft.ui_schema.get("b", {}).get("ui:placeholder") == "x"

    def test_property_collision_raises(self):
        ft = FormType.objects.create(
            name="Base",
            form_type="application",
            schema={"properties": {"x": {"type": "string"}}},
        )
        tpl = FormStepTemplate.objects.create(
            name="Dup",
            step_title="T",
            default_step_key="s1",
            schema_properties={"x": {"type": "number"}},
        )
        with pytest.raises(ValidationError):
            apply_step_template_to_form_type(ft, tpl)

    def test_duplicate_step_key_raises(self):
        ft = FormType.objects.create(
            name="Base",
            form_type="application",
            schema={"properties": {"a": {"type": "string"}}},
            step_definitions=[{"key": "docs", "title": "D", "field_names": ["a"]}],
        )
        tpl = FormStepTemplate.objects.create(
            name="T2",
            step_title="T",
            default_step_key="docs",
            schema_properties={"b": {"type": "string"}},
        )
        with pytest.raises(ValidationError):
            apply_step_template_to_form_type(ft, tpl)

    def test_inactive_template_raises(self):
        ft = FormType.objects.create(name="Base", form_type="application", schema={})
        tpl = FormStepTemplate.objects.create(
            name="Off",
            step_title="T",
            default_step_key="k",
            schema_properties={"z": {"type": "string"}},
            is_active=False,
        )
        with pytest.raises(ValidationError):
            apply_step_template_to_form_type(ft, tpl)


@pytest.mark.django_db
class TestApplyStepTemplateAPI:
    def setup_method(self):
        self.client = APIClient()
        self.admin = TestUtils.create_test_user(username="stadmin", role="admin")
        self.student = TestUtils.create_test_user(username="ststudent", role="student")
        self.form = FormType.objects.create(
            name="API Form",
            form_type="application",
            schema={"type": "object", "properties": {}, "required": []},
            created_by=self.admin,
        )
        self.tpl = FormStepTemplate.objects.create(
            name="API tpl",
            step_title="Step",
            default_step_key="extra",
            schema_properties={"f1": {"type": "string"}},
        )

    def test_apply_as_admin_returns_updated_form(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("application_forms:formtype-apply-step-template", kwargs={"pk": self.form.pk})
        r = self.client.post(url, {"template_id": self.tpl.id}, format="json")
        assert r.status_code == status.HTTP_200_OK
        assert "f1" in r.data.get("schema", {}).get("properties", {})

    def test_apply_forbidden_for_student(self):
        self.client.force_authenticate(user=self.student)
        url = reverse("application_forms:formtype-apply-step-template", kwargs={"pk": self.form.pk})
        r = self.client.post(url, {"template_id": self.tpl.id}, format="json")
        assert r.status_code == status.HTTP_403_FORBIDDEN

    def test_apply_by_slug(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("application_forms:formtype-apply-step-template", kwargs={"pk": self.form.pk})
        r = self.client.post(url, {"slug": self.tpl.slug}, format="json")
        assert r.status_code == status.HTTP_200_OK
