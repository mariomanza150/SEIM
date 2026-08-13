"""Google Calendar OAuth2 linking and two-way sync of SEIM events.

SEIM is the source of truth for mapped events: Google edits are overwritten
on sync. Unmapped Google events are cached as a read-only overlay.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.core import signing
from django.utils import timezone

from accounts.models import GoogleCalendarConnection
from exchange.calendar_events import build_calendar_event_dicts

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
GOOGLE_EVENTS_URL = "https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events"
SCOPE = "https://www.googleapis.com/auth/calendar.events https://www.googleapis.com/auth/userinfo.email"
STATE_SALT = "seim-google-calendar"
STATE_MAX_AGE = 600


def is_configured() -> bool:
    return bool(
        getattr(settings, "GOOGLE_OAUTH_CLIENT_ID", "")
        and getattr(settings, "GOOGLE_OAUTH_CLIENT_SECRET", "")
    )


def callback_uri(request) -> str:
    override = (getattr(settings, "GOOGLE_OAUTH_REDIRECT_URI", "") or "").strip()
    if override:
        return override
    return request.build_absolute_uri("/api/calendar/events/google-callback/")


def spa_settings_url(query: str = "") -> str:
    base = getattr(settings, "FRONTEND_BASE_URL", "http://localhost:8001").rstrip("/")
    url = f"{base}/seim/settings"
    return f"{url}?{query}" if query else url


def connection_status(user) -> dict:
    conn = GoogleCalendarConnection.objects.filter(user=user).first()
    return {
        "configured": is_configured(),
        "connected": bool(conn and conn.is_connected),
        "google_email": conn.google_email if conn else "",
        "last_synced_at": conn.last_synced_at.isoformat() if conn and conn.last_synced_at else None,
        "last_sync_error": conn.last_sync_error if conn else "",
    }


def build_authorization_url(request, user) -> str:
    if not is_configured():
        raise ValueError("Google Calendar OAuth is not configured.")
    state = signing.dumps(
        {"uid": str(user.pk), "nonce": uuid.uuid4().hex},
        salt=STATE_SALT,
    )
    params = {
        "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
        "redirect_uri": callback_uri(request),
        "response_type": "code",
        "scope": SCOPE,
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }
    return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"


def _load_state(state: str) -> str:
    data = signing.loads(state, salt=STATE_SALT, max_age=STATE_MAX_AGE)
    uid = data.get("uid")
    if not uid:
        raise signing.BadSignature("missing uid")
    return uid


def exchange_code(request, code: str, state: str) -> GoogleCalendarConnection:
    from django.contrib.auth import get_user_model

    User = get_user_model()
    uid = _load_state(state)
    user = User.objects.filter(pk=uid).first()
    if not user:
        raise ValueError("User not found for OAuth state.")
    token_resp = requests.post(
        GOOGLE_TOKEN_URL,
        data={
            "code": code,
            "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
            "redirect_uri": callback_uri(request),
            "grant_type": "authorization_code",
        },
        timeout=20,
    )
    token_resp.raise_for_status()
    payload = token_resp.json()
    access = payload.get("access_token") or ""
    refresh = payload.get("refresh_token") or ""
    expires_in = int(payload.get("expires_in") or 3600)
    email = ""
    if access:
        info = requests.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access}"},
            timeout=15,
        )
        if info.ok:
            email = (info.json() or {}).get("email") or ""
    conn, _ = GoogleCalendarConnection.objects.get_or_create(user=user)
    conn.access_token = access
    if refresh:
        conn.refresh_token = refresh
    conn.token_expiry = timezone.now() + timedelta(seconds=max(expires_in - 60, 60))
    conn.google_email = email
    conn.last_sync_error = ""
    conn.save()
    return conn


def disconnect(user) -> None:
    GoogleCalendarConnection.objects.filter(user=user).delete()


def _ensure_access_token(conn: GoogleCalendarConnection) -> str:
    if (
        conn.access_token
        and conn.token_expiry
        and conn.token_expiry > timezone.now()
    ):
        return conn.access_token
    if not conn.refresh_token:
        raise ValueError("Google Calendar is not connected.")
    resp = requests.post(
        GOOGLE_TOKEN_URL,
        data={
            "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
            "refresh_token": conn.refresh_token,
            "grant_type": "refresh_token",
        },
        timeout=20,
    )
    resp.raise_for_status()
    payload = resp.json()
    conn.access_token = payload.get("access_token") or ""
    expires_in = int(payload.get("expires_in") or 3600)
    conn.token_expiry = timezone.now() + timedelta(seconds=max(expires_in - 60, 60))
    conn.save(update_fields=["access_token", "token_expiry", "updated_at"])
    return conn.access_token


def _iso_prefix(value) -> str:
    if value is None:
        return ""
    if hasattr(value, "isoformat"):
        text = value.isoformat()
    else:
        text = str(value)
    text = text.replace("Z", "+00:00")
    if len(text) == 10:
        text = f"{text}T00:00"
    return text[:16]


def _seim_fingerprint(event: dict) -> tuple[str, str]:
    return ((event.get("title") or "").strip(), _iso_prefix(event.get("start")))


def _google_fingerprint(g_event: dict) -> tuple[str, str]:
    start = g_event.get("start") or {}
    raw = start.get("dateTime") or start.get("date") or ""
    return ((g_event.get("summary") or "").strip(), _iso_prefix(raw))


def _google_seim_id(g_event: dict) -> str:
    props = (g_event.get("extendedProperties") or {}).get("private") or {}
    return str(props.get("seim_event_id") or "")


def _parse_google_dt(g_event: dict, which: str = "start"):
    block = g_event.get(which) or {}
    raw = block.get("dateTime") or block.get("date")
    if not raw:
        return None
    text = str(raw).replace("Z", "+00:00")
    if len(text) == 10:
        from datetime import datetime as dt

        from django.utils import timezone as dj_tz

        return dj_tz.make_aware(dt.fromisoformat(f"{text}T00:00:00"))
    try:
        from datetime import datetime as dt

        parsed = dt.fromisoformat(text)
        if parsed.tzinfo is None:
            from django.utils import timezone as dj_tz

            return dj_tz.make_aware(parsed)
        return parsed
    except ValueError:
        return None


def _list_remote_events(headers: dict, calendar_id: str) -> list[dict]:
    from django.utils import timezone as dj_tz

    now = dj_tz.now()
    params = {
        "singleEvents": "true",
        "maxResults": 250,
        "timeMin": (now - timedelta(days=90)).isoformat(),
        "timeMax": (now + timedelta(days=365)).isoformat(),
    }
    base = GOOGLE_EVENTS_URL.format(calendar_id=calendar_id)
    resp = requests.get(base, headers=headers, params=params, timeout=20)
    resp.raise_for_status()
    items = (resp.json() or {}).get("items") or []
    return [item for item in items if item.get("status") != "cancelled"]


def imported_event_dicts(user, start_param=None, end_param=None) -> list[dict]:
    """Read-only Google-only events cached from the last two-way sync."""
    conn = GoogleCalendarConnection.objects.filter(user=user).first()
    if not conn:
        return []
    events = []
    for item in conn.imported_events or []:
        if not isinstance(item, dict):
            continue
        events.append(dict(item))
    if not start_param and not end_param:
        return events
    try:
        start_dt = (
            datetime.fromisoformat(start_param.replace("Z", "+00:00"))
            if start_param
            else None
        )
    except (ValueError, AttributeError):
        start_dt = None
    try:
        end_dt = (
            datetime.fromisoformat(end_param.replace("Z", "+00:00"))
            if end_param
            else None
        )
    except (ValueError, AttributeError):
        end_dt = None
    if start_dt is None and end_dt is None:
        return events
    filtered = []
    for ev in events:
        raw = ev.get("start")
        try:
            ev_start = (
                datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
                if raw and not hasattr(raw, "isoformat")
                else raw
            )
        except ValueError:
            filtered.append(ev)
            continue
        if start_dt and ev_start and ev_start < start_dt:
            continue
        if end_dt and ev_start and ev_start > end_dt:
            continue
        filtered.append(ev)
    return filtered


def _event_body(event: dict) -> dict:
    start = event.get("start")
    if hasattr(start, "isoformat"):
        start_iso = start.isoformat()
        all_day = bool(event.get("allDay"))
    else:
        start_iso = str(start or "")
        all_day = bool(event.get("allDay"))
    end = event.get("end")
    if end is None:
        end_iso = start_iso
    elif hasattr(end, "isoformat"):
        end_iso = end.isoformat()
    else:
        end_iso = str(end)
    body = {
        "summary": event.get("title") or "SEIM event",
        "extendedProperties": {"private": {"seim_event_id": str(event.get("id") or "")}},
    }
    if all_day:
        body["start"] = {"date": start_iso[:10]}
        body["end"] = {"date": (end_iso or start_iso)[:10]}
    else:
        body["start"] = {"dateTime": start_iso}
        body["end"] = {"dateTime": end_iso or start_iso}
    return body


def _overlay_from_google(g_event: dict) -> dict | None:
    gid = g_event.get("id")
    if not gid:
        return None
    start = _parse_google_dt(g_event, "start")
    if start is None:
        return None
    end = _parse_google_dt(g_event, "end")
    all_day = bool((g_event.get("start") or {}).get("date"))
    return {
        "id": f"google-{gid}",
        "title": g_event.get("summary") or "Google event",
        "start": start.isoformat(),
        "end": end.isoformat() if end else None,
        "allDay": all_day,
        "className": "event-google",
        "backgroundColor": "#34a853",
        "borderColor": "#34a853",
        "spa_path": "/settings",
        "source": "google",
    }


def sync_user_events(user) -> dict:
    """Two-way sync: push SEIM events (SEIM wins conflicts) and cache Google-only overlay."""
    conn = GoogleCalendarConnection.objects.filter(user=user).first()
    if not conn or not conn.is_connected:
        raise ValueError("Google Calendar is not connected.")
    token = _ensure_access_token(conn)
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    events = build_calendar_event_dicts(user, event_type="all")
    event_map = dict(conn.event_map or {})
    created = 0
    updated = 0
    conflicts_resolved = 0
    calendar_id = conn.google_calendar_id or "primary"
    base = GOOGLE_EVENTS_URL.format(calendar_id=calendar_id)
    try:
        remote = _list_remote_events(headers, calendar_id)
        remote_by_id = {item.get("id"): item for item in remote if item.get("id")}
        remote_by_seim = {}
        for item in remote:
            sid = _google_seim_id(item)
            if sid:
                remote_by_seim[sid] = item
                if item.get("id"):
                    event_map.setdefault(sid, item["id"])

        for event in events:
            seim_id = str(event.get("id") or "")
            if not seim_id:
                continue
            body = _event_body(event)
            google_id = event_map.get(seim_id)
            remote_event = remote_by_id.get(google_id) if google_id else None
            if remote_event is None:
                remote_event = remote_by_seim.get(seim_id)
                if remote_event and remote_event.get("id"):
                    google_id = remote_event["id"]
                    event_map[seim_id] = google_id
            if google_id:
                if remote_event and _google_fingerprint(remote_event) != _seim_fingerprint(
                    event
                ):
                    conflicts_resolved += 1
                resp = requests.put(
                    f"{base}/{google_id}",
                    headers=headers,
                    json=body,
                    timeout=20,
                )
                if resp.status_code == 404:
                    google_id = None
                else:
                    resp.raise_for_status()
                    updated += 1
                    continue
            resp = requests.post(base, headers=headers, json=body, timeout=20)
            resp.raise_for_status()
            gid = (resp.json() or {}).get("id")
            if gid:
                event_map[seim_id] = gid
            created += 1

        seim_ids = {str(ev.get("id") or "") for ev in events}
        mapped_google_ids = set(event_map.values())
        imported = []
        for item in remote:
            sid = _google_seim_id(item)
            if sid and sid in seim_ids:
                continue
            if item.get("id") in mapped_google_ids:
                continue
            overlay = _overlay_from_google(item)
            if overlay:
                imported.append(overlay)

        conn.event_map = event_map
        conn.imported_events = imported
        conn.last_synced_at = timezone.now()
        conn.last_sync_error = ""
        conn.save(
            update_fields=[
                "event_map",
                "imported_events",
                "last_synced_at",
                "last_sync_error",
                "updated_at",
            ]
        )
        return {
            "created": created,
            "updated": updated,
            "conflicts_resolved": conflicts_resolved,
            "imported": len(imported),
            "total": len(events),
        }
    except Exception as exc:
        conn.last_sync_error = str(exc)
        conn.save(update_fields=["last_sync_error", "updated_at"])
        raise
