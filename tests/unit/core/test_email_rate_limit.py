"""Unit tests for rate-limited email backend, quota, outbox, and drain task."""

from __future__ import annotations

import smtplib
from datetime import timedelta
from io import StringIO
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest
from django.core.cache import cache
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.core.management import call_command
from django.test import override_settings
from django.utils import timezone

from core.email.backends import RateLimitedEmailBackend, is_transient_provider_error
from core.email.errors import sanitize_last_error
from core.email.pacing import (
    CACHE_LOCK_KEY,
    CACHE_NEXT_KEY,
    CacheUnavailable,
    wait_for_send_slot,
)
from core.email.priority import PRIORITY_HEADER, detect_priority, strip_priority_header
from core.email.quota import (
    current_quota_date,
    next_day_boundary,
    next_month_boundary,
    release_slot,
    remaining_headroom,
    try_reserve_slot,
)
from core.models import DeferredEmail, EmailDailyUsage
from core.tasks import drain_deferred_emails, reclaim_stale_sending

LOCMEM_CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "email-rate-limit-tests",
    }
}

RATE_LIMIT_SETTINGS = {
    "EMAIL_BACKEND": "core.email.backends.RateLimitedEmailBackend",
    "EMAIL_DELIVERY_BACKEND": "django.core.mail.backends.locmem.EmailBackend",
    "EMAIL_DAILY_LIMIT": 10,
    "EMAIL_PRIORITY_RESERVE": 3,
    "EMAIL_MONTHLY_LIMIT": 100,
    "EMAIL_MIN_INTERVAL_SECONDS": 0,
    "EMAIL_QUOTA_RESET_TIMEZONE": "UTC",
    "EMAIL_DEFERRED_MAX_RETRIES": 3,
    "CACHES": LOCMEM_CACHES,
}


@pytest.fixture(autouse=True)
def _clean_email_state(db):
    cache.clear()
    EmailDailyUsage.objects.all().delete()
    DeferredEmail.objects.all().delete()
    yield
    cache.clear()
    EmailDailyUsage.objects.all().delete()
    DeferredEmail.objects.all().delete()


def _msg(subject="Hello", body="Body", to=None, priority=None):
    headers = {}
    if priority:
        headers[PRIORITY_HEADER] = priority
    return EmailMessage(
        subject=subject,
        body=body,
        from_email="noreply@example.com",
        to=to or ["student@example.edu"],
        headers=headers,
    )


@override_settings(**RATE_LIMIT_SETTINGS)
def test_daily_limit_persists_across_backend_instances():
    backend_a = RateLimitedEmailBackend()
    for i in range(7):  # normal cap = 10 - 3 = 7
        assert backend_a.send_messages([_msg(subject=f"n{i}")]) == 1
    assert EmailDailyUsage.objects.get().sent_count == 7

    backend_b = RateLimitedEmailBackend()
    assert backend_b.send_messages([_msg(subject="overflow")]) == 1
    assert (
        DeferredEmail.objects.filter(status=DeferredEmail.STATUS_PENDING).count() == 1
    )
    assert EmailDailyUsage.objects.get().sent_count == 7


@override_settings(**RATE_LIMIT_SETTINGS)
def test_priority_reserve_headroom():
    backend = RateLimitedEmailBackend()
    for i in range(7):
        backend.send_messages([_msg(subject=f"n{i}")])

    # 8th normal is deferred
    backend.send_messages([_msg(subject="normal-overflow")])
    deferred_normal = DeferredEmail.objects.get(subject="normal-overflow")
    assert deferred_normal.priority == DeferredEmail.PRIORITY_NORMAL
    assert deferred_normal.status == DeferredEmail.STATUS_PENDING

    # High priority can still use reserve up to daily=10
    for i in range(3):
        assert backend.send_messages([_msg(subject=f"h{i}", priority="high")]) == 1
    assert EmailDailyUsage.objects.get().sent_count == 10

    # Next high is also deferred as high
    backend.send_messages([_msg(subject="high-overflow", priority="high")])
    deferred_high = DeferredEmail.objects.get(subject="high-overflow")
    assert deferred_high.priority == DeferredEmail.PRIORITY_HIGH


@override_settings(
    **{**RATE_LIMIT_SETTINGS, "EMAIL_MONTHLY_LIMIT": 5, "EMAIL_DAILY_LIMIT": 90}
)
def test_monthly_limit_schedules_next_month():
    backend = RateLimitedEmailBackend()
    for i in range(5):
        backend.send_messages([_msg(subject=f"m{i}")])
    backend.send_messages([_msg(subject="month-overflow")])
    row = DeferredEmail.objects.get(subject="month-overflow")
    expected = next_month_boundary()
    assert abs((row.scheduled_for - expected).total_seconds()) < 2


@override_settings(**RATE_LIMIT_SETTINGS)
def test_next_day_scheduled_for_utc_and_custom_tz():
    backend = RateLimitedEmailBackend()
    for i in range(7):
        backend.send_messages([_msg(subject=f"n{i}")])
    backend.send_messages([_msg(subject="day-overflow")])
    row = DeferredEmail.objects.get(subject="day-overflow")
    expected = next_day_boundary()
    assert row.scheduled_for.astimezone(ZoneInfo("UTC")).hour == 0
    assert row.scheduled_for.astimezone(ZoneInfo("UTC")).minute == 1
    assert abs((row.scheduled_for - expected).total_seconds()) < 2

    with override_settings(EMAIL_QUOTA_RESET_TIMEZONE="America/New_York"):
        boundary = next_day_boundary()
        assert boundary.tzinfo is not None
        local = boundary.astimezone(ZoneInfo("America/New_York"))
        assert local.hour == 0 and local.minute == 1


@override_settings(**RATE_LIMIT_SETTINGS)
def test_priority_header_stripped_before_delivery():
    captured = []

    class CapturingBackend:
        def __init__(self, *args, **kwargs):
            pass

        def send_messages(self, email_messages):
            for m in email_messages:
                captured.append(dict(m.extra_headers or {}))
            return len(email_messages)

    with patch(
        "core.email.backends.get_connection",
        return_value=CapturingBackend(),
    ):
        RateLimitedEmailBackend().send_messages([_msg(subject="auth", priority="high")])

    assert captured
    assert PRIORITY_HEADER not in captured[0]
    assert not any(str(k).lower() == PRIORITY_HEADER.lower() for k in captured[0])


@override_settings(**RATE_LIMIT_SETTINGS)
def test_detect_priority_subject_fallback():
    assert detect_priority(_msg(subject="Password Reset Request")) == "high"
    assert detect_priority(_msg(subject="Email Verification Required")) == "high"
    assert detect_priority(_msg(subject="Application update")) == "normal"


@override_settings(**RATE_LIMIT_SETTINGS)
def test_strip_priority_header_returns_priority():
    msg = _msg(priority="high")
    assert strip_priority_header(msg) == "high"
    assert PRIORITY_HEADER not in (msg.extra_headers or {})


@override_settings(**{**RATE_LIMIT_SETTINGS, "EMAIL_MIN_INTERVAL_SECONDS": 0.5})
def test_pacing_wall_clock_shared_and_contention_retry():
    """Shared pacing uses wall-clock time.time and retries on lock contention."""
    sleeps: list[float] = []
    clock = {"t": 1_700_000_000.0}
    add_calls = {"n": 0}

    def fake_clock():
        return clock["t"]

    def fake_sleep(seconds):
        sleeps.append(seconds)
        clock["t"] += seconds

    # First wait takes the lock and sets next_allowed = now + interval in shared cache.
    start = clock["t"]
    wait_for_send_slot(sleep=fake_sleep, clock=fake_clock, max_lock_attempts=5)
    assert cache.get(CACHE_NEXT_KEY) == pytest.approx(start + 0.5, abs=0.01)

    # Second wait should sleep ~0.5s based on wall-clock next_allowed.
    wait_for_send_slot(sleep=fake_sleep, clock=fake_clock, max_lock_attempts=5)
    assert any(s == pytest.approx(0.5, abs=0.01) for s in sleeps)

    # Contention: lock already held → retry loop sleeps briefly, then acquires.
    sleeps.clear()
    cache.set(CACHE_LOCK_KEY, "held", 5)
    real_add = cache.add

    def add_then_clear(key, value, timeout):
        add_calls["n"] += 1
        if key == CACHE_LOCK_KEY and add_calls["n"] == 1:
            # Simulate another worker releasing the lock after our first miss.
            cache.delete(CACHE_LOCK_KEY)
            return False
        return real_add(key, value, timeout)

    with patch("core.email.pacing.cache.add", side_effect=add_then_clear):
        wait_for_send_slot(sleep=fake_sleep, clock=fake_clock, max_lock_attempts=5)

    assert sleeps  # contended path slept at least once
    assert add_calls["n"] >= 2


@override_settings(**{**RATE_LIMIT_SETTINGS, "EMAIL_MIN_INTERVAL_SECONDS": 0.5})
def test_pacing_falls_back_only_when_cache_unavailable():
    sleeps: list[float] = []
    clock = {"t": 100.0}

    def fake_clock():
        return clock["t"]

    def fake_sleep(seconds):
        sleeps.append(seconds)
        clock["t"] += seconds

    with patch(
        "core.email.pacing._cache_add",
        side_effect=CacheUnavailable("redis down"),
    ):
        wait_for_send_slot(sleep=fake_sleep, clock=fake_clock)
        wait_for_send_slot(sleep=fake_sleep, clock=fake_clock)

    assert sleeps
    assert sleeps[0] == pytest.approx(0.5, abs=0.01)


def test_is_transient_provider_error():
    assert is_transient_provider_error(smtplib.SMTPResponseException(421, b"busy"))
    assert is_transient_provider_error(smtplib.SMTPResponseException(450, b"try later"))
    assert is_transient_provider_error(RuntimeError("HTTP 429 Too Many Requests"))
    assert not is_transient_provider_error(ValueError("bad recipient"))


def test_sanitize_last_error_redacts_addresses():
    text = sanitize_last_error(
        ValueError("failed for student@example.edu"), prefix="transient"
    )
    assert "example.edu" not in text
    assert "[redacted]" in text
    assert text.startswith("transient:")
    assert len(text) <= 500


@override_settings(**RATE_LIMIT_SETTINGS)
def test_transient_error_defers_and_refunds_quota():
    class FlakyBackend:
        def __init__(self, *args, **kwargs):
            pass

        def send_messages(self, email_messages):
            raise smtplib.SMTPResponseException(421, b"try again later")

    with patch("core.email.backends.get_connection", return_value=FlakyBackend()):
        handled = RateLimitedEmailBackend().send_messages([_msg(subject="flaky")])

    assert handled == 1
    assert EmailDailyUsage.objects.get().sent_count == 0
    assert DeferredEmail.objects.filter(subject="flaky").exists()


@override_settings(**RATE_LIMIT_SETTINGS)
def test_release_slot_uses_exact_reserved_usage_date():
    reserved = try_reserve_slot("normal")
    assert reserved.reserved is True
    assert reserved.usage_date == current_quota_date()
    assert EmailDailyUsage.objects.get(usage_date=reserved.usage_date).sent_count == 1

    # Refund the exact reserved day (not "today" after a midnight crossover).
    release_slot(reserved.usage_date)
    assert EmailDailyUsage.objects.get(usage_date=reserved.usage_date).sent_count == 0


@override_settings(**RATE_LIMIT_SETTINGS)
def test_drain_high_before_normal_clears_bodies_and_respects_limits():
    now = timezone.now()
    DeferredEmail.objects.create(
        priority=DeferredEmail.PRIORITY_NORMAL,
        status=DeferredEmail.STATUS_PENDING,
        subject="normal-first",
        body="secret-normal",
        html_body="<p>secret-normal</p>",
        attachments=[
            {"name": "a.txt", "mimetype": "text/plain", "content_base64": "YQ=="}
        ],
        from_email="noreply@example.com",
        to=["a@example.edu"],
        scheduled_for=now - timedelta(minutes=1),
    )
    DeferredEmail.objects.create(
        priority=DeferredEmail.PRIORITY_HIGH,
        status=DeferredEmail.STATUS_PENDING,
        subject="high-first",
        body="secret-high",
        html_body="<p>secret-high</p>",
        attachments=[],
        from_email="noreply@example.com",
        to=["b@example.edu"],
        scheduled_for=now - timedelta(minutes=1),
    )

    # Fill normal cap so only high (and remaining daily) can send; leave room for 1 high.
    EmailDailyUsage.objects.create(
        usage_date=current_quota_date(),
        sent_count=7,
    )

    result = drain_deferred_emails(batch_size=10)
    assert result["sent"] >= 1

    high = DeferredEmail.objects.get(subject="high-first")
    assert high.status == DeferredEmail.STATUS_SENT
    assert high.body == ""
    assert high.html_body == ""
    assert high.attachments == []
    assert high.sent_at is not None

    # Normal should be rescheduled or still pending because normal cap is exhausted.
    normal = DeferredEmail.objects.get(subject="normal-first")
    assert normal.status == DeferredEmail.STATUS_PENDING
    assert normal.body == "secret-normal"  # not cleared until sent


@override_settings(**RATE_LIMIT_SETTINGS)
def test_drain_retries_then_fails():
    now = timezone.now()
    row = DeferredEmail.objects.create(
        priority=DeferredEmail.PRIORITY_HIGH,
        status=DeferredEmail.STATUS_PENDING,
        subject="retry-me",
        body="x",
        from_email="noreply@example.com",
        to=["c@example.edu"],
        scheduled_for=now - timedelta(seconds=1),
        attempts=0,
    )

    class Always429:
        def __init__(self, *args, **kwargs):
            pass

        def send_messages(self, email_messages):
            raise RuntimeError("HTTP 429 rate limit for user@example.edu")

    with patch("django.core.mail.get_connection", return_value=Always429()):
        for _ in range(3):
            DeferredEmail.objects.filter(pk=row.pk).update(
                status=DeferredEmail.STATUS_PENDING,
                scheduled_for=timezone.now() - timedelta(seconds=1),
            )
            drain_deferred_emails(batch_size=5)

    row.refresh_from_db()
    assert row.status == DeferredEmail.STATUS_FAILED
    assert row.attempts >= 3
    assert "example.edu" not in row.last_error
    assert "[redacted]" in row.last_error


@override_settings(**RATE_LIMIT_SETTINGS)
def test_drain_idempotent_no_double_send():
    now = timezone.now()
    DeferredEmail.objects.create(
        priority=DeferredEmail.PRIORITY_HIGH,
        status=DeferredEmail.STATUS_PENDING,
        subject="once",
        body="body",
        from_email="noreply@example.com",
        to=["d@example.edu"],
        scheduled_for=now - timedelta(seconds=1),
    )
    first = drain_deferred_emails(batch_size=5)
    second = drain_deferred_emails(batch_size=5)
    assert first["sent"] == 1
    assert second["sent"] == 0
    assert DeferredEmail.objects.filter(status=DeferredEmail.STATUS_SENT).count() == 1


@override_settings(**RATE_LIMIT_SETTINGS)
def test_drain_reclaims_stale_sending_rows():
    now = timezone.now()
    stale = DeferredEmail.objects.create(
        priority=DeferredEmail.PRIORITY_HIGH,
        status=DeferredEmail.STATUS_SENDING,
        subject="stale-sending",
        body="secret",
        from_email="noreply@example.com",
        to=["stale@example.edu"],
        scheduled_for=now - timedelta(hours=1),
    )
    # Force updated_at into the past (auto_now would otherwise overwrite on save).
    DeferredEmail.objects.filter(pk=stale.pk).update(
        updated_at=now - timedelta(minutes=30)
    )

    reclaimed = reclaim_stale_sending(stale_minutes=15)
    assert reclaimed == 1
    stale.refresh_from_db()
    assert stale.status == DeferredEmail.STATUS_PENDING
    assert "reclaimed stale" in stale.last_error

    # Fresh sending row must not be reclaimed.
    fresh = DeferredEmail.objects.create(
        priority=DeferredEmail.PRIORITY_NORMAL,
        status=DeferredEmail.STATUS_SENDING,
        subject="fresh-sending",
        from_email="noreply@example.com",
        to=["fresh@example.edu"],
        scheduled_for=now,
    )
    assert reclaim_stale_sending(stale_minutes=15) == 0
    fresh.refresh_from_db()
    assert fresh.status == DeferredEmail.STATUS_SENDING

    # Full drain should reclaim then send the stale row.
    result = drain_deferred_emails(batch_size=5)
    assert result["reclaimed"] >= 0
    assert DeferredEmail.objects.get(subject="stale-sending").status == (
        DeferredEmail.STATUS_SENT
    )


@override_settings(**RATE_LIMIT_SETTINGS)
def test_email_quota_status_command():
    EmailDailyUsage.objects.create(usage_date=current_quota_date(), sent_count=4)
    DeferredEmail.objects.create(
        priority=DeferredEmail.PRIORITY_HIGH,
        status=DeferredEmail.STATUS_PENDING,
        subject="pending-high",
        scheduled_for=timezone.now() + timedelta(hours=1),
        to=["e@example.edu"],
    )
    out = StringIO()
    call_command("email_quota_status", stdout=out)
    text = out.getvalue()
    assert "Sent today: 4" in text
    assert "Pending deferred (high): 1" in text
    snap = remaining_headroom()
    assert snap["sent_today"] == 4
    assert snap["normal_remaining"] == 3  # cap 7 - 4


@override_settings(**RATE_LIMIT_SETTINGS)
def test_html_and_attachments_roundtrip_on_defer():
    msg = EmailMultiAlternatives(
        subject="html-mail",
        body="plain",
        from_email="noreply@example.com",
        to=["f@example.edu"],
    )
    msg.attach_alternative("<p>Hi</p>", "text/html")
    msg.attach("note.txt", b"hello", "text/plain")

    backend = RateLimitedEmailBackend()
    for i in range(7):
        backend.send_messages([_msg(subject=f"fill{i}")])
    backend.send_messages([msg])
    row = DeferredEmail.objects.get(subject="html-mail")
    assert row.html_body == "<p>Hi</p>"
    assert row.attachments and row.attachments[0]["name"] == "note.txt"
