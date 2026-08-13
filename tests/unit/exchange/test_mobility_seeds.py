"""Seed consistency for mobility schemes + MX document catalog."""

import pytest

from documents.mobility_document_catalog import (
    MOBILITY_DOCUMENT_TYPES,
    assign_scheme_document_requirements,
    seed_mobility_document_types,
)
from documents.models import DocumentType
from exchange.mobility_schemes import MOBILITY_SCHEME_SPECS, seed_mobility_schemes
from exchange.models import Program, ProgramDocumentRequirement


@pytest.mark.django_db
@pytest.mark.unit
class TestMobilitySeeds:
    def test_seed_schemes_creates_three_and_updates_eligibility(self):
        programs = seed_mobility_schemes()
        assert len(programs) == 3
        names = {p.name for p in programs}
        assert names == {spec["name"] for spec in MOBILITY_SCHEME_SPECS}

        nacional = Program.objects.get(name="Movilidad Nacional")
        nacional.min_semester = 1
        nacional.min_gpa = 1.0
        nacional.save(update_fields=["min_semester", "min_gpa"])

        seed_mobility_schemes()
        nacional.refresh_from_db()
        assert nacional.min_semester == 3
        assert nacional.min_gpa == 3.0

    def test_mx_document_catalog_and_scheme_requirements(self):
        seed_mobility_schemes()
        types = seed_mobility_document_types()
        assert len(types) == len(MOBILITY_DOCUMENT_TYPES)
        assert DocumentType.objects.filter(slug="solicitud_participacion").exists()
        assert DocumentType.objects.filter(slug="carta_homologacion").exists()

        # First call may create rows; re-run is idempotent (created count may be 0).
        assign_scheme_document_requirements()
        assign_scheme_document_requirements()
        for name in (
            "Movilidad Nacional",
            "Movilidad Internacional Habla Hispana",
            "Movilidad Internacional",
        ):
            program = Program.objects.get(name=name)
            assert ProgramDocumentRequirement.objects.filter(program=program).exists()
            assert ProgramDocumentRequirement.objects.filter(
                program=program,
                document_type__slug="solicitud_participacion",
                is_required=True,
            ).exists()
