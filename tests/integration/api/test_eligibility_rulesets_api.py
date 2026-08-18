from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import Role
from exchange.models import EligibilityRuleSet, Program


class TestEligibilityRuleSetsApi(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.student = User.objects.create_user(
            username="student",
            email="student@example.com",
            password="TestPass123!",
        )
        self.coordinator = User.objects.create_user(
            username="coord",
            email="coord@example.com",
            password="TestPass123!",
        )
        coordinator_role, _ = Role.objects.get_or_create(name="coordinator")
        self.coordinator.roles.add(coordinator_role)
        self.ruleset = EligibilityRuleSet.objects.create(
            name="Default",
            description="test",
            schema_version=1,
            rules_json={"rules": []},
            is_active=True,
        )
        self.program = Program.objects.create(
            name="Test Program",
            description="x",
            is_active=True,
            start_date="2026-01-01",
            end_date="2026-06-01",
            eligibility_ruleset=self.ruleset,
        )

    def test_rulesets_list_forbidden_for_student(self):
        self.client.force_authenticate(user=self.student)
        resp = self.client.get("/api/eligibility-rulesets/")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_rulesets_list_allowed_for_coordinator(self):
        self.client.force_authenticate(user=self.coordinator)
        resp = self.client.get("/api/eligibility-rulesets/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("results", resp.data)

    def test_program_check_eligibility_includes_ruleset_snapshot(self):
        self.client.force_authenticate(user=self.coordinator)
        resp = self.client.get(f"/api/programs/{self.program.id}/check_eligibility/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("ruleset", resp.data)
        self.assertEqual(str(resp.data["ruleset"]["id"]), str(self.ruleset.id))

    def test_program_check_eligibility_can_use_ruleset_toggle(self):
        # Override min_gpa to force a failure for a student with no GPA => still skipped, so
        # instead override required_language to something unmet (student has no profile language).
        self.ruleset.rules_json = {
            "program_overrides": {
                "required_language": "Klingon",
            }
        }
        self.ruleset.save()
        self.client.force_authenticate(user=self.coordinator)
        resp = self.client.get(
            f"/api/programs/{self.program.id}/check_eligibility/",
            {"use_ruleset": "true"},
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["schema_version"], 8)
        self.assertTrue(resp.data.get("using_ruleset"))

    def test_check_eligibility_applies_active_ruleset_overrides(self):
        from accounts.models import Profile
        from exchange.services import ApplicationService

        Profile.objects.get_or_create(user=self.student)
        self.ruleset.rules_json = {
            "program_overrides": {
                "required_language": "Klingon",
            }
        }
        self.ruleset.save()
        program = Program.objects.select_related("eligibility_ruleset").get(
            pk=self.program.pk
        )
        with self.assertRaises(ValueError) as ctx:
            ApplicationService.check_eligibility(self.student, program)
        self.assertIn("Klingon", str(ctx.exception))

    def test_check_eligibility_ignores_inactive_ruleset(self):
        from accounts.models import Profile
        from exchange.services import ApplicationService

        Profile.objects.get_or_create(user=self.student)
        self.ruleset.rules_json = {
            "program_overrides": {
                "required_language": "Klingon",
            }
        }
        self.ruleset.is_active = False
        self.ruleset.save()
        program = Program.objects.select_related("eligibility_ruleset").get(
            pk=self.program.pk
        )
        result = ApplicationService.check_eligibility(self.student, program)
        self.assertTrue(result["eligible"])

    def test_evaluate_eligibility_with_application_unwraps_ruleset_proxy(self):
        from accounts.models import Profile
        from exchange.eligibility_rules import evaluate_eligibility
        from exchange.models import Application, ApplicationStatus
        from exchange.services import _program_for_eligibility

        Profile.objects.get_or_create(user=self.student)
        submitted, _ = ApplicationStatus.objects.get_or_create(
            name="submitted", defaults={"order": 2}
        )
        app = Application.objects.create(
            student=self.student, program=self.program, status=submitted
        )
        program = Program.objects.select_related("eligibility_ruleset").get(
            pk=self.program.pk
        )
        proxy = _program_for_eligibility(program)
        ev = evaluate_eligibility(self.student, proxy, application=app)
        self.assertIsNotNone(ev)

    def test_coordinator_can_create_ruleset(self):
        self.client.force_authenticate(user=self.coordinator)
        resp = self.client.post(
            "/api/eligibility-rulesets/",
            {
                "name": "Strict GPA",
                "description": "",
                "is_active": True,
                "schema_version": 1,
                "rules_json": {"program_overrides": {"min_gpa": 3.5}},
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["name"], "Strict GPA")
        self.assertEqual(resp.data["rules_json"]["program_overrides"]["min_gpa"], 3.5)
