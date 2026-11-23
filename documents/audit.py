"""Structured audit logging for document type and upload actions.

Uses logger ``seim.audit``. Log ids and actions only — never file contents,
tokens, passwords, or full personal data.
"""

from __future__ import annotations

import logging
from typing import Any

audit_logger = logging.getLogger("seim.audit")


def actor_role(user) -> str:
    """Best-effort primary role label for audit lines."""
    if user is None or not getattr(user, "is_authenticated", False):
        return "anonymous"
    has_role = getattr(user, "has_role", None)
    if callable(has_role):
        for role in ("admin", "coordinator", "student", "partner"):
            if has_role(role):
                return role
    if getattr(user, "is_superuser", False) or getattr(user, "is_staff", False):
        return "staff"
    return "user"


def audit_info(action: str, *, actor=None, **fields: Any) -> None:
    """Emit an info-level audit event."""
    extra = _base_extra(action, actor=actor, **fields)
    audit_logger.info(action, extra=extra)


def audit_warning(action: str, *, actor=None, **fields: Any) -> None:
    """Emit a warning-level audit event (e.g. rejected uploads)."""
    extra = _base_extra(action, actor=actor, **fields)
    audit_logger.warning(action, extra=extra)


def _base_extra(action: str, *, actor=None, **fields: Any) -> dict[str, Any]:
    extra: dict[str, Any] = {"action": action}
    if actor is not None:
        extra["actor_id"] = getattr(actor, "pk", None)
        extra["actor_role"] = actor_role(actor)
    for key, value in fields.items():
        if value is None:
            continue
        extra[key] = value
    return extra
