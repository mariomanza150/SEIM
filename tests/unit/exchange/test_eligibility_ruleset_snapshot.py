"""Unit tests for apply-time eligibility ruleset document freeze."""

from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models import Profile
from exchange.eligibility_rulesets import (
    build_ruleset_snapshot,
    parse_ruleset_overrides_from_snapshot,
)
from exchange.models import Application, ApplicationStatus, EligibilityRuleSet, Program
from exchange.services import ApplicationService, _program_for_eligibility


class TestEligibilityRulesetSnapshot(TestCase):
    def setUp(self):
        User = get_user_model()
        self.student = User.objects.create_user(
            username="snap_student",
            email="snap@example.com",
            password="TestPass123!",
        )
        Profile.objects.update_or_create(
            user=self.student,
            defaults={"language": "English", "language_level": "B2"},
        )
        self.ruleset = EligibilityRuleSet.objects.create(
            name="Overlay",
            schema_version=2,
            content_revision=1,
            rules_json={
                "program_overrides": {
                    "required_language": "English",
                    "min_gpa": 3.0,
                }
            },
            is_active=True,
        )
        self.program = Program.objects.create(
            name="Snap Program",
            description="x",
            is_active=True,
            start_date="2026-01-01",
            end_date="2026-06-01",
            eligibility_ruleset=self.ruleset,
        )
        draft, _ = ApplicationStatus.objects.get_or_create(
            name="draft", defaults={"order": 1}
        )
        self.app = Application.objects.create(
            student=self.student, program=self.program, status=draft
        )

    def test_build_ruleset_snapshot_copies_document(self):
        snap = build_ruleset_snapshot(self.ruleset)
        self.assertEqual(snap["schema_version"], 2)
        self.assertEqual(snap["content_revision"], 1)
        self.assertEqual(
            snap["rules_json"]["program_overrides"]["required_language"], "English"
        )
        # Mutating live ruleset must not alter the frozen copy.
        self.ruleset.rules_json = {"program_overrides": {"required_language": "Klingon"}}
        self.assertEqual(
            snap["rules_json"]["program_overrides"]["required_language"], "English"
        )

    def test_capture_freezes_active_ruleset(self):
        ApplicationService.capture_eligibility_snapshot(self.app)
        self.app.refresh_from_db()
        snap = self.app.eligibility_ruleset_snapshot
        self.assertIsNotNone(snap)
        self.assertEqual(snap["id"], str(self.ruleset.id))
        self.assertEqual(snap["content_revision"], 1)
        self.assertEqual(
            snap["rules_json"]["program_overrides"]["min_gpa"], 3.0
        )

    def test_frozen_snapshot_survives_live_ruleset_edit(self):
        ApplicationService.capture_eligibility_snapshot(self.app)
        self.app.refresh_from_db()

        # Staff tightens language after apply — live check would fail.
        self.ruleset.rules_json = {
            "program_overrides": {"required_language": "Klingon"}
        }
        self.ruleset.content_revision = 2
        self.ruleset.save()

        live = _program_for_eligibility(self.program)
        self.assertEqual(live.required_language, "Klingon")

        frozen = _program_for_eligibility(self.program, application=self.app)
        self.assertEqual(frozen.required_language, "English")
        self.assertEqual(frozen.min_gpa, 3.0)

        # Service check with application must use frozen overlay.
        result = ApplicationService.check_eligibility(
            self.student, self.program, application=self.app
        )
        self.assertTrue(result["eligible"])

    def test_inactive_ruleset_yields_null_snapshot(self):
        self.ruleset.is_active = False
        self.ruleset.save()
        ApplicationService.capture_eligibility_snapshot(self.app)
        self.app.refresh_from_db()
        self.assertIsNone(self.app.eligibility_ruleset_snapshot)
        overrides = parse_ruleset_overrides_from_snapshot(None)
        self.assertIsNone(overrides)
