import pytest
from django.contrib.auth.models import Group
from django.utils import timezone
from django.core.exceptions import ValidationError

from exchange.models import BaseProfile, StudentProfile
from exchange.models import University  # Adjust import if needed

pytestmark = pytest.mark.django_db  # Applies to all tests in this module


class TestBaseProfile:

    def test_create_user_defaults(self):
        user = BaseProfile.objects.create_user(
            username="johndoe",
            password="securepassword123",
            email="john@example.com",
            first_name="John",
            last_name="Doe"
        )
        assert user.username == "johndoe"
        assert user.is_verified is False
        assert user.verification_date is None
        assert user.check_password("securepassword123") is True

    def test_ensure_default_groups(self):
        BaseProfile.ensure_default_groups()
        for name in ["CASE_MANAGER", "SUPERVISOR", "SYSTEM"]:
            assert Group.objects.filter(name=name).exists()

    def test_get_system_user_creates_user_and_group(self):
        user = BaseProfile.get_system_user()
        assert user.username == "system"
        assert not user.is_staff
        assert not user.is_superuser

        group = Group.objects.get(name="SYSTEM")
        assert group in user.groups.all()

    def test_get_system_user_idempotency(self):
        user1 = BaseProfile.get_system_user()
        user2 = BaseProfile.get_system_user()
        assert user1.id == user2.id