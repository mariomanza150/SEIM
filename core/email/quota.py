"""Persistent email quota tracking and atomic slot reservation."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from django.conf import settings
from django.db import connection, transaction
from django.db.models import Sum
from django.utils import timezone

logger = logging.getLogger(__name__)

PRIORITY_HIGH = "high"
PRIORITY_NORMAL = "normal"


@dataclass(frozen=True)
class QuotaLimits:
    daily_limit: int
    priority_reserve: int
    monthly_limit: int
    timezone_name: str

    @property
    def normal_daily_cap(self) -> int | None:
        """Max normal-priority sends per day, or None when daily cap is disabled."""
        if self.daily_limit <= 0:
            return None
        reserve = min(max(self.priority_reserve, 0), self.daily_limit)
        return self.daily_limit - reserve

    @property
    def tz(self) -> ZoneInfo:
        return ZoneInfo(self.timezone_name or "UTC")


def get_quota_limits() -> QuotaLimits:
    return QuotaLimits(
        daily_limit=int(getattr(settings, "EMAIL_DAILY_LIMIT", 90) or 0),
        priority_reserve=int(getattr(settings, "EMAIL_PRIORITY_RESERVE", 15) or 0),
        monthly_limit=int(getattr(settings, "EMAIL_MONTHLY_LIMIT", 2850) or 0),
        timezone_name=str(
            getattr(settings, "EMAIL_QUOTA_RESET_TIMEZONE", "UTC") or "UTC"
        ),
    )


def quota_now(limits: QuotaLimits | None = None) -> datetime:
    limits = limits or get_quota_limits()
    return timezone.now().astimezone(limits.tz)


def quota_today(limits: QuotaLimits | None = None) -> date:
    return quota_now(limits).date()


# Alias used by tests/ops docs for the quota-timezone calendar date.
current_quota_date = quota_today


def month_bounds(day: date) -> tuple[date, date]:
    """Inclusive start and exclusive end dates for the calendar month of ``day``."""
    start = day.replace(day=1)
    if start.month == 12:
        end = date(start.year + 1, 1, 1)
    else:
        end = date(start.year, start.month + 1, 1)
    return start, end


def next_day_boundary(limits: QuotaLimits | None = None) -> datetime:
    """Next quota-day drain time: tomorrow 00:01 in the quota timezone."""
    limits = limits or get_quota_limits()
    now = quota_now(limits)
    tomorrow = now.date() + timedelta(days=1)
    local = datetime.combine(tomorrow, time(hour=0, minute=1), tzinfo=limits.tz)
    return local


def next_month_boundary(limits: QuotaLimits | None = None) -> datetime:
    """First of next month 00:01 in the quota timezone."""
    limits = limits or get_quota_limits()
    now = quota_now(limits)
    _, month_end = month_bounds(now.date())
    local = datetime.combine(month_end, time(hour=0, minute=1), tzinfo=limits.tz)
    return local


def _select_for_update(queryset, *, skip_locked: bool = False):
    """Apply select_for_update when the DB supports it (SQLite-safe)."""
    if not connection.features.has_select_for_update:
        return queryset
    kwargs: dict = {}
    if skip_locked and connection.features.has_select_for_update_skip_locked:
        kwargs["skip_locked"] = True
    return queryset.select_for_update(**kwargs)


@dataclass(frozen=True)
class ReservationResult:
    reserved: bool
    defer_reason: str | None = None  # "daily" | "monthly" | None
    sent_count: int = 0
    month_total: int = 0
    usage_date: date | None = None


def _month_total_locked(usage_model, today: date) -> int:
    start, end = month_bounds(today)
    total = (
        usage_model.objects.filter(usage_date__gte=start, usage_date__lt=end).aggregate(
            total=Sum("sent_count")
        )["total"]
        or 0
    )
    return int(total)


@transaction.atomic
def try_reserve_slot(priority: str = PRIORITY_NORMAL) -> ReservationResult:
    """Atomically reserve one send slot against daily/monthly limits.

    Returns ``reserved=False`` with ``defer_reason`` when the message should be
    deferred. Concurrent callers never exceed the configured caps.
    """
    from core.models import EmailDailyUsage

    limits = get_quota_limits()
    today = quota_today(limits)
    priority = PRIORITY_HIGH if priority == PRIORITY_HIGH else PRIORITY_NORMAL

    qs = EmailDailyUsage.objects.filter(usage_date=today)
    locked = list(_select_for_update(qs))
    if locked:
        usage = locked[0]
    else:
        usage, _ = EmailDailyUsage.objects.get_or_create(
            usage_date=today, defaults={"sent_count": 0}
        )
        usage = _select_for_update(EmailDailyUsage.objects.filter(pk=usage.pk)).get()

    month_total = _month_total_locked(EmailDailyUsage, today)

    if limits.monthly_limit > 0 and month_total >= limits.monthly_limit:
        return ReservationResult(
            reserved=False,
            defer_reason="monthly",
            sent_count=usage.sent_count,
            month_total=month_total,
            usage_date=today,
        )

    if limits.daily_limit > 0:
        if priority == PRIORITY_NORMAL:
            normal_cap = limits.normal_daily_cap or 0
            if usage.sent_count >= normal_cap:
                return ReservationResult(
                    reserved=False,
                    defer_reason="daily",
                    sent_count=usage.sent_count,
                    month_total=month_total,
                    usage_date=today,
                )
        elif usage.sent_count >= limits.daily_limit:
            return ReservationResult(
                reserved=False,
                defer_reason="daily",
                sent_count=usage.sent_count,
                month_total=month_total,
                usage_date=today,
            )

    usage.sent_count += 1
    usage.save(update_fields=["sent_count", "updated_at"])
    return ReservationResult(
        reserved=True,
        defer_reason=None,
        sent_count=usage.sent_count,
        month_total=month_total + 1,
        usage_date=today,
    )


@transaction.atomic
def release_slot(usage_date: date | None = None) -> int:
    """Refund one previously reserved slot (e.g. after a failed provider send)."""
    from core.models import EmailDailyUsage

    limits = get_quota_limits()
    day = usage_date or quota_today(limits)
    qs = _select_for_update(EmailDailyUsage.objects.filter(usage_date=day))
    usage = qs.first()
    if usage is None or usage.sent_count <= 0:
        return 0
    usage.sent_count -= 1
    usage.save(update_fields=["sent_count", "updated_at"])
    return usage.sent_count


def remaining_headroom(limits: QuotaLimits | None = None) -> dict[str, int | None]:
    """Read-only headroom snapshot for ops/status commands."""
    from core.models import EmailDailyUsage

    limits = limits or get_quota_limits()
    today = quota_today(limits)
    usage = EmailDailyUsage.objects.filter(usage_date=today).first()
    sent = usage.sent_count if usage else 0
    month_total = (
        EmailDailyUsage.objects.filter(
            usage_date__gte=month_bounds(today)[0],
            usage_date__lt=month_bounds(today)[1],
        ).aggregate(total=Sum("sent_count"))["total"]
        or 0
    )

    daily_remaining = None
    normal_remaining = None
    priority_remaining = None
    if limits.daily_limit > 0:
        daily_remaining = max(0, limits.daily_limit - sent)
        normal_cap = limits.normal_daily_cap or 0
        normal_remaining = max(0, normal_cap - sent)
        # Priority headroom is whatever remains of the full daily cap.
        priority_remaining = daily_remaining

    monthly_remaining = None
    if limits.monthly_limit > 0:
        monthly_remaining = max(0, limits.monthly_limit - int(month_total))

    return {
        "usage_date": today.isoformat(),
        "sent_today": sent,
        "daily_limit": limits.daily_limit or None,
        "priority_reserve": limits.priority_reserve,
        "normal_daily_cap": limits.normal_daily_cap,
        "normal_remaining": normal_remaining,
        "priority_remaining": priority_remaining,
        "daily_remaining": daily_remaining,
        "month_total": int(month_total),
        "monthly_limit": limits.monthly_limit or None,
        "monthly_remaining": monthly_remaining,
        "timezone": limits.timezone_name,
    }
