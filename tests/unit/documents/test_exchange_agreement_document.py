from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from documents.filters import ExchangeAgreementDocumentFilter
from documents.models import ExchangeAgreementDocument
from exchange.models import ExchangeAgreement


class ExchangeAgreementDocumentFilterTests(TestCase):
    def setUp(self):
        self.agreement = ExchangeAgreement.objects.create(
            title="Agr",
            partner_institution_name="Uni",
            status=ExchangeAgreement.Status.ACTIVE,
        )

    def test_current_only_excludes_superseded(self):
        f1 = SimpleUploadedFile("v1.pdf", b"%PDF-1.4 test", content_type="application/pdf")
        f2 = SimpleUploadedFile("v2.pdf", b"%PDF-1.4 test2", content_type="application/pdf")
        old = ExchangeAgreementDocument.objects.create(
            agreement=self.agreement,
            category=ExchangeAgreementDocument.Category.SIGNED_COPY,
            file=f1,
        )
        new = ExchangeAgreementDocument.objects.create(
            agreement=self.agreement,
            category=ExchangeAgreementDocument.Category.SIGNED_COPY,
            file=f2,
            supersedes=old,
        )

        qs = ExchangeAgreementDocument.objects.all()
        flt = ExchangeAgreementDocumentFilter(
            data={"current_only": "true"},
            queryset=qs,
        )
        self.assertTrue(flt.is_valid(), flt.errors)
        self.assertEqual(list(flt.qs), [new])


class ExchangeAgreementDocumentSerializerValidationTests(TestCase):
    def setUp(self):
        self.agreement = ExchangeAgreement.objects.create(
            title="Agr",
            partner_institution_name="Uni",
            status=ExchangeAgreement.Status.ACTIVE,
        )
        self.other = ExchangeAgreement.objects.create(
            title="Other",
            partner_institution_name="X",
            status=ExchangeAgreement.Status.ACTIVE,
        )

    @patch("documents.serializers.DocumentService.virus_scan", return_value=True)
    @patch("documents.serializers.DocumentService.validate_file_type_and_size")
    def test_rejects_supersedes_from_other_agreement(self, _mock_validate, _mock_virus):
        from django.contrib.auth import get_user_model
        from rest_framework.test import APIRequestFactory

        from documents.serializers import ExchangeAgreementDocumentSerializer

        f1 = SimpleUploadedFile("v1.pdf", b"%PDF-1.4", content_type="application/pdf")
        old = ExchangeAgreementDocument.objects.create(
            agreement=self.other,
            category=ExchangeAgreementDocument.Category.SIGNED_COPY,
            file=f1,
        )
        User = get_user_model()
        user = User.objects.create_user(username="c1", email="c1@e.com", password="x")
        request = APIRequestFactory().post("/")
        request.user = user

        f2 = SimpleUploadedFile("v2.pdf", b"%PDF-1.4", content_type="application/pdf")
        ser = ExchangeAgreementDocumentSerializer(
            data={
                "agreement": str(self.agreement.id),
                "category": ExchangeAgreementDocument.Category.SIGNED_COPY,
                "file": f2,
                "supersedes": str(old.id),
            },
            context={"request": request},
        )
        self.assertFalse(ser.is_valid())
        self.assertIn("supersedes", ser.errors)
