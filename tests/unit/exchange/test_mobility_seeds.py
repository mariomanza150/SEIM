"""Seed consistency for mobility schemes + MX document catalog."""

import pytest

from documents.mobility_document_catalog import (
    MOBILITY_DOCUMENT_TYPES,
    assign_scheme_document_requirements,
    seed_mobility_document_types,
)
from documents.models import DocumentType
from exchange.mobility_schemes import (
    MOBILITY_SCHEME_HISPANA,
    MOBILITY_SCHEME_INGLESa,
    MOBILITY_SCHEME_SPECS,
    seed_mobility_schemes,
)
from exchange.models import Program, ProgramDocumentRequirement


@pytest.mark.django_db
@pytest.mark.unit
class TestMobilitySeeds:
    def test_seed_schemes_creates_two_and_updates_eligibility(self):
        programs = seed_mobility_schemes()
        assert len(programs) == 2
        names = {p.name for p in programs}
        assert names == {spec["name"] for spec in MOBILITY_SCHEME_SPECS}

        hispana = Program.objects.get(name=MOBILITY_SCHEME_HISPANA)
        hispana.min_semester = 1
        hispana.min_gpa = 1.0
        hispana.min_toefl_score = 100
        hispana.save(update_fields=["min_semester", "min_gpa", "min_toefl_score"])

        seed_mobility_schemes()
        hispana.refresh_from_db()
        assert hispana.min_semester == 4
        assert hispana.min_gpa == 3.6
        assert hispana.min_toefl_score == 450

        inglesa = Program.objects.get(name=MOBILITY_SCHEME_INGLESa)
        assert inglesa.min_gpa == 3.4
        assert inglesa.min_toefl_score == 550
        assert not Program.objects.filter(name="Movilidad Nacional", is_active=True).exists()

    def test_mx_document_catalog_and_scheme_requirements(self):
        seed_mobility_schemes()
        types = seed_mobility_document_types()
        assert len(types) == len(MOBILITY_DOCUMENT_TYPES)
        assert DocumentType.objects.filter(slug="solicitud_participacion").exists()
        assert DocumentType.objects.filter(slug="carta_homologacion").exists()
        inscription = DocumentType.objects.get(slug="inscripcion_uadec")
        assert inscription.name == "Inscripción UAdeC"

        assign_scheme_document_requirements()
        assign_scheme_document_requirements()
        for name in (MOBILITY_SCHEME_HISPANA, MOBILITY_SCHEME_INGLESa):
            program = Program.objects.get(name=name)
            assert ProgramDocumentRequirement.objects.filter(program=program).exists()
            assert ProgramDocumentRequirement.objects.filter(
                program=program,
                document_type__slug="solicitud_participacion",
                is_required=True,
            ).exists()

    def test_inscription_label_uses_institution_short_name(self, settings):
        settings.INSTITUTION_SHORT_NAME = "ExampleU"
        seed_mobility_document_types()
        inscription = DocumentType.objects.get(slug="inscripcion_uadec")
        assert inscription.name == "Inscripción ExampleU"
        assert "ExampleU" in inscription.description
