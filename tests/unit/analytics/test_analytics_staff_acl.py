"""Regression: students must not read institution-wide analytics APIs."""

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from tests.utils import TestUtils


@pytest.mark.django_db
class TestAnalyticsStaffAcl:
    def setup_method(self):
        self.student = TestUtils.create_test_user(
            username="analytics_acl_student",
            email="analytics_acl_student@example.com",
            role="student",
        )
        self.coordinator = TestUtils.create_test_user(
            username="analytics_acl_coord",
            email="analytics_acl_coord@example.com",
            role="coordinator",
        )
        self.client = APIClient()

    def test_student_denied_application_statistics(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get(reverse("analytics:api_application_statistics"))
        assert response.status_code == 403

    def test_student_denied_dashboard_and_user_report(self):
        self.client.force_authenticate(user=self.student)
        dash = self.client.get(reverse("api:analytics-dashboard"))
        users = self.client.get(
            reverse("api:analytics-report-detail", kwargs={"report_type": "users"})
        )
        export = self.client.get(reverse("api:analytics-export"))
        assert dash.status_code == 403
        assert users.status_code == 403
        assert export.status_code == 403

    def test_student_denied_metrics_viewset(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get("/api/metrics/")
        assert response.status_code == 403

    def test_coordinator_can_read_dashboard(self):
        self.client.force_authenticate(user=self.coordinator)
        response = self.client.get(reverse("api:analytics-dashboard"))
        assert response.status_code == 200
        assert "metrics" in response.data
