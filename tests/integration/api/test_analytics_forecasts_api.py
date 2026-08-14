"""Predictive analytics forecasts for staff."""

from django.urls import reverse

from tests.utils import APITestCase


class TestAnalyticsForecastsAPI(APITestCase):
    def setUp(self):
        super().setUp()
        self.coord = self.create_user(role="coordinator")
        self.student = self.create_user(role="student")
        self.program = self.create_program()
        self.create_application(
            student=self.student, program=self.program, status_name="submitted"
        )

    def test_coordinator_can_read_forecasts(self):
        self.authenticate_user(self.coord)
        url = reverse("api:admin-dashboard-forecasts")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("demand", resp.data)
        self.assertIn("forecast", resp.data["demand"])
        self.assertIn("bottlenecks", resp.data)
        self.assertIn("deadline_risk", resp.data)
        self.assertEqual(len(resp.data["demand"]["history"]), 8)
        self.assertEqual(len(resp.data["demand"]["forecast"]), 4)

    def test_student_forbidden(self):
        self.authenticate_user(self.student)
        url = reverse("api:admin-dashboard-forecasts")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 403)
