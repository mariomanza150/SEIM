"""Detect and strip SEIM email priority markers."""

from __future__ import annotations

import re

PRIORITY_HEADER = "X-SEIM-Email-Priority"
PRIORITY_HIGH = "high"
PRIORITY_NORMAL = "normal"

# Fallback subjects for Django built-in / legacy auth mail when the explicit
# header is absent. Matching is case-insensitive on the subject string.
_HIGH_PRIORITY_SUBJECT_RE = re.compile(
    r"(password\s*reset|reset\s*your\s*password|email\s*verif|"
    r"verify\s*(your\s*)?email|account\s*lock|confirm\s*(your\s*)?email)",
    re.IGNORECASE,
)


def normalize_priority(value: str | None) -> str:
    if value and str(value).strip().lower() == PRIORITY_HIGH:
        return PRIORITY_HIGH
    return PRIORITY_NORMAL


def detect_priority(message) -> str:
    """Return ``high`` or ``normal`` for a Django email message."""
    extra = getattr(message, "extra_headers", None) or {}
    # Django stores custom headers on EmailMessage.extra_headers; some callers
    # also set them via message[<header>].
    header_val = None
    if isinstance(extra, dict):
        for key, val in extra.items():
            if str(key).lower() == PRIORITY_HEADER.lower():
                header_val = val
                break
    if normalize_priority(header_val) == PRIORITY_HIGH:
        return PRIORITY_HIGH

    subject = str(getattr(message, "subject", "") or "")
    if _HIGH_PRIORITY_SUBJECT_RE.search(subject):
        return PRIORITY_HIGH
    return PRIORITY_NORMAL


def strip_priority_header(message) -> str:
    """Remove ``X-SEIM-Email-Priority`` before handing off to delivery backend.

    Returns the detected priority (after reading the header).
    """
    priority = detect_priority(message)
    extra = getattr(message, "extra_headers", None)
    if isinstance(extra, dict):
        to_remove = [
            key
            for key in list(extra.keys())
            if str(key).lower() == PRIORITY_HEADER.lower()
        ]
        for key in to_remove:
            extra.pop(key, None)
    return priority
