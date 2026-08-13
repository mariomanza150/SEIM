"""Partner portal API."""

from django.urls import reverse

from accounts.models import Role
from exchange.models import Comment, ExchangeAgreement, PartnerContact
from tests.utils import APITestCase


class TestPartnerPortalAPI(APITestCase):
    def setUp(self):
        super().setUp()
        self.partner = self.create_user(
            role="partner", username="partner1", email="partner@example.com"
        )
        self.student = self.create_user(role="student")
        self.coord = self.create_user(role="coordinator")
        self.program = self.create_program()
        self.agreement = ExchangeAgreement.objects.create(
            title="MoU",
            partner_institution_name="TU Berlin",
            status=ExchangeAgreement.Status.ACTIVE,
        )
        self.agreement.programs.add(self.program)
        self.app = self.create_application(
            student=self.student, program=self.program, status_name="submitted"
        )

    def test_partner_sees_linked_agreement_only(self):
        PartnerContact.objects.create(user=self.partner, agreement=self.agreement)
        self.authenticate_user(self.partner)
        url = reverse("api:partner-agreement-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        results = resp.data["results"] if isinstance(resp.data, dict) else resp.data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "MoU")

    def test_unlinked_partner_sees_empty(self):
        self.authenticate_user(self.partner)
        url = reverse("api:partner-agreement-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        results = resp.data["results"] if isinstance(resp.data, dict) else resp.data
        self.assertEqual(len(results), 0)

    def test_partner_sees_limited_applicant_fields(self):
        PartnerContact.objects.create(user=self.partner, agreement=self.agreement)
        self.authenticate_user(self.partner)
        url = reverse("api:partner-application-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        results = resp.data["results"] if isinstance(resp.data, dict) else resp.data
        self.assertEqual(len(results), 1)
        row = results[0]
        self.assertIn("student_display_name", row)
        self.assertNotIn("student_email", row)
        self.assertIn("document_checklist", row)

    def test_student_forbidden(self):
        self.authenticate_user(self.student)
        url = reverse("api:partner-agreement-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 403)

    def test_staff_can_link_partner_by_email(self):
        Role.objects.get_or_create(name="partner")
        self.authenticate_user(self.coord)
        url = reverse(
            "api:partner-agreement-add-partner-contact",
            kwargs={"pk": self.agreement.pk},
        )
        resp = self.client.post(
            url, {"email": self.partner.email, "title": "IRO"}, format="json"
        )
        self.assertIn(resp.status_code, (200, 201))
        self.assertTrue(
            PartnerContact.objects.filter(
                user=self.partner, agreement=self.agreement
            ).exists()
        )

    def test_partner_can_post_and_list_public_thread(self):
        PartnerContact.objects.create(user=self.partner, agreement=self.agreement)
        Comment.objects.create(
            application=self.app,
            author=self.coord,
            text="Staff private",
            is_private=True,
        )
        Comment.objects.create(
            application=self.app,
            author=self.coord,
            text="Hello partner",
            is_private=False,
        )
        self.authenticate_user(self.partner)
        url = reverse(
            "api:partner-application-comments", kwargs={"pk": self.app.pk}
        )
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        texts = [row["text"] for row in resp.data]
        self.assertIn("Hello partner", texts)
        self.assertNotIn("Staff private", texts)
        post = self.client.post(url, {"text": "Nomination received"}, format="json")
        self.assertEqual(post.status_code, 201)
        self.assertEqual(post.data["text"], "Nomination received")
        self.assertTrue(
            Comment.objects.filter(
                application=self.app,
                author=self.partner,
                text="Nomination received",
                is_private=False,
            ).exists()
        )

    def test_unlinked_partner_cannot_comment(self):
        self.authenticate_user(self.partner)
        url = reverse(
            "api:partner-application-comments", kwargs={"pk": self.app.pk}
        )
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)
