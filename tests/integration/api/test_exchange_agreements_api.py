from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Role
from exchange.models import ExchangeAgreement, Program

User = get_user_model()


def _grant_role(user, role_name: str):
    role, _ = Role.objects.get_or_create(name=role_name)
    user.roles.add(role)


class ExchangeAgreementsAPITests(APITestCase):
    def setUp(self):
        self.url = reverse("api:exchange-agreement-list")

    def test_student_forbidden(self):
        student = User.objects.create_user(
            username="stu_ag", email="stu_ag@example.com", password="pass12345"
        )
        _grant_role(student, "student")
        self.client.force_authenticate(student)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_coordinator_can_list_and_create(self):
        coordinator = User.objects.create_user(
            username="coord_ag", email="coord_ag@example.com", password="pass12345"
        )
        _grant_role(coordinator, "coordinator")
        self.client.force_authenticate(coordinator)

        today = timezone.localdate()
        program = Program.objects.create(
            name="Test Program AG",
            description="Desc",
            start_date=today + timedelta(days=60),
            end_date=today + timedelta(days=300),
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        payload = {
            "title": "Bilateral accord",
            "partner_institution_name": "Example University",
            "partner_country": "Spain",
            "agreement_type": ExchangeAgreement.AgreementType.BILATERAL,
            "status": ExchangeAgreement.Status.ACTIVE,
            "programs": [str(program.id)],
        }
        create_resp = self.client.post(self.url, payload, format="json")
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED, create_resp.data)
        self.assertEqual(ExchangeAgreement.objects.count(), 1)
        agreement = ExchangeAgreement.objects.get()
        self.assertEqual(list(agreement.programs.all()), [program])

    def test_filter_expiring_within_days_query_param(self):
        coordinator = User.objects.create_user(
            username="coord_ag2", email="coord_ag2@example.com", password="pass12345"
        )
        _grant_role(coordinator, "coordinator")
        self.client.force_authenticate(coordinator)
        today = timezone.localdate()

        ExchangeAgreement.objects.create(
            title="E1",
            partner_institution_name="P1",
            status=ExchangeAgreement.Status.ACTIVE,
            start_date=today - timedelta(days=1),
            end_date=today + timedelta(days=10),
        )
        ExchangeAgreement.objects.create(
            title="E2",
            partner_institution_name="P2",
            status=ExchangeAgreement.Status.ACTIVE,
            start_date=today,
            end_date=today + timedelta(days=100),
        )

        response = self.client.get(self.url, {"expiring_within_days": "30"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "E1")

    def test_mark_renewal_pending_action(self):
        coordinator = User.objects.create_user(
            username="coord_ren_api", email="cra@example.com", password="pass12345"
        )
        _grant_role(coordinator, "coordinator")
        self.client.force_authenticate(coordinator)
        today = timezone.localdate()
        ag = ExchangeAgreement.objects.create(
            title="Renew me",
            partner_institution_name="Uni",
            status=ExchangeAgreement.Status.ACTIVE,
            start_date=today - timedelta(days=1),
            end_date=today + timedelta(days=50),
        )
        url = reverse(
            "api:exchange-agreement-mark-renewal-pending",
            kwargs={"pk": str(ag.id)},
        )
        with patch("exchange.agreement_renewal._notify_staff"):
            resp = self.client.post(
                url, {"renewal_follow_up_due": str(today + timedelta(days=7))}, format="json"
            )
        self.assertEqual(resp.status_code, status.HTTP_200_OK, resp.data)
        ag.refresh_from_db()
        self.assertEqual(ag.status, ExchangeAgreement.Status.RENEWAL_PENDING)

    def test_create_renewal_successor_action(self):
        coordinator = User.objects.create_user(
            username="coord_succ", email="cs@example.com", password="pass12345"
        )
        _grant_role(coordinator, "coordinator")
        self.client.force_authenticate(coordinator)
        today = timezone.localdate()
        ag = ExchangeAgreement.objects.create(
            title="Parent",
            partner_institution_name="Uni",
            status=ExchangeAgreement.Status.ACTIVE,
            start_date=today - timedelta(days=1),
            end_date=today + timedelta(days=50),
        )
        url = reverse(
            "api:exchange-agreement-create-renewal-successor",
            kwargs={"pk": str(ag.id)},
        )
        with patch("exchange.agreement_renewal._notify_staff"):
            resp = self.client.post(url, {"copy_documents": False}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, resp.data)
        self.assertEqual(resp.data["status"], ExchangeAgreement.Status.DRAFT)
        self.assertEqual(str(resp.data["renewed_from"]), str(ag.id))
