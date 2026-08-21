"""Partner portal API."""

from unittest.mock import patch

from django.urls import reverse

from accounts.models import Role
from exchange.models import AgreementComment, Comment, ExchangeAgreement, PartnerContact
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

    def test_partner_checklist_is_read_only_summary(self):
        from documents.models import DocumentType

        doc_type = DocumentType.objects.create(name="Official Transcript")
        self.program.required_document_types.add(doc_type)
        PartnerContact.objects.create(user=self.partner, agreement=self.agreement)
        self.authenticate_user(self.partner)
        url = reverse("api:partner-application-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        results = resp.data["results"] if isinstance(resp.data, dict) else resp.data
        checklist = results[0]["document_checklist"]
        self.assertFalse(checklist["complete"])
        self.assertEqual(checklist["required_count"], 1)
        self.assertEqual(checklist["approved_count"], 0)
        self.assertEqual(len(checklist["items"]), 1)
        item = checklist["items"][0]
        self.assertEqual(item["name"], "Official Transcript")
        self.assertEqual(item["status"], "missing")
        self.assertTrue(item["required"])
        self.assertNotIn("document_id", item)
        self.assertNotIn("instructions", item)
        self.assertNotIn("faq", item)

    def test_partner_can_acknowledge_nomination(self):
        from exchange.models import ApplicationStatus

        PartnerContact.objects.create(user=self.partner, agreement=self.agreement)
        nominated, _ = ApplicationStatus.objects.get_or_create(
            name="nominated", defaults={"order": 16}
        )
        self.app.status = nominated
        self.app.save(update_fields=["status"])
        self.authenticate_user(self.partner)
        url = reverse(
            "api:partner-application-acknowledge-nomination",
            kwargs={"pk": self.app.pk},
        )
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIsNotNone(resp.data.get("partner_nomination_acknowledged_at"))
        self.app.refresh_from_db()
        self.assertIsNotNone(self.app.partner_nomination_acknowledged_at)

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
        url = reverse("api:partner-application-comments", kwargs={"pk": self.app.pk})
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
        url = reverse("api:partner-application-comments", kwargs={"pk": self.app.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_partner_can_post_and_list_agreement_thread(self):
        PartnerContact.objects.create(user=self.partner, agreement=self.agreement)
        AgreementComment.objects.create(
            agreement=self.agreement,
            author=self.coord,
            text="Staff private",
            is_private=True,
        )
        AgreementComment.objects.create(
            agreement=self.agreement,
            author=self.coord,
            text="Public renewal note",
            is_private=False,
        )
        self.authenticate_user(self.partner)
        url = reverse(
            "api:partner-agreement-comments", kwargs={"pk": self.agreement.pk}
        )
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        texts = [row["text"] for row in resp.data]
        self.assertIn("Public renewal note", texts)
        self.assertNotIn("Staff private", texts)
        post = self.client.post(url, {"text": "We can sign in June"}, format="json")
        self.assertEqual(post.status_code, 201)
        self.assertEqual(post.data["text"], "We can sign in June")
        self.assertNotIn("is_private", post.data)
        self.assertTrue(
            AgreementComment.objects.filter(
                agreement=self.agreement,
                author=self.partner,
                text="We can sign in June",
                is_private=False,
            ).exists()
        )

    def test_unlinked_partner_cannot_comment_on_agreement(self):
        self.authenticate_user(self.partner)
        url = reverse(
            "api:partner-agreement-comments", kwargs={"pk": self.agreement.pk}
        )
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    @patch("documents.serializers.DocumentService.virus_scan", return_value=True)
    @patch("documents.serializers.DocumentService.validate_file_type_and_size")
    def test_partner_can_upload_agreement_document(self, _mock_validate, _mock_virus):
        from django.core.files.uploadedfile import SimpleUploadedFile

        from documents.models import ExchangeAgreementDocument

        PartnerContact.objects.create(user=self.partner, agreement=self.agreement)
        self.authenticate_user(self.partner)
        url = reverse(
            "api:partner-agreement-documents", kwargs={"pk": self.agreement.pk}
        )
        pdf = SimpleUploadedFile(
            "signed.pdf", b"%PDF-1.4", content_type="application/pdf"
        )
        resp = self.client.post(
            url,
            {
                "category": ExchangeAgreementDocument.Category.SIGNED_COPY,
                "title": "Partner signed copy",
                "file": pdf,
            },
            format="multipart",
        )
        self.assertEqual(resp.status_code, 201, resp.data)
        self.assertEqual(resp.data["title"], "Partner signed copy")
        self.assertEqual(resp.data["category"], "signed_copy")
        row = ExchangeAgreementDocument.objects.get()
        self.assertEqual(row.agreement_id, self.agreement.id)
        self.assertEqual(row.uploaded_by_id, self.partner.id)

        listed = self.client.get(url)
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(len(listed.data), 1)

    def test_unlinked_partner_cannot_upload_agreement_document(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        self.authenticate_user(self.partner)
        url = reverse(
            "api:partner-agreement-documents", kwargs={"pk": self.agreement.pk}
        )
        pdf = SimpleUploadedFile(
            "signed.pdf", b"%PDF-1.4", content_type="application/pdf"
        )
        resp = self.client.post(
            url,
            {"category": "signed_copy", "file": pdf},
            format="multipart",
        )
        self.assertEqual(resp.status_code, 404)

    @patch("documents.serializers.DocumentService.virus_scan", return_value=True)
    @patch("documents.serializers.DocumentService.validate_file_type_and_size")
    def test_partner_cannot_upload_staff_only_category(self, _mock_validate, _mock_virus):
        from django.core.files.uploadedfile import SimpleUploadedFile

        PartnerContact.objects.create(user=self.partner, agreement=self.agreement)
        self.authenticate_user(self.partner)
        url = reverse(
            "api:partner-agreement-documents", kwargs={"pk": self.agreement.pk}
        )
        pdf = SimpleUploadedFile(
            "mou.pdf", b"%PDF-1.4", content_type="application/pdf"
        )
        resp = self.client.post(
            url,
            {"category": "mou", "file": pdf},
            format="multipart",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("category", resp.data)

    @patch("documents.serializers.DocumentService.virus_scan", return_value=True)
    @patch("documents.serializers.DocumentService.validate_file_type_and_size")
    def test_partner_can_supersede_signed_copy(self, _mock_validate, _mock_virus):
        from django.core.files.uploadedfile import SimpleUploadedFile

        from documents.models import ExchangeAgreementDocument

        PartnerContact.objects.create(user=self.partner, agreement=self.agreement)
        old_file = SimpleUploadedFile(
            "prior.pdf", b"%PDF-1.4", content_type="application/pdf"
        )
        old = ExchangeAgreementDocument.objects.create(
            agreement=self.agreement,
            category=ExchangeAgreementDocument.Category.SIGNED_COPY,
            title="Prior signed",
            file=old_file,
            uploaded_by=self.coord,
        )
        self.authenticate_user(self.partner)
        url = reverse(
            "api:partner-agreement-documents", kwargs={"pk": self.agreement.pk}
        )
        pdf = SimpleUploadedFile(
            "signed-v2.pdf", b"%PDF-1.4", content_type="application/pdf"
        )
        resp = self.client.post(
            url,
            {
                "category": ExchangeAgreementDocument.Category.SIGNED_COPY,
                "title": "Updated signed",
                "file": pdf,
                "supersedes": str(old.id),
            },
            format="multipart",
        )
        self.assertEqual(resp.status_code, 201, resp.data)
        self.assertEqual(str(resp.data["supersedes"]), str(old.id))
        new = ExchangeAgreementDocument.objects.get(title="Updated signed")
        self.assertEqual(new.supersedes_id, old.id)

        listed = self.client.get(url)
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(len(listed.data), 2)

        current = self.client.get(url, {"current_only": "true"})
        self.assertEqual(current.status_code, 200)
        self.assertEqual(len(current.data), 1)
        self.assertEqual(current.data[0]["title"], "Updated signed")
