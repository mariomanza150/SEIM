"""Tests for CGRI sample ingest, file_url, and official university list seeding.

Wagtail Document tagging tests require::

    DJANGO_SETTINGS_MODULE=seim.settings.test_cms
"""

from __future__ import annotations

import pytest
from django.conf import settings
from django.core.files.base import ContentFile

from cms.cgri_samples import CGRI_SAMPLE_SPECS, key_tag, samples_dir
from cms.uadec_resources import FILES, file_url
from documents.cgri_ingest import ingest_cgri_samples
from documents.mobility_document_catalog import seed_mobility_document_types
from documents.models import DocumentType
from exchange.cgri_partner_catalog import (
    MOBILITY_SCHEME_HISPANA,
    MOBILITY_SCHEME_INGLESa,
    seed_official_university_lists,
)
from exchange.mobility_schemes import seed_mobility_schemes
from exchange.models import ExchangeAgreement, HostInstitution

# Keys the CMS must serve from SAMPLES (not SEIM-generated PDFs).
_CMS_STATIC_KEYS = {
    "solicitud_participacion_entrante": "AF_Solicitud de Participacion.pdf",
    "lineamientos": "FS-LD Lineamientos y disposiciones.pdf",
    "convocatoria_entrante": "ConvocatoriaMIEntrante.pdf",
    "convocatoria_saliente": "ConvocatoriaMISaliente.pdf",
    "universidades_convenio": "UniversidadesPorConvenio.pdf",
    "universidades_conahec": "UniversidadesPorCONAHEC.pdf",
}


def _require_wagtail():
    if "cms" not in settings.INSTALLED_APPS or not any(
        a.startswith("wagtail") for a in settings.INSTALLED_APPS
    ):
        pytest.skip("Wagtail/CMS not in INSTALLED_APPS for this settings module")


@pytest.mark.unit
class TestCgriSampleSpecs:
    def test_cms_static_keys_map_to_expected_filenames(self):
        by_key = {s["key"]: s for s in CGRI_SAMPLE_SPECS}
        for key, filename in _CMS_STATIC_KEYS.items():
            assert key in by_key, f"missing CGRI sample spec for {key}"
            assert by_key[key]["filename"] == filename
            assert key in FILES, f"missing remote fallback FILES[{key}]"

    def test_af_entrante_is_cms_only_fs_sp_not_document_type_template(self):
        by_key = {s["key"]: s for s in CGRI_SAMPLE_SPECS}
        assert by_key["solicitud_participacion_entrante"]["document_type_slug"] is None
        # Blank FS-SP stays Wagtail-only; outgoing uses system-generated PDF.
        assert by_key["solicitud_participacion_saliente"]["document_type_slug"] is None
        assert by_key["homologacion"]["document_type_slug"] is None
        assert by_key["lineamientos"]["document_type_slug"] == "reglamento_movilidad"


@pytest.mark.django_db
@pytest.mark.unit
class TestFileUrl:
    def test_falls_back_to_remote_when_no_wagtail_doc(self):
        assert file_url("lineamientos") == FILES["lineamientos"]

    def test_prefers_wagtail_document_when_tagged(self):
        _require_wagtail()
        from wagtail.documents.models import Document
        from wagtail.models import Collection

        root = Collection.get_first_root_node()
        collection = Collection(name="CGRI Official Test")
        root.add_child(instance=collection)
        doc = Document(title="Lineamientos test", collection=collection)
        doc.file.save("FS-LD.pdf", ContentFile(b"%PDF-1.4 test"), save=False)
        doc.save()
        doc.tags.add(key_tag("lineamientos"))

        url = file_url("lineamientos")
        assert url != FILES["lineamientos"]
        assert bool(url)


@pytest.mark.django_db
@pytest.mark.unit
class TestOfficialUniversityLists:
    def test_seed_creates_conahec_and_convenio_hosts(self):
        seed_mobility_schemes()
        counts = seed_official_university_lists()
        assert counts["institutions"] > 0
        assert HostInstitution.objects.filter(
            program__name=MOBILITY_SCHEME_INGLESa,
            name="West Virginia University",
        ).exists()
        assert HostInstitution.objects.filter(
            program__name=MOBILITY_SCHEME_HISPANA,
            name="Universidad de Oviedo",
        ).exists()
        assert ExchangeAgreement.objects.filter(
            partner_institution_name="West Virginia University",
            agreement_type=ExchangeAgreement.AgreementType.CONAHEC,
        ).exists()
        assert ExchangeAgreement.objects.filter(
            partner_institution_name="Universidad de León",
            agreement_type=ExchangeAgreement.AgreementType.BILATERAL,
        ).exists()

        again = seed_official_university_lists()
        assert again["agreements"] == 0

    def test_conahec_is_valid_agreement_type_choice(self):
        values = {c.value for c in ExchangeAgreement.AgreementType}
        assert "conahec" in values


class _Stdout:
    def __init__(self):
        self.lines: list[str] = []

    def write(self, msg):
        self.lines.append(str(msg))


@pytest.mark.django_db
@pytest.mark.unit
class TestIngestCgriSamples:
    def test_missing_samples_dir_warns_and_still_seeds_universities(
        self, settings, tmp_path
    ):
        settings.BASE_DIR = tmp_path
        seed_mobility_schemes()
        out = _Stdout()
        ingest_cgri_samples(stdout=out)
        assert any("SAMPLES directory not found" in line for line in out.lines)
        assert HostInstitution.objects.filter(name="Langara College").exists()

    def test_attaches_templates_from_samples(self):
        base = samples_dir()
        if not base.is_dir():
            pytest.skip("SAMPLES/ not present in this environment")

        needed = [s for s in CGRI_SAMPLE_SPECS if s.get("document_type_slug")]
        present = [s for s in needed if (base / s["filename"]).is_file()]
        if not present:
            pytest.skip("No template sample files found")

        seed_mobility_document_types()
        ingest_cgri_samples(skip_universities=True, skip_wagtail=True)

        for spec in present:
            dt = DocumentType.objects.get(slug=spec["document_type_slug"])
            assert dt.template_file, f"expected template on {spec['document_type_slug']}"

        # System-generated solicitud must not receive the blank FS-SP as template.
        solicitud = DocumentType.objects.get(slug="solicitud_participacion")
        assert solicitud.submission_mode == DocumentType.SubmissionMode.SYSTEM_GENERATED
        assert not solicitud.template_file

    def test_wagtail_tags_cms_static_keys(self):
        _require_wagtail()
        base = samples_dir()
        if not base.is_dir():
            pytest.skip("SAMPLES/ not present in this environment")

        missing = [
            key
            for key, filename in _CMS_STATIC_KEYS.items()
            if not (base / filename).is_file()
        ]
        if missing:
            pytest.skip(f"Missing sample files for: {', '.join(missing)}")

        from wagtail.documents.models import Document

        ingest_cgri_samples(skip_universities=True, skip_templates=True)
        for key in _CMS_STATIC_KEYS:
            doc = Document.objects.filter(tags__name=key_tag(key)).first()
            assert doc is not None, f"expected Wagtail Document tagged {key_tag(key)}"
            assert doc.file, f"expected file on Wagtail Document for {key}"
            assert file_url(key) != FILES[key]
