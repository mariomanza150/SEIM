"""Regression: notification prefs and batch_send must not leak across users."""

import pytest
from rest_framework.test import APIClient

from notifications.models import Notification, NotificationPreference, NotificationType
from tests.utils import TestUtils


@pytest.mark.django_db
class TestNotificationPrefsAndBatchSendAcl:
    def setup_method(self):
        self.student_a = TestUtils.create_test_user(
            username="notif_acl_a",
            email="notif_acl_a@example.com",
            role="student",
        )
        self.student_b = TestUtils.create_test_user(
            username="notif_acl_b",
            email="notif_acl_b@example.com",
            role="student",
        )
        self.coordinator = TestUtils.create_test_user(
            username="notif_acl_coord",
            email="notif_acl_coord@example.com",
            role="coordinator",
        )
        self.n_type, _ = NotificationType.objects.get_or_create(name="acl_info")
        self.pref_a = NotificationPreference.objects.create(
            user=self.student_a, type=self.n_type, enabled=True
        )
        self.pref_b = NotificationPreference.objects.create(
            user=self.student_b, type=self.n_type, enabled=True
        )
        self.client = APIClient()

    def test_student_list_only_own_preferences(self):
        self.client.force_authenticate(user=self.student_a)
        response = self.client.get("/api/notification-preferences/")
        assert response.status_code == 200
        results = response.data.get("results", response.data)
        user_ids = {str(row["user"]) for row in results}
        assert user_ids == {str(self.student_a.id)}

    def test_student_cannot_patch_other_preference(self):
        self.client.force_authenticate(user=self.student_a)
        response = self.client.patch(
            f"/api/notification-preferences/{self.pref_b.id}/",
            {"enabled": False},
            format="json",
        )
        assert response.status_code in (403, 404)
        self.pref_b.refresh_from_db()
        assert self.pref_b.enabled is True

    def test_student_batch_send_forbidden(self):
        self.client.force_authenticate(user=self.student_a)
        before = Notification.objects.filter(recipient=self.student_b).count()
        response = self.client.post(
            "/api/notifications/batch_send/",
            {
                "users": [str(self.student_b.id)],
                "title": "Ping",
                "message": "hello",
            },
            format="json",
        )
        assert response.status_code == 403
        assert Notification.objects.filter(recipient=self.student_b).count() == before

    def test_coordinator_batch_send_ok(self):
        self.client.force_authenticate(user=self.coordinator)
        response = self.client.post(
            "/api/notifications/batch_send/",
            {
                "users": [str(self.student_b.id)],
                "title": "Staff notice",
                "message": "Please update your profile.",
            },
            format="json",
        )
        assert response.status_code == 200
        assert response.data["sent"] == 1
        assert Notification.objects.filter(
            recipient=self.student_b, title="Staff notice"
        ).exists()

    def test_student_can_patch_own_is_read(self):
        note = Notification.objects.create(
            recipient=self.student_a,
            title="Inbox item",
            message="body",
            category="info",
            is_read=True,
        )
        self.client.force_authenticate(user=self.student_a)
        response = self.client.patch(
            f"/api/notifications/{note.id}/",
            {"is_read": False},
            format="json",
        )
        assert response.status_code == 200
        note.refresh_from_db()
        assert note.is_read is False

    def test_student_cannot_create_notification(self):
        self.client.force_authenticate(user=self.student_a)
        response = self.client.post(
            "/api/notifications/",
            {
                "title": "Nope",
                "message": "should be forbidden",
                "category": "info",
            },
            format="json",
        )
        assert response.status_code == 403
