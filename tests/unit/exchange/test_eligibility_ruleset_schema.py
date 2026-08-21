"""Unit tests for eligibility ruleset document schema (v2)."""

import pytest
from django.core.exceptions import ValidationError

from exchange.eligibility_ruleset_schema import (
    RULESET_DOCUMENT_SCHEMA_VERSION,
    describe_ruleset_schema,
    validate_and_normalize_rules_json,
)


def test_describe_ruleset_schema_reports_current_version():
    desc = describe_ruleset_schema()
    assert desc["schema_version"] == RULESET_DOCUMENT_SCHEMA_VERSION
    assert 2 in desc["supported_versions"]
    assert "min_gpa" in desc["program_override_keys"]


def test_normalize_v2_typed_overrides():
    out = validate_and_normalize_rules_json(
        {
            "program_overrides": {
                "min_gpa": "3.50",
                "min_semester": "4",
                "required_language": " English ",
                "min_language_level": "B2",
                "application_open_date": "2026-01-15",
            },
            "meta": {"note": "Fulbright overlay"},
        },
        schema_version=2,
    )
    assert out["program_overrides"]["min_gpa"] == 3.5
    assert out["program_overrides"]["min_semester"] == 4
    assert out["program_overrides"]["required_language"] == "English"
    assert out["program_overrides"]["application_open_date"] == "2026-01-15"
    assert out["meta"]["note"] == "Fulbright overlay"


def test_v2_rejects_unknown_override_keys():
    with pytest.raises(ValidationError) as ctx:
        validate_and_normalize_rules_json(
            {"program_overrides": {"min_gpa": 3.0, "unknown_flag": True}},
            schema_version=2,
        )
    assert "unknown_flag" in str(ctx.value)


def test_v2_rejects_unknown_top_level_keys():
    with pytest.raises(ValidationError) as ctx:
        validate_and_normalize_rules_json(
            {"program_overrides": {}, "rules": []},
            schema_version=2,
        )
    assert "rules" in str(ctx.value)


def test_v1_strips_legacy_rules_key_without_error():
    out = validate_and_normalize_rules_json(
        {"program_overrides": {"min_gpa": 3.2}, "rules": [{"id": "legacy"}]},
        schema_version=1,
    )
    assert "rules" not in out
    assert out["program_overrides"]["min_gpa"] == 3.2


def test_v2_rejects_invalid_cefr_and_age_range():
    with pytest.raises(ValidationError):
        validate_and_normalize_rules_json(
            {"program_overrides": {"min_language_level": "Z9"}},
            schema_version=2,
        )
    with pytest.raises(ValidationError):
        validate_and_normalize_rules_json(
            {"program_overrides": {"min_age": 30, "max_age": 18}},
            schema_version=2,
        )
