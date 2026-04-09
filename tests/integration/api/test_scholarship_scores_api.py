"""API tests for scholarship allocation scoring (staff detail + cohort CSV)."""

from django.urls import reverse
from rest_framework import status

from tests.utils import APITestCase


class TestScholarshipScoresAPI(APITestCase):
    def test_student_detail_omits_scholarship_score(self):
        student = self.create_user(role="student")
        app = self.create_application(student=student, status_name="submitted")
        self.authenticate_user(student)
        url = reverse("api:application-detail", args=[app.id])
        response = self.client.get(url)
        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertIsNone(response.data.get("scholarship_allocation_score"))

    def test_coordinator_detail_includes_score(self):
        student = self.create_user(role="student")
        coordinator = self.create_user(role="coordinator")
        app = self.create_application(student=student, status_name="submitted")
        self.authenticate_user(coordinator)
        url = reverse("api:application-detail", args=[app.id])
        response = self.client.get(url)
        self.assert_response_success(response, status.HTTP_200_OK)
        sc = response.data.get("scholarship_allocation_score")
        self.assertIsNotNone(sc)
        self.assertEqual(sc["ruleset_id"], "default_v1")
        self.assertEqual(len(sc["factors"]), 5)

    def test_export_requires_program_param(self):
        coordinator = self.create_user(role="coordinator")
        self.authenticate_user(coordinator)
        url = reverse("api:application-scholarship-scores-export")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_export_student_forbidden(self):
        student = self.create_user(role="student")
        program = self.create_program()
        self.authenticate_user(student)
        url = reverse("api:application-scholarship-scores-export")
        response = self.client.get(url, {"program": str(program.id)})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_export_coordinator_csv(self):
        program = self.create_program()
        student = self.create_user(role="student")
        self.create_application(student=student, program=program, status_name="submitted")
        coordinator = self.create_user(role="coordinator")
        self.authenticate_user(coordinator)
        url = reverse("api:application-scholarship-scores-export")
        response = self.client.get(url, {"program": str(program.id)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("text/csv", response["Content-Type"])
        body = response.content.decode("utf-8")
        assert "rank" in body.splitlines()[0]
        assert "default_v1" in body
