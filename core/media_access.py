"""Classify MEDIA paths and enforce object-level access for protected uploads.

Public CMS/Wagtail image prefixes remain world-readable. Student documents,
agreement repository files, document templates, and QA attachments require
authentication plus the same object-level rules used by the documents API.
"""

from __future__ import annotations

import posixpath
from dataclasses import dataclass
from enum import Enum

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, AnonymousUser

UserLike = AbstractBaseUser | AnonymousUser


class MediaAccessKind(str, Enum):
    PUBLIC = "public"
    PROTECTED = "protected"
    DENY = "deny"


@dataclass(frozen=True)
class MediaAccessDecision:
    """Result of a media ACL check."""

    allowed: bool
    status: int  # HTTP status when not allowed (401/403/404)
    kind: MediaAccessKind
    reason: str = ""


DEFAULT_PUBLIC_MEDIA_PREFIXES: tuple[str, ...] = (
    "images/",
    "original_images/",
)

DEFAULT_PROTECTED_MEDIA_PREFIXES: tuple[str, ...] = (
    "documents/",
    "agreement_repository/",
    "document_templates/",
    "qa_issues/",
)


def public_media_prefixes() -> tuple[str, ...]:
    configured = getattr(settings, "MEDIA_PUBLIC_PREFIXES", None)
    if configured is None:
        return DEFAULT_PUBLIC_MEDIA_PREFIXES
    return tuple(configured)


def protected_media_prefixes() -> tuple[str, ...]:
    configured = getattr(settings, "MEDIA_PROTECTED_PREFIXES", None)
    if configured is None:
        return DEFAULT_PROTECTED_MEDIA_PREFIXES
    return tuple(configured)


def normalize_media_path(path: str) -> str | None:
    """Return a safe relative media path, or None if the path is invalid."""
    if path is None:
        return None
    raw = str(path).replace("\\", "/").lstrip("/")
    if not raw or raw.endswith("/"):
        return None
    # Collapse . / .. without resolving outside the media root.
    cleaned = posixpath.normpath(raw)
    if (
        cleaned in ("", ".", "..")
        or cleaned.startswith("../")
        or cleaned.startswith("/")
    ):
        return None
    if "\x00" in cleaned:
        return None
    return cleaned


def classify_media_path(path: str) -> MediaAccessKind:
    """Classify a normalized media-relative path."""
    normalized = normalize_media_path(path)
    if not normalized:
        return MediaAccessKind.DENY

    for prefix in public_media_prefixes():
        if normalized == prefix.rstrip("/") or normalized.startswith(prefix):
            return MediaAccessKind.PUBLIC

    for prefix in protected_media_prefixes():
        if normalized == prefix.rstrip("/") or normalized.startswith(prefix):
            return MediaAccessKind.PROTECTED

    # Unknown prefixes: treat as protected (fail closed).
    return MediaAccessKind.PROTECTED


def _is_staff_or_admin(user: UserLike) -> bool:
    if not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
        return True
    has_role = getattr(user, "has_role", None)
    if callable(has_role) and (has_role("admin") or has_role("coordinator")):
        return True
    return False


def _user_can_access_application_document(user: UserLike, relative_path: str) -> bool:
    from documents.models import Document
    from documents.services import DocumentService

    document = (
        Document.objects.select_related("application", "uploaded_by")
        .filter(file=relative_path)
        .first()
    )
    if document is None:
        return False
    return DocumentService.user_can_access_document(user, document)


def _user_can_access_agreement_document(user: UserLike, relative_path: str) -> bool:
    from documents.models import ExchangeAgreementDocument

    if not _is_staff_or_admin(user):
        return False
    return ExchangeAgreementDocument.objects.filter(file=relative_path).exists()


def _user_can_access_document_template(user: UserLike, relative_path: str) -> bool:
    from documents.models import DocumentType

    if not getattr(user, "is_authenticated", False):
        return False
    return DocumentType.objects.filter(template_file=relative_path).exists()


def _user_can_access_qa_attachment(user: UserLike, relative_path: str) -> bool:
    from qa.models import IssueAttachment

    if not getattr(user, "is_authenticated", False):
        return False
    attachment = (
        IssueAttachment.objects.select_related("issue", "uploaded_by")
        .filter(file=relative_path)
        .first()
    )
    if attachment is None:
        return False
    if _is_staff_or_admin(user):
        return True
    if attachment.uploaded_by_id and attachment.uploaded_by_id == getattr(
        user, "id", None
    ):
        return True
    issue = attachment.issue
    reporter_id = getattr(issue, "reporter_id", None) or getattr(
        issue, "created_by_id", None
    )
    return reporter_id is not None and reporter_id == getattr(user, "id", None)


def user_may_access_media(user: UserLike, path: str) -> MediaAccessDecision:
    """Decide whether ``user`` may fetch ``path`` under MEDIA_ROOT."""
    normalized = normalize_media_path(path)
    if not normalized:
        return MediaAccessDecision(
            allowed=False, status=404, kind=MediaAccessKind.DENY, reason="invalid_path"
        )

    kind = classify_media_path(normalized)
    if kind == MediaAccessKind.PUBLIC:
        return MediaAccessDecision(
            allowed=True,
            status=200,
            kind=MediaAccessKind.PUBLIC,
            reason="public_prefix",
        )

    if not getattr(user, "is_authenticated", False):
        return MediaAccessDecision(
            allowed=False,
            status=401,
            kind=MediaAccessKind.PROTECTED,
            reason="authentication_required",
        )

    if normalized.startswith("documents/"):
        if _user_can_access_application_document(user, normalized):
            return MediaAccessDecision(
                allowed=True, status=200, kind=kind, reason="document_acl"
            )
        return MediaAccessDecision(
            allowed=False, status=404, kind=kind, reason="document_denied"
        )

    if normalized.startswith("agreement_repository/"):
        if _user_can_access_agreement_document(user, normalized):
            return MediaAccessDecision(
                allowed=True, status=200, kind=kind, reason="agreement_acl"
            )
        return MediaAccessDecision(
            allowed=False, status=404, kind=kind, reason="agreement_denied"
        )

    if normalized.startswith("document_templates/"):
        if _user_can_access_document_template(user, normalized):
            return MediaAccessDecision(
                allowed=True, status=200, kind=kind, reason="template_acl"
            )
        return MediaAccessDecision(
            allowed=False, status=404, kind=kind, reason="template_denied"
        )

    if normalized.startswith("qa_issues/"):
        if _user_can_access_qa_attachment(user, normalized):
            return MediaAccessDecision(
                allowed=True, status=200, kind=kind, reason="qa_acl"
            )
        return MediaAccessDecision(
            allowed=False, status=404, kind=kind, reason="qa_denied"
        )

    # Unknown protected path: staff/admin only, and only if the file exists on disk
    # (existence checked by the view). Authenticated non-staff get 404.
    if _is_staff_or_admin(user):
        return MediaAccessDecision(
            allowed=True, status=200, kind=kind, reason="staff_fallback"
        )
    return MediaAccessDecision(
        allowed=False, status=404, kind=kind, reason="unknown_protected"
    )
