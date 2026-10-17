import pytest
from django.core.management import call_command
from django.core.management.base import SystemCheckError

from qa import gating
from qa.checks import tester_tools_not_in_production as qa_check

from .conftest import client_for

pytestmark = pytest.mark.django_db


def test_tools_disabled_by_default(settings):
    settings.TESTER_TOOLS_ENABLED = False
    settings.DEPLOY_TIER = "test"
    assert gating.tester_tools_enabled() is False


@pytest.mark.parametrize("tier", ["production", "staging", ""])
def test_tools_off_outside_dev_test(settings, tier):
    settings.TESTER_TOOLS_ENABLED = True
    settings.DEPLOY_TIER = tier
    assert gating.tester_tools_enabled() is False


def test_tools_on_for_test_tier(tools_on):
    assert gating.tester_tools_enabled() is True


@pytest.mark.parametrize("path", ["/api/qa/context/", "/api/qa/issues/"])
def test_all_qa_routes_404_in_production_even_for_superuser(settings, make_user, path):
    settings.TESTER_TOOLS_ENABLED = True
    settings.DEPLOY_TIER = "production"
    su = make_user(
        "root@example.com",
        role="admin",
        is_superuser=True,
        is_staff=True,
        is_tester=True,
    )
    assert client_for(su).get(path).status_code == 404


def test_context_404_when_flag_off(settings, tester):
    settings.TESTER_TOOLS_ENABLED = False
    settings.DEPLOY_TIER = "test"
    assert client_for(tester).get("/api/qa/context/").status_code == 404


def test_context_for_non_tester(tools_on, plain_user):
    data = client_for(plain_user).get("/api/qa/context/").json()
    assert data["enabled"] is True
    assert data["is_tester"] is False
    assert data["is_triager"] is False


def test_context_for_tester_and_triager(tools_on, tester, admin_tester):
    assert client_for(tester).get("/api/qa/context/").json()["is_tester"] is True
    data = client_for(admin_tester).get("/api/qa/context/").json()
    assert data["is_tester"] is True and data["is_triager"] is True
    assert data["deploy_tier"] == "test"


def test_issue_list_404_for_non_tester(tools_on, plain_user):
    assert client_for(plain_user).get("/api/qa/issues/").status_code == 404


def test_switched_token_resolves_original_tester(tools_on, tester, make_user):
    demo = make_user("demo.coord@example.com", role="coordinator", is_demo_account=True)
    data = (
        client_for(demo, qa_switched_from=str(tester.pk)).get("/api/qa/context/").json()
    )
    assert data["is_tester"] is True
    assert data["tester"]["email"] == tester.email
    assert data["acting_as"]["email"] == demo.email


def test_switched_token_from_revoked_tester_is_rejected(tools_on, tester, make_user):
    demo = make_user("demo2@example.com", role="student", is_demo_account=True)
    tester.is_tester = False
    tester.save()
    client = client_for(demo, qa_switched_from=str(tester.pk))
    assert client.get("/api/qa/context/").json()["is_tester"] is False


def test_get_tester_none_for_anonymous(tools_on, rf):
    from django.contrib.auth.models import AnonymousUser

    req = rf.get("/")
    req.user = AnonymousUser()
    assert gating.get_tester(req) is None


def test_system_check_errors_when_enabled_in_production(settings):
    settings.TESTER_TOOLS_ENABLED = True
    settings.DEPLOY_TIER = "production"
    errors = qa_check(None)
    assert errors and errors[0].id == "qa.E001"


def test_system_check_errors_for_capture_backend_in_production(settings):
    settings.TESTER_TOOLS_ENABLED = False
    settings.DEPLOY_TIER = "production"
    settings.EMAIL_BACKEND = "qa.mail.CaptureEmailBackend"
    errors = qa_check(None)
    assert errors and errors[0].id == "qa.E002"


def test_system_check_clean_on_test_tier(tools_on):
    assert qa_check(None) == []


def test_manage_check_fails_in_production(settings):
    settings.TESTER_TOOLS_ENABLED = True
    settings.DEPLOY_TIER = "production"
    with pytest.raises(SystemCheckError):
        call_command("check")
