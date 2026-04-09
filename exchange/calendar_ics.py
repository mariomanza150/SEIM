"""
Signed per-user calendar subscribe tokens and iCalendar (ICS) rendering.
"""

from datetime import datetime, timezone
from urllib.parse import urlencode

from django.core.signing import BadSignature, Signer

SUBSCRIBE_SALT = "seim.calendar-subscribe"


def sign_calendar_subscribe_token(user_id: int) -> str:
    return Signer(salt=SUBSCRIBE_SALT).sign(str(int(user_id)))


def unsign_calendar_subscribe_token(token: str) -> int | None:
    try:
        raw = Signer(salt=SUBSCRIBE_SALT).unsign(token)
        return int(raw)
    except BadSignature:
        return None


def _ics_escape(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\n", "\\n")
        .replace("\r", "")
    )


def _fold_line(line: str) -> str:
    """Fold long lines per RFC 5545 (octet-oriented; keep simple for UTF-8)."""
    if len(line) <= 75:
        return line
    parts = []
    rest = line
    while rest:
        chunk = rest[:75]
        parts.append(chunk)
        rest = rest[75:]
    return "\r\n ".join(parts)


def _dtstamp_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _date_value(dt) -> str:
    """All-day DATE from aware datetime (wall date in the datetime's tz)."""
    return dt.strftime("%Y%m%d")


def events_to_ics(events: list[dict], *, cal_name: str = "SEIM deadlines") -> str:
    """Render FullCalendar-style dicts to VCALENDAR (all-day events)."""
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//SEIM//Student Exchange//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{_ics_escape(cal_name)}",
    ]
    stamp = _dtstamp_utc()
    for ev in events:
        uid = f"{ev.get('id', 'event')}@seim-calendar"
        title = _ics_escape(str(ev.get("title", "Event")))
        start = ev.get("start")
        if hasattr(start, "strftime"):
            d = _date_value(start)
        else:
            continue
        desc_parts = []
        if ev.get("spa_path"):
            desc_parts.append(f"In SEIM: {ev['spa_path']}")
        desc = _ics_escape("\n".join(desc_parts))
        lines.extend(
            [
                "BEGIN:VEVENT",
                _fold_line(f"UID:{uid}"),
                f"DTSTAMP:{stamp}",
                f"DTSTART;VALUE=DATE:{d}",
                _fold_line(f"SUMMARY;CHARSET=UTF-8:{title}"),
            ]
        )
        if desc:
            lines.append(_fold_line(f"DESCRIPTION;CHARSET=UTF-8:{desc}"))
        lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


def build_subscribe_query(token: str) -> str:
    return urlencode({"token": token})
