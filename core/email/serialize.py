"""Serialize Django EmailMessage instances to/from DeferredEmail payloads."""

from __future__ import annotations

import base64
from email.mime.base import MIMEBase
from typing import Any

from django.core.mail import EmailMultiAlternatives


def _listify(value) -> list[str]:
    if not value:
        return []
    if isinstance(value, list | tuple):
        return [str(v) for v in value if str(v).strip()]
    return [str(value)]


def _attachment_dicts(message) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
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
                "name": str(name),
                "mimetype": str(content_type),
                "content_base64": base64.b64encode(payload).decode("ascii"),
            }
        )
    return items


def _extract_html(message) -> str:
    for content, mimetype in getattr(message, "alternatives", None) or []:
        if mimetype == "text/html":
            return str(content)
    if getattr(message, "content_subtype", "plain") == "html":
        return str(message.body or "")
    return ""


def message_to_payload(message) -> dict[str, Any]:
    """Flatten a Django email message into DeferredEmail field values."""
    headers = {}
    extra = getattr(message, "extra_headers", None) or {}
    if isinstance(extra, dict):
        headers = {str(k): str(v) for k, v in extra.items()}
    return {
        "subject": str(getattr(message, "subject", "") or ""),
        "body": str(getattr(message, "body", "") or ""),
        "html_body": _extract_html(message),
        "from_email": str(getattr(message, "from_email", "") or ""),
        "to": _listify(getattr(message, "to", None)),
        "cc": _listify(getattr(message, "cc", None)),
        "bcc": _listify(getattr(message, "bcc", None)),
        "reply_to": _listify(getattr(message, "reply_to", None)),
        "headers": headers,
        "attachments": _attachment_dicts(message),
    }


def payload_to_message(payload: dict[str, Any]):
    """Rebuild an EmailMultiAlternatives from a DeferredEmail payload."""
    body = str(payload.get("body") or "")
    html = str(payload.get("html_body") or "")
    msg = EmailMultiAlternatives(
        subject=str(payload.get("subject") or ""),
        body=body,
        from_email=str(payload.get("from_email") or "") or None,
        to=_listify(payload.get("to")),
        cc=_listify(payload.get("cc")),
        bcc=_listify(payload.get("bcc")),
        reply_to=_listify(payload.get("reply_to")),
        headers=dict(payload.get("headers") or {}),
    )
    if html:
        msg.attach_alternative(html, "text/html")
    for item in payload.get("attachments") or []:
        if not isinstance(item, dict):
            continue
        raw = base64.b64decode(item.get("content_base64") or "", validate=False)
        msg.attach(
            item.get("name") or "attachment",
            raw,
            item.get("mimetype") or "application/octet-stream",
        )
    return msg
