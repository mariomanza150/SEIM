"""Resolve whether a viewer may see application-document version history."""

from __future__ import annotations

from core.models import InstitutionFeatureSettings
from documents.models import DocumentType


def _viewer_role_keys(user) -> list[str]:
    """Return role keys to check (most privileged first for OR visibility)."""
    keys: list[str] = []
    if not user or not getattr(user, "is_authenticated", False):
        return keys
    has_role = getattr(user, "has_role", None)
    if getattr(user, "is_superuser", False) or (
        callable(has_role) and has_role("admin")
    ):
        keys.append("admin")
    if callable(has_role) and has_role("coordinator"):
        keys.append("coordinator")
    if callable(has_role) and has_role("student"):
        keys.append("student")
    # Staff without explicit roles: treat as admin for history visibility.
    if not keys and (
        getattr(user, "is_staff", False) or getattr(user, "is_superuser", False)
    ):
        keys.append("admin")
    return keys


def _institution_role_flag(settings_obj: InstitutionFeatureSettings, role: str) -> bool:
    if role == "admin":
        return bool(settings_obj.document_version_history_admin)
    if role == "coordinator":
        return bool(settings_obj.document_version_history_coordinator)
    if role == "student":
        return bool(settings_obj.document_version_history_student)
    return False


def _type_role_flag(document_type: DocumentType | None, role: str):
    if document_type is None:
        return None
    if role == "admin":
        return document_type.version_history_admin
    if role == "coordinator":
        return document_type.version_history_coordinator
    if role == "student":
        return document_type.version_history_student
    return None


def can_view_document_version_history(user, document_type: DocumentType | None) -> bool:
    """
    Institution master switch + per-type visibility + role flags.

    visible = institution.enabled
      AND (type.visibility != hidden)
      AND role_flag
    role_flag =
      if type.visibility == custom and type.version_history_<role> is not null:
        type.version_history_<role>
      else:
        institution.document_version_history_<role>
    """
    settings_obj = InstitutionFeatureSettings.get_solo()
    if not settings_obj.document_version_history_enabled:
        return False

    if document_type is not None:
        mode = document_type.version_history_visibility or DocumentType.VersionHistoryVisibility.INHERIT
        if mode == DocumentType.VersionHistoryVisibility.HIDDEN:
            return False
    else:
        mode = DocumentType.VersionHistoryVisibility.INHERIT

    roles = _viewer_role_keys(user)
    if not roles:
        return False

    for role in roles:
        if (
            mode == DocumentType.VersionHistoryVisibility.CUSTOM
            and document_type is not None
        ):
            override = _type_role_flag(document_type, role)
            if override is not None:
                if override:
                    return True
                continue
        if _institution_role_flag(settings_obj, role):
            return True
    return False
