"""GenderOption catalog, structured birth place and approved/total credits."""

from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from accounts.gender_catalog import GENDER_SPECS, seed_gender_options
from accounts.geo_catalog import (
    city_options,
    compose_birthplace,
    country_options,
    resolve_country_code,
    state_options,
)
from accounts.models import GenderOption, Profile

User = get_user_model()
PROFILE_URL = "/api/accounts/profile/"


@pytest.fixture
def student(db):
    user = User.objects.create_user(
        username="geo-student", email="geo@example.com", password="pw-123456!"
    )
    Profile.objects.get_or_create(user=user)
    return user


@pytest.fixture
def client(student):
    api = APIClient()
    api.force_authenticate(student)
    return api


@pytest.mark.django_db
@pytest.mark.unit
class TestGenderOptions:
    def test_migration_seeded_legacy_codes(self):
        codes = set(GenderOption.objects.values_list("code", flat=True))
        assert {code for code, _es, _en in GENDER_SPECS} <= codes

    def test_seed_is_idempotent_and_keeps_stray_profile_codes(self, student):
        Profile.objects.filter(user=student).update(gender="agender")
        seed_gender_options(profile_model=Profile)
        seed_gender_options(profile_model=Profile)
        assert GenderOption.objects.filter(code="agender", is_active=True).count() == 1
        assert GenderOption.objects.filter(code="female").count() == 1

    def test_catalog_endpoint_lists_active_options_only(self, client):
        GenderOption.objects.filter(code="other").update(is_active=False)
        response = client.get("/api/accounts/catalogs/gender-options/")
        assert response.status_code == 200
        rows = {row["code"]: row for row in response.json()}
        assert "other" not in rows
        assert rows["female"]["label_es"] == "Femenino"
        assert rows["female"]["label_en"] == "Female"
        assert "sort_order" in rows["female"]

    def test_profile_rejects_unknown_gender(self, client):
        response = client.patch(PROFILE_URL, {"gender": "not-a-code"}, format="json")
        assert response.status_code == 400
        assert "gender" in response.json()

    def test_profile_accepts_catalog_gender_and_returns_label(self, client):
        response = client.patch(PROFILE_URL, {"gender": "female"}, format="json")
        assert response.status_code == 200, response.content
        assert response.json()["gender"] == "female"
        assert response.json()["gender_label"] in ("Femenino", "Female")

    def test_profile_keeps_deactivated_existing_value(self, client, student):
        Profile.objects.filter(user=student).update(gender="other")
        GenderOption.objects.filter(code="other").update(is_active=False)
        response = client.patch(PROFILE_URL, {"gender": "other"}, format="json")
        assert response.status_code == 200, response.content


@pytest.mark.unit
class TestGeoCatalog:
    def test_country_lookup_by_code_and_names(self):
        assert resolve_country_code("MX") == "MX"
        assert resolve_country_code("mexico") == "MX"
        assert resolve_country_code("Spain") == "ES"
        assert resolve_country_code("Narnia") is None
        mx = next(row for row in country_options() if row["code"] == "MX")
        assert mx["value"] == "México" and mx["has_states"] is True

    def test_mexico_states_and_cities(self):
        states = state_options("México")
        assert len(states) == 32
        cities = {row["value"] for row in city_options("MX", "Coahuila de Zaragoza")}
        assert {"Saltillo", "Torreón", "Ramos Arizpe"} <= cities
        assert len(cities) == 38

    def test_other_countries_have_no_states(self):
        assert state_options("ES") == []
        assert city_options("ES", "Madrid") == []

    def test_compose_birthplace(self):
        assert compose_birthplace("Saltillo", "", "México") == "Saltillo, México"
        assert compose_birthplace("", None, "") == ""


@pytest.mark.django_db
@pytest.mark.unit
class TestGeoEndpointsAndBirthplace:
    def test_geo_endpoints(self, client):
        countries = client.get("/api/accounts/catalogs/geo/countries/")
        assert countries.status_code == 200 and len(countries.json()) > 200
        states = client.get("/api/accounts/catalogs/geo/states/", {"country": "MX"})
        assert len(states.json()) == 32
        cities = client.get(
            "/api/accounts/catalogs/geo/cities/", {"country": "MX", "state": "COA"}
        )
        assert any(row["value"] == "Saltillo" for row in cities.json())

    def test_geo_endpoints_require_auth(self):
        assert APIClient().get("/api/accounts/catalogs/geo/countries/").status_code in (
            401,
            403,
        )

    def test_structured_birthplace_composes_legacy_string(self, client, student):
        response = client.patch(
            PROFILE_URL,
            {
                "birth_country": "México",
                "birth_state": "Coahuila",
                "birth_city": "Saltillo",
            },
            format="json",
        )
        assert response.status_code == 200, response.content
        profile = Profile.objects.get(user=student)
        assert profile.birthplace == "Saltillo, Coahuila, México"
        assert response.json()["birth_city"] == "Saltillo"

    def test_freehand_values_are_accepted(self, client, student):
        response = client.patch(
            PROFILE_URL,
            {
                "birth_country": "Atlantis",
                "birth_state": "",
                "birth_city": "Poseidonia",
            },
            format="json",
        )
        assert response.status_code == 200, response.content
        assert Profile.objects.get(user=student).birthplace == "Poseidonia, Atlantis"

    def test_legacy_birthplace_untouched_without_structured_fields(
        self, client, student
    ):
        Profile.objects.filter(user=student).update(birthplace="Saltillo")
        response = client.patch(PROFILE_URL, {"postal_code": "25000"}, format="json")
        assert response.status_code == 200, response.content
        assert Profile.objects.get(user=student).birthplace == "Saltillo"


@pytest.mark.django_db
@pytest.mark.unit
class TestCredits:
    def test_percentage_auto_calculated(self, client, student):
        response = client.patch(
            PROFILE_URL,
            {"credits_approved": "150", "credits_total": "400"},
            format="json",
        )
        assert response.status_code == 200, response.content
        profile = Profile.objects.get(user=student)
        assert profile.credits_approved == Decimal("150")
        assert profile.credits_total == Decimal("400")
        assert profile.credits_approved_percent == Decimal("37.50")
        assert response.json()["credits_approved_percent"] == pytest.approx(37.5)

    def test_percentage_can_be_entered_directly(self, client, student):
        response = client.patch(
            PROFILE_URL, {"credits_approved_percent": 62.5}, format="json"
        )
        assert response.status_code == 200, response.content
        assert Profile.objects.get(user=student).credits_approved_percent == Decimal(
            "62.50"
        )

    def test_approved_cannot_exceed_total(self, client):
        response = client.patch(
            PROFILE_URL,
            {"credits_approved": "500", "credits_total": "400"},
            format="json",
        )
        assert response.status_code == 400
        assert "credits_approved" in response.json()

    def test_total_must_be_positive(self, client):
        response = client.patch(
            PROFILE_URL, {"credits_approved": "0", "credits_total": "0"}, format="json"
        )
        assert response.status_code == 400
        assert "credits_total" in response.json()

    def test_model_clean_rejects_approved_over_total(self, student):
        from django.core.exceptions import ValidationError

        profile = Profile.objects.get(user=student)
        profile.credits_approved = Decimal("10")
        profile.credits_total = Decimal("5")
        with pytest.raises(ValidationError):
            profile.clean()
