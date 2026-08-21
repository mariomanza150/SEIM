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
        self.program = self.create_program(
            enrollment_capacity=1, waitlist_when_full=True
        )
        submitted, _ = ApplicationStatus.objects.get_or_create(name="submitted")
        ApplicationStatus.objects.get_or_create(
            name="nominated", defaults={"order": 16}
        )
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
        match_url = reverse(
            "api:program-nominations-match", kwargs={"pk": self.program.pk}
        )
        matched = self.client.post(match_url)
        self.assertEqual(matched.status_code, 200)
        self.assertEqual(matched.data["matched"]["nominated"], 1)
        self.assertEqual(matched.data["matched"]["waitlisted"], 1)
        self.app_a.refresh_from_db()
        self.app_b.refresh_from_db()
        names = {self.app_a.status.name, self.app_b.status.name}
        self.assertEqual(names, {"nominated", "waitlist"})

    def test_rematch_does_not_waitlist_existing_nominee(self):
        self.test_staff_can_rank_and_match()
        match_url = reverse(
            "api:program-nominations-match", kwargs={"pk": self.program.pk}
        )
        listed = self.client.get(
            reverse("api:program-nominations", kwargs={"pk": self.program.pk})
        )
        self.assertEqual(listed.data["slots_remaining"], 0)
        rematch = self.client.post(match_url)
        self.assertEqual(rematch.status_code, 200)
        self.assertEqual(rematch.data["matched"]["nominated"], 0)
        self.assertEqual(rematch.data["matched"]["waitlisted"], 0)
        self.app_a.refresh_from_db()
        self.app_b.refresh_from_db()
        names = {self.app_a.status.name, self.app_b.status.name}
        self.assertEqual(names, {"nominated", "waitlist"})

    def test_student_forbidden(self):
        self.authenticate_user(self.student_a)
        url = reverse("api:program-nominations", kwargs={"pk": self.program.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 403)

    def test_slots_remaining_ignores_under_review_pool_apps(self):
        """Submit-time occupancy counts under_review; Match slots must not."""
        under_review, _ = ApplicationStatus.objects.get_or_create(
            name="under_review", defaults={"order": 20}
        )
        self.app_a.status = under_review
        self.app_a.save(update_fields=["status"])
        self.authenticate_user(self.coord)
        url = reverse("api:program-nominations", kwargs={"pk": self.program.pk})
        listed = self.client.get(url)
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(self.program.enrollment_slots_remaining(), 0)
        self.assertEqual(listed.data["slots_remaining"], 1)

    def test_nomination_cycle_quota_and_partner_allocation(self):
        from datetime import date, timedelta

        from exchange.models import ExchangeAgreement, NominationCycle

        self.authenticate_user(self.coord)
        today = date.today()
        cycles_url = reverse(
            "api:program-nomination-cycles", kwargs={"pk": self.program.pk}
        )
        created = self.client.post(
            cycles_url,
            {
                "name": "Fall 2026",
                "opens_at": today.isoformat(),
                "closes_at": (today + timedelta(days=30)).isoformat(),
                "seat_quota": 1,
                "is_active": True,
            },
            format="json",
        )
        self.assertEqual(created.status_code, 201)
        cycle_id = created.data["id"]
        agreement = ExchangeAgreement.objects.create(
            title="Partner MoU",
            partner_institution_name="TU Berlin",
            status=ExchangeAgreement.Status.ACTIVE,
            start_date=today,
            end_date=today + timedelta(days=365),
        )
        agreement.programs.add(self.program)
        alloc_url = reverse(
            "api:program-nomination-partner-allocations",
            kwargs={"pk": self.program.pk, "cycle_id": cycle_id},
        )
        alloc = self.client.post(
            alloc_url,
            {"agreement_id": str(agreement.id), "seat_quota": 1},
            format="json",
        )
        self.assertEqual(alloc.status_code, 200)
        self.assertEqual(alloc.data["allocation"]["seat_quota"], 1)

        listed = self.client.get(
            reverse("api:program-nominations", kwargs={"pk": self.program.pk})
        )
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(listed.data["active_cycle"]["name"], "Fall 2026")
        self.assertEqual(listed.data["slots_remaining"], 1)
        self.assertEqual(len(listed.data["partner_allocations"]), 1)

        self.client.put(
            reverse("api:program-nominations", kwargs={"pk": self.program.pk}),
            {
                "ranks": [
                    {"id": str(self.app_a.id), "rank": 1},
                    {"id": str(self.app_b.id), "rank": 2},
                ]
            },
            format="json",
        )
        matched = self.client.post(
            reverse("api:program-nominations-match", kwargs={"pk": self.program.pk})
        )
        self.assertEqual(matched.status_code, 200)
        self.assertEqual(matched.data["matched"]["nominated"], 1)
        self.assertEqual(matched.data["matched"]["cycle_id"], cycle_id)
        self.app_a.refresh_from_db()
        self.app_b.refresh_from_db()
        nominee = self.app_a if self.app_a.status.name == "nominated" else self.app_b
        self.assertEqual(str(nominee.nomination_cycle_id), cycle_id)
