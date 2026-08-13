"""Scholarship award state machine."""

from decimal import Decimal

import pytest

from exchange.models import ScholarshipAward
from exchange.scholarship_awards import serialize_award, transition_award, upsert_award
from tests.utils import APITestCase


@pytest.mark.django_db
class TestScholarshipAwards(APITestCase):
    def setUp(self):
        super().setUp()
        self.student = self.create_user(role="student")
        self.coord = self.create_user(role="coordinator")
        self.program = self.create_program()
        self.app = self.create_application(student=self.student, program=self.program)

    def test_nominate_and_award(self):
        award = upsert_award(self.app, self.coord, status_value="nominated", amount="12000")
        self.assertEqual(award.status, ScholarshipAward.Status.NOMINATED)
        self.assertEqual(award.amount, Decimal("12000"))
        award = transition_award(award, self.coord, "awarded")
        self.assertEqual(award.status, ScholarshipAward.Status.AWARDED)
        payload = serialize_award(award)
        self.assertEqual(payload["status"], "awarded")
        self.assertEqual(
            sorted(payload["allowed_transitions"]),
            ["declined", "disbursing", "withdrawn"],
        )

    def test_illegal_transition(self):
        award = upsert_award(self.app, self.coord, status_value="nominated")
        with self.assertRaises(ValueError):
            transition_award(award, self.coord, "disbursed")
