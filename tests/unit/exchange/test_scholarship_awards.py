"""Scholarship award state machine."""

from decimal import Decimal

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from documents.models import Document, DocumentType
from exchange.models import ScholarshipAward
from exchange.scholarship_awards import serialize_award, transition_award, upsert_award
from tests.utils import APITestCase


@pytest.mark.django_db
class TestScholarshipAwards(APITestCase):
    def setUp(self):
        super().setUp()
        self.student = self.create_user(role="student")
        self.coord = self.create_user(role="coordinator")
        self.program = self.create_program()
        self.app = self.create_application(student=self.student, program=self.program)

    def _ensure_type(self, slug, name):
        dt = DocumentType.objects.filter(slug=slug).first()
        if dt:
            return dt
        dt = DocumentType.objects.filter(name=name).first()
        if dt:
            if dt.slug != slug:
                dt.slug = slug
                dt.save(update_fields=["slug"])
            return dt
        return DocumentType.objects.create(name=name, slug=slug)

    def _attach_evidence(self, slug, name, *, is_valid=True):
        dt = self._ensure_type(slug, name)
        return Document.objects.create(
            application=self.app,
            type=dt,
            uploaded_by=self.student,
            is_valid=is_valid,
            file=SimpleUploadedFile(
                "evidence.pdf", b"%PDF-1.4 test", content_type="application/pdf"
            ),
        )

    def test_nominate_and_award(self):
        self._attach_evidence("carta_beca", "Carta Beca", is_valid=True)
        award = upsert_award(
            self.app, self.coord, status_value="nominated", amount="12000"
        )
        self.assertEqual(award.status, ScholarshipAward.Status.NOMINATED)
        self.assertEqual(award.amount, Decimal("12000"))
        award = transition_award(award, self.coord, "awarded")
        self.assertEqual(award.status, ScholarshipAward.Status.AWARDED)
        payload = serialize_award(award)
        self.assertEqual(payload["status"], "awarded")
        self.assertEqual(
            sorted(payload["allowed_transitions"]),
            ["declined", "disbursing", "withdrawn"],
        )

    def test_illegal_transition(self):
        award = upsert_award(self.app, self.coord, status_value="nominated")
        with self.assertRaises(ValueError):
            transition_award(award, self.coord, "disbursed")

    def test_first_disbursement_moves_awarded_to_disbursing_despite_prefetch(self):
        from exchange.models import ScholarshipAward as AwardModel
        from exchange.scholarship_awards import upsert_disbursement

        self._attach_evidence("carta_beca", "Carta Beca", is_valid=True)
        award = upsert_award(self.app, self.coord, status_value="nominated")
        award = transition_award(award, self.coord, "awarded")
        cached = AwardModel.objects.prefetch_related("disbursements").get(pk=award.pk)
        upsert_disbursement(
            cached, {"label": "Fall disbursement", "amount": "1000"}, actor=self.coord
        )
        cached.refresh_from_db()
        self.assertEqual(cached.status, AwardModel.Status.DISBURSING)

    def test_awarded_requires_validated_letter_when_catalog_present(self):
        self._ensure_type("carta_beca", "Carta Beca")
        award = upsert_award(self.app, self.coord, status_value="nominated")
        with self.assertRaises(ValueError) as ctx:
            transition_award(award, self.coord, "awarded")
        self.assertIn("carta_beca", str(ctx.exception))
        self._attach_evidence("oficio_asignacion_beca", "Oficio de Asignación de Beca")
        award = transition_award(award, self.coord, "awarded")
        self.assertEqual(award.status, ScholarshipAward.Status.AWARDED)
        gates = serialize_award(award)["evidence_gates"]
        self.assertTrue(gates["awarded"]["configured"])
        self.assertTrue(gates["awarded"]["satisfied"])

    def test_disbursed_requires_validated_recibo_when_catalog_present(self):
        self._attach_evidence("carta_beca", "Carta Beca")
        self._ensure_type("recibo_beca", "Recibo de Beca")
        award = upsert_award(self.app, self.coord, status_value="nominated")
        award = transition_award(award, self.coord, "awarded")
        award = transition_award(award, self.coord, "disbursing")
        with self.assertRaises(ValueError) as ctx:
            transition_award(award, self.coord, "disbursed")
        self.assertIn("recibo_beca", str(ctx.exception))
        self._attach_evidence("recibo_beca", "Recibo de Beca")
        award = transition_award(award, self.coord, "disbursed")
        self.assertEqual(award.status, ScholarshipAward.Status.DISBURSED)

    def test_upsert_to_awarded_blocked_without_letter(self):
        self._ensure_type("carta_beca", "Carta Beca")
        with self.assertRaises(ValueError):
            upsert_award(self.app, self.coord, status_value="awarded", amount="1000")
        self.assertFalse(ScholarshipAward.objects.filter(application=self.app).exists())
