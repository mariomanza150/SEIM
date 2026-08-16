"""Unit tests for Phase 1 semester / credits eligibility rules."""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from accounts.models import Profile
from exchange.eligibility_rules import ELIGIBILITY_SCHEMA_VERSION, evaluate_eligibility
from exchange.models import Application, ApplicationStatus, Program
from tests.conftest import UserFactory


@pytest.mark.django_db
class TestSemesterHelper:
    def test_calculate_semester_from_ingress(self):
        ingress = date(2024, 1, 1)
        assert (
            Profile.calculate_semester_from_ingress(ingress, on_date=date(2024, 1, 1))
            == 1
        )
        assert (
            Profile.calculate_semester_from_ingress(ingress, on_date=date(2024, 7, 1))
            == 2
        )
        assert (
            Profile.calculate_semester_from_ingress(ingress, on_date=date(2025, 1, 1))
            == 3
        )

    def test_effective_semester_prefers_override(self):
        user = UserFactory()
        profile = user.profile
        profile.ingress_date = date(2020, 1, 1)
        profile.current_semester = 2
        profile.save()
        assert profile.get_effective_semester() == 2


@pytest.mark.django_db
class TestMinSemesterAndCreditsRules:
    def _program(self, **kwargs):
        today = date.today()
        defaults = {
            "name": "Test Scheme",
            "description": "x",
            "start_date": today + timedelta(days=60),
            "end_date": today + timedelta(days=200),
            "is_active": True,
            "min_semester": 4,
            "min_credits_approved_percent": Decimal("50.00"),
        }
        defaults.update(kwargs)
        return Program.objects.create(**defaults)

    def test_fails_when_semester_below_min(self):
        user = UserFactory()
        profile = user.profile
        profile.current_semester = 2
        profile.credits_approved_percent = Decimal("80.00")
        profile.save()
        program = self._program()

        ev = evaluate_eligibility(user, program)
        assert ev.eligible is False
        assert any(r.rule_id == "min_semester" and not r.passed for r in ev.rules)

    def test_fails_when_credits_below_min(self):
        user = UserFactory()
        profile = user.profile
        profile.current_semester = 6
        profile.credits_approved_percent = Decimal("20.00")
        profile.save()
        program = self._program()

        ev = evaluate_eligibility(user, program)
        assert ev.eligible is False
        assert any(r.rule_id == "min_credits" and not r.passed for r in ev.rules)

    def test_passes_with_profile_values(self):
        user = UserFactory()
        profile = user.profile
        profile.current_semester = 6
        profile.credits_approved_percent = Decimal("75.00")
        profile.save()
        program = self._program()

        ev = evaluate_eligibility(user, program)
        assert ev.eligible is True

    def test_application_snapshot_overrides_profile(self):
        user = UserFactory()
        profile = user.profile
        profile.current_semester = 6
        profile.credits_approved_percent = Decimal("90.00")
        profile.save()
        program = self._program()
        status, _ = ApplicationStatus.objects.get_or_create(
            name="draft", defaults={"order": 1}
        )
        application = Application.objects.create(
            program=program,
            student=user,
            status=status,
            semester_at_apply=2,
            credits_percent_at_apply=Decimal("10.00"),
        )

        ev = evaluate_eligibility(user, program, application=application)
        assert ev.eligible is False
        assert any(r.rule_id == "min_semester" and not r.passed for r in ev.rules)
        assert any(r.rule_id == "min_credits" and not r.passed for r in ev.rules)

    def test_schema_version_constant(self):
        assert ELIGIBILITY_SCHEMA_VERSION == 8
