"""Integration tests for scholarship scoring ruleset API."""

from rest_framework import status
from rest_framework.test import APITestCase

from exchange.models import ScholarshipScoringRuleset
from exchange.scholarship_scoring import DEFAULT_FACTOR_MAX, RULESET_ID
from tests.utils import TestUtils


class ScholarshipScoringRulesetApiTests(APITestCase):
    def setUp(self):
        self.admin = TestUtils.create_test_user(role="admin", username="ssr_admin")
        self.coordinator = TestUtils.create_test_user(
            role="coordinator", username="ssr_coord"
        )
        self.student = TestUtils.create_test_user(role="student", username="ssr_stu")
        self.ruleset = ScholarshipScoringRuleset.objects.filter(slug=RULESET_ID).first()
        if self.ruleset is None:
            self.ruleset = ScholarshipScoringRuleset.objects.create(
                slug=RULESET_ID,
                label="Default scholarship rubric (v1)",
                factor_weights=dict(DEFAULT_FACTOR_MAX),
                is_active=True,
            )

    def test_student_forbidden(self):
        self.client.force_authenticate(self.student)
        resp = self.client.get("/api/scholarship-scoring-rulesets/")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_coordinator_lists_and_gets_active(self):
        self.client.force_authenticate(self.coordinator)
        resp = self.client.get("/api/scholarship-scoring-rulesets/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        results = resp.data.get("results", resp.data)
        self.assertTrue(any(r["slug"] == RULESET_ID for r in results))

        active = self.client.get("/api/scholarship-scoring-rulesets/active/")
        self.assertEqual(active.status_code, status.HTTP_200_OK)
        self.assertEqual(active.data["slug"], RULESET_ID)
        self.assertIn("factor_catalog", active.data)
        self.assertEqual(len(active.data["factor_catalog"]), 5)

    def test_admin_patches_weights(self):
        self.client.force_authenticate(self.admin)
        new_weights = {
            **DEFAULT_FACTOR_MAX,
            "academic": 30.0,
            "language": 15.0,
        }
        resp = self.client.patch(
            f"/api/scholarship-scoring-rulesets/{self.ruleset.id}/",
            {"factor_weights": new_weights, "label": "Custom weighted rubric"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["factor_weights"]["academic"], 30.0)
        self.ruleset.refresh_from_db()
        self.assertEqual(self.ruleset.label, "Custom weighted rubric")
        self.assertEqual(float(self.ruleset.factor_weights["academic"]), 30.0)

    def test_rejects_invalid_weight(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.patch(
            f"/api/scholarship-scoring-rulesets/{self.ruleset.id}/",
            {"factor_weights": {**DEFAULT_FACTOR_MAX, "academic": 0}},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
