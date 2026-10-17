import pytest
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMultiAlternatives
from django.core.management import call_command
from django.core.management.base import CommandError
from django.urls import reverse
from rest_framework_simplejwt.tokens import AccessToken

from qa.gating import CLAIM_IMPERSONATOR, CLAIM_SWITCHED_FROM, demo_password
from qa.mail import CaptureEmailBackend
from qa.models import CapturedEmail, QAAuditEvent

from .conftest import _user, client_for

# Not a real secret; built at runtime so secret scanners do not flag the fixture.
ROTATED_PW = "-".join(["rotated", "demo", "pw", "42"])

pytestmark = pytest.mark.django_db


@pytest.fixture
def demo_student(db):
    return _user("student@test.com", role="student", is_demo_account=True)


@pytest.fixture
def demo_admin(db):
    return _user("admin@test.com", role="admin", is_demo_account=True, is_staff=True)


# ---- demo password / tier guards -------------------------------------------------


def test_demo_password_requires_env_on_test(settings):
    settings.DEPLOY_TIER = "test"
    settings.TESTER_DEMO_PASSWORD = ""
    with pytest.raises(CommandError):
        demo_password("legacy")
    settings.TESTER_DEMO_PASSWORD = "from-env-xyz"
    assert demo_password("legacy") == "from-env-xyz"


def test_demo_password_fallback_on_development(settings):
    settings.DEPLOY_TIER = "development"
    settings.TESTER_DEMO_PASSWORD = ""
    assert demo_password("legacy") == "legacy"


@pytest.mark.parametrize(
    "command",
    [
        "seed_test_accounts",
        "reset_demo_data",
        "seed_demo_readiness",
        "create_vue_test_users",
    ],
)
def test_seed_commands_refuse_production(settings, command):
    settings.DEPLOY_TIER = "production"
    with pytest.raises(CommandError, match="production"):
        call_command(command)


def test_seed_test_accounts_flags_and_rotates(settings, make_user):
    settings.DEPLOY_TIER = "test"
    settings.TESTER_DEMO_PASSWORD = ROTATED_PW
    legacy = make_user("admin@test.com", role="admin", is_superuser=True, is_staff=True)
    real = make_user("real@example.com", role="admin")
    call_command("seed_test_accounts", tester=["real@example.com"], verbosity=0)
    legacy.refresh_from_db()
    real.refresh_from_db()
    assert legacy.is_demo_account and not legacy.is_superuser
    assert legacy.check_password(ROTATED_PW)
    assert real.is_tester and not real.is_demo_account
    from django.contrib.auth import get_user_model

    users = get_user_model().objects.filter(is_demo_account=True)
    assert users.filter(email="student.new@test.com").exists()
    assert not users.filter(is_superuser=True).exists()


def test_seed_test_accounts_rejects_demo_tester(settings):
    settings.DEPLOY_TIER = "test"
    settings.TESTER_DEMO_PASSWORD = ROTATED_PW
    with pytest.raises(CommandError):
        call_command("seed_test_accounts", tester=["student@test.com"], verbosity=0)


# ---- role switcher ---------------------------------------------------------------


def test_demo_accounts_404_when_gate_closed(settings, tester, demo_student):
    settings.TESTER_TOOLS_ENABLED = False
    resp = client_for(tester).get("/api/qa/demo-accounts/")
    assert resp.status_code == 404


def test_demo_accounts_hidden_from_non_testers(tools_on, plain_user, demo_student):
    assert client_for(plain_user).get("/api/qa/demo-accounts/").status_code == 404


def test_demo_accounts_lists_only_demo_users(
    tools_on, tester, demo_student, plain_user
):
    resp = client_for(tester).get("/api/qa/demo-accounts/")
    assert resp.status_code == 200
    emails = [a["email"] for a in resp.data["results"]]
    assert emails == ["student@test.com"]


def test_switch_into_demo_account(tools_on, tester, demo_student):
    resp = client_for(tester).post(
        "/api/qa/demo-login/", {"user_id": str(demo_student.pk)}, format="json"
    )
    assert resp.status_code == 200
    token = AccessToken(resp.data["access"])
    assert str(token["user_id"]) == str(demo_student.pk)
    assert token[CLAIM_SWITCHED_FROM] == str(tester.pk)
    assert QAAuditEvent.objects.filter(
        actor=tester, target=demo_student, action="demo_switch"
    ).exists()

    # The switched token still resolves the tester (context + reporting work).
    switched = client_for(demo_student, **{CLAIM_SWITCHED_FROM: str(tester.pk)})
    ctx = switched.get("/api/qa/context/").data
    assert ctx["is_tester"] is True
    assert ctx["acting_as"]["email"] == "student@test.com"
    assert ctx["acting_as"]["mode"] == "switch"

    ret = switched.post("/api/qa/demo-login/return/", {}, format="json")
    assert ret.status_code == 204
    assert QAAuditEvent.objects.filter(action="demo_return").exists()


def test_cannot_switch_into_real_user(tools_on, tester, plain_user):
    resp = client_for(tester).post(
        "/api/qa/demo-login/", {"user_id": str(plain_user.pk)}, format="json"
    )
    assert resp.status_code == 404


def test_demo_account_self_service_blocked(tools_on, tester, demo_student):
    client = client_for(demo_student, **{CLAIM_SWITCHED_FROM: str(tester.pk)})
    resp = client.post(
        reverse("accounts:change_password"),
        {},
        format="json",
    )
    assert resp.status_code == 403
    # Direct demo login (no switch claim) is also blocked.
    direct = client_for(demo_student)
    resp = direct.post(
        reverse("accounts:change_password"),
        {},
        format="json",
    )
    assert resp.status_code == 403


# ---- impersonation ---------------------------------------------------------------


def test_impersonation_requires_triager(tools_on, tester, plain_user):
    resp = client_for(tester).post(
        "/api/qa/impersonate/", {"user_id": str(plain_user.pk)}, format="json"
    )
    assert resp.status_code == 404


def test_triager_impersonates_and_is_audited(tools_on, admin_tester, plain_user):
    client = client_for(admin_tester)
    found = client.get("/api/qa/impersonate/search/", {"q": "plain"}).data["results"]
    assert [u["email"] for u in found] == ["plain@example.com"]
    resp = client.post(
        "/api/qa/impersonate/",
        {"user_id": str(plain_user.pk), "reason": "repro #12"},
        format="json",
    )
    assert resp.status_code == 200
    token = AccessToken(resp.data["access"])
    assert token[CLAIM_IMPERSONATOR] == str(admin_tester.pk)
    assert resp.data["expires_in"] == 1800
    event = QAAuditEvent.objects.get(action="impersonate_start")
    assert event.note == "repro #12"

    acting = client_for(plain_user, **{CLAIM_IMPERSONATOR: str(admin_tester.pk)})
    assert acting.get("/api/qa/context/").data["acting_as"]["mode"] == "impersonate"
    assert (
        acting.post("/api/qa/demo-login/return/", {}, format="json").status_code == 204
    )
    assert QAAuditEvent.objects.filter(action="impersonate_stop").exists()


def test_triager_cannot_impersonate_superuser(tools_on, admin_tester, make_user):
    su = make_user("root@example.com", is_superuser=True, is_staff=True)
    resp = client_for(admin_tester).post(
        "/api/qa/impersonate/", {"user_id": str(su.pk)}, format="json"
    )
    assert resp.status_code == 403


def test_demo_admin_is_not_triager(tools_on, demo_admin, make_user):
    demo_admin.is_tester = True
    demo_admin.save()
    target = make_user("x@example.com")
    resp = client_for(demo_admin).post(
        "/api/qa/impersonate/", {"user_id": str(target.pk)}, format="json"
    )
    assert resp.status_code == 404


# ---- capture backend + outbox ----------------------------------------------------


def test_capture_backend_refuses_production(settings):
    settings.DEPLOY_TIER = "production"
    with pytest.raises(ImproperlyConfigured):
        CaptureEmailBackend()


def _send(settings, to, subject="Hello", html=None):
    settings.EMAIL_BACKEND = "qa.mail.CaptureEmailBackend"
    msg = EmailMultiAlternatives(subject, "plain body", "noreply@seim.test", to)
    if html:
        msg.attach_alternative(html, "text/html")
    msg.send()


def test_capture_backend_stores_messages(tools_on):
    _send(tools_on, ["Student@Test.com"], html="<p>Hi</p>")
    stored = CapturedEmail.objects.get()
    assert stored.body_html == "<p>Hi</p>"
    assert stored.body_text == "plain body"
    assert "student@test.com" in stored.recipients_index


def test_outbox_visibility(tools_on, tester, admin_tester, demo_student):
    _send(tools_on, ["student@test.com"], subject="To demo")
    _send(tools_on, ["someone.real@example.com"], subject="To real")
    _send(tools_on, ["tester@example.com"], subject="To me")

    mine = client_for(tester).get("/api/qa/outbox/").data
    assert mine["capturing"] is True
    assert sorted(m["subject"] for m in mine["results"]) == ["To demo", "To me"]

    everything = client_for(admin_tester).get("/api/qa/outbox/").data["results"]
    assert len(everything) == 3

    real = CapturedEmail.objects.get(subject="To real")
    assert client_for(tester).get(f"/api/qa/outbox/{real.pk}/").status_code == 404
    detail = client_for(admin_tester).get(f"/api/qa/outbox/{real.pk}/")
    assert detail.status_code == 200
    assert detail["Cache-Control"] == "private, no-store"


# ---- flags + reset ---------------------------------------------------------------


def test_flags(tools_on, tester):
    resp = client_for(tester).get("/api/qa/flags/")
    assert resp.status_code == 200
    env = resp.data["environment"]
    assert env["deploy_tier"] == "test"
    assert "TESTER_DEMO_PASSWORD" not in str(resp.data)
    assert set(env) >= {"demo_password_configured", "email_capture", "commit"}


def test_reset_only_for_triagers(tools_on, tester):
    resp = client_for(tester).post(
        "/api/qa/reset-demo/", {"confirm": "RESET"}, format="json"
    )
    assert resp.status_code == 404


def test_reset_requires_confirmation_and_queues(tools_on, admin_tester, monkeypatch):
    from django.core.cache import cache

    from qa import tasks

    cache.delete(tasks.RESET_LOCK_KEY)
    calls = []
    monkeypatch.setattr(tasks.reset_demo_data_task, "delay", lambda: calls.append(1))
    client = client_for(admin_tester)
    assert client.post("/api/qa/reset-demo/", {}, format="json").status_code == 400
    resp = client.post("/api/qa/reset-demo/", {"confirm": "reset"}, format="json")
    assert resp.status_code == 202
    assert calls == [1]
    assert QAAuditEvent.objects.filter(action="reset_demo").exists()
    cache.delete(tasks.RESET_LOCK_KEY)


def test_reset_task_runs_command_and_releases_lock(monkeypatch):
    from django.core.cache import cache

    from qa import tasks

    called = []
    monkeypatch.setattr(tasks, "call_command", lambda *a, **k: called.append(a))
    cache.set(tasks.RESET_LOCK_KEY, "1")
    assert tasks.reset_demo_data_task.run() == "ok"
    assert called == [("reset_demo_data",)]
    assert cache.get(tasks.RESET_LOCK_KEY) is None
