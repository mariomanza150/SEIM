"""Tests for GET /api/accounts/dashboard/coordinator-workload/."""

from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from exchange.models import Application
from tests.utils import APITestCase


class TestCoordinatorWorkloadAPI(APITestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("api:accounts:coordinator_workload")

    def test_requires_staff(self):
        student = self.create_user(role="student")
        self.authenticate_user(student)
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_coordinator_sees_you_block_not_global(self):
        coord = self.create_user(role="coordinator")
        student = self.create_user(role="student")
        p = self.create_program()
        p.coordinators.add(coord)
        self.create_application(
            student=student,
            program=p,
            status_name="submitted",
            assigned_coordinator=coord,
        )

        self.authenticate_user(coord)
        r = self.client.get(self.url)
        self.assert_response_success(r)
        self.assertEqual(r.data["you"]["assigned_pending_review"], 1)
        self.assertEqual(r.data["you"]["coordinated_programs_pending"], 1)
        self.assertIsNone(r.data["global"])
        self.assertIsNone(r.data["distribution"])

    def test_admin_sees_global_and_distribution(self):
        admin = self.create_user(role="admin")
        c1 = self.create_user(role="coordinator", username="coord_one")
        c2 = self.create_user(role="coordinator", username="coord_two")
        student = self.create_user(role="student")
        p = self.create_program()
        self.create_application(
            student=student,
            program=p,
            status_name="submitted",
            assigned_coordinator=c1,
        )
        self.create_application(
            student=student,
            program=p,
            status_name="under_review",
            assigned_coordinator=c2,
        )

        self.authenticate_user(admin)
        r = self.client.get(self.url)
        self.assert_response_success(r)
        self.assertIsNotNone(r.data["global"])
        self.assertEqual(r.data["global"]["pending_review_total"], 2)
        self.assertEqual(r.data["global"]["unassigned_pending_review"], 0)
        dist = r.data["distribution"]
        self.assertIsInstance(dist, list)
        by_id = {row["coordinator_id"]: row["assigned_pending_review"] for row in dist}
        self.assertEqual(by_id[str(c1.id)], 1)
        self.assertEqual(by_id[str(c2.id)], 1)

    def test_stale_under_review_count(self):
        admin = self.create_user(role="admin")
        student = self.create_user(role="student")
        p = self.create_program()
        app = self.create_application(
            student=student,
            program=p,
            status_name="under_review",
        )
        old = timezone.now() - timedelta(days=20)
        Application.objects.filter(pk=app.pk).update(updated_at=old)

        self.authenticate_user(admin)
        r = self.client.get(self.url)
        self.assert_response_success(r)
        self.assertGreaterEqual(r.data["global"]["stale_under_review_14d"], 1)
