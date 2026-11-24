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

# How many times to retry when another worker holds the shared lock.
_DEFAULT_MAX_LOCK_ATTEMPTS = 40


def get_min_interval_seconds() -> float:
    try:
        return float(getattr(settings, "EMAIL_MIN_INTERVAL_SECONDS", 0.6) or 0.0)
    except (TypeError, ValueError):
        return 0.6


class CacheUnavailable(Exception):
    """Raised when the shared cache backend cannot be used for pacing."""


def _cache_add(key: str, value, timeout: int) -> bool:
    """Atomic set-if-absent. Raises ``CacheUnavailable`` on backend errors."""
    try:
        return bool(cache.add(key, value, timeout))
    except Exception as exc:
        raise CacheUnavailable(str(exc)) from exc


def _cache_get(key: str):
    try:
        return cache.get(key)
    except Exception as exc:
        raise CacheUnavailable(str(exc)) from exc


def _cache_set(key: str, value, timeout: int) -> None:
    try:
        cache.set(key, value, timeout)
    except Exception as exc:
        raise CacheUnavailable(str(exc)) from exc


def _cache_delete(key: str) -> None:
    try:
        cache.delete(key)
    except Exception:
        logger.debug("Email pacer cache delete failed", exc_info=True)


def _wait_with_shared_cache(
    interval: float,
    *,
    sleep: Callable[[float], None],
    clock: Callable[[], float],
    max_lock_attempts: int,
) -> float:
    """Acquire the shared lock (retrying on contention) and pace with wall clock."""
    slept = 0.0
    lock_timeout = max(int(interval * 4) + 1, 2)
    # Brief pause while another worker holds the lock (still cross-process safe).
    contention_delay = min(max(interval / 5, 0.01), 0.1)

    for _ in range(max_lock_attempts):
        got_lock = _cache_add(CACHE_LOCK_KEY, "1", lock_timeout)
        if not got_lock:
            sleep(contention_delay)
            slept += contention_delay
            continue

        try:
            now = clock()
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
                slept += delay
                now = clock()
            _cache_set(
                CACHE_NEXT_KEY,
                now + interval,
                lock_timeout + int(interval) + 1,
            )
            return slept
        finally:
            _cache_delete(CACHE_LOCK_KEY)

    # Exhausted contention retries — wait a full interval then take the slot.
    sleep(interval)
    slept += interval
    now = clock()
    got_lock = _cache_add(CACHE_LOCK_KEY, "1", lock_timeout)
    if got_lock:
        try:
            _cache_set(
                CACHE_NEXT_KEY,
                now + interval,
                lock_timeout + int(interval) + 1,
            )
        finally:
            _cache_delete(CACHE_LOCK_KEY)
    return slept


def _wait_with_local_lock(
    interval: float,
    *,
    sleep: Callable[[float], None],
    clock: Callable[[], float],
) -> float:
    """In-process fallback when the shared cache backend is unavailable."""
    global _LOCAL_NEXT_ALLOWED
    slept = 0.0
    with _LOCAL_LOCK:
        now = clock()
        if _LOCAL_NEXT_ALLOWED > now:
            delay = _LOCAL_NEXT_ALLOWED - now
            sleep(delay)
            slept = delay
            now = clock()
        _LOCAL_NEXT_ALLOWED = now + interval
        return slept


def wait_for_send_slot(
    *,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], float] = time.time,
    max_lock_attempts: int = _DEFAULT_MAX_LOCK_ATTEMPTS,
) -> float:
    """Block until the next send is allowed by ``EMAIL_MIN_INTERVAL_SECONDS``.

    Uses wall-clock ``time.time()`` in the shared Redis/cache key so pacing works
    across separate Docker containers (monotonic clocks are not comparable).
    Contended locks retry in a bounded loop; the in-process lock is used only when
    the cache backend raises / is unavailable.

    Returns the seconds slept (for tests/metrics).
    """
    interval = get_min_interval_seconds()
    if interval <= 0:
        return 0.0

    try:
        return _wait_with_shared_cache(
            interval,
            sleep=sleep,
            clock=clock,
            max_lock_attempts=max_lock_attempts,
        )
    except CacheUnavailable:
        logger.debug(
            "Email pacer shared cache unavailable; falling back to in-process lock",
            exc_info=True,
        )
        return _wait_with_local_lock(interval, sleep=sleep, clock=clock)
