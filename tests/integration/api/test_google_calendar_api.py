"""Google Calendar OAuth helpers (mocked HTTP)."""

from datetime import timedelta
from unittest.mock import patch

from django.core import signing
from django.test import RequestFactory, override_settings
from django.urls import reverse
from django.utils import timezone

from accounts.models import GoogleCalendarConnection
from exchange.calendar_events import build_calendar_event_dicts
from exchange.google_calendar import (
    STATE_SALT,
    build_authorization_url,
    connection_status,
    disconnect,
    exchange_code,
    is_configured,
    sync_user_events,
)
from tests.utils import APITestCase


class TestGoogleCalendarAPI(APITestCase):
    def setUp(self):
        super().setUp()
        self.user = self.create_user(role="student")

    def test_status_unconfigured(self):
        self.authenticate_user(self.user)
        url = reverse("api:calendar-event-google-status")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.data["configured"])
        self.assertFalse(resp.data["connected"])

    @override_settings(
        GOOGLE_OAUTH_CLIENT_ID="cid",
        GOOGLE_OAUTH_CLIENT_SECRET="secret",
    )
    def test_authorize_returns_url(self):
        self.authenticate_user(self.user)
        url = reverse("api:calendar-event-google-authorize")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("accounts.google.com", resp.data["authorization_url"])

    def test_authorize_unconfigured_is_503(self):
        self.authenticate_user(self.user)
        url = reverse("api:calendar-event-google-authorize")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 503)

    @override_settings(
        GOOGLE_OAUTH_CLIENT_ID="cid",
        GOOGLE_OAUTH_CLIENT_SECRET="secret",
        GOOGLE_OAUTH_REDIRECT_URI="http://testserver/api/calendar/events/google-callback/",
    )
    def test_exchange_code_stores_tokens(self):
        rf = RequestFactory()
        request = rf.get("/api/calendar/events/google-callback/")
        state = signing.dumps({"uid": str(self.user.pk), "nonce": "n"}, salt=STATE_SALT)
        token_json = {
            "access_token": "at",
            "refresh_token": "rt",
            "expires_in": 3600,
        }
        with patch("exchange.google_calendar.requests.post") as post, patch(
            "exchange.google_calendar.requests.get"
        ) as get:
            post.return_value.status_code = 200
            post.return_value.json.return_value = token_json
            post.return_value.raise_for_status = lambda: None
            get.return_value.ok = True
            get.return_value.json.return_value = {"email": "u@gmail.com"}
            conn = exchange_code(request, "auth-code", state)
        self.assertEqual(conn.google_email, "u@gmail.com")
        self.assertEqual(conn.refresh_token, "rt")
        self.assertTrue(connection_status(self.user)["connected"])
        disconnect(self.user)
        self.assertFalse(GoogleCalendarConnection.objects.filter(user=self.user).exists())

    def test_is_configured_false_by_default(self):
        self.assertFalse(is_configured())

    def test_two_way_sync_resolves_conflicts_and_imports(self):
        self.create_program()
        seim_events = build_calendar_event_dicts(self.user, event_type="all")
        self.assertTrue(seim_events)
        seim_id = seim_events[0]["id"]
        start = seim_events[0]["start"]
        start_date = start.date().isoformat() if hasattr(start, "date") else str(start)[:10]
        conn = GoogleCalendarConnection.objects.create(
            user=self.user,
            access_token="at",
            refresh_token="rt",
            token_expiry=timezone.now() + timedelta(hours=1),
            event_map={seim_id: "g1"},
        )
        list_payload = {
            "items": [
                {
                    "id": "g1",
                    "summary": "EDITED IN GOOGLE",
                    "start": {"date": start_date},
                    "end": {"date": start_date},
                    "extendedProperties": {"private": {"seim_event_id": seim_id}},
                },
                {
                    "id": "g-ext",
                    "summary": "Office hours",
                    "start": {"dateTime": "2026-09-01T10:00:00+00:00"},
                    "end": {"dateTime": "2026-09-01T11:00:00+00:00"},
                },
            ]
        }

        class FakeResp:
            def __init__(self, payload=None, status=200):
                self._payload = payload or {}
                self.status_code = status

            def json(self):
                return self._payload

            def raise_for_status(self):
                if self.status_code >= 400:
                    raise RuntimeError("http error")

        def fake_get(url, **kwargs):
            return FakeResp(list_payload)

        def fake_put(url, **kwargs):
            return FakeResp({"id": "g1"})

        def fake_post(url, **kwargs):
            return FakeResp({"id": "g-new"})

        with patch("exchange.google_calendar.requests.get", side_effect=fake_get), patch(
            "exchange.google_calendar.requests.put", side_effect=fake_put
        ), patch("exchange.google_calendar.requests.post", side_effect=fake_post):
            result = sync_user_events(self.user)
        self.assertGreaterEqual(result["conflicts_resolved"], 1)
        self.assertEqual(result["imported"], 1)
        conn.refresh_from_db()
        self.assertEqual(len(conn.imported_events), 1)
        self.assertTrue(conn.imported_events[0]["id"].startswith("google-"))

    def test_calendar_list_includes_imported_google_overlay(self):
        GoogleCalendarConnection.objects.create(
            user=self.user,
            access_token="at",
            refresh_token="rt",
            token_expiry=timezone.now() + timedelta(hours=1),
            imported_events=[
                {
                    "id": "google-g-ext",
                    "title": "Office hours",
                    "start": "2026-09-01T10:00:00+00:00",
                    "end": "2026-09-01T11:00:00+00:00",
                    "allDay": False,
                    "source": "google",
                }
            ],
        )
        self.authenticate_user(self.user)
        resp = self.client.get(reverse("api:calendar-event-list"), {"type": "google"})
        self.assertEqual(resp.status_code, 200)
        titles = [row["title"] for row in resp.data]
        self.assertIn("Office hours", titles)
