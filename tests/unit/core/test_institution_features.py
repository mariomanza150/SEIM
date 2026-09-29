"""Tests for GET/PATCH /api/features/ and scholarship omission when disabled."""

from django.urls import reverse
from rest_framework import status

from core.models import InstitutionFeatureSettings
from tests.utils import APITestCase


class TestInstitutionFeaturesAPI(APITestCase):
    def test_get_requires_auth(self):
        response = self.client.get("/api/features/")
        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_get_returns_default_enabled(self):
        user = self.create_user(role="student")
        self.authenticate_user(user)
        response = self.client.get("/api/features/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["scholarships_enabled"])

    def test_patch_admin_only(self):
        student = self.create_user(role="student")
        self.authenticate_user(student)
        response = self.client.patch(
            "/api/features/", {"scholarships_enabled": False}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        coordinator = self.create_user(role="coordinator")
        self.authenticate_user(coordinator)
        response = self.client.patch(
            "/api/features/", {"scholarships_enabled": False}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        admin = self.create_user(role="admin")
        self.authenticate_user(admin)
        response = self.client.patch(
            "/api/features/", {"scholarships_enabled": False}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["scholarships_enabled"])
        self.assertFalse(InstitutionFeatureSettings.get_solo().scholarships_enabled)

    def test_application_detail_omits_scholarship_fields_when_disabled(self):
        InstitutionFeatureSettings.get_solo()
        InstitutionFeatureSettings.objects.filter(pk=1).update(scholarships_enabled=False)

        student = self.create_user(role="student")
        app = self.create_application(student=student, status_name="submitted")
        self.authenticate_user(student)
        url = reverse("api:application-detail", args=[app.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("scholarship_allocation_score", response.data)
        self.assertNotIn("scholarship_award", response.data)

    def test_scholarship_endpoints_404_when_disabled(self):
        InstitutionFeatureSettings.get_solo()
        InstitutionFeatureSettings.objects.filter(pk=1).update(scholarships_enabled=False)

        coordinator = self.create_user(role="coordinator")
        program = self.create_program()
        student = self.create_user(role="student")
        app = self.create_application(
            student=student, program=program, status_name="submitted"
        )
        self.authenticate_user(coordinator)

        rulesets = self.client.get("/api/scholarship-scoring-rulesets/")
        self.assertEqual(rulesets.status_code, status.HTTP_404_NOT_FOUND)

        scores = self.client.get(
            reverse("api:application-scholarship-scores-export"),
            {"program": str(program.id)},
        )
        self.assertEqual(scores.status_code, status.HTTP_404_NOT_FOUND)

        awards = self.client.get(
            reverse("api:application-scholarship-awards-export"),
            {"program": str(program.id)},
        )
        self.assertEqual(awards.status_code, status.HTTP_404_NOT_FOUND)

        award = self.client.get(
            reverse("api:application-scholarship-award", kwargs={"pk": app.id})
        )
        self.assertEqual(award.status_code, status.HTTP_404_NOT_FOUND)
