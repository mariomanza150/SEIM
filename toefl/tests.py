import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from accounts.models import Profile
from toefl.models import PracticeAttempt
from toefl.security import sign_payload

User = get_user_model()


@override_settings(
    TOEFL_SIGNING_SECRET="test-signing-secret",
    TOEFL_API_BASE_URL="http://toefl.test",
    TOEFL_API_KEY="test-api-key",
    TOEFL_CALLBACK_URL="http://web:8000/api/toefl/webhook/",
    TOEFL_RETURN_URL="http://localhost/seim/toefl-practice",
    TOEFL_DEFAULT_EXAM_CODE="director_extracted",
)
class ToeflWebhookTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="student1",
            email="student1@example.com",
            password="pass12345",
        )
        Profile.objects.get_or_create(user=self.user)
        self.user.profile.toefl_score = 550
        self.user.profile.save(update_fields=["toefl_score"])

    def _signed_post(self, payload: dict, secret: str = "test-signing-secret"):
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode(
            "utf-8"
        )
        return self.client.generic(
            "POST",
            "/api/toefl/webhook/",
            data=body,
            content_type="application/json",
            HTTP_X_WEBHOOK_SIGNATURE=sign_payload(body, secret),
        )

    def test_webhook_creates_attempt_without_touching_profile_score(self):
        payload = {
            "session_id": "sess-abc",
            "client_ref": str(self.user.pk),
            "exam_code": "director_extracted",
            "macro_id": "all",
            "completed_at": "2026-08-30T18:00:00+00:00",
            "score": {"earned": 8, "total": 10, "percent": 80.0},
            "categories": [{"name": "verbs", "percent": 50}],
            "weakest": [{"name": "verbs"}],
            "items": [],
        }
        resp = self._signed_post(payload)
        self.assertIn(resp.status_code, (200, 201))
        attempt = PracticeAttempt.objects.get(external_session_id="sess-abc")
        self.assertEqual(attempt.user_id, self.user.pk)
        self.assertEqual(attempt.percent, 80.0)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.toefl_score, 550)

    def test_webhook_upsert_is_idempotent(self):
        payload = {
            "session_id": "sess-upsert",
            "client_ref": str(self.user.pk),
            "exam_code": "director_extracted",
            "score": {"earned": 5, "total": 10, "percent": 50.0},
            "categories": [{"name": "verbs"}],
            "weakest": [],
            "items": [],
        }
        first = self._signed_post(payload)
        self.assertIn(first.status_code, (200, 201))
        payload["score"] = {"earned": 9, "total": 10, "percent": 90.0}
        second = self._signed_post(payload)
        self.assertIn(second.status_code, (200, 201))
        self.assertEqual(
            PracticeAttempt.objects.filter(external_session_id="sess-upsert").count(),
            1,
        )
        attempt = PracticeAttempt.objects.get(external_session_id="sess-upsert")
        self.assertEqual(attempt.earned, 9)
        self.assertEqual(attempt.percent, 90.0)

    def test_webhook_rejects_bad_signature(self):
        payload = {
            "session_id": "sess-bad",
            "client_ref": str(self.user.pk),
            "score": {"earned": 1, "total": 1, "percent": 100},
        }
        resp = self._signed_post(payload, secret="wrong-secret")
        self.assertEqual(resp.status_code, 401)
        self.assertFalse(
            PracticeAttempt.objects.filter(external_session_id="sess-bad").exists()
        )

    def test_attempts_list_requires_auth_and_scopes_to_owner(self):
        PracticeAttempt.objects.create(
            user=self.user,
            external_session_id="sess-1",
            percent=70,
            earned=7,
            total=10,
        )
        other = User.objects.create_user(
            username="other", email="other@example.com", password="pass12345"
        )
        PracticeAttempt.objects.create(
            user=other,
            external_session_id="sess-2",
            percent=90,
            earned=9,
            total=10,
        )
        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/toefl/attempts/")
        self.assertEqual(resp.status_code, 200)
        results = resp.data.get("results", resp.data)
        ids = {row["external_session_id"] for row in results}
        self.assertEqual(ids, {"sess-1"})


@override_settings(
    TOEFL_SIGNING_SECRET="test-signing-secret",
    TOEFL_API_BASE_URL="http://toefl.test",
    TOEFL_API_KEY="test-api-key",
    TOEFL_CALLBACK_URL="http://web:8000/api/toefl/webhook/",
    TOEFL_RETURN_URL="http://localhost/seim/toefl-practice",
    TOEFL_DEFAULT_EXAM_CODE="director_extracted",
)
class ToeflLaunchTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="launcher",
            email="launcher@example.com",
            password="pass12345",
        )
        self.client.force_authenticate(user=self.user)

    @patch("toefl.views.create_launch_token")
    def test_launch_happy_path(self, mock_create):
        mock_create.return_value = {
            "launch_url": "https://toefl.example/launch?token=tok",
            "token": "tok",
        }
        resp = self.client.post("/api/toefl/launch/", {"n": 20}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["launch_url"], "https://toefl.example/launch?token=tok")
        mock_create.assert_called_once()
        kwargs = mock_create.call_args.kwargs
        self.assertEqual(kwargs["client_ref"], str(self.user.pk))
        self.assertEqual(kwargs["exam_code"], "director_extracted")
        self.assertEqual(kwargs["n"], 20)
        self.assertEqual(
            kwargs["callback_url"], "http://web:8000/api/toefl/webhook/"
        )
        self.assertEqual(
            kwargs["return_url"], "http://localhost/seim/toefl-practice"
        )

    @override_settings(TOEFL_CALLBACK_URL="", TOEFL_RETURN_URL="")
    def test_launch_missing_config_returns_503(self):
        resp = self.client.post("/api/toefl/launch/", {"n": 20}, format="json")
        self.assertEqual(resp.status_code, 503)
        self.assertIn("not configured", resp.data["detail"].lower())

    def test_launch_requires_auth(self):
        self.client.force_authenticate(user=None)
        resp = self.client.post("/api/toefl/launch/", {"n": 20}, format="json")
        self.assertIn(resp.status_code, (401, 403))
