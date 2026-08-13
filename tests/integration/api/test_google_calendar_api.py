"""Google Calendar OAuth helpers (mocked HTTP)."""

from unittest.mock import patch

from django.core import signing
from django.test import RequestFactory, override_settings
from django.urls import reverse

from accounts.models import GoogleCalendarConnection
from exchange.google_calendar import (
    STATE_SALT,
    build_authorization_url,
    connection_status,
    disconnect,
    exchange_code,
    is_configured,
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
