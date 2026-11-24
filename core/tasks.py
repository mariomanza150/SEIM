"""Celery tasks owned by the ``core`` app."""

from __future__ import annotations

import logging
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from core.celery_utils import log_celery_failure, retryable_task_kwargs
from core.email.outbox import claim_due_emails, scheduled_for_reason
from core.email.pacing import wait_for_send_slot
from core.email.quota import release_slot, try_reserve_slot
from core.email.serialize import payload_to_message

logger = logging.getLogger(__name__)


def _max_retries() -> int:
    return int(getattr(settings, "EMAIL_DEFERRED_MAX_RETRIES", 5) or 5)


def _backoff_seconds(attempts: int) -> int:
    # Exponential backoff: 1, 2, 4, 8, 16 minutes (capped).
    return min(60 * (2 ** max(attempts - 1, 0)), 60 * 60)


def _delivery_backend_path() -> str:
    path = getattr(settings, "EMAIL_DELIVERY_BACKEND", "") or (
        "django.core.mail.backends.smtp.EmailBackend"
    )
    if path == "core.email.backends.RateLimitedEmailBackend":
        return "django.core.mail.backends.smtp.EmailBackend"
    return path


def _send_deferred_row(row) -> str:
    """Attempt delivery for one claimed DeferredEmail. Returns outcome label."""
    from django.core.mail import get_connection

    from core.models import DeferredEmail

    reservation = try_reserve_slot(row.priority)
    if not reservation.reserved:
        reason = reservation.defer_reason or "daily"
        row.status = DeferredEmail.STATUS_PENDING
        row.scheduled_for = scheduled_for_reason(reason)
        row.last_error = f"quota:{reason}"
        row.save(update_fields=["status", "scheduled_for", "last_error"])
        logger.info(
            "email_drain_rescheduled id=%s priority=%s reason=%s",
            row.pk,
            row.priority,
            reason,
        )
        return "rescheduled"

    wait_for_send_slot()
    payload = {
        "subject": row.subject,
        "body": row.body,
        "html_body": row.html_body,
        "from_email": row.from_email,
        "to": row.to,
        "cc": row.cc,
        "bcc": row.bcc,
        "reply_to": row.reply_to,
        "headers": row.headers,
        "attachments": row.attachments,
    }
    message = payload_to_message(payload)
    row.attempts += 1
    try:
        connection = get_connection(
            backend=_delivery_backend_path(), fail_silently=False
        )
        sent = connection.send_messages([message])
        if not sent:
            raise RuntimeError("delivery backend returned 0")
        row.status = DeferredEmail.STATUS_SENT
        row.sent_at = timezone.now()
        row.last_error = ""
        row.clear_sensitive_content()
        row.save(
            update_fields=[
                "status",
                "sent_at",
                "last_error",
                "attempts",
                "body",
                "html_body",
                "attachments",
            ]
        )
        logger.info(
            "email_drain_sent id=%s priority=%s attempts=%s",
            row.pk,
            row.priority,
            row.attempts,
        )
        return "sent"
    except Exception as exc:
        from core.email.backends import is_transient_provider_error

        release_slot()
        max_retries = _max_retries()
        if is_transient_provider_error(exc) and row.attempts < max_retries:
            row.status = DeferredEmail.STATUS_PENDING
            row.scheduled_for = timezone.now() + timedelta(
                seconds=_backoff_seconds(row.attempts)
            )
            row.last_error = f"transient:{exc.__class__.__name__}"[:2000]
            row.save(
                update_fields=["status", "scheduled_for", "last_error", "attempts"]
            )
            logger.warning(
                "email_drain_retry id=%s priority=%s attempts=%s error_type=%s",
                row.pk,
                row.priority,
                row.attempts,
                exc.__class__.__name__,
            )
            return "retry"
        row.status = DeferredEmail.STATUS_FAILED
        row.last_error = f"{exc.__class__.__name__}:{exc}"[:2000]
        row.save(update_fields=["status", "last_error", "attempts"])
        logger.error(
            "email_drain_failed id=%s priority=%s attempts=%s error_type=%s",
            row.pk,
            row.priority,
            row.attempts,
            exc.__class__.__name__,
        )
        return "failed"


@shared_task(on_failure=log_celery_failure, **retryable_task_kwargs())
def drain_deferred_emails(self, batch_size: int = 50):
    """Drain due DeferredEmail rows, high priority first.

    Stops when daily/reserve/monthly budget is exhausted so remaining rows stay
    pending for the next boundary. Safe for overlapping beat runs via
    ``select_for_update(skip_locked=True)`` (SQLite-safe fallback).
    """
    from core.models import DeferredEmail

    claimed_ids = claim_due_emails(limit=batch_size)
    counts = {
        "claimed": len(claimed_ids),
        "sent": 0,
        "rescheduled": 0,
        "retry": 0,
        "failed": 0,
    }
    stop_draining = False

    for pk in claimed_ids:
        if stop_draining:
            # Release any remaining claimed rows back to pending without sending.
            with transaction.atomic():
                DeferredEmail.objects.filter(
                    pk=pk, status=DeferredEmail.STATUS_SENDING
                ).update(status=DeferredEmail.STATUS_PENDING)
            continue

        try:
            row = DeferredEmail.objects.get(pk=pk)
        except DeferredEmail.DoesNotExist:
            continue

        outcome = _send_deferred_row(row)
        if outcome in counts:
            counts[outcome] += 1
        if outcome == "rescheduled":
            # Budget exhausted — leave the rest pending for next run/boundary.
            stop_draining = True

    logger.info(
        "email_drain_complete claimed=%s sent=%s rescheduled=%s retry=%s failed=%s",
        counts["claimed"],
        counts["sent"],
        counts["rescheduled"],
        counts["retry"],
        counts["failed"],
    )
    return counts
