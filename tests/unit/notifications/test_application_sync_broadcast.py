"""Tests for NotificationService.broadcast_application_sync."""

from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth import get_user_model

from exchange.models import Application, ApplicationStatus, Program
from notifications.services import NotificationService

User = get_user_model()


@pytest.mark.django_db
def test_broadcast_application_sync_calls_group_send_per_stakeholder():
    student = User.objects.create_user(username="stu", email="stu@t.com", password="x")
    coord = User.objects.create_user(username="crd", email="crd@t.com", password="x")
    program = Program.objects.create(
        name="P",
        description="d",
        start_date="2030-01-01",
        end_date="2030-06-01",
    )
    program.coordinators.add(coord)
    status, _ = ApplicationStatus.objects.get_or_create(name="draft", defaults={"order": 0})
    app = Application.objects.create(student=student, program=program, status=status)

    sync_send = MagicMock()
    with patch("notifications.services.get_channel_layer", return_value=MagicMock()):
        with patch("notifications.services.async_to_sync", return_value=sync_send):
            NotificationService.broadcast_application_sync(str(app.id), "comment_added")

    assert sync_send.call_count == 2
    for call in sync_send.call_args_list:
        group, message = call[0]
        assert group.startswith("notifications_")
        assert message["type"] == "application.sync"
        assert message["application_id"] == str(app.id)
        assert message["change_type"] == "comment_added"
