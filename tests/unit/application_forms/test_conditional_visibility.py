import pytest
from django.core.exceptions import ValidationError

from application_forms.models import FormType
from application_forms.services import FormSubmissionService
from application_forms.visibility import (
    field_effective_visible,
    field_is_visible,
    iter_visible_steps_from_form_type,
    visible_when_satisfied,
)


@pytest.mark.parametrize(
    "rule,responses,expected",
    [
        ({}, {"a": 1}, True),
        (None, {}, True),
        ({"field": "x", "equals": "yes"}, {"x": "yes"}, True),
        ({"field": "x", "equals": "yes"}, {"x": "no"}, False),
        ({"field": "x", "notEquals": 0}, {"x": 1}, True),
        ({"field": "x", "in": [1, 2]}, {"x": 2}, True),
        ({"field": "x", "in": [1, 2]}, {"x": 3}, False),
        ({"field": "x", "truthy": True}, {"x": "hi"}, True),
        ({"field": "x", "truthy": True}, {"x": ""}, False),
        ({"field": "x", "truthy": False}, {"x": ""}, True),
    ],
)
def test_visible_when_satisfied(rule, responses, expected):
    assert visible_when_satisfied(rule, responses) is expected


def test_visible_when_satisfied_program_id_context():
    rule = {"program_id": 5}
    assert visible_when_satisfied(rule, {}, {"program_id": 5}) is True
    assert visible_when_satisfied(rule, {}, {"program_id": 6}) is False
    assert visible_when_satisfied(rule, {}, None) is False


def test_visible_when_program_id_plus_field():
    rule = {"program_id": 1, "field": "a", "equals": "z"}
    assert visible_when_satisfied(rule, {"a": "z"}, {"program_id": 1}) is True
    assert visible_when_satisfied(rule, {"a": "y"}, {"program_id": 1}) is False
    assert visible_when_satisfied(rule, {"a": "z"}, {"program_id": 2}) is False


def test_visible_when_staff_only_and_roles_any():
    assert visible_when_satisfied({"staff_only": True}, {}, {"viewer_roles": ["student"]}) is False
    assert visible_when_satisfied({"staff_only": True}, {}, {"viewer_roles": ["coordinator"]}) is True
    assert visible_when_satisfied({"staff_only": True}, {}, {"viewer_roles": ["admin"]}) is True
    assert visible_when_satisfied({"roles_any": ["admin", "student"]}, {}, {"viewer_roles": ["student"]}) is True
    assert visible_when_satisfied({"roles_any": ["admin"]}, {}, {"viewer_roles": ["student"]}) is False


@pytest.mark.django_db
def test_validate_responses_visibility_context_program_id_only():
    ft = FormType.objects.create(
        name="ProgBranch",
        form_type="application",
        schema={
            "type": "object",
            "properties": {
                "extra": {
                    "type": "string",
                    "title": "Extra",
                    "x-seim-visibleWhen": {"program_id": 42},
                },
            },
            "required": ["extra"],
        },
    )
    FormSubmissionService.validate_responses(
        ft, {}, visibility_context={"program_id": 7, "has_assigned_coordinator": False}
    )
    with pytest.raises(ValidationError):
        FormSubmissionService.validate_responses(
            ft, {}, visibility_context={"program_id": 42, "has_assigned_coordinator": False}
        )


@pytest.mark.django_db
def test_validate_responses_staff_only_field_skipped_for_student():
    ft = FormType.objects.create(
        name="StaffFld",
        form_type="application",
        schema={
            "type": "object",
            "properties": {
                "internal_note": {
                    "type": "string",
                    "x-seim-visibleWhen": {"staff_only": True},
                },
            },
            "required": ["internal_note"],
        },
    )
    FormSubmissionService.validate_responses(
        ft,
        {},
        visibility_context={"viewer_roles": ["student"], "program_id": 1},
    )
    with pytest.raises(ValidationError):
        FormSubmissionService.validate_responses(
            ft,
            {},
            visibility_context={"viewer_roles": ["coordinator"], "program_id": 1},
        )


@pytest.mark.django_db
def test_validate_responses_skips_required_when_hidden():
    ft = FormType.objects.create(
        name="Cond",
        form_type="application",
        schema={
            "type": "object",
            "properties": {
                "gate": {"type": "string", "title": "Gate"},
                "extra": {
                    "type": "string",
                    "title": "Extra",
                    "x-seim-visibleWhen": {"field": "gate", "equals": "show"},
                },
            },
            "required": ["gate", "extra"],
        },
    )
    FormSubmissionService.validate_responses(ft, {"gate": "hide"})
    with pytest.raises(ValidationError):
        FormSubmissionService.validate_responses(ft, {"gate": "show"})


@pytest.mark.django_db
def test_validate_step_patch_uses_merged_for_visibility():
    ft = FormType.objects.create(
        name="Step",
        form_type="application",
        schema={
            "type": "object",
            "properties": {
                "a": {"type": "string"},
                "b": {
                    "type": "string",
                    "x-seim-visibleWhen": {"field": "a", "equals": "x"},
                },
            },
            "required": ["a", "b"],
        },
    )
    merged = {"a": "y", "b": ""}
    FormSubmissionService.validate_step_patch(
        ft, {"a": "y"}, ["a", "b"], merged_responses=merged
    )
    merged2 = {"a": "x"}
    with pytest.raises(ValidationError):
        FormSubmissionService.validate_step_patch(
            ft, {"a": "x"}, ["a", "b"], merged_responses=merged2
        )


def test_field_is_visible_unknown_key():
    cfg = {"x-seim-visibleWhen": {"field": "m", "equals": 1}}
    assert field_is_visible(cfg, {}) is False
    assert field_is_visible(cfg, {"m": 1}) is True


@pytest.mark.django_db
def test_iter_visible_steps_skips_conditional():
    ft = FormType.objects.create(
        name="Branch",
        form_type="application",
        schema={
            "type": "object",
            "properties": {
                "branch": {"type": "string"},
                "a": {"type": "string"},
                "b": {"type": "string"},
            },
            "required": [],
        },
        step_definitions=[
            {"key": "s1", "title": "One", "field_names": ["branch"]},
            {
                "key": "s2",
                "title": "Two",
                "field_names": ["a"],
                "visible_when": {"field": "branch", "equals": "x"},
            },
            {"key": "s3", "title": "Three", "field_names": ["b"]},
        ],
    )
    keys_hide = [s["key"] for s in iter_visible_steps_from_form_type(ft, {"branch": "n"})]
    assert keys_hide == ["s1", "s3"]
    keys_show = [s["key"] for s in iter_visible_steps_from_form_type(ft, {"branch": "x"})]
    assert keys_show == ["s1", "s2", "s3"]


@pytest.mark.django_db
def test_field_effective_visible_respects_step_visibility():
    ft = FormType.objects.create(
        name="Eff",
        form_type="application",
        schema={
            "type": "object",
            "properties": {
                "g": {"type": "string"},
                "h": {"type": "string"},
            },
            "required": ["h"],
        },
        step_definitions=[
            {"key": "s1", "title": "One", "field_names": ["g"]},
            {
                "key": "s2",
                "title": "Two",
                "field_names": ["h"],
                "visible_when": {"field": "g", "equals": "yes"},
            },
        ],
    )
    assert field_effective_visible(ft, "h", {"g": "no"}) is False
    FormSubmissionService.validate_responses(ft, {"g": "no"})
    with pytest.raises(ValidationError):
        FormSubmissionService.validate_responses(ft, {"g": "yes"})
