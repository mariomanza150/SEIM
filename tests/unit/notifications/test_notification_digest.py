"""Tests for scheduled notification digests."""

from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from accounts.models import UserSettings
from notifications.digest import process_notification_digests
from notifications.models import Notification
from notifications.services import NotificationService

User = get_user_model()


@pytest.mark.django_db
def test_digest_skips_when_no_unread():
    user = User.objects.create_user(username="d1", email="d1@example.com", password="x")
    settings, _ = UserSettings.objects.get_or_create(user=user)
    settings.notification_digest_frequency = UserSettings.NotificationDigestFrequency.DAILY
    settings.save()

    with patch("notifications.digest.NotificationService.send_notification") as m:
        r = process_notification_digests()
    assert r["digests_sent"] == 0
    assert r["skipped_no_unread"] >= 1
    m.assert_not_called()


@pytest.mark.django_db
def test_digest_creates_digest_notification_and_updates_timestamp():
    user = User.objects.create_user(username="d2", email="d2@example.com", password="x")
    settings, _ = UserSettings.objects.get_or_create(user=user)
    settings.notification_digest_frequency = UserSettings.NotificationDigestFrequency.DAILY
    settings.save()

    NotificationService.send_notification(
        recipient=user,
        title="Hello",
        message="Body",
        notification_type="in_app",
    )

    now = timezone.now()
    r = process_notification_digests(now=now)

    assert r["digests_sent"] == 1
    assert Notification.objects.filter(recipient=user, data__is_digest=True).count() == 1
    settings.refresh_from_db()
    assert settings.notification_digest_last_sent_at is not None
    assert abs((settings.notification_digest_last_sent_at - now).total_seconds()) < 2.0


@pytest.mark.django_db
def test_digest_respects_daily_cadence():
    user = User.objects.create_user(username="d3", email="d3@example.com", password="x")
    settings, _ = UserSettings.objects.get_or_create(user=user)
    settings.notification_digest_frequency = UserSettings.NotificationDigestFrequency.DAILY
    settings.notification_digest_last_sent_at = timezone.now()
    settings.save()

    NotificationService.send_notification(
        recipient=user,
        title="Hello",
        message="Body",
        notification_type="in_app",
    )

    with patch("notifications.digest.NotificationService.send_notification") as m:
        r = process_notification_digests()
    assert r["digests_sent"] == 0
    assert r["skipped_cadence"] >= 1
    m.assert_not_called()


@pytest.mark.django_db
def test_digest_uses_both_when_email_digest_enabled():
    user = User.objects.create_user(username="d4", email="d4@example.com", password="x")
    settings, _ = UserSettings.objects.get_or_create(user=user)
    settings.notification_digest_frequency = UserSettings.NotificationDigestFrequency.DAILY
    settings.email_system = True
    settings.email_notification_digest = True
    settings.save()

    NotificationService.send_notification(
        recipient=user,
        title="Ping",
        message="Pong",
        notification_type="in_app",
    )

    with patch("notifications.digest.NotificationService.send_notification") as m:
        process_notification_digests()

    digest_kw = [c.kwargs for c in m.call_args_list if c.kwargs.get("data") == {"is_digest": True}]
    assert len(digest_kw) == 1
    assert digest_kw[0]["notification_type"] == "both"
    assert digest_kw[0]["settings_category"] == "system"


@pytest.mark.django_db
def test_digest_suppressed_when_in_app_only_and_inapp_system_off():
    user = User.objects.create_user(username="d5", email="d5@example.com", password="x")
    settings, _ = UserSettings.objects.get_or_create(user=user)
    settings.notification_digest_frequency = UserSettings.NotificationDigestFrequency.DAILY
    settings.email_notification_digest = False
    settings.inapp_system = False
    settings.save()

    NotificationService.send_notification(
        recipient=user,
        title="Ping",
        message="Pong",
        notification_type="in_app",
    )

    now = timezone.now()
    r = process_notification_digests(now=now)

    assert r["digests_sent"] == 0
    assert r["skipped_suppressed"] == 1
    assert Notification.objects.filter(recipient=user, data__is_digest=True).count() == 0
    settings.refresh_from_db()
    assert settings.notification_digest_last_sent_at is not None
    assert abs((settings.notification_digest_last_sent_at - now).total_seconds()) < 2.0
