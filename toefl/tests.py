import json

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

    def test_webhook_rejects_bad_signature(self):
        payload = {
            "session_id": "sess-bad",
            "client_ref": str(self.user.pk),
            "score": {"earned": 1, "total": 1, "percent": 100},
        }
        resp = self._signed_post(payload, secret="wrong-secret")
        self.assertEqual(resp.status_code, 401)
        self.assertFalse(PracticeAttempt.objects.filter(external_session_id="sess-bad").exists())

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
