from datetime import date, timedelta

import pytest

from exchange.models import Program

from .conftest import client_for

pytestmark = pytest.mark.django_db

URL = "/api/programs/eligibility-overview/"


def _program(name, **extra):
    today = date.today()
    defaults = {
        "description": "x",
        "start_date": today + timedelta(days=60),
        "end_date": today + timedelta(days=200),
        "is_active": True,
    }
    defaults.update(extra)
    return Program.objects.create(name=name, **defaults)


def test_404_for_non_tester(tools_on, plain_user):
    assert client_for(plain_user).get(URL).status_code == 404


def test_404_when_tools_off_even_for_tester(settings, tester):
    settings.TESTER_TOOLS_ENABLED = True
    settings.DEPLOY_TIER = "production"
    assert client_for(tester).get(URL).status_code == 404


def test_payload_lists_blocking_checks(tools_on, tester):
    open_prog = _program("A open")
    _program("B inactive", is_active=False)
    _program("C english", required_language="English")
    closed = _program(
        "D closed",
        application_open_date=date.today() - timedelta(days=30),
        application_deadline=date.today() - timedelta(days=1),
    )
    tester.profile.language = "Spanish"
    tester.profile.save()

    resp = client_for(tester).get(URL)
    assert resp.status_code == 200
    rows = {r["name"]: r for r in resp.json()["results"]}
    assert set(rows["A open"]) == {"id", "name", "is_active", "listed", "blocking"}
    assert rows["A open"]["id"] == str(open_prog.pk)
    assert rows["A open"]["listed"] is True and rows["A open"]["blocking"] == []
    assert rows["B inactive"]["listed"] is False
    assert [b["id"] for b in rows["B inactive"]["blocking"]] == ["is_active"]
    assert rows["B inactive"]["blocking"][0]["message_key"] == "program_inactive"
    eng = rows["C english"]
    assert eng["listed"] is False
    assert [b["id"] for b in eng["blocking"]] == ["required_language"]
    assert eng["blocking"][0]["message_key"] == "language_unmet"
    # A closed window alone does not hide a program (mirrors eligible_for_me).
    assert rows["D closed"]["listed"] is True
    assert rows["D closed"]["id"] == str(closed.pk)
