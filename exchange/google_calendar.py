"""Google Calendar OAuth2 linking and one-way push of SEIM events."""

from __future__ import annotations

import uuid
from datetime import timedelta
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


def sync_user_events(user) -> dict:
    """Push SEIM calendar events to the user's primary Google Calendar (upsert by seim id)."""
    conn = GoogleCalendarConnection.objects.filter(user=user).first()
    if not conn or not conn.is_connected:
        raise ValueError("Google Calendar is not connected.")
    token = _ensure_access_token(conn)
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    events = build_calendar_event_dicts(user, event_type="all")
    event_map = dict(conn.event_map or {})
    created = 0
    updated = 0
    calendar_id = conn.google_calendar_id or "primary"
    base = GOOGLE_EVENTS_URL.format(calendar_id=calendar_id)
    try:
        for event in events:
            seim_id = str(event.get("id") or "")
            if not seim_id:
                continue
            body = _event_body(event)
            google_id = event_map.get(seim_id)
            if google_id:
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
        conn.event_map = event_map
        conn.last_synced_at = timezone.now()
        conn.last_sync_error = ""
        conn.save(
            update_fields=[
                "event_map",
                "last_synced_at",
                "last_sync_error",
                "updated_at",
            ]
        )
        return {"created": created, "updated": updated, "total": len(events)}
    except Exception as exc:
        conn.last_sync_error = str(exc)
        conn.save(update_fields=["last_sync_error", "updated_at"])
        raise
