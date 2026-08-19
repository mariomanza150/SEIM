"""Admin write access for notification type catalog."""

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from notifications.models import NotificationType

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.views
class TestNotificationTypeCRUD(APITestCase):
    def setUp(self):
        cache.clear()
        self.student = User.objects.create_user(
            username="ntstudent",
            email="ntstudent@example.com",
            password="testpass123",
        )
        self.admin = User.objects.create_user(
            username="ntadmin",
            email="ntadmin@example.com",
            password="adminpass123",
            is_staff=True,
        )
        self.client = APIClient()
        self.list_url = reverse("api:notificationtype-list")
        NotificationType.objects.get_or_create(name="qa_nt_seed")

    def test_student_get_ok_post_forbidden(self):
        self.client.force_authenticate(user=self.student)
        get_response = self.client.get(self.list_url)
        post_response = self.client.post(
            self.list_url, {"name": "custom_alert"}, format="json"
        )

        assert get_response.status_code == status.HTTP_200_OK
        names = {row["name"] for row in get_response.data}
        assert "qa_nt_seed" in names
        assert post_response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_crud_and_invalid_slug(self):
        self.client.force_authenticate(user=self.admin)
        create = self.client.post(
            self.list_url, {"name": "qa_nt_created"}, format="json"
        )
        assert create.status_code == status.HTTP_201_CREATED
        type_id = create.data["id"]

        listed = self.client.get(self.list_url)
        assert listed.status_code == status.HTTP_200_OK
        assert {row["name"] for row in listed.data} >= {"qa_nt_seed", "qa_nt_created"}

        bad = self.client.post(
            self.list_url, {"name": "Bad Type"}, format="json"
        )
        assert bad.status_code == status.HTTP_400_BAD_REQUEST

        detail = reverse("api:notificationtype-detail", args=[type_id])
        patched = self.client.patch(
            detail, {"name": "qa_nt_renamed"}, format="json"
        )
        assert patched.status_code == status.HTTP_200_OK
        assert patched.data["name"] == "qa_nt_renamed"

        deleted = self.client.delete(detail)
        assert deleted.status_code == status.HTTP_204_NO_CONTENT
        assert not NotificationType.objects.filter(id=type_id).exists()

    def test_list_refreshes_after_create(self):
        cache.clear()
        self.client.force_authenticate(user=self.admin)
        first = self.client.get(self.list_url)
        names_before = {row["name"] for row in first.data}

        created = self.client.post(
            self.list_url, {"name": "qa_nt_cached"}, format="json"
        )
        assert created.status_code == status.HTTP_201_CREATED

        second = self.client.get(self.list_url)
        assert {row["name"] for row in second.data} >= {*names_before, "qa_nt_cached"}
