"""Eligibility ruleset document schema (versioned ``rules_json``).

Distinct from ``ELIGIBILITY_SCHEMA_VERSION`` on the evaluation engine payload.
``EligibilityRuleSet.schema_version`` tracks this document format.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import date, datetime
from typing import Any

from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.dateparse import parse_date

# Current persisted rules_json document shape.
RULESET_DOCUMENT_SCHEMA_VERSION = 2
SUPPORTED_RULESET_SCHEMA_VERSIONS = frozenset({1, 2})

PROGRAM_OVERRIDE_KEYS = frozenset(
    {
        "application_open_date",
        "application_deadline",
        "min_gpa",
        "min_semester",
        "min_credits_approved_percent",
        "required_language",
        "min_language_level",
        "min_age",
        "max_age",
    }
)

CEFR_LEVELS = frozenset({"A1", "A2", "B1", "B2", "C1", "C2"})

# Top-level keys allowed on schema_version >= 2 documents.
V2_TOP_LEVEL_KEYS = frozenset({"program_overrides", "meta"})
# Schema v1 accepted loose payloads; unknown keys are stripped on normalize to v2.
V1_TOP_LEVEL_KEYS = frozenset({"program_overrides", "meta", "rules"})


def describe_ruleset_schema() -> dict[str, Any]:
    """Machine-readable description for staff clients / OpenAPI consumers."""
    return {
        "schema_version": RULESET_DOCUMENT_SCHEMA_VERSION,
        "supported_versions": sorted(SUPPORTED_RULESET_SCHEMA_VERSIONS),
        "top_level_keys": sorted(V2_TOP_LEVEL_KEYS),
        "program_override_keys": sorted(PROGRAM_OVERRIDE_KEYS),
        "min_language_level_values": sorted(CEFR_LEVELS),
        "notes": (
            "program_overrides overlay Program scalar eligibility fields when the "
            "ruleset is active. meta is optional free-form metadata (strings only). "
            "On apply/submit, Application.eligibility_ruleset_snapshot freezes the "
            "active ruleset document (schema_version + content_revision + rules_json) "
            "so later edits do not rewrite historical evaluations."
        ),
    }


def _as_date(value: Any, field: str) -> str | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, str):
        parsed = parse_date(value.strip())
        if parsed is None:
            raise DjangoValidationError({field: f"Invalid ISO date for {field}."})
        return parsed.isoformat()
    raise DjangoValidationError({field: f"{field} must be an ISO date string."})


def _as_float(value: Any, field: str, *, min_value: float | None = None, max_value: float | None = None) -> float | None:
    if value in (None, ""):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise DjangoValidationError({field: f"{field} must be a number."}) from exc
    if min_value is not None and number < min_value:
        raise DjangoValidationError({field: f"{field} must be >= {min_value}."})
    if max_value is not None and number > max_value:
        raise DjangoValidationError({field: f"{field} must be <= {max_value}."})
    return number


def _as_int(value: Any, field: str, *, min_value: int | None = None) -> int | None:
    if value in (None, ""):
        return None
    try:
        if isinstance(value, bool):
            raise TypeError
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise DjangoValidationError({field: f"{field} must be an integer."}) from exc
    if min_value is not None and number < min_value:
        raise DjangoValidationError({field: f"{field} must be >= {min_value}."})
    return number


def _as_str(value: Any, field: str) -> str | None:
    if value in (None, ""):
        return None
    if not isinstance(value, str):
        raise DjangoValidationError({field: f"{field} must be a string."})
    text = value.strip()
    return text or None


def normalize_program_overrides(overrides: dict[str, Any], *, strict: bool) -> dict[str, Any]:
    if not isinstance(overrides, dict):
        raise DjangoValidationError({"program_overrides": "program_overrides must be a JSON object."})

    unknown = set(overrides) - PROGRAM_OVERRIDE_KEYS
    if unknown and strict:
        raise DjangoValidationError(
            {
                "program_overrides": (
                    f"Unknown override keys: {', '.join(sorted(unknown))}."
                )
            }
        )

    out: dict[str, Any] = {}
    for key in PROGRAM_OVERRIDE_KEYS:
        if key not in overrides:
            continue
        raw = overrides[key]
        if key in ("application_open_date", "application_deadline"):
            normalized = _as_date(raw, key)
        elif key == "min_gpa":
            normalized = _as_float(raw, key, min_value=0.0, max_value=4.0)
        elif key == "min_credits_approved_percent":
            normalized = _as_float(raw, key, min_value=0.0, max_value=100.0)
        elif key in ("min_semester", "min_age", "max_age"):
            normalized = _as_int(raw, key, min_value=0)
        elif key == "min_language_level":
            normalized = _as_str(raw, key)
            if normalized and normalized not in CEFR_LEVELS:
                raise DjangoValidationError(
                    {key: f"min_language_level must be one of {', '.join(sorted(CEFR_LEVELS))}."}
                )
        else:
            normalized = _as_str(raw, key)
        if normalized is not None:
            out[key] = normalized

    if (
        "min_age" in out
        and "max_age" in out
        and out["min_age"] is not None
        and out["max_age"] is not None
        and out["min_age"] > out["max_age"]
    ):
        raise DjangoValidationError({"max_age": "max_age must be >= min_age."})

    return out


def normalize_meta(meta: Any, *, strict: bool) -> dict[str, str]:
    if meta is None:
        return {}
    if not isinstance(meta, dict):
        raise DjangoValidationError({"meta": "meta must be a JSON object."})
    out: dict[str, str] = {}
    for key, value in meta.items():
        if not isinstance(key, str):
            raise DjangoValidationError({"meta": "meta keys must be strings."})
        if value is None:
            continue
        if not isinstance(value, str):
            if strict:
                raise DjangoValidationError({"meta": f"meta.{key} must be a string."})
            continue
        out[key] = value
    return out


def validate_and_normalize_rules_json(
    rules_json: Any,
    *,
    schema_version: int,
) -> dict[str, Any]:
    """
    Validate and normalize a ruleset document for the given schema_version.

    Returns a cleaned dict suitable for persistence. Raises Django ValidationError
    (dict messages) on failure — callers map to DRF ValidationError.
    """
    if schema_version not in SUPPORTED_RULESET_SCHEMA_VERSIONS:
        raise DjangoValidationError(
            {
                "schema_version": (
                    f"Unsupported schema_version {schema_version}; "
                    f"supported: {sorted(SUPPORTED_RULESET_SCHEMA_VERSIONS)}."
                )
            }
        )

    if rules_json in (None, ""):
        rules_json = {}
    if not isinstance(rules_json, dict):
        raise DjangoValidationError({"rules_json": "Must be a JSON object."})

    strict = schema_version >= 2
    allowed = V2_TOP_LEVEL_KEYS if strict else V1_TOP_LEVEL_KEYS
    unknown = set(rules_json) - allowed
    if unknown and strict:
        raise DjangoValidationError(
            {
                "rules_json": (
                    f"Unknown top-level keys for schema_version {schema_version}: "
                    f"{', '.join(sorted(unknown))}."
                )
            }
        )

    raw = deepcopy(rules_json)
    overrides = normalize_program_overrides(raw.get("program_overrides") or {}, strict=strict)
    meta = normalize_meta(raw.get("meta"), strict=strict)

    out: dict[str, Any] = {}
    if overrides:
        out["program_overrides"] = overrides
    if meta:
        out["meta"] = meta
    return out
