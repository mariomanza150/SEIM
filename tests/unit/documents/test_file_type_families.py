from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from documents.file_type_families import (
    FILE_TYPE_FAMILY_SPECS,
    infer_family_slugs_from_extensions,
    seed_file_type_families,
)
from documents.mobility_document_catalog import seed_mobility_document_types
from documents.models import DocumentType, FileTypeFamily
from documents.services import DocumentService
from tests.utils import TestUtils


class TestFileTypeFamilies(TestCase):
    def test_infer_maps_extensions_to_umbrella_slugs(self):
        self.assertEqual(
            infer_family_slugs_from_extensions("pdf,jpg,jpeg,png,docx"),
            ["pdf", "image", "word"],
        )

    def test_seed_creates_healthy_catalog(self):
        families = seed_file_type_families()
        slugs = list(families.values_list("slug", flat=True))
        self.assertGreaterEqual(len(slugs), 8)
        self.assertIn("pdf", slugs)
        self.assertIn("image", slugs)
        self.assertIn("word", slugs)
        image = FileTypeFamily.objects.get(slug="image")
        self.assertIn("jpg", image.parsed_extensions())
        self.assertIn("png", image.parsed_extensions())

    def test_parsed_accepted_extensions_expands_families(self):
        seed_file_type_families()
        dt = DocumentType.objects.create(name="ID scan", accepted_extensions="svg")
        dt.file_type_families.set(FileTypeFamily.objects.filter(slug__in=["pdf", "image"]))
        exts = dt.parsed_accepted_extensions()
        self.assertIn("pdf", exts)
        self.assertIn("jpg", exts)
        self.assertIn("png", exts)
        self.assertIn("svg", exts)

    def test_image_family_allows_jpeg_upload(self):
        seed_file_type_families()
        dt = DocumentType.objects.create(name="Photo only")
        dt.file_type_families.set(FileTypeFamily.objects.filter(slug="image"))
        uploaded = SimpleUploadedFile(
            "id.jpg", b"\xff\xd8\xff" + b"x" * 20, content_type="image/jpeg"
        )
        uploaded.seek(0)
        self.assertTrue(DocumentService.validate_file_type_and_size(uploaded, dt))

    def test_mobility_seed_assigns_families_to_all_types(self):
        types = seed_mobility_document_types()
        self.assertEqual(FileTypeFamily.objects.count(), len(FILE_TYPE_FAMILY_SPECS))
        for dt in types:
            self.assertTrue(
                dt.file_type_families.exists(),
                f"{dt.slug} should have at least one file-type family",
            )
        passport = DocumentType.objects.get(slug="pasaporte_vigente")
        slugs = set(passport.file_type_families.values_list("slug", flat=True))
        self.assertEqual(slugs, {"pdf", "image"})
        postulacion = DocumentType.objects.get(slug="carta_postulacion")
        self.assertEqual(
            set(postulacion.file_type_families.values_list("slug", flat=True)),
            {"pdf", "word"},
        )

    def test_admin_can_list_and_assign_families(self):
        seed_file_type_families()
        admin = TestUtils.create_test_user(username="ftf_admin", role="admin")
        dt = DocumentType.objects.create(name="Assign families")
        image = FileTypeFamily.objects.get(slug="image")
        client = APIClient()
        client.force_authenticate(user=admin)
        list_res = client.get(reverse("api:documenttype-file-type-families"))
        self.assertEqual(list_res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(list_res.data["results"]), 8)
        patch_res = client.patch(
            reverse("api:documenttype-detail", args=[dt.id]),
            {"file_type_family_ids": [image.id]},
            format="json",
        )
        self.assertEqual(patch_res.status_code, status.HTTP_200_OK, patch_res.data)
        dt.refresh_from_db()
        self.assertEqual(list(dt.file_type_families.values_list("slug", flat=True)), ["image"])
        self.assertEqual(patch_res.data["file_type_family_ids"], [image.id])
