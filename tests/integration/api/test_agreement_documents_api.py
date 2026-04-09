from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Role
from documents.models import ExchangeAgreementDocument
from exchange.models import ExchangeAgreement

User = get_user_model()


def _grant_role(user, role_name: str):
    role, _ = Role.objects.get_or_create(name=role_name)
    user.roles.add(role)


class AgreementDocumentsAPITests(APITestCase):
    def setUp(self):
        self.url = reverse("api:agreement-document-list")
        self.agreement = ExchangeAgreement.objects.create(
            title="API Agr",
            partner_institution_name="Partner",
            status=ExchangeAgreement.Status.ACTIVE,
        )

    def test_student_forbidden(self):
        student = User.objects.create_user(
            username="stu_ad", email="stu_ad@example.com", password="pass12345"
        )
        _grant_role(student, "student")
        self.client.force_authenticate(student)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch("documents.serializers.DocumentService.virus_scan", return_value=True)
    @patch("documents.serializers.DocumentService.validate_file_type_and_size")
    def test_coordinator_multipart_create(self, _mock_validate, _mock_virus):
        coord = User.objects.create_user(
            username="coord_ad", email="coord_ad@example.com", password="pass12345"
        )
        _grant_role(coord, "coordinator")
        self.client.force_authenticate(coord)

        pdf = SimpleUploadedFile("signed.pdf", b"%PDF-1.4", content_type="application/pdf")
        response = self.client.post(
            self.url,
            {
                "agreement": str(self.agreement.id),
                "category": ExchangeAgreementDocument.Category.SIGNED_COPY,
                "title": "Signed 2025",
                "file": pdf,
            },
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(ExchangeAgreementDocument.objects.count(), 1)
        row = ExchangeAgreementDocument.objects.get()
        self.assertEqual(row.uploaded_by_id, coord.id)

    @patch("documents.serializers.DocumentService.virus_scan", return_value=True)
    @patch("documents.serializers.DocumentService.validate_file_type_and_size")
    def test_current_only_query_param(self, _mock_validate, _mock_virus):
        coord = User.objects.create_user(
            username="coord_ad2", email="coord_ad2@example.com", password="pass12345"
        )
        _grant_role(coord, "coordinator")
        self.client.force_authenticate(coord)

        f1 = SimpleUploadedFile("a.pdf", b"%PDF-1.4", content_type="application/pdf")
        f2 = SimpleUploadedFile("b.pdf", b"%PDF-1.4", content_type="application/pdf")
        old = ExchangeAgreementDocument.objects.create(
            agreement=self.agreement,
            category=ExchangeAgreementDocument.Category.OTHER,
            file=f1,
            uploaded_by=coord,
        )
        ExchangeAgreementDocument.objects.create(
            agreement=self.agreement,
            category=ExchangeAgreementDocument.Category.OTHER,
            file=f2,
            uploaded_by=coord,
            supersedes=old,
        )

        response = self.client.get(self.url, {"current_only": "true", "agreement": str(self.agreement.id)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
