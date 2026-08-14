"""Nomination ranking and seat matching."""

from django.urls import reverse

from exchange.models import ApplicationStatus
from tests.utils import APITestCase


class TestNominationMatchingAPI(APITestCase):
    def setUp(self):
        super().setUp()
        self.coord = self.create_user(role="coordinator")
        self.student_a = self.create_user(role="student", username="nom_a")
        self.student_b = self.create_user(role="student", username="nom_b")
        self.program = self.create_program(enrollment_capacity=1, waitlist_when_full=True)
        submitted, _ = ApplicationStatus.objects.get_or_create(name="submitted")
        ApplicationStatus.objects.get_or_create(name="nominated", defaults={"order": 16})
        ApplicationStatus.objects.get_or_create(name="waitlist", defaults={"order": 15})
        self.app_a = self.create_application(
            student=self.student_a, program=self.program, status_name="submitted"
        )
        self.app_b = self.create_application(
            student=self.student_b, program=self.program, status_name="submitted"
        )
        self.app_a.status = submitted
        self.app_a.save()
        self.app_b.status = submitted
        self.app_b.save()

    def test_staff_can_rank_and_match(self):
        self.authenticate_user(self.coord)
        url = reverse("api:program-nominations", kwargs={"pk": self.program.pk})
        listed = self.client.get(url)
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(len(listed.data["applications"]), 2)
        put = self.client.put(
            url,
            {
                "ranks": [
                    {"id": str(self.app_a.id), "rank": 1},
                    {"id": str(self.app_b.id), "rank": 2},
                ]
            },
            format="json",
        )
        self.assertEqual(put.status_code, 200)
        match_url = reverse("api:program-nominations-match", kwargs={"pk": self.program.pk})
        matched = self.client.post(match_url)
        self.assertEqual(matched.status_code, 200)
        self.assertEqual(matched.data["matched"]["nominated"], 1)
        self.assertEqual(matched.data["matched"]["waitlisted"], 1)
        self.app_a.refresh_from_db()
        self.app_b.refresh_from_db()
        names = {self.app_a.status.name, self.app_b.status.name}
        self.assertEqual(names, {"nominated", "waitlist"})

    def test_student_forbidden(self):
        self.authenticate_user(self.student_a)
        url = reverse("api:program-nominations", kwargs={"pk": self.program.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 403)
