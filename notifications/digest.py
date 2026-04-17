"""
Periodic unread-notification digests (daily / weekly) driven by UserSettings.
"""

from __future__ import annotations

from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from accounts.models import UserSettings

from .models import Notification
from .services import NotificationService


def _digest_eligible_queryset():
    # Compare stored string values (DB + ORM __in must match primitive values).
    return UserSettings.objects.filter(
        notification_digest_frequency__in=(
            UserSettings.NotificationDigestFrequency.DAILY.value,
            UserSettings.NotificationDigestFrequency.WEEKLY.value,
        )
    ).select_related("user")


def _unread_non_digest_notifications(user):
    # Use contains (not key=True) so missing ``is_digest`` is not dropped on PostgreSQL.
    return Notification.objects.filter(recipient=user, is_read=False).exclude(
        data__contains={"is_digest": True}
    )


def _should_send_daily(settings_row: UserSettings, now) -> bool:
    last = settings_row.notification_digest_last_sent_at
    if last is None:
        return True
    return timezone.localtime(last).date() < timezone.localdate(now)


def _should_send_weekly(settings_row: UserSettings, now) -> bool:
    last = settings_row.notification_digest_last_sent_at
    if last is None:
        return True
    return (now - last) >= timedelta(days=7)


def _should_send(settings_row: UserSettings, now) -> bool:
    freq = settings_row.notification_digest_frequency
    fv = getattr(freq, "value", freq)
    if fv == UserSettings.NotificationDigestFrequency.DAILY.value:
        return _should_send_daily(settings_row, now)
    if fv == UserSettings.NotificationDigestFrequency.WEEKLY.value:
        return _should_send_weekly(settings_row, now)
    return False


def process_notification_digests(now=None) -> dict[str, int]:
    """
    Send one digest notification per eligible user when cadence allows and unread count > 0.

    Digests use ``settings_category="system"`` so ``email_system`` / ``inapp_system`` apply
    (and ``email_notification_digest`` still gates the email half when ``notification_type`` is
    ``both``). If all requested channels are disabled, no notification is created; the digest
    timestamp is still advanced so cadence does not stall on hourly/task reruns.

    Returns counts: eligible_users, digests_sent, skipped_no_unread, skipped_cadence,
    skipped_suppressed.
    """
    now = now or timezone.now()
    eligible_users = 0
    digests_sent = 0
    skipped_no_unread = 0
    skipped_cadence = 0
    skipped_suppressed = 0

    for settings_row in _digest_eligible_queryset().iterator():
        eligible_users += 1
        user = settings_row.user
        if not _should_send(settings_row, now):
            skipped_cadence += 1
            continue

        unread_qs = _unread_non_digest_notifications(user)
        total = unread_qs.count()
        if total == 0:
            skipped_no_unread += 1
            continue

        previews = list(unread_qs.order_by("-sent_at").values_list("title", flat=True)[:3])
        preview_lines = "\n".join(f"• {t or 'Notification'}" for t in previews)
        if total > len(previews):
            preview_lines += f"\n… and {total - len(previews)} more."

        message = f"You have {total} unread notification(s).\n\n{preview_lines}"

        email_ok = (
            settings_row.email_system
            and settings_row.email_notification_digest
        )
        ntype = "both" if email_ok else "in_app"

        with transaction.atomic():
            locked = UserSettings.objects.select_for_update().get(pk=settings_row.pk)
            if not _should_send(locked, now):
                skipped_cadence += 1
                continue
            if _unread_non_digest_notifications(locked.user).count() == 0:
                skipped_no_unread += 1
                continue

            notif = NotificationService.send_notification(
                recipient=locked.user,
                title="Your notification digest",
                message=message,
                notification_type=ntype,
                category="info",
                action_url="/notifications",
                action_text="Open notifications",
                data={"is_digest": True},
                settings_category="system",
                transactional_route_key="notification_digest_unread_summary",
            )
            locked.notification_digest_last_sent_at = now
            locked.save(update_fields=["notification_digest_last_sent_at", "updated_at"])

        if notif is None:
            skipped_suppressed += 1
        else:
            digests_sent += 1

    return {
        "eligible_users": eligible_users,
        "digests_sent": digests_sent,
        "skipped_no_unread": skipped_no_unread,
        "skipped_cadence": skipped_cadence,
        "skipped_suppressed": skipped_suppressed,
    }
