import pytest
from exchange.models.profiles import StaffProfile
from exchange.models.places.university import University

pytestmark = pytest.mark.django_db

class TestStaffProfile:
    def test_create_staff_profile_defaults(self):
        university = University.objects.create(name="Test U", label="Test U", description="", active=True, code="TU", country_id=1, type="PUBLIC")
        staff = StaffProfile.objects.create_user(
            username="staff1",
            password="pass",
            university=university,
            role="COORDINATOR",
            position="International Coordinator",
            office_phone="555-1234"
        )
        assert staff.username == "staff1"
        assert staff.university.name == "Test U"
        assert staff.role == "COORDINATOR"
        assert staff.position == "International Coordinator"
        assert staff.office_phone == "555-1234"

    def test_role_methods(self):
        staff = StaffProfile.objects.create_user(username="adminuser", password="pass", role="ADMIN")
        assert staff.is_admin()
        assert not staff.is_coordinator()
        assert not staff.is_manager()
        assert staff.is_staff_role()

        staff.role = "MANAGER"
        assert staff.is_manager()
        assert staff.is_staff_role()
        staff.role = "COORDINATOR"
        assert staff.is_coordinator()
        assert staff.is_staff_role()

    def test_blank_optional_fields(self):
        staff = StaffProfile.objects.create_user(username="blankstaff", password="pass", role="COORDINATOR")
        assert staff.position is None
        assert staff.office_phone is None 