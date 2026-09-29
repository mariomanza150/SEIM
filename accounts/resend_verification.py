"""Per-email cooldown for verification email resends."""

from __future__ import annotations

import time

from django.core.cache import cache

RESEND_VERIFICATION_COOLDOWN_SECONDS = 300
_CACHE_KEY_PREFIX = "accounts:resend_verification:"


def normalize_resend_email(email: str) -> str:
    return (email or "").strip().lower()


def resend_verification_cache_key(email: str) -> str:
    return f"{_CACHE_KEY_PREFIX}{normalize_resend_email(email)}"


def check_resend_verification_allowed(email: str) -> tuple[bool, int]:
    """Return (allowed, retry_after_seconds).

    retry_after_seconds is 0 when allowed. Stores an absolute expiry timestamp
    in the cache value so backends without ``cache.ttl`` (e.g. LocMem) still
    report accurate Retry-After.
    """
    key = resend_verification_cache_key(email)
    expires_at = cache.get(key)
    if expires_at is None:
        return True, 0

    try:
        remaining = int(float(expires_at) - time.time())
    except (TypeError, ValueError):
        remaining = RESEND_VERIFICATION_COOLDOWN_SECONDS

    if remaining <= 0:
        cache.delete(key)
        return True, 0
    return False, remaining


def mark_resend_verification_sent(email: str) -> None:
    """Start the cooldown after a verification email was queued/sent."""
    expires_at = time.time() + RESEND_VERIFICATION_COOLDOWN_SECONDS
    cache.set(
        resend_verification_cache_key(email),
        expires_at,
        timeout=RESEND_VERIFICATION_COOLDOWN_SECONDS,
    )
