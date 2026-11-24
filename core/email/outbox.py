"""Enqueue and claim deferred emails for the rate-limited outbox."""

from __future__ import annotations

import logging
from datetime import datetime

from django.db import transaction
from django.utils import timezone

from core.email.errors import sanitize_last_error
from core.email.priority import PRIORITY_HIGH, PRIORITY_NORMAL
from core.email.quota import (
    _select_for_update,
    next_day_boundary,
    next_month_boundary,
)
from core.email.serialize import message_to_payload

logger = logging.getLogger(__name__)


def scheduled_for_reason(defer_reason: str) -> datetime:
    if defer_reason == "monthly":
        return next_month_boundary()
    return next_day_boundary()


@transaction.atomic
def enqueue_message(
    message,
    *,
    priority: str = PRIORITY_NORMAL,
    defer_reason: str = "daily",
    last_error: str = "",
    scheduled_for: datetime | None = None,
):
    """Persist a Django email message into the DeferredEmail outbox."""
    from core.models import DeferredEmail

    payload = message_to_payload(message)
    # Never persist the internal priority header in outbox headers.
    headers = dict(payload.get("headers") or {})
    headers = {
        k: v for k, v in headers.items() if str(k).lower() != "x-seim-email-priority"
    }
    when = scheduled_for or scheduled_for_reason(defer_reason)
    priority = PRIORITY_HIGH if priority == PRIORITY_HIGH else PRIORITY_NORMAL

    row = DeferredEmail.objects.create(
        priority=priority,
        status=DeferredEmail.STATUS_PENDING,
        subject=payload["subject"],
        body=payload["body"],
        html_body=payload["html_body"],
        from_email=payload["from_email"],
        to=payload["to"],
        cc=payload["cc"],
        bcc=payload["bcc"],
        reply_to=payload["reply_to"],
        headers=headers,
        attachments=payload["attachments"],
        scheduled_for=when,
        attempts=0,
        last_error=sanitize_last_error(last_error) if last_error else "",
    )
    logger.info(
        "email_outbox_enqueued id=%s priority=%s defer_reason=%s scheduled_for=%s",
        row.pk,
        row.priority,
        defer_reason,
        row.scheduled_for.isoformat(),
    )
    return row


def claim_due_emails(*, limit: int = 50):
    """Claim due pending rows as ``sending`` (high priority first, then FIFO)."""
    from django.db.models import Case, IntegerField, Value, When

    from core.models import DeferredEmail

    now = timezone.now()
    claimed = []
    with transaction.atomic():
        qs = (
            DeferredEmail.objects.filter(
                status=DeferredEmail.STATUS_PENDING,
                scheduled_for__lte=now,
            )
            .annotate(
                _prio_rank=Case(
                    When(priority=DeferredEmail.PRIORITY_HIGH, then=Value(0)),
                    default=Value(1),
                    output_field=IntegerField(),
                )
            )
            .order_by("_prio_rank", "created_at")
        )
        rows = list(_select_for_update(qs, skip_locked=True)[:limit])
        for row in rows:
            row.status = DeferredEmail.STATUS_SENDING
            row.save(update_fields=["status", "updated_at"])
            claimed.append(row.pk)
    return claimed
