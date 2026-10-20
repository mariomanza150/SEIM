from datetime import timedelta
from unittest.mock import patch

import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory
from django.utils import timezone

from accounts.admin import UserAdmin
from accounts.services import AccountService

User = get_user_model()
pytestmark = pytest.mark.django_db


def _locked(email):
    u = User.objects.create_user(
        username=email.split("@")[0], email=email, password="x-Long-pass-123"
    )
    User.objects.filter(pk=u.pk).update(
        failed_login_attempts=3, lockout_until=timezone.now() + timedelta(minutes=30)
    )
    u.refresh_from_db()
    return u


def test_reset_password_clears_lockout():
    u = _locked("locked@example.com")
    User.objects.filter(pk=u.pk).update(email_verification_token="tok123")
    with patch("notifications.services.send_notification_by_id.delay"):
        AccountService.reset_password("locked@example.com", "tok123", "N3w-Long-pass!")
    u.refresh_from_db()
    assert u.failed_login_attempts == 0
    assert u.lockout_until is None
    assert not AccountService.is_account_locked(u)
    assert u.check_password("N3w-Long-pass!")


def test_failed_reset_does_not_clear_lockout():
    u = _locked("locked2@example.com")
    User.objects.filter(pk=u.pk).update(email_verification_token="tok123")
    with pytest.raises(ValueError):
        AccountService.reset_password("locked2@example.com", "wrong", "N3w-Long-pass!")
    u.refresh_from_db()
    assert u.lockout_until is not None


def test_admin_unlock_selected_action():
    a = _locked("a@example.com")
    b = _locked("b@example.com")
    other = _locked("c@example.com")
    model_admin = UserAdmin(User, AdminSite())
    assert "unlock_selected" in model_admin.actions
    request = RequestFactory().post("/")
    request.user = User.objects.create_superuser(
        "root", "root@example.com", "x-Pass-123"
    )
    request.session = {}
    request._messages = FallbackStorage(request)
    model_admin.unlock_selected(request, User.objects.filter(pk__in=[a.pk, b.pk]))
    for u in (a, b):
        u.refresh_from_db()
        assert u.failed_login_attempts == 0 and u.lockout_until is None
    other.refresh_from_db()
    assert other.lockout_until is not None
