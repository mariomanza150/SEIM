"""Sanitize email outbox / ops error strings (no raw addresses)."""

from __future__ import annotations

import re

_EMAIL_RE = re.compile(
    r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}",
    re.UNICODE,
)
_MAX_LAST_ERROR = 500


def sanitize_last_error(exc: BaseException | str, *, prefix: str = "") -> str:
    """Build a short, address-free last_error for DeferredEmail rows."""
    if isinstance(exc, BaseException):
        name = exc.__class__.__name__
        raw = str(exc) or ""
        text = f"{name}:{raw}" if raw else name
    else:
        text = str(exc)
    text = _EMAIL_RE.sub("[redacted]", text)
    # Collapse whitespace / control chars for log-friendly storage.
    text = " ".join(text.split())
    if prefix:
        text = f"{prefix}:{text}"
    return text[:_MAX_LAST_ERROR]
