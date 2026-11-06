"""Django email backends for SEIM."""

from __future__ import annotations

import base64
import logging
from email.mime.base import MIMEBase

from django.core.mail.backends.base import BaseEmailBackend

from core.email.ms_graph import MicrosoftGraphAuthError, send_mail_payload

logger = logging.getLogger(__name__)


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
