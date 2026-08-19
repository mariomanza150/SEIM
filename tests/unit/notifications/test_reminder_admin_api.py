"""Admin listing and assignment for reminders."""

from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from notifications.models import Reminder

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.views
class TestReminderAdminAccess(APITestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username="remstudent",
            email="remstudent@example.com",
            password="testpass123",
        )
        self.admin = User.objects.create_user(
            username="remadmin",
            email="remadmin@example.com",
            password="adminpass123",
            is_staff=True,
        )
        self.other_reminder = Reminder.objects.create(
            user=self.student,
            event_type="custom",
            event_id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            event_title="Student reminder",
            remind_at=timezone.now() + timedelta(days=2),
        )
        self.client = APIClient()
        self.list_url = reverse("api:reminder-list")

    def test_student_does_not_see_admin_created_foreign_rows_when_listing_own(self):
        Reminder.objects.create(
            user=self.admin,
            event_type="custom",
            event_id="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
            event_title="Admin reminder",
            remind_at=timezone.now() + timedelta(days=3),
        )
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        titles = {row["event_title"] for row in response.data["results"]}
        assert titles == {"Student reminder"}

    def test_admin_lists_all_and_creates_for_another_user(self):
        self.client.force_authenticate(user=self.admin)
        listed = self.client.get(self.list_url)
        assert listed.status_code == status.HTTP_200_OK
        titles = {row["event_title"] for row in listed.data["results"]}
        assert "Student reminder" in titles

        created = self.client.post(
            self.list_url,
            {
                "user": self.student.id,
                "event_type": "custom",
                "event_id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
                "event_title": "Assigned reminder",
                "remind_at": (timezone.now() + timedelta(days=4)).isoformat(),
            },
            format="json",
        )
        assert created.status_code == status.HTTP_201_CREATED
        assert str(created.data["user"]) == str(self.student.id)
        assert created.data["user_email"] == self.student.email
        assert Reminder.objects.filter(
            event_title="Assigned reminder", user=self.student
        ).exists()
