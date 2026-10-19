from types import SimpleNamespace

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from accounts.models import Role
from accounts.serializers import AdminUserSerializer, UserSerializer

User = get_user_model()
pytestmark = pytest.mark.django_db

PW = "x-Long-pass-123"


def _user(email, role=None, **extra):
    u = User.objects.create_user(
        username=email.split("@")[0], email=email, password=PW, **extra
    )
    if role:
        u.roles.add(Role.objects.get_or_create(name=role)[0])
    u.is_email_verified = True
    u.save(update_fields=["is_email_verified"])
    return u


def _client(user):
    c = APIClient()
    c.force_authenticate(user)
    return c


def test_admin_can_toggle_tester_and_filter():
    admin = _user("admin@example.com", role="admin", is_superuser=True)
    target = _user("target@example.com", role="student")
    c = _client(admin)
    r = c.patch(f"/api/users/{target.pk}/", {"is_tester": True}, format="json")
    assert r.status_code == 200, r.content
    assert r.json()["is_tester"] is True
    target.refresh_from_db()
    assert target.is_tester is True
    listed = c.get("/api/users/", {"is_tester": "true"}).json()
    rows = listed.get("results", listed)
    assert [row["email"] for row in rows] == ["target@example.com"]
    r = c.patch(f"/api/users/{target.pk}/", {"is_tester": False}, format="json")
    assert r.status_code == 200
    target.refresh_from_db()
    assert target.is_tester is False


def test_non_admin_cannot_use_users_api_to_set_tester():
    student = _user("student@example.com", role="student")
    r = _client(student).patch(
        f"/api/users/{student.pk}/", {"is_tester": True}, format="json"
    )
    assert r.status_code in (403, 404)
    student.refresh_from_db()
    assert student.is_tester is False


def test_admin_serializer_rejects_tester_change_by_non_admin_actor():
    coordinator = _user("coord@example.com", role="coordinator", is_staff=True)
    target = _user("t2@example.com", role="student")
    ser = AdminUserSerializer(
        target,
        data={"is_tester": True},
        partial=True,
        context={"request": SimpleNamespace(user=coordinator)},
    )
    assert not ser.is_valid()
    assert "is_tester" in ser.errors


def test_base_user_serializer_is_tester_read_only():
    u = _user("self@example.com", role="student")
    ser = UserSerializer(u, data={"is_tester": True}, partial=True)
    assert ser.is_valid(), ser.errors
    ser.save()
    u.refresh_from_db()
    assert u.is_tester is False
    assert UserSerializer(u).data["is_tester"] is False


def test_self_profile_update_cannot_set_tester():
    u = _user("me@example.com", role="student")
    c = _client(u)
    for url in ("/api/accounts/profile/", "/api/accounts/profile/update/"):
        c.patch(url, {"is_tester": True}, format="json")
        c.post(url, {"is_tester": True}, format="json")
    u.refresh_from_db()
    assert u.is_tester is False


def test_login_response_exposes_tester_read_only():
    u = _user("login@example.com", role="student", is_tester=True)
    r = APIClient().post(
        "/api/accounts/login/", {"login": u.email, "password": PW}, format="json"
    )
    assert r.status_code == 200, r.content
    assert r.json()["user"]["is_tester"] is True
