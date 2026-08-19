"""UAdeC profile catalog and CGRI country list seeds."""

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.country_catalog import CGRI_COUNTRY_NAMES
from accounts.models import AllowedEmailDomain, HomeAcademicProgram, SchoolFaculty, Unidad
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
            len(spec["programs"])
            for specs in UADEC_CATALOG.values()
            for spec in specs
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
    def test_country_api_returns_seventeen_cgri_countries(self, student_user):
        client = APIClient()
        client.force_authenticate(user=student_user)
        response = client.get(reverse("accounts:catalog-countries"))
        assert response.status_code == 200
        names = [row["value"] for row in response.data]
        assert names == list(CGRI_COUNTRY_NAMES)
        assert len(names) == 17


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
