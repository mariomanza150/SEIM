"""UAdeC profile catalog and CGRI country list seeds."""

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.country_catalog import CGRI_COUNTRY_NAMES
from accounts.models import (
    AllowedEmailDomain,
    HomeAcademicProgram,
    SchoolFaculty,
    Unidad,
)
from accounts.profile_catalogs import seed_profile_catalogs
from accounts.uadec_catalog_data import UADEC_CATALOG
from grades.models import GradeScale


@pytest.mark.django_db
@pytest.mark.unit
class TestUadecCatalogSeeds:
    def test_seed_profile_catalogs_creates_unidad_faculties_and_programs(self):
        for name in UADEC_CATALOG:
            Unidad.objects.get_or_create(
                name=name,
                defaults={"code": name.lower(), "is_active": True},
            )

        schools, programs, _banks = seed_profile_catalogs()
        expected_faculties = sum(len(specs) for specs in UADEC_CATALOG.values())
        expected_programs = sum(
            len(spec["programs"]) for specs in UADEC_CATALOG.values() for spec in specs
        )
        assert len(schools) == expected_faculties
        assert len(programs) == expected_programs
        assert SchoolFaculty.objects.filter(unidad__name="Sureste").exists()
        assert HomeAcademicProgram.objects.filter(
            school__name="Facultad de Sistemas",
            school__unidad__name="Sureste",
        ).exists()

    def test_uadec_email_domain_seeded(self):
        AllowedEmailDomain.objects.update_or_create(
            name="uadec.edu.mx",
            defaults={"code": "uadec", "is_active": True},
        )
        assert AllowedEmailDomain.objects.filter(
            name="uadec.edu.mx", is_active=True
        ).exists()


@pytest.mark.django_db
@pytest.mark.unit
class TestCgriCountryCatalog:
    def test_country_api_returns_full_catalog(self, student_user):
        client = APIClient()
        client.force_authenticate(user=student_user)
        response = client.get(reverse("accounts:catalog-countries"))
        assert response.status_code == 200
        names = [row["value"] for row in response.data]
        for legacy in CGRI_COUNTRY_NAMES:
            assert legacy in names
        assert {"Ecuador", "Bolivia"} <= set(names)
        assert len(names) > 200
        spain = next(row for row in response.data if row["value"] == "España")
        assert "Spain" in spain.get("aliases", [])
        usa = next(row for row in response.data if row["value"] == "EUA")
        assert "United States" in usa["aliases"]

    def test_every_seed_country_resolves_to_an_option(self):
        import json
        from pathlib import Path

        from accounts.country_catalog import country_options, resolve_country_option

        values = {row["value"] for row in country_options()}
        data_dir = Path(__file__).resolve().parents[3] / "exchange" / "data"
        seeds = set()
        for name in (
            "universidades_por_conahec.json",
            "universidades_por_convenio.json",
        ):
            rows = json.loads((data_dir / name).read_text(encoding="utf-8"))
            seeds |= {row["country"] for row in rows if row.get("country")}
        assert seeds
        for country in seeds:
            assert resolve_country_option(country) in values, country

    def test_every_spanish_speaking_country_present(self):
        from accounts.country_catalog import resolve_country_option
        from exchange.cgri_partner_catalog import SPANISH_SPEAKING_COUNTRIES

        for country in SPANISH_SPEAKING_COUNTRIES:
            assert resolve_country_option(country), country


@pytest.mark.django_db
@pytest.mark.unit
class TestMxGradeScales:
    def test_mx_scales_exist_after_seed(self):
        from django.core.management import call_command

        call_command("seed_grade_scales", verbosity=0)
        mx100 = GradeScale.objects.get(code="MX_0_100")
        mx10 = GradeScale.objects.get(code="MX_0_10")
        assert mx100.passing_value == 70.0
        assert mx10.passing_value == 7.0
        band_90 = mx100.grade_values.filter(min_percentage=90.0).first()
        assert band_90 is not None
        assert band_90.gpa_equivalent >= 3.6
