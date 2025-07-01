import pytest
from exchange.models.profiles import ContactProfile
from exchange.models.places.university import University

pytestmark = pytest.mark.django_db

class TestContactProfile:
    def test_create_contact_profile_defaults(self):
        university = University.objects.create(name="Test U", label="Test U", description="", active=True, code="TU", country_id=1, type="PUBLIC")
        contact = ContactProfile.objects.create(
            university=university,
            position="Advisor",
            phone="123456789",
            office_phone="987654321",
            address="123 Main St",
            city="Metropolis",
            country="Freedonia"
        )
        assert contact.position == "Advisor"
        assert contact.phone == "123456789"
        assert contact.office_phone == "987654321"
        assert contact.address == "123 Main St"
        assert contact.city == "Metropolis"
        assert contact.country == "Freedonia"
        assert contact.university.name == "Test U"

    def test_blank_optional_fields(self):
        contact = ContactProfile.objects.create()
        assert contact.position is None
        assert contact.phone is None
        assert contact.office_phone is None
        assert contact.address is None
        assert contact.city is None
        assert contact.country is None 