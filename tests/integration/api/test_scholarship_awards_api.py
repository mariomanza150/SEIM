"""API tests for scholarship award workflow."""

from django.urls import reverse

from exchange.models import ScholarshipAward
from tests.utils import APITestCase


class TestScholarshipAwardsAPI(APITestCase):
    def setUp(self):
        super().setUp()
        self.student = self.create_user(role="student")
        self.coord = self.create_user(role="coordinator")
        self.program = self.create_program()
        self.app = self.create_application(student=self.student, program=self.program)

    def test_staff_can_create_award(self):
        self.authenticate_user(self.coord)
        url = reverse("api:application-scholarship-award", kwargs={"pk": self.app.pk})
        resp = self.client.put(
            url,
            {
                "status": "nominated",
                "amount": "5000",
                "currency": "MXN",
                "notes": "merit",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["status"], "nominated")
        self.assertTrue(ScholarshipAward.objects.filter(application=self.app).exists())

    def test_student_cannot_mutate_award(self):
        self.authenticate_user(self.student)
        url = reverse("api:application-scholarship-award", kwargs={"pk": self.app.pk})
        resp = self.client.put(url, {"status": "awarded"}, format="json")
        self.assertEqual(resp.status_code, 403)

    def test_student_sees_award_on_detail(self):
        ScholarshipAward.objects.create(
            application=self.app, status=ScholarshipAward.Status.AWARDED, amount=1000
        )
        self.authenticate_user(self.student)
        url = reverse("api:application-detail", kwargs={"pk": self.app.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["scholarship_award"]["status"], "awarded")

    def test_export_requires_staff(self):
        self.authenticate_user(self.student)
        url = reverse("api:application-scholarship-awards-export")
        resp = self.client.get(url, {"program": str(self.program.pk)})
        self.assertEqual(resp.status_code, 403)
