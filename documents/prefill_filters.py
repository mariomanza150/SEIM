"""Active filter helpers for DocumentType.prefill_students auto-inclusion.

Staff can persist domain / unidad / school filters on a document type. While
those filters are set, matching students are added to the prefill allow-list
automatically (on create or attribute change). Manual additions stay; manual
removals are tracked as exclusions so they are not re-added until filters
change or the student is added again.
"""

from __future__ import annotations

import logging
from typing import Any

from django.contrib.auth import get_user_model
from django.db.models import QuerySet

from .models import DocumentType

logger = logging.getLogger(__name__)
User = get_user_model()


def normalize_email_domain(raw: str | None) -> str:
    """Exact domain after ``@`` (no subdomain expansion); lowercase, no leading @."""
    domain = str(raw or "").strip().lower().lstrip("@")
    if "@" in domain:
        domain = domain.rsplit("@", 1)[-1].strip()
    return domain


def parse_prefill_filter_params(data: Any) -> dict:
    """Parse optional domain / unidad / school filters (AND). Empty = all students."""
    if hasattr(data, "dict"):
        data = data.dict()
    elif not isinstance(data, dict):
        data = {}
    domain = normalize_email_domain(data.get("domain") or data.get("email_domain"))
    unidad_id = data.get("unidad_id") or data.get("unidad") or None
    school_id = data.get("school_id") or data.get("school") or None
    if unidad_id in ("", None):
        unidad_id = None
    else:
        unidad_id = str(unidad_id)
    if school_id in ("", None):
        school_id = None
    else:
        school_id = str(school_id)
    return {
        "domain": domain,
        "unidad_id": unidad_id,
        "school_id": school_id,
    }


def normalize_stored_filters(filters: dict | None) -> dict | None:
    """Return a canonical filter dict, or None when auto-inclusion should be off."""
    if filters is None:
        return None
    return parse_prefill_filter_params(filters)


def has_active_filters(doc_type: DocumentType) -> bool:
    return getattr(doc_type, "prefill_active_filters", None) is not None


def prefill_filter_queryset(filters: dict) -> QuerySet:
    """Active student-role users matching optional domain/unidad/school (AND).

    Domain match is case-insensitive on the exact host after ``@`` only
    (``example.edu`` matches ``a@example.edu``, not ``a@mail.example.edu``).
    """
    qs = (
        User.objects.filter(roles__name="student", is_active=True)
        .select_related("profile", "profile__unidad", "profile__school")
        .distinct()
        .order_by("last_name", "first_name", "username")
    )
    domain = filters.get("domain") or ""
    if domain:
        qs = qs.filter(email__iendswith=f"@{domain}")
    unidad_id = filters.get("unidad_id")
    if unidad_id:
        qs = qs.filter(profile__unidad_id=unidad_id)
    school_id = filters.get("school_id")
    if school_id:
        qs = qs.filter(profile__school_id=school_id)
    return qs


def user_matches_prefill_filters(user, filters: dict) -> bool:
    """Return True when an active student matches the given filters."""
    if not getattr(user, "is_active", False):
        return False
    has_student = False
    if hasattr(user, "roles"):
        has_student = user.roles.filter(name="student").exists()
    if not has_student:
        return False
    return prefill_filter_queryset(filters).filter(pk=user.pk).exists()


def bulk_add_prefill_students(doc_type: DocumentType, student_ids) -> int:
    """Idempotent M2M add in chunks; returns number newly added."""
    ids = list(student_ids)
    if not ids:
        return 0
    existing = set(
        doc_type.prefill_students.filter(pk__in=ids).values_list("id", flat=True)
    )
    to_add = [pk for pk in ids if pk not in existing]
    chunk_size = 500
    for i in range(0, len(to_add), chunk_size):
        doc_type.prefill_students.add(*to_add[i : i + chunk_size])
    return len(to_add)


def eligible_ids_for_active_filters(doc_type: DocumentType, filters: dict) -> list:
    """Matched student ids minus current list and manual exclusions."""
    matched_qs = prefill_filter_queryset(filters)
    listed_ids = set(doc_type.prefill_students.values_list("id", flat=True))
    excluded_ids = set(doc_type.prefill_filter_exclusions.values_list("id", flat=True))
    skip = listed_ids | excluded_ids
    if not skip:
        return list(matched_qs.values_list("id", flat=True))
    return list(matched_qs.exclude(pk__in=skip).values_list("id", flat=True))


def sync_prefill_students_for_filters(doc_type: DocumentType, filters: dict) -> int:
    """Add currently matching students (respecting exclusions). Never removes."""
    return bulk_add_prefill_students(
        doc_type, eligible_ids_for_active_filters(doc_type, filters)
    )


def set_prefill_active_filters(
    doc_type: DocumentType,
    filters: dict | None,
    *,
    sync: bool = True,
    clear_exclusions_on_change: bool = True,
) -> dict:
    """Persist active filters and optionally sync the allow-list.

    Returns ``{"filter": dict, "added": int, "matched": int, "already_listed": int}``.
    """
    normalized = normalize_stored_filters(filters)
    if normalized is None:
        raise ValueError("filters must be a mapping when activating")

    previous = doc_type.prefill_active_filters
    filters_changed = previous != normalized
    doc_type.prefill_active_filters = normalized
    doc_type.save(update_fields=["prefill_active_filters"])

    if clear_exclusions_on_change and (filters_changed or previous is None):
        doc_type.prefill_filter_exclusions.clear()

    matched_ids = set(prefill_filter_queryset(normalized).values_list("id", flat=True))
    matched = len(matched_ids)
    listed_before = set(doc_type.prefill_students.values_list("id", flat=True))
    already_listed = len(listed_before & matched_ids)
    added = 0
    if sync:
        added = sync_prefill_students_for_filters(doc_type, normalized)

    return {
        "filter": normalized,
        "matched": matched,
        "added": added,
        "already_listed": already_listed,
    }


def clear_prefill_active_filters(doc_type: DocumentType) -> None:
    """Stop auto-inclusion without removing already-listed students."""
    doc_type.prefill_active_filters = None
    doc_type.save(update_fields=["prefill_active_filters"])
    doc_type.prefill_filter_exclusions.clear()


def remember_prefill_exclusion(doc_type: DocumentType, user) -> None:
    """Record a manual removal so active filters do not re-add the student."""
    if not has_active_filters(doc_type):
        return
    doc_type.prefill_filter_exclusions.add(user)


def forget_prefill_exclusion(doc_type: DocumentType, user) -> None:
    """Clear exclusion when staff manually re-adds a student."""
    if not has_active_filters(doc_type):
        return
    doc_type.prefill_filter_exclusions.remove(user)


def serialize_active_filters(doc_type: DocumentType) -> dict:
    """API payload for the active-filters indicator and editor."""
    filters = doc_type.prefill_active_filters
    active = filters is not None
    normalized = normalize_stored_filters(filters) if active else None
    labels = {"domain": "", "unidad": "", "school": ""}
    if normalized:
        labels["domain"] = normalized.get("domain") or ""
        unidad_id = normalized.get("unidad_id")
        school_id = normalized.get("school_id")
        if unidad_id:
            from accounts.models import Unidad

            labels["unidad"] = (
                Unidad.objects.filter(pk=unidad_id)
                .values_list("name", flat=True)
                .first()
                or ""
            )
        if school_id:
            from accounts.models import SchoolFaculty

            labels["school"] = (
                SchoolFaculty.objects.filter(pk=school_id)
                .values_list("name", flat=True)
                .first()
                or ""
            )
    return {
        "active": active,
        "filter": normalized,
        "labels": labels,
    }


def apply_prefill_active_filters_for_user(user_id) -> int:
    """Idempotently add ``user_id`` to every matching document type with active filters.

    Returns the number of document types the user was newly added to.
    """
    if not DocumentType.objects.filter(prefill_active_filters__isnull=False).exists():
        return 0

    try:
        user = (
            User.objects.filter(pk=user_id)
            .select_related("profile", "profile__unidad", "profile__school")
            .prefetch_related("roles")
            .get()
        )
    except User.DoesNotExist:
        return 0

    if not user.is_active or not user.roles.filter(name="student").exists():
        return 0

    doc_types = DocumentType.objects.filter(
        prefill_active_filters__isnull=False
    ).prefetch_related("prefill_students", "prefill_filter_exclusions")
    added_types = 0
    for doc_type in doc_types.iterator(chunk_size=50):
        filters = normalize_stored_filters(doc_type.prefill_active_filters)
        if not filters:
            continue
        if doc_type.prefill_filter_exclusions.filter(pk=user.pk).exists():
            continue
        if doc_type.prefill_students.filter(pk=user.pk).exists():
            continue
        if not user_matches_prefill_filters(user, filters):
            continue
        doc_type.prefill_students.add(user)
        added_types += 1
        logger.info(
            "document_template_prefill_auto_include",
            extra={
                "action": "prefill_auto_include",
                "document_type_id": doc_type.pk,
                "document_type_slug": doc_type.slug or "",
                "student_id": user.pk,
                "filter": filters,
            },
        )
    return added_types
