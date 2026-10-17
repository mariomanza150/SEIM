"""
Email backend that captures outgoing mail in the database (Outbox) instead of
delivering it. For test servers only: refuses to load on DEPLOY_TIER=production.

    EMAIL_BACKEND=qa.mail.CaptureEmailBackend
"""

from __future__ import annotations

import logging
from datetime import timedelta

from django.core.exceptions import ImproperlyConfigured
from django.core.mail.backends.base import BaseEmailBackend
from django.utils import timezone

from .gating import ALLOWED_TIERS, deploy_tier

logger = logging.getLogger(__name__)
RETENTION_DAYS = 14
MAX_BODY = 200_000


def _addresses(values):
    return [str(v)[:320] for v in (values or [])][:100]


class CaptureEmailBackend(BaseEmailBackend):
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        if deploy_tier() not in ALLOWED_TIERS:
            raise ImproperlyConfigured(
                "qa.mail.CaptureEmailBackend is for test servers only "
                f"(DEPLOY_TIER={deploy_tier()!r})."
            )

    def send_messages(self, email_messages):
        from .models import CapturedEmail

        sent = 0
        for message in email_messages or []:
            try:
                html = ""
                for content, mimetype in getattr(message, "alternatives", None) or []:
                    if mimetype == "text/html":
                        html = str(content)
                        break
                if not html and getattr(message, "content_subtype", "") == "html":
                    html = str(message.body or "")
                to, cc, bcc = (
                    _addresses(message.to),
                    _addresses(message.cc),
                    _addresses(message.bcc),
                )
                CapturedEmail.objects.create(
                    subject=str(message.subject or "")[:998],
                    from_email=str(message.from_email or "")[:320],
                    to=to,
                    cc=cc,
                    bcc=bcc,
                    body_text=str(message.body or "")[:MAX_BODY]
                    if getattr(message, "content_subtype", "plain") != "html"
                    else "",
                    body_html=html[:MAX_BODY],
                    recipients_index=" ".join(a.lower() for a in to + cc + bcc),
                )
                sent += 1
            except Exception:
                logger.exception("Could not capture outgoing email")
                if not self.fail_silently:
                    raise
        if sent:
            cutoff = timezone.now() - timedelta(days=RETENTION_DAYS)
            CapturedEmail.objects.filter(created_at__lt=cutoff).delete()
        return sent
