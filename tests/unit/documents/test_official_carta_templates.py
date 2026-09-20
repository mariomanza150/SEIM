"""Official FS-CC / FS-CP / FS-PR blank DOCX templates for student download."""

from __future__ import annotations

from pathlib import Path

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from cms.cgri_samples import (
    OFFICIAL_DOCX_DOWNLOAD_NAMES,
    official_sample_path,
    official_template_download_name,
    samples_dir,
)
from documents.cgri_ingest import ingest_cgri_samples
from documents.mailmerge import docx_has_fillable_fields, merge_docx
from documents.mobility_document_catalog import seed_mobility_document_types
from documents.models import DocumentType
from exchange.models import Application, ApplicationStatus
from tests.utils import TestUtils

OFFICIAL_CARTA_SLUGS = (
    "carta_compromiso",
    "carta_postulacion",
    "carta_retorno_programa",
)


def _require_samples():
    base = samples_dir()
    if not base.is_dir():
        pytest.skip("SAMPLES/ not present")
    missing = [
        slug
        for slug in OFFICIAL_CARTA_SLUGS
        if official_sample_path(slug) is None
    ]
    if missing:
        pytest.skip(f"Missing official samples for: {', '.join(missing)}")


@pytest.mark.unit
class TestOfficialCartaSampleFiles:
    def test_official_samples_have_no_merge_fields(self):
        _require_samples()
        for slug in OFFICIAL_CARTA_SLUGS:
            path = official_sample_path(slug)
            assert path is not None
            raw = path.read_bytes()
            assert not docx_has_fillable_fields(raw), slug
            # merge_docx would rewrite ZIP/XML; downloads must skip it.
            assert merge_docx(raw, {"FirstName": "Ana"}) != raw

    def test_download_names_use_fs_prefixes(self):
        assert official_template_download_name("carta_compromiso").startswith("FS-CC_")
        assert official_template_download_name("carta_postulacion").startswith("FS-CP_")
        assert official_template_download_name("carta_retorno_programa").startswith(
            "FS-PR_"
        )
        for slug, name in OFFICIAL_DOCX_DOWNLOAD_NAMES.items():
            assert name.endswith(".docx")
            assert official_template_download_name(slug) == name


@pytest.mark.django_db
@pytest.mark.unit
class TestOfficialCartaTemplateDownload:
    def setup_method(self):
        _require_samples()
        seed_mobility_document_types()
        ingest_cgri_samples(skip_universities=True, skip_wagtail=True)
        self.client = APIClient()
        self.student = TestUtils.create_test_user(
            username="cartastudent",
            role="student",
            first_name="Ana",
            last_name="Lopez",
        )
        self.program = TestUtils.create_test_program(name="National Mobility")
        app_status, _ = ApplicationStatus.objects.get_or_create(
            name="draft", defaults={"order": 1}
        )
        self.application = Application.objects.create(
            student=self.student, program=self.program, status=app_status
        )

    def test_ingest_attaches_exact_sample_bytes(self):
        for slug in OFFICIAL_CARTA_SLUGS:
            dt = DocumentType.objects.get(slug=slug)
            assert dt.template_file
            sample = official_sample_path(slug).read_bytes()
            with dt.template_file.open("rb") as handle:
                stored = handle.read()
            assert stored == sample
            assert Path(dt.template_file.name).name == OFFICIAL_DOCX_DOWNLOAD_NAMES[slug]

    def test_download_serves_exact_bytes_even_with_application(self):
        self.client.force_authenticate(user=self.student)
        for slug in OFFICIAL_CARTA_SLUGS:
            dt = DocumentType.objects.get(slug=slug)
            sample = official_sample_path(slug).read_bytes()
            url = reverse("api:documenttype-download-template", kwargs={"pk": dt.pk})
            response = self.client.get(url, {"application": str(self.application.id)})
            assert response.status_code == status.HTTP_200_OK, slug
            assert response.content == sample
            cd = response["Content-Disposition"]
            prefix = OFFICIAL_DOCX_DOWNLOAD_NAMES[slug].removesuffix(".docx")
            assert f'filename="{prefix}_cartastudent.docx"' in cd

    def test_download_falls_back_to_samples_when_template_missing(self):
        self.client.force_authenticate(user=self.student)
        dt = DocumentType.objects.get(slug="carta_compromiso")
        if dt.template_file:
            dt.template_file.delete(save=True)
        sample = official_sample_path("carta_compromiso").read_bytes()
        url = reverse("api:documenttype-download-template", kwargs={"pk": dt.pk})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.content == sample
        assert 'filename="FS-CC_Carta_Compromiso.docx"' in response["Content-Disposition"]
