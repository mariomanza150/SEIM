"""Snapshot and prune historic ApplicationSubjectSelection sets."""

from __future__ import annotations

from decimal import Decimal

from django.db import transaction

from exchange.models import (
    MAX_SUBJECT_PLAN_VERSIONS,
    ApplicationSubjectPlanVersion,
)

SUBJECT_PLAN_MAPPING_FIELDS = frozenset(
    {
        "host_subject",
        "custom_code",
        "custom_name",
        "custom_credits",
        "home_course_label",
        "home_course_code",
        "credits",
        "notes",
    }
)


def _json_scalar(value):
    if value is None:
        return None
    if isinstance(value, Decimal):
        return str(value)
    return value


def _grade_label(grade) -> str | None:
    if grade is None:
        return None
    return getattr(grade, "label", None)


def selection_to_snapshot_dict(row) -> dict:
    """Serialize one live selection for a historic payload."""
    proposed_at = row.proposed_at.isoformat() if row.proposed_at else None
    confirmed_at = row.confirmed_at.isoformat() if row.confirmed_at else None
    return {
        "id": str(row.id),
        "host_subject": str(row.host_subject_id) if row.host_subject_id else None,
        "host_course_code": row.host_course_code or "",
        "host_course_name": row.host_course_name or "",
        "custom_code": row.custom_code or "",
        "custom_name": row.custom_name or "",
        "custom_credits": _json_scalar(row.custom_credits),
        "home_course_label": row.home_course_label or "",
        "home_course_code": row.home_course_code or "",
        "credits": _json_scalar(row.credits),
        "notes": row.notes or "",
        "proposed_host_grade": (
            str(row.proposed_host_grade_id) if row.proposed_host_grade_id else None
        ),
        "proposed_host_grade_label": _grade_label(row.proposed_host_grade),
        "confirmed_host_grade": (
            str(row.confirmed_host_grade_id) if row.confirmed_host_grade_id else None
        ),
        "confirmed_host_grade_label": _grade_label(row.confirmed_host_grade),
        "home_grade": str(row.home_grade_id) if row.home_grade_id else None,
        "home_grade_label": _grade_label(row.home_grade),
        "grade_status": row.grade_status,
        "confirmation_notes": row.confirmation_notes or "",
        "proposed_at": proposed_at,
        "confirmed_at": confirmed_at,
    }


def build_subject_plan_payload(application) -> list[dict]:
    """Return the current live selection set as a JSON-serializable list."""
    rows = (
        application.subject_selections.select_related(
            "host_subject",
            "proposed_host_grade",
            "confirmed_host_grade",
            "home_grade",
        )
        .order_by("created_at", "id")
    )
    return [selection_to_snapshot_dict(row) for row in rows]


def prune_subject_plan_versions(application) -> int:
    """Delete oldest historic versions beyond ``MAX_SUBJECT_PLAN_VERSIONS``.

    Returns the number of rows deleted.
    """
    keep_ids = list(
        application.subject_plan_versions.order_by("-version_number").values_list(
            "id", flat=True
        )[:MAX_SUBJECT_PLAN_VERSIONS]
    )
    stale = application.subject_plan_versions
    if keep_ids:
        stale = stale.exclude(id__in=keep_ids)
    deleted, _ = stale.delete()
    return deleted


def _scalar_changed(old, new) -> bool:
    if old is None and new in (None, ""):
        return False
    if new is None and old in (None, ""):
        return False
    if isinstance(old, Decimal) or isinstance(new, Decimal):
        if old is None or new is None:
            return True
        return Decimal(str(old)) != Decimal(str(new))
    return old != new


def subject_plan_mapping_changed(instance, validated_data) -> bool:
    """True when mapping fields in ``validated_data`` differ from ``instance``."""
    for field in SUBJECT_PLAN_MAPPING_FIELDS:
        if field not in validated_data:
            continue
        new = validated_data[field]
        if field == "host_subject":
            new_id = getattr(new, "pk", new)
            if instance.host_subject_id != new_id:
                return True
            continue
        if _scalar_changed(getattr(instance, field), new):
            return True
    return False


def snapshot_subject_plan(
    application,
    user=None,
    *,
    trigger=ApplicationSubjectPlanVersion.Trigger.MAPPING_CHANGED,
):
    """Persist the current live set if it differs from the latest historic row.

    Skips an empty first snapshot (no prior version and no live rows).
    When a 4th distinct historic version would be stored, the oldest is
    deleted so at most ``MAX_SUBJECT_PLAN_VERSIONS`` remain.

    Returns the created ``ApplicationSubjectPlanVersion``, or ``None`` if
    no new row was written.
    """
    payload = build_subject_plan_payload(application)
    latest = application.subject_plan_versions.order_by("-version_number").first()
    if latest is not None and latest.payload == payload:
        return None
    if not payload and latest is None:
        return None

    created_by = user if getattr(user, "is_authenticated", False) else None
    next_number = (latest.version_number + 1) if latest is not None else 1
    with transaction.atomic():
        version = ApplicationSubjectPlanVersion.objects.create(
            application=application,
            version_number=next_number,
            created_by=created_by,
            trigger=trigger,
            payload=payload,
        )
        prune_subject_plan_versions(application)
    return version
