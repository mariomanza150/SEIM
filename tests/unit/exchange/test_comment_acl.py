"""Regression: students must not comment on other students' applications."""

import pytest
from rest_framework.test import APIClient

from tests.utils import TestUtils


@pytest.mark.django_db
class TestCommentCrossUserAcl:
    def setup_method(self):
        self.student_a = TestUtils.create_test_user(
            username="comment_acl_a",
            email="comment_acl_a@example.com",
            role="student",
        )
        self.student_b = TestUtils.create_test_user(
            username="comment_acl_b",
            email="comment_acl_b@example.com",
            role="student",
        )
        self.coordinator = TestUtils.create_test_user(
            username="comment_acl_coord",
            email="comment_acl_coord@example.com",
            role="coordinator",
        )
        self.app_b = TestUtils.create_test_application(student=self.student_b)
        self.client = APIClient()

    def test_student_cannot_comment_on_other_application(self):
        self.client.force_authenticate(user=self.student_a)
        response = self.client.post(
            "/api/comments/",
            {
                "application": str(self.app_b.id),
                "text": "should not land",
                "is_private": False,
            },
            format="json",
        )
        assert response.status_code == 400
        assert "own applications" in str(response.data).lower()

    def test_student_can_comment_on_own_application(self):
        app_a = TestUtils.create_test_application(student=self.student_a)
        self.client.force_authenticate(user=self.student_a)
        response = self.client.post(
            "/api/comments/",
            {
                "application": str(app_a.id),
                "text": "own note",
                "is_private": False,
            },
            format="json",
        )
        assert response.status_code == 201
        assert response.data["text"] == "own note"

    def test_coordinator_can_comment_on_student_application(self):
        self.client.force_authenticate(user=self.coordinator)
        response = self.client.post(
            "/api/comments/",
            {
                "application": str(self.app_b.id),
                "text": "staff note",
                "is_private": True,
            },
            format="json",
        )
        assert response.status_code == 201
