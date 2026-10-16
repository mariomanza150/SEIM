"""Seed consistency for student profile School / Program / Bank catalogs."""

import pytest

from accounts.models import BankInstitution, HomeAcademicProgram, SchoolFaculty
from accounts.profile_catalogs import BANK_SPECS, SCHOOL_SPECS, seed_profile_catalogs


@pytest.mark.django_db
@pytest.mark.unit
class TestProfileCatalogSeeds:
    def test_seed_creates_schools_programs_and_banks(self):
        schools, programs, banks = seed_profile_catalogs()

        expected_school_names = {spec["name"] for spec in SCHOOL_SPECS}
        expected_program_count = sum(len(spec["programs"]) for spec in SCHOOL_SPECS)
        expected_bank_names = {name for name, _code in BANK_SPECS}

        assert {s.name for s in schools} == expected_school_names
        assert len(programs) == expected_program_count
        assert {b.name for b in banks} == expected_bank_names

        ingenieria = SchoolFaculty.objects.get(name="Ingeniería")
        assert HomeAcademicProgram.objects.filter(school=ingenieria).count() == 4
        assert BankInstitution.objects.filter(name="BBVA", code="bbva").exists()

    def test_seed_is_idempotent(self):
        seed_profile_catalogs()
        school_count = SchoolFaculty.objects.count()
        program_count = HomeAcademicProgram.objects.count()
        bank_count = BankInstitution.objects.count()

        # Use a school owned by the current UADEC seed (legacy flat rows are not re-seeded).
        seeded_spec = SCHOOL_SPECS[0]
        ingenieria = SchoolFaculty.objects.get(
            name=seeded_spec["name"], code=seeded_spec["code"]
        )
        ingenieria.code = "changed"
        ingenieria.is_active = False
        ingenieria.save(update_fields=["code", "is_active"])

        seed_profile_catalogs()
        ingenieria.refresh_from_db()
        assert ingenieria.code == seeded_spec["code"]
        assert ingenieria.is_active is True
        assert SchoolFaculty.objects.count() == school_count
        assert HomeAcademicProgram.objects.count() == program_count
        assert BankInstitution.objects.count() == bank_count
        # Legacy flat schools from historical migrations have no unidad and are not seeded.
        assert SchoolFaculty.objects.filter(unidad__isnull=False).count() == len(
            SCHOOL_SPECS
        )
        assert bank_count == len(BANK_SPECS)
