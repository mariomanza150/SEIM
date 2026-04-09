"""Integration tests for GET /api/notifications/routing-reference/."""

from django.urls import reverse
from rest_framework import status

from tests.utils import APITestCase


class TestNotificationRoutingReferenceAPI(APITestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("api:notification-routing-reference")

    def test_requires_auth(self):
        response = self.client.get(self.url)
        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_student_forbidden(self):
        student = self.create_user(role="student")
        self.authenticate_user(student)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_coordinator_receives_matrix(self):
        coordinator = self.create_user(role="coordinator")
        self.authenticate_user(coordinator)
        response = self.client.get(self.url)
        self.assert_response_success(response)
        self.assertEqual(response.data["schema_version"], 6)
        self.assertIn("coordinator", response.data["reference_api_access"]["roles_any"])
        cats = response.data["settings_categories"]
        self.assertIn("applications", cats)
        self.assertIn("system", cats)
        self.assertIn("typical_triggers", cats["documents"])
        self.assertIn("primary_recipients", cats["comments"])
        self.assertTrue(cats["applications"]["primary_recipients"])
        self.assertEqual(
            cats["applications"]["email_user_settings_field"],
            "email_applications",
        )
        self.assertEqual(
            cats["system"]["inapp_user_settings_field"],
            "inapp_system",
        )
        self.assertIn(
            "application_deadline",
            response.data["reminder_event_type_to_settings_category"],
        )
        rdesc = response.data["reminder_event_type_descriptions"]
        self.assertIn("document_deadline", rdesc)
        self.assertTrue(len(rdesc["document_deadline"]) > 10)
        self.assertEqual(response.data["digest"]["settings_category"], "system")
        self.assertIn("typical_triggers", response.data["digest"])
        self.assertTrue(response.data["digest"]["typical_triggers"])
