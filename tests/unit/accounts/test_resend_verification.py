"""Tests for per-email resend-verification cooldown."""

import uuid

from django.core.cache import cache
from django.test import override_settings
from django.urls import reverse
from rest_framework import status

from accounts.resend_verification import (
    RESEND_VERIFICATION_COOLDOWN_SECONDS,
    mark_resend_verification_sent,
)
from tests.utils import APITestCase, TestUtils

LOC_MEM_CACHE = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "resend-verification-tests",
    }
}


@override_settings(CACHES=LOC_MEM_CACHE)
class TestResendVerificationAPI(APITestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("accounts:resend_verification")
        self.uid = uuid.uuid4().hex[:8]
        cache.clear()

    def test_first_resend_succeeds(self):
        email = f"unverified_{self.uid}@example.com"
        TestUtils.create_test_user(email=email, is_email_verified=False)

        response = self.client.post(self.url, {"email": email}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)

    def test_second_resend_same_email_is_rate_limited(self):
        email = f"unverified_{self.uid}@example.com"
        TestUtils.create_test_user(email=email, is_email_verified=False)

        first = self.client.post(self.url, {"email": email}, format="json")
        self.assertEqual(first.status_code, status.HTTP_200_OK)

        second = self.client.post(self.url, {"email": email}, format="json")
        self.assertEqual(second.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(second.data.get("code"), "resend_verification_rate_limited")
        self.assertIn("Retry-After", second)
        retry_after = int(second["Retry-After"])
        self.assertGreater(retry_after, 0)
        self.assertLessEqual(retry_after, RESEND_VERIFICATION_COOLDOWN_SECONDS)

    def test_different_email_still_allowed(self):
        email_a = f"a_{self.uid}@example.com"
        email_b = f"b_{self.uid}@example.com"
        TestUtils.create_test_user(email=email_a, is_email_verified=False)
        TestUtils.create_test_user(email=email_b, is_email_verified=False)

        first = self.client.post(self.url, {"email": email_a}, format="json")
        self.assertEqual(first.status_code, status.HTTP_200_OK)

        other = self.client.post(self.url, {"email": email_b}, format="json")
        self.assertEqual(other.status_code, status.HTTP_200_OK)

    def test_already_verified_does_not_block_other_email(self):
        verified = f"verified_{self.uid}@example.com"
        unverified = f"unverified_{self.uid}@example.com"
        TestUtils.create_test_user(email=verified, is_email_verified=True)
        TestUtils.create_test_user(email=unverified, is_email_verified=False)

        bad = self.client.post(self.url, {"email": verified}, format="json")
        self.assertEqual(bad.status_code, status.HTTP_400_BAD_REQUEST)

        ok = self.client.post(self.url, {"email": unverified}, format="json")
        self.assertEqual(ok.status_code, status.HTTP_200_OK)

    def test_already_verified_twice_still_400_not_429(self):
        email = f"verified_{self.uid}@example.com"
        TestUtils.create_test_user(email=email, is_email_verified=True)

        first = self.client.post(self.url, {"email": email}, format="json")
        second = self.client.post(self.url, {"email": email}, format="json")

        self.assertEqual(first.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST)

    def test_mark_helper_is_used_by_cooldown(self):
        email = f"helper_{self.uid}@example.com"
        TestUtils.create_test_user(email=email, is_email_verified=False)
        mark_resend_verification_sent(email)

        response = self.client.post(self.url, {"email": email}, format="json")
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
