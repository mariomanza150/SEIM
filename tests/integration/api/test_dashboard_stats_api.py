"""Integration tests for GET /api/accounts/dashboard/stats/."""

from django.urls import reverse
from rest_framework import status

from tests.utils import APITestCase


class TestDashboardStatsAPI(APITestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("api:accounts:dashboard_stats")

    def test_requires_auth(self):
        response = self.client.get(self.url)
        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_student_counts_only_own_applications(self):
        student = self.create_user(role="student")
        other = self.create_user(role="student")
        p1 = self.create_program()
        p2 = self.create_program()
        self.create_application(student=student, program=p1, status_name="draft")
        self.create_application(student=other, program=p2, status_name="draft")

        self.authenticate_user(student)
        response = self.client.get(self.url)
        self.assert_response_success(response)
        self.assertEqual(response.data["applications"], 1)
        self.assertEqual(response.data["pending"], 1)

    def test_coordinator_sees_all_application_count_and_staff_pending(self):
        student = self.create_user(role="student")
        coordinator = self.create_user(role="coordinator")
        p1 = self.create_program()
        p2 = self.create_program()
        self.create_application(student=student, program=p1, status_name="draft")
        self.create_application(student=student, program=p2, status_name="submitted", withdrawn=False)

        self.authenticate_user(coordinator)
        response = self.client.get(self.url)
        self.assert_response_success(response)
        self.assertEqual(response.data["applications"], 2)
        self.assertEqual(response.data["pending"], 1)
