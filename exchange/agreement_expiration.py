"""
Pre-expiry notifications for exchange agreements (staff: admins + relevant coordinators).
"""

from __future__ import annotations

from datetime import date
from typing import List

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.urls import reverse

from notifications.services import NotificationService

from .models import AgreementExpirationReminderLog, ExchangeAgreement

User = get_user_model()

NOTIFICATION_TYPE_NAME = "agreement_expiration"


def _reminder_day_offsets() -> List[int]:
    raw = getattr(settings, "AGREEMENT_EXPIRATION_REMINDER_DAYS", [90, 30, 7])
    out = []
    for x in raw:
        try:
            n = int(x)
        except (TypeError, ValueError):
            continue
        if n >= 0:
            out.append(n)
    return sorted(set(out), reverse=True) or [90, 30, 7]


def _statuses_to_remind() -> List[str]:
    return list(
        getattr(
            settings,
            "AGREEMENT_EXPIRATION_REMINDER_STATUSES",
            [
                ExchangeAgreement.Status.ACTIVE,
                ExchangeAgreement.Status.RENEWAL_PENDING,
            ],
        )
    )


def recipients_for_agreement(agreement: ExchangeAgreement):
    """Admins plus coordinators linked to the agreement's programs (or all coordinators if none)."""
    admin_qs = User.objects.filter(roles__name="admin").distinct()
    programs = agreement.programs.all()
    if programs.exists():
        coord_qs = User.objects.filter(
            roles__name="coordinator",
            coordinated_programs__in=programs,
        ).distinct()
    else:
        coord_qs = User.objects.filter(roles__name="coordinator").distinct()
    return admin_qs.union(coord_qs)


def process_agreement_expiration_reminders(today: date | None = None) -> dict:
    """
    For each active agreement with an end date, on the calendar day that is exactly
    N days before expiry (for each configured N), send in-app (+ email per user prefs)
    notifications to staff. Idempotent per (agreement, N, end_date snapshot).
    """
    from django.utils import timezone

    today = today or timezone.localdate()
    offsets = _reminder_day_offsets()
    statuses = _statuses_to_remind()

    agreements = ExchangeAgreement.objects.filter(
        status__in=statuses,
        end_date__isnull=False,
        end_date__gte=today,
    )

    notifications_sent = 0
    milestones_processed = 0

    for agreement in agreements:
        assert agreement.end_date is not None
        days_left = (agreement.end_date - today).days

        for days_before in offsets:
            if days_left != days_before:
                continue

            if AgreementExpirationReminderLog.objects.filter(
                agreement=agreement,
                days_before=days_before,
                agreement_end_date=agreement.end_date,
            ).exists():
                continue

            recipients = list(recipients_for_agreement(agreement))
            admin_path = reverse(
                "admin:exchange_exchangeagreement_change", args=[agreement.pk]
            )
            title = (
                f"Agreement expires in {days_before} day(s): {agreement.title}"
                if days_before != 1
                else f"Agreement expires tomorrow: {agreement.title}"
            )
            message = (
                f'Partner: {agreement.partner_institution_name}. '
                f'End date: {agreement.end_date:%Y-%m-%d}. '
                f"Review renewal status and linked programs in admin."
            )

            sent_for_milestone = 0
            with transaction.atomic():
                for user in recipients:
                    if not NotificationService.is_enabled(user, NOTIFICATION_TYPE_NAME):
                        continue
                    NotificationService.send_notification(
                        recipient=user,
                        title=title,
                        message=message,
                        notification_type="both",
                        category="warning",
                        action_url=admin_path,
                        action_text="Open agreement",
                        data={
                            "kind": "agreement_expiration",
                            "agreement_id": str(agreement.pk),
                            "days_before": days_before,
                            "end_date": agreement.end_date.isoformat(),
                        },
                        settings_category="system",
                        transactional_route_key="agreement_expiration_alert",
                    )
                    sent_for_milestone += 1
                    notifications_sent += 1

                if sent_for_milestone:
                    AgreementExpirationReminderLog.objects.create(
                        agreement=agreement,
                        days_before=days_before,
                        agreement_end_date=agreement.end_date,
                    )
                    milestones_processed += 1

    return {
        "notifications_sent": notifications_sent,
        "milestones_logged": milestones_processed,
        "date": today.isoformat(),
    }
