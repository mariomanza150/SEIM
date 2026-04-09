from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from grades.models import GradeScale, GradeTranslation, GradeValue


User = get_user_model()


class TestGradesAPI(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="grades-api-user",
            email="grades-api@example.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)

        self.source_scale = GradeScale.objects.create(
            name="US GPA 4.0 Scale",
            code="US_GPA_4_API",
            country="United States",
            min_value=0.0,
            max_value=4.0,
            passing_value=2.0,
        )
        self.target_scale = GradeScale.objects.create(
            name="ECTS Scale",
            code="ECTS_API",
            country="Europe",
            min_value=0.0,
            max_value=100.0,
            passing_value=50.0,
        )

        self.source_grade = GradeValue.objects.create(
            grade_scale=self.source_scale,
            label="A",
            numeric_value=4.0,
            gpa_equivalent=4.0,
            order=1,
        )
        self.target_grade = GradeValue.objects.create(
            grade_scale=self.target_scale,
            label="A",
            numeric_value=95.0,
            gpa_equivalent=4.0,
            order=1,
        )
        GradeTranslation.objects.create(
            source_grade=self.source_grade,
            target_grade=self.target_grade,
            confidence=1.0,
            created_by=self.user,
        )

    def test_grade_scale_list_is_exposed_under_grades_api(self):
        response = self.client.get(reverse("grades:gradescale-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        items = response.data.get("results", response.data)
        returned_ids = {str(item["id"]) for item in items}
        self.assertIn(str(self.source_scale.id), returned_ids)
        self.assertIn(str(self.target_scale.id), returned_ids)

    def test_grade_values_by_scale_endpoint_is_exposed(self):
        response = self.client.get(
            reverse("grades:gradevalue-by-scale"),
            {"grade_scale": str(self.source_scale.id)},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["label"], "A")
        self.assertEqual(str(response.data[0]["grade_scale"]), str(self.source_scale.id))

    def test_grade_translation_endpoint_translates_between_scales(self):
        response = self.client.post(
            reverse("grades:gradetranslation-translate"),
            {
                "source_grade_value_id": str(self.source_grade.id),
                "target_scale_id": str(self.target_scale.id),
                "fallback_to_gpa": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["translation_method"], "direct")
        self.assertEqual(response.data["source_grade"]["id"], str(self.source_grade.id))
        self.assertEqual(response.data["target_grade"]["id"], str(self.target_grade.id))
