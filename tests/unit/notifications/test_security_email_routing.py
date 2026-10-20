"""Account-security email always goes to ``user.email``; other mail may use secondary_email."""

from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.core import mail

from accounts.models import Profile
from accounts.services import AccountService
from notifications.models import Notification
from notifications.services import NotificationService
from notifications.tasks import (
    PRIMARY_EMAIL_ROUTE_KEYS,
    get_user_email,
    send_notification_by_id,
)

User = get_user_model()
pytestmark = pytest.mark.django_db

PRIMARY = "primary@example.com"
SECONDARY = "secondary@example.org"


@pytest.fixture
def user():
    u = User.objects.create_user(
        username="dual", email=PRIMARY, password="x-Long-pass-123"
    )
    u.is_email_verified = True
    u.save(update_fields=["is_email_verified"])
    profile, _ = Profile.objects.get_or_create(user=u)
    profile.secondary_email = SECONDARY
    profile.save(update_fields=["secondary_email"])
    u.refresh_from_db()
    return u


def _send(user, **kwargs):
    with patch("notifications.services.send_notification_by_id.delay") as delay:
        n = NotificationService.send_notification(
            recipient=user, title="T", message="M", notification_type="email", **kwargs
        )
    assert delay.called
    mail.outbox.clear()
    send_notification_by_id.run(n.id)
    return n


def test_get_user_email_default_prefers_secondary(user):
    assert get_user_email(user) == SECONDARY
    assert get_user_email(user, primary_only=True) == PRIMARY


def test_get_user_email_falls_back_to_primary_without_secondary(user):
    user.profile.secondary_email = ""
    user.profile.save(update_fields=["secondary_email"])
    user.refresh_from_db()
    assert get_user_email(user) == PRIMARY


def test_account_security_route_goes_to_primary(user):
    assert "account_security_email" in PRIMARY_EMAIL_ROUTE_KEYS
    n = _send(user, transactional_route_key="account_security_email")
    assert n.data["transactional_route_key"] == "account_security_email"
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == [PRIMARY]


def test_other_routes_keep_secondary(user):
    _send(user, transactional_route_key="application_status_update")
    assert mail.outbox[0].to == [SECONDARY]


def test_no_route_key_keeps_secondary(user):
    n = _send(user, data={"x": 1})
    assert n.data == {"x": 1}
    assert mail.outbox[0].to == [SECONDARY]


def test_caller_data_preserved_with_route_key(user):
    n = _send(user, data={"x": 1}, transactional_route_key="account_security_email")
    assert n.data == {"x": 1, "transactional_route_key": "account_security_email"}


def test_password_reset_flow_sends_to_primary(user):
    with patch("notifications.services.send_notification_by_id.delay") as delay:
        AccountService.initiate_password_reset(PRIMARY)
    note = Notification.objects.filter(recipient=user).latest("created_at")
    assert delay.called
    mail.outbox.clear()
    send_notification_by_id.run(note.id)
    assert mail.outbox[0].to == [PRIMARY]


def test_lockout_notice_sends_to_primary(user):
    with patch("notifications.services.send_notification_by_id.delay"):
        for _ in range(AccountService.MAX_LOGIN_ATTEMPTS):
            AccountService.increment_failed_login_attempts(user)
    note = Notification.objects.filter(recipient=user, title="Account Locked").get()
    mail.outbox.clear()
    send_notification_by_id.run(note.id)
    assert mail.outbox[0].to == [PRIMARY]
