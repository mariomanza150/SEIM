"""Django email backends for SEIM."""

from __future__ import annotations

import base64
import logging
import smtplib
from email.mime.base import MIMEBase

from django.conf import settings
from django.core.mail import get_connection
from django.core.mail.backends.base import BaseEmailBackend

from core.email.ms_graph import MicrosoftGraphAuthError, send_mail_payload

logger = logging.getLogger(__name__)

DEFAULT_DELIVERY_BACKEND = "django.core.mail.backends.smtp.EmailBackend"


def is_transient_provider_error(exc: BaseException) -> bool:
    """True for provider rate-limit / temporary refusal errors (defer, don't drop)."""
    if isinstance(exc, smtplib.SMTPResponseException):
        if exc.smtp_code in (421, 450, 451):
            return True
    if isinstance(exc, smtplib.SMTPServerDisconnected):
        return True
    text = str(exc).lower()
    markers = (
        "429",
        "too many requests",
        "rate limit",
        "throttl",
        "try again later",
        "421",
        "450",
        "451",
    )
    return any(m in text for m in markers)


def _recipient_list(addresses) -> list[dict]:
    return [
        {"emailAddress": {"address": str(addr).strip()}}
        for addr in (addresses or [])
        if str(addr).strip()
    ]


def _extract_html(message) -> str | None:
    for content, mimetype in getattr(message, "alternatives", None) or []:
        if mimetype == "text/html":
            return str(content)
    if getattr(message, "content_subtype", "plain") == "html":
        return str(message.body or "")
    return None


def _attachment_items(message) -> list[dict]:
    items: list[dict] = []
    for attachment in getattr(message, "attachments", None) or []:
        if isinstance(attachment, MIMEBase):
            payload = attachment.get_payload(decode=True) or b""
            name = attachment.get_filename() or "attachment"
            content_type = attachment.get_content_type() or "application/octet-stream"
        else:
            name, content, content_type = attachment
            if isinstance(content, str):
                content = content.encode("utf-8")
            payload = content or b""
            content_type = content_type or "application/octet-stream"
        items.append(
            {
                "@odata.type": "#microsoft.graph.fileAttachment",
                "name": name,
                "contentType": content_type,
                "contentBytes": base64.b64encode(payload).decode("ascii"),
            }
        )
    return items


def email_message_to_graph_payload(message) -> dict:
    """Map a Django EmailMessage / EmailMultiAlternatives to Graph sendMail JSON."""
    html = _extract_html(message)
    if html is not None:
        body = {"contentType": "HTML", "content": html}
    else:
        body = {"contentType": "Text", "content": str(message.body or "")}

    graph_message: dict = {
        "subject": str(message.subject or ""),
        "body": body,
        "toRecipients": _recipient_list(message.to),
    }
    cc = _recipient_list(getattr(message, "cc", None))
    bcc = _recipient_list(getattr(message, "bcc", None))
    if cc:
        graph_message["ccRecipients"] = cc
    if bcc:
        graph_message["bccRecipients"] = bcc

    attachments = _attachment_items(message)
    if attachments:
        graph_message["attachments"] = attachments

    return {"message": graph_message, "saveToSentItems": True}


class MicrosoftGraphEmailBackend(BaseEmailBackend):
    """Send mail via Microsoft Graph ``POST /v1.0/me/sendMail`` (delegated OAuth2).

    Select with::

        EMAIL_BACKEND=core.email.backends.MicrosoftGraphEmailBackend
    """

    def send_messages(self, email_messages):
        if not email_messages:
            return 0
        sent = 0
        for message in email_messages:
            try:
                payload = email_message_to_graph_payload(message)
                send_mail_payload(payload)
                sent += 1
            except MicrosoftGraphAuthError:
                logger.exception("Microsoft Graph email send failed")
                if not self.fail_silently:
                    raise
            except Exception:
                logger.exception("Unexpected error sending via Microsoft Graph")
                if not self.fail_silently:
                    raise
        return sent


class RateLimitedEmailBackend(BaseEmailBackend):
    """Wrap a delivery backend with daily/monthly quotas and outbox deferral.

    Configure production with::

        EMAIL_BACKEND=core.email.backends.RateLimitedEmailBackend
        EMAIL_DELIVERY_BACKEND=django.core.mail.backends.smtp.EmailBackend
    """

    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently)
        self._delivery_kwargs = kwargs

    def _delivery_backend_path(self) -> str:
        path = (
            getattr(settings, "EMAIL_DELIVERY_BACKEND", "") or DEFAULT_DELIVERY_BACKEND
        )
        if path == "core.email.backends.RateLimitedEmailBackend":
            # Avoid infinite recursion if misconfigured.
            return DEFAULT_DELIVERY_BACKEND
        return path

    def open(self):
        return False

    def close(self):
        return None

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        from core.email.outbox import enqueue_message
        from core.email.pacing import wait_for_send_slot
        from core.email.priority import strip_priority_header
        from core.email.quota import release_slot, try_reserve_slot

        handled = 0
        delivery_path = self._delivery_backend_path()

        for message in email_messages:
            priority = strip_priority_header(message)
            reservation = try_reserve_slot(priority)
            if not reservation.reserved:
                enqueue_message(
                    message,
                    priority=priority,
                    defer_reason=reservation.defer_reason or "daily",
                )
                handled += 1
                logger.info(
                    "email_deferred priority=%s reason=%s sent_today=%s month_total=%s",
                    priority,
                    reservation.defer_reason,
                    reservation.sent_count,
                    reservation.month_total,
                )
                continue

            wait_for_send_slot()
            try:
                connection = get_connection(
                    backend=delivery_path,
                    fail_silently=False,
                    **self._delivery_kwargs,
                )
                sent = connection.send_messages([message])
                if not sent:
                    release_slot()
                    enqueue_message(
                        message,
                        priority=priority,
                        defer_reason="daily",
                        last_error="delivery backend returned 0",
                    )
                    handled += 1
                    continue
                handled += int(sent)
                logger.info(
                    "email_sent priority=%s backend=%s",
                    priority,
                    delivery_path.rsplit(".", 1)[-1],
                )
            except Exception as exc:
                release_slot()
                if is_transient_provider_error(exc):
                    enqueue_message(
                        message,
                        priority=priority,
                        defer_reason="daily",
                        last_error=f"transient:{exc.__class__.__name__}",
                    )
                    handled += 1
                    logger.warning(
                        "email_deferred_transient priority=%s error_type=%s",
                        priority,
                        exc.__class__.__name__,
                    )
                    continue
                logger.exception(
                    "email_send_failed priority=%s error_type=%s",
                    priority,
                    exc.__class__.__name__,
                )
                if not self.fail_silently:
                    raise
        return handled


# Keep import_string happy for settings introspection / docs.
__all__ = [
    "MicrosoftGraphEmailBackend",
    "RateLimitedEmailBackend",
    "email_message_to_graph_payload",
    "is_transient_provider_error",
]
