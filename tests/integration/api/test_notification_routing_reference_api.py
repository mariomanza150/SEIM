"""Integration tests for GET /api/notifications/routing-reference/."""

from django.urls import reverse
from rest_framework import status

from notifications.models import NotificationRoutingOverride
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

        NotificationRoutingOverride.objects.create(
            kind=NotificationRoutingOverride.KIND_REMINDER_EVENT_TYPE,
            key="application_deadline",
            settings_category="documents",
            is_active=True,
        )
        NotificationRoutingOverride.objects.create(
            kind=NotificationRoutingOverride.KIND_TRANSACTIONAL_ROUTE_KEY,
            key="application_submitted",
            settings_category="system",
            is_active=True,
        )

        response = self.client.get(self.url)
        self.assert_response_success(response)
        self.assertEqual(response.data["schema_version"], 12)
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
        self.assertEqual(
            response.data["reminder_event_type_to_settings_category"]["application_deadline"],
            "documents",
        )
        rsum = response.data["reminder_event_type_recipient_summaries"]
        self.assertIn("application_deadline", rsum)
        self.assertIn("reminder owner", rsum["application_deadline"].lower())
        tx_idx = response.data["transactional_route_keys_by_settings_category"]
        self.assertIn("ungated", tx_idx)
        self.assertIn("application_submitted", tx_idx["system"])
        rem_idx = response.data["reminder_event_types_by_settings_category"]
        self.assertIn("application_deadline", rem_idx["documents"])
        rdesc = response.data["reminder_event_type_descriptions"]
        self.assertIn("document_deadline", rdesc)
        self.assertTrue(len(rdesc["document_deadline"]) > 10)
        self.assertEqual(response.data["digest"]["settings_category"], "system")
        self.assertIn("typical_triggers", response.data["digest"])
        self.assertTrue(response.data["digest"]["typical_triggers"])
        self.assertIn(
            "digest job",
            response.data["digest"]["recipient_summary"].lower(),
        )
        routes = response.data["transactional_routes"]
        self.assertIsInstance(routes, list)
        self.assertGreaterEqual(len(routes), 10)
        self.assertEqual(routes[0]["route_key"], "account_security_email")
        self.assertIsNone(routes[0]["settings_category"])
        self.assertIn("end user", routes[0]["recipient_summary"].lower())
