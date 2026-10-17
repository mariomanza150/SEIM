"""Incoming/outgoing split and exchange-period filters for applications."""

from datetime import date

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from exchange.filters import ApplicationFilter, ProgramFilter, parse_exchange_period
from exchange.models import Application, ApplicationStatus, Program

User = get_user_model()


def _program(name, start, end, direction="outgoing"):
    return Program.objects.create(
        name=name,
        description=name,
        start_date=start,
        end_date=end,
        is_active=True,
        mobility_direction=direction,
    )


@pytest.fixture
def setup(db):
    student = User.objects.create_user(
        username="dir-student", email="dir@example.com", password="pw-123456!"
    )
    draft = ApplicationStatus.objects.get_or_create(
        name="draft", defaults={"order": 0}
    )[0]
    out_spring = _program("Out Spring", date(2027, 1, 15), date(2027, 6, 15))
    out_fall = _program("Out Fall", date(2027, 8, 1), date(2027, 12, 15))
    inc_fall = _program("Inc Fall", date(2027, 8, 1), date(2027, 12, 15), "incoming")
    apps = {
        p.name: Application.objects.create(student=student, program=p, status=draft)
        for p in (out_spring, out_fall, inc_fall)
    }
    return {"programs": (out_spring, out_fall, inc_fall), "apps": apps}


def _names(data):
    fs = ApplicationFilter(data=data, queryset=Application.objects.all())
    assert fs.is_valid(), fs.errors
    return sorted(app.program.name for app in fs.qs)


@pytest.mark.unit
def test_parse_exchange_period():
    assert parse_exchange_period("2027") == (date(2027, 1, 1), date(2027, 12, 31))
    assert parse_exchange_period("2027-1") == (date(2027, 1, 1), date(2027, 6, 30))
    assert parse_exchange_period("2027-2") == (date(2027, 7, 1), date(2027, 12, 31))
    assert parse_exchange_period("spring") is None
    assert parse_exchange_period("") is None


@pytest.mark.django_db
@pytest.mark.unit
class TestApplicationDirectionAndPeriod:
    def test_default_direction_is_outgoing(self, db):
        program = Program.objects.create(
            name="Default",
            description="d",
            start_date=date(2027, 1, 1),
            end_date=date(2027, 2, 1),
        )
        assert program.mobility_direction == Program.MobilityDirection.OUTGOING

    def test_direction_filter(self, setup):
        assert _names({"direction": "incoming"}) == ["Inc Fall"]
        assert _names({"direction": "outgoing"}) == ["Out Fall", "Out Spring"]

    def test_invalid_direction_rejected(self, setup):
        fs = ApplicationFilter(
            data={"direction": "sideways"}, queryset=Application.objects.all()
        )
        assert not fs.is_valid()

    def test_period_filter(self, setup):
        assert _names({"period": "2027-1"}) == ["Out Spring"]
        assert _names({"period": "2027-2", "direction": "outgoing"}) == ["Out Fall"]
        assert _names({"period": "2027"}) == ["Inc Fall", "Out Fall", "Out Spring"]
        assert _names({"period": "2030"}) == []
        # Unparseable periods are ignored rather than emptying the list.
        assert len(_names({"period": "nonsense"})) == 3

    def test_date_range_overlap(self, setup):
        assert _names({"start_date": "2027-07-01"}) == ["Inc Fall", "Out Fall"]
        assert _names({"end_date": "2027-03-01"}) == ["Out Spring"]
        assert _names({"start_date": "2027-06-01", "end_date": "2027-08-05"}) == [
            "Inc Fall",
            "Out Fall",
            "Out Spring",
        ]

    def test_program_filter(self, setup):
        out_fall = setup["programs"][1]
        assert _names({"program": str(out_fall.id)}) == ["Out Fall"]

    def test_program_list_direction_filter(self, setup):
        mine = Program.objects.filter(pk__in=[p.pk for p in setup["programs"]])
        fs = ProgramFilter(data={"direction": "outgoing"}, queryset=mine)
        assert fs.is_valid()
        assert sorted(p.name for p in fs.qs) == ["Out Fall", "Out Spring"]

    def test_api_filters_and_payload(self, setup):
        client = APIClient()
        client.force_authenticate(User.objects.get(username="dir-student"))
        response = client.get(
            "/api/applications/", {"direction": "incoming", "period": "2027-2"}
        )
        assert response.status_code == 200, response.content
        rows = response.json()["results"]
        assert [row["program_name"] for row in rows] == ["Inc Fall"]
        assert rows[0]["program_mobility_direction"] == "incoming"
        program_rows = client.get("/api/programs/", {"direction": "incoming"}).json()
        program_rows = program_rows.get("results", program_rows)
        incoming = [row for row in program_rows if row["name"] == "Inc Fall"]
        assert incoming and incoming[0]["mobility_direction"] == "incoming"
        assert all(row["mobility_direction"] == "incoming" for row in program_rows)
