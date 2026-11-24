"""Cross-process email send pacing (Redis with in-process fallback)."""

from __future__ import annotations

import logging
import threading
import time
from collections.abc import Callable

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

_LOCAL_LOCK = threading.Lock()
_LOCAL_NEXT_ALLOWED = 0.0

CACHE_NEXT_KEY = "seim:email:pacer:next_allowed"
CACHE_LOCK_KEY = "seim:email:pacer:lock"


def get_min_interval_seconds() -> float:
    try:
        return float(getattr(settings, "EMAIL_MIN_INTERVAL_SECONDS", 0.6) or 0.0)
    except (TypeError, ValueError):
        return 0.6


def _try_cache_add(key: str, value, timeout: int) -> bool:
    """Atomic set-if-absent via Django cache ``add``."""
    try:
        return bool(cache.add(key, value, timeout))
    except Exception:
        logger.debug("Email pacer cache add failed; falling back to local lock")
        return False


def _cache_get(key: str):
    try:
        return cache.get(key)
    except Exception:
        return None


def _cache_set(key: str, value, timeout: int) -> None:
    try:
        cache.set(key, value, timeout)
    except Exception:
        logger.debug("Email pacer cache set failed", exc_info=True)


def wait_for_send_slot(
    *,
    sleep: Callable[[float], None] = time.sleep,
    monotonic: Callable[[], float] = time.monotonic,
) -> float:
    """Block until the next send is allowed by ``EMAIL_MIN_INTERVAL_SECONDS``.

    Uses a Redis/cache lock + next-allowed timestamp when available, otherwise
    an in-process lock. Returns the seconds slept (for tests/metrics).
    """
    interval = get_min_interval_seconds()
    if interval <= 0:
        return 0.0

    slept = 0.0
    # Prefer shared cache when ``add`` works (Redis / LocMem); else local lock.
    lock_timeout = max(int(interval * 4) + 1, 2)
    got_cache_lock = _try_cache_add(CACHE_LOCK_KEY, "1", lock_timeout)

    if got_cache_lock:
        try:
            now = monotonic()
            next_allowed = _cache_get(CACHE_NEXT_KEY)
            try:
                next_allowed_f = (
                    float(next_allowed) if next_allowed is not None else 0.0
                )
            except (TypeError, ValueError):
                next_allowed_f = 0.0
            if next_allowed_f > now:
                delay = next_allowed_f - now
                sleep(delay)
                slept = delay
                now = monotonic()
            _cache_set(CACHE_NEXT_KEY, now + interval, lock_timeout + int(interval) + 1)
            return slept
        finally:
            try:
                cache.delete(CACHE_LOCK_KEY)
            except Exception:
                pass

    global _LOCAL_NEXT_ALLOWED
    with _LOCAL_LOCK:
        now = monotonic()
        if _LOCAL_NEXT_ALLOWED > now:
            delay = _LOCAL_NEXT_ALLOWED - now
            sleep(delay)
            slept = delay
            now = monotonic()
        _LOCAL_NEXT_ALLOWED = now + interval
        return slept
