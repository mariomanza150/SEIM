"""Ensure Celery and Redis cache stay on JSON (no pickle)."""

from __future__ import annotations

import ast
import json
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

import pytest
from django.conf import settings
from django_redis.serializers.json import JSONSerializer


def test_celery_serializers_are_json_only():
    assert settings.CELERY_TASK_SERIALIZER == "json"
    assert settings.CELERY_RESULT_SERIALIZER == "json"
    assert settings.CELERY_ACCEPT_CONTENT == ["json"]
    assert "pickle" not in settings.CELERY_ACCEPT_CONTENT


def test_django_redis_json_serializer_round_trip():
    ser = JSONSerializer(options={})
    payload = {"id": str(uuid4()), "ok": True}
    encoded = ser.dumps(payload)
    assert isinstance(encoded, bytes)
    assert json.loads(encoded.decode("utf-8")) == payload
    assert ser.loads(encoded) == payload


def test_settings_modules_have_no_pickle_serializer():
    for rel in (
        "seim/settings/base.py",
        "seim/settings/development.py",
        "seim/settings/production.py",
    ):
        source = Path(rel).read_text(encoding="utf-8")
        assert "PickleSerializer" not in source, rel
        assert "JSONSerializer" in source, rel
        ast.parse(source)


@pytest.mark.django_db
def test_send_notification_delay_passes_string_id():
    from django.contrib.auth import get_user_model

    from notifications.services import NotificationService

    User = get_user_model()
    user = User.objects.create_user(
        username="json-celery-user",
        email="json-celery@example.com",
        password="testpass123",
    )
    with patch("notifications.services.send_notification_by_id.delay") as delay:
        NotificationService.send_notification(
            recipient=user,
            title="Hello",
            message="World",
            notification_type="email",
        )
    delay.assert_called_once()
    (arg,) = delay.call_args.args
    assert isinstance(arg, str)
    # stdlib json rejects UUID; string IDs must survive CELERY_TASK_SERIALIZER=json
    json.dumps([arg])
