"""Admin write access for application status catalog."""

from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from exchange.models import Application, ApplicationStatus, Program

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.views
class TestApplicationStatusCRUD(APITestCase):
    def setUp(self):
        cache.clear()
        self.student = User.objects.create_user(
            username="statusstudent",
            email="statusstudent@example.com",
            password="testpass123",
        )
        self.admin = User.objects.create_user(
            username="statusadmin",
            email="statusadmin@example.com",
            password="adminpass123",
            is_staff=True,
        )
        self.client = APIClient()
        self.list_url = reverse("api:applicationstatus-list")
        self.seed, _ = ApplicationStatus.objects.get_or_create(
            name="qa_status_seed", defaults={"order": 1}
        )

    def test_student_get_ok_post_forbidden(self):
        self.client.force_authenticate(user=self.student)
        get_response = self.client.get(self.list_url)
        post_response = self.client.post(
            self.list_url, {"name": "custom_status", "order": 9}, format="json"
        )

        assert get_response.status_code == status.HTTP_200_OK
        names = {row["name"] for row in get_response.data}
        assert "qa_status_seed" in names
        assert post_response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_crud_rejects_invalid_slug_and_protects_in_use(self):
        self.client.force_authenticate(user=self.admin)
        create = self.client.post(
            self.list_url, {"name": "qa_status_created", "order": 8}, format="json"
        )
        assert create.status_code == status.HTTP_201_CREATED
        status_id = create.data["id"]

        listed = self.client.get(self.list_url)
        assert listed.status_code == status.HTTP_200_OK
        assert {row["name"] for row in listed.data} >= {
            "qa_status_seed",
            "qa_status_created",
        }

        bad = self.client.post(
            self.list_url, {"name": "Not A Slug", "order": 2}, format="json"
        )
        assert bad.status_code == status.HTTP_400_BAD_REQUEST

        detail = reverse("api:applicationstatus-detail", args=[status_id])
        patched = self.client.patch(detail, {"order": 12}, format="json")
        assert patched.status_code == status.HTTP_200_OK
        assert patched.data["order"] == 12

        unused = ApplicationStatus.objects.create(name="qa_status_unused", order=99)
        unused_url = reverse("api:applicationstatus-detail", args=[unused.id])
        deleted = self.client.delete(unused_url)
        assert deleted.status_code == status.HTTP_204_NO_CONTENT
        assert not ApplicationStatus.objects.filter(id=unused.id).exists()

        program = Program.objects.create(
            name="Status Program",
            description="For protect test",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
        )
        in_use = ApplicationStatus.objects.create(name="qa_status_in_use", order=20)
        Application.objects.create(
            student=self.student, program=program, status=in_use
        )
        blocked = self.client.delete(
            reverse("api:applicationstatus-detail", args=[in_use.id])
        )
        assert blocked.status_code == status.HTTP_400_BAD_REQUEST
        assert ApplicationStatus.objects.filter(id=in_use.id).exists()

    def test_list_refreshes_after_create(self):
        cache.clear()
        self.client.force_authenticate(user=self.admin)
        first = self.client.get(self.list_url)
        assert first.status_code == status.HTTP_200_OK
        names_before = {row["name"] for row in first.data}

        created = self.client.post(
            self.list_url, {"name": "qa_status_cached", "order": 15}, format="json"
        )
        assert created.status_code == status.HTTP_201_CREATED

        second = self.client.get(self.list_url)
        assert second.status_code == status.HTTP_200_OK
        assert {row["name"] for row in second.data} >= {*names_before, "qa_status_cached"}
