"""IDOR guards for notification preferences and batch_send."""

from unittest.mock import patch

from django.urls import reverse
from rest_framework import status

from notifications.models import NotificationPreference, NotificationType
from tests.utils import APITestCase


class TestNotificationPreferenceIsolationAPI(APITestCase):
    def setUp(self):
        super().setUp()
        self.owner = self.create_user(
            role="student", username="pref_owner", email="pref_owner@example.com"
        )
        self.other = self.create_user(
            role="student", username="pref_other", email="pref_other@example.com"
        )
        self.coordinator = self.create_user(
            role="coordinator", username="pref_coord", email="pref_coord@example.com"
        )
        self.ntype = NotificationType.objects.create(name="pref_isolation_type")
        self.owner_pref = NotificationPreference.objects.create(
            user=self.owner, type=self.ntype, enabled=True
        )
        self.other_pref = NotificationPreference.objects.create(
            user=self.other, type=self.ntype, enabled=False
        )
        self.list_url = reverse("api:notificationpreference-list")

    def test_list_only_own_preferences(self):
        self.authenticate_user(self.owner)
        response = self.client.get(self.list_url)
        self.assert_response_success(response)
        results = response.data.get("results", response.data)
        ids = {str(row["id"]) for row in results}
        self.assertIn(str(self.owner_pref.id), ids)
        self.assertNotIn(str(self.other_pref.id), ids)

    def test_retrieve_other_preference_is_404(self):
        self.authenticate_user(self.owner)
        response = self.client.get(
            reverse(
                "api:notificationpreference-detail", kwargs={"pk": self.other_pref.pk}
            )
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_patch_other_preference(self):
        self.authenticate_user(self.owner)
        response = self.client.patch(
            reverse(
                "api:notificationpreference-detail", kwargs={"pk": self.other_pref.pk}
            ),
            {"enabled": True},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.other_pref.refresh_from_db()
        self.assertFalse(self.other_pref.enabled)

    def test_create_binds_to_request_user(self):
        self.authenticate_user(self.owner)
        ntype = NotificationType.objects.create(name="pref_create_type")
        response = self.client.post(
            self.list_url,
            {"type": ntype.id, "enabled": False, "user": self.other.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        pref = NotificationPreference.objects.get(id=response.data["id"])
        self.assertEqual(pref.user_id, self.owner.id)
        self.assertNotEqual(pref.user_id, self.other.id)

    def test_student_batch_send_forbidden(self):
        self.authenticate_user(self.owner)
        response = self.client.post(
            reverse("api:notification-batch-send"),
            {
                "users": [str(self.other.id)],
                "type_name": "email",
                "message": "hello",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_coordinator_batch_send_allowed(self):
        self.authenticate_user(self.coordinator)
        with patch(
            "notifications.views.NotificationService.batch_send_notifications",
            return_value=["ok"],
            create=True,
        ) as mock_send:
            response = self.client.post(
                reverse("api:notification-batch-send"),
                {
                    "users": [str(self.other.id)],
                    "type_name": "email",
                    "message": "hello",
                },
                format="json",
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"sent": 1})
        mock_send.assert_called_once()
