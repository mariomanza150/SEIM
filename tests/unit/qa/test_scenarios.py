import pytest
from django.core.management import call_command

from qa.models import Issue, IssueComment, ScenarioResult, TestScenario
from qa.scenarios import SCENARIOS
from qa.services import triage_url, triager_queryset

from .conftest import _user, client_for

pytestmark = pytest.mark.django_db


@pytest.fixture
def scenarios(db):
    call_command("seed_test_scenarios", verbosity=0)
    return TestScenario.objects.all()


def _issue(reporter, status="fixed", **extra):
    return Issue.objects.create(
        title="Broken", reporter=reporter, status=status, **extra
    )


def test_seed_is_idempotent_and_keeps_admin_edits(scenarios):
    assert scenarios.count() == len(SCENARIOS)
    codes = [s["code"] for s in SCENARIOS]
    assert len(codes) == len(set(codes))
    assert all(s["title_es"] and s["steps_es"] and s["expected_es"] for s in SCENARIOS)
    first = TestScenario.objects.get(code="AUTH-01")
    first.title = "Edited"
    first.save()
    call_command("seed_test_scenarios", verbosity=0)
    first.refresh_from_db()
    assert first.title == "Edited"
    call_command("seed_test_scenarios", overwrite=True, verbosity=0)
    first.refresh_from_db()
    assert first.title != "Edited"


def test_scenarios_404_when_gate_closed(settings, tester, scenarios):
    settings.TESTER_TOOLS_ENABLED = False
    assert client_for(tester).get("/api/qa/scenarios/").status_code == 404


def test_tester_records_results_per_build(tools_on, tester, scenarios):
    tools_on.BUILD_COMMIT = "abc1234"
    client = client_for(tester)
    data = client.get("/api/qa/scenarios/").json()
    assert data["build"] == "abc1234"
    assert data["summary"]["todo"] == len(SCENARIOS)
    sid = data["results"][0]["id"]

    issue = _issue(tester, status="new")
    resp = client.post(
        f"/api/qa/scenarios/{sid}/result/",
        {"outcome": "fail", "note": "boom", "issue_number": issue.number},
        format="json",
    )
    assert resp.status_code == 200
    assert resp.json()["issue_number"] == issue.number
    # Second post updates the same row.
    client.post(f"/api/qa/scenarios/{sid}/result/", {"outcome": "pass"}, format="json")
    assert ScenarioResult.objects.count() == 1
    assert ScenarioResult.objects.get().outcome == "pass"

    data = client.get("/api/qa/scenarios/").json()
    assert data["summary"]["pass"] == 1
    # New build: checklist starts fresh.
    tools_on.BUILD_COMMIT = "def5678"
    assert client.get("/api/qa/scenarios/").json()["summary"].get("pass") is None

    tools_on.BUILD_COMMIT = "abc1234"
    assert client.delete(f"/api/qa/scenarios/{sid}/result/").status_code == 204
    assert ScenarioResult.objects.count() == 0


def test_result_validation(tools_on, tester, scenarios):
    sid = scenarios.first().pk
    client = client_for(tester)
    assert (
        client.post(
            f"/api/qa/scenarios/{sid}/result/", {"outcome": "meh"}, format="json"
        ).status_code
        == 400
    )
    assert (
        client.post(
            f"/api/qa/scenarios/{sid}/result/",
            {"outcome": "fail", "issue_number": 999},
            format="json",
        ).status_code
        == 400
    )


def test_scenarios_spanish(tools_on, tester, scenarios):
    data = client_for(tester).get("/api/qa/scenarios/?lang=es").json()
    row = next(r for r in data["results"] if r["code"] == "AUTH-01")
    assert row["title"] == "Iniciar y cerrar sesión"


def test_matrix_for_triagers_only(tools_on, tester, admin_tester, scenarios):
    tools_on.BUILD_COMMIT = "abc1234"
    s = scenarios.first()
    ScenarioResult.objects.create(
        scenario=s, tester=tester, build_commit="abc1234", outcome="pass"
    )
    ScenarioResult.objects.create(
        scenario=s, tester=admin_tester, build_commit="abc1234", outcome="fail"
    )
    ScenarioResult.objects.create(
        scenario=s, tester=tester, build_commit="old0001", outcome="pass"
    )
    assert client_for(tester).get("/api/qa/scenarios/matrix/").status_code == 404
    data = client_for(admin_tester).get("/api/qa/scenarios/matrix/").json()
    assert data["current"] == "abc1234"
    assert set(data["builds"]) == {"abc1234", "old0001"}
    row = next(r for r in data["results"] if r["id"] == str(s.pk))
    assert row["builds"]["abc1234"]["outcome"] == "fail"
    assert row["builds"]["abc1234"]["counts"] == {"pass": 1, "fail": 1}
    assert row["builds"]["old0001"]["outcome"] == "pass"


def test_triagers_endpoint(tools_on, tester, admin_tester, make_user):
    make_user("admin.notester@example.com", role="admin")
    assert client_for(tester).get("/api/qa/triagers/").status_code == 404
    emails = [
        u["email"]
        for u in client_for(admin_tester).get("/api/qa/triagers/").json()["results"]
    ]
    assert emails == ["boss@example.com"]
    assert list(triager_queryset()) == [admin_tester]


# ---- verify / reopen ---------------------------------------------------------------


def test_reporter_verifies_fix(tools_on, tester):
    issue = _issue(tester)
    resp = client_for(tester).post(
        f"/api/qa/issues/{issue.pk}/verify/", {"result": "verified"}, format="json"
    )
    assert resp.status_code == 200
    issue.refresh_from_db()
    assert issue.status == "verified"
    assert IssueComment.objects.filter(issue=issue, is_system=True).exists()


def test_reporter_reopens_with_comment(
    tools_on, tester, admin_tester, django_capture_on_commit_callbacks
):
    issue = _issue(tester, assignee=admin_tester)
    client = client_for(tester)
    url = f"/api/qa/issues/{issue.pk}/verify/"
    assert client.post(url, {"result": "reopen"}, format="json").status_code == 400
    with django_capture_on_commit_callbacks(execute=True):
        resp = client.post(
            url, {"result": "reopen", "comment": "Still broken"}, format="json"
        )
    assert resp.status_code == 200
    issue.refresh_from_db()
    assert issue.status == "triaged"
    assert IssueComment.objects.filter(issue=issue, body="Still broken").exists()
    from notifications.models import Notification

    assert Notification.objects.filter(
        recipient=admin_tester, title__contains="reopened"
    ).exists()


def test_verify_requires_fixed_status(tools_on, tester):
    issue = _issue(tester, status="in_progress")
    resp = client_for(tester).post(
        f"/api/qa/issues/{issue.pk}/verify/", {"result": "verified"}, format="json"
    )
    assert resp.status_code == 400
    resp = client_for(tester).post(
        f"/api/qa/issues/{_issue(tester).pk}/verify/", {"result": "x"}, format="json"
    )
    assert resp.status_code == 400


def test_other_tester_cannot_verify(tools_on, tester, make_user):
    other = make_user("other@example.com", role="student", is_tester=True)
    issue = _issue(other)
    resp = client_for(tester).post(
        f"/api/qa/issues/{issue.pk}/verify/", {"result": "verified"}, format="json"
    )
    assert resp.status_code == 404


def test_triage_url_points_to_vue_page(tester):
    issue = _issue(tester)
    assert triage_url(issue) == f"/seim/tester/reports/{issue.pk}"


def test_reset_demo_data_runs_all_steps(settings, monkeypatch):
    settings.DEPLOY_TIER = "test"
    calls = []
    from qa.management.commands import reset_demo_data

    monkeypatch.setattr(
        reset_demo_data, "call_command", lambda name, **k: calls.append(name)
    )
    call_command("reset_demo_data", verbosity=0)
    assert calls == [
        "cleanup_demo_data",
        "seed_demo_readiness",
        "seed_test_accounts",
        "seed_test_scenarios",
    ]


def test_issue_list_assigned_filters(tools_on, tester, admin_tester):
    mine = _issue(tester, status="new", assignee=admin_tester)
    _issue(tester, status="new")
    client = client_for(admin_tester)
    rows = client.get("/api/qa/issues/?assigned=me").json()["results"]
    assert [r["id"] for r in rows] == [str(mine.pk)]
    assert rows[0]["assignee"]["email"] == "boss@example.com"
    assert len(client.get("/api/qa/issues/?assigned=none").json()["results"]) == 1
