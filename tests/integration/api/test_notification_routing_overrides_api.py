"""Integration tests for /api/notification-routing-overrides/."""

from django.urls import reverse
from rest_framework import status

from notifications.models import NotificationRoutingOverride
from tests.utils import APITestCase


class TestNotificationRoutingOverridesAPI(APITestCase):
    def setUp(self):
        super().setUp()
        self.list_url = reverse("api:notification-routing-override-list")

    def test_requires_auth(self):
        response = self.client.get(self.list_url)
        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_student_forbidden(self):
        student = self.create_user(role="student")
        self.authenticate_user(student)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_coordinator_can_crud_overrides(self):
        coordinator = self.create_user(role="coordinator")
        self.authenticate_user(coordinator)

        # Create
        payload = {
            "kind": NotificationRoutingOverride.KIND_REMINDER_EVENT_TYPE,
            "key": "application_deadline",
            "settings_category": NotificationRoutingOverride.SETTINGS_CATEGORY_DOCUMENTS,
            "is_active": True,
        }
        create_resp = self.client.post(self.list_url, payload, format="json")
        self.assert_response_success(create_resp, status_code=status.HTTP_201_CREATED)
        override_id = create_resp.data["id"]
        detail_url = reverse("api:notification-routing-override-detail", args=[override_id])

        # List contains it
        list_resp = self.client.get(self.list_url)
        self.assert_response_success(list_resp)
        rows = (
            list_resp.data.get("results", [])
            if isinstance(list_resp.data, dict)
            else list_resp.data
        )
        ids = {row["id"] for row in rows}
        self.assertIn(override_id, ids)

        # Patch deactivate
        patch_resp = self.client.patch(detail_url, {"is_active": False}, format="json")
        self.assert_response_success(patch_resp)
        self.assertEqual(patch_resp.data["is_active"], False)

        # Delete
        del_resp = self.client.delete(detail_url)
        self.assertEqual(del_resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(NotificationRoutingOverride.objects.filter(id=override_id).exists())

