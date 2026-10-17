"""Institution default/locked grade scale and Promedio range validation."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from accounts.models import AllowedEmailDomain, Profile, Role
from grades.models import GradeScale

User = get_user_model()
PROFILE_URL = "/api/accounts/profile/"


@pytest.fixture
def scales(db):
    ten = GradeScale.objects.create(
        name="MX 0-10", code="MX_10_T", min_value=0, max_value=10, passing_value=6
    )
    four = GradeScale.objects.create(
        name="US 0-4", code="US_4_T", min_value=0, max_value=4, passing_value=2
    )
    return ten, four


@pytest.fixture
def domain(scales):
    ten, _ = scales
    return AllowedEmailDomain.objects.create(
        name="uni.test.mx", default_grade_scale=ten, lock_grade_scale=True
    )


def _student(email):
    user = User.objects.create_user(
        username=email.split("@")[0], email=email, password="pw-123456!"
    )
    role, _ = Role.objects.get_or_create(name="student")
    user.roles.add(role)
    Profile.objects.get_or_create(user=user)
    client = APIClient()
    client.force_authenticate(user)
    return user, client


@pytest.mark.django_db
@pytest.mark.unit
class TestGradeScaleLock:
    def test_policy_reported_on_profile(self, domain, scales):
        _user, client = _student("ana@uni.test.mx")
        policy = client.get(PROFILE_URL).json()["grade_scale_policy"]
        assert policy == {
            "locked": True,
            "default_grade_scale": str(scales[0].pk),
            "default_grade_scale_name": "MX 0-10",
        }

    def test_locked_student_cannot_change_scale(self, domain, scales):
        _user, client = _student("ana@uni.test.mx")
        response = client.patch(
            PROFILE_URL, {"grade_scale": str(scales[1].pk)}, format="json"
        )
        assert response.status_code == 400
        assert "grade_scale" in response.json()

    def test_locked_student_gets_default_scale_enforced(self, domain, scales):
        user, client = _student("ana@uni.test.mx")
        response = client.patch(PROFILE_URL, {"gpa": 8.7}, format="json")
        assert response.status_code == 200, response.content
        assert Profile.objects.get(user=user).grade_scale_id == scales[0].pk

    def test_clearing_scale_falls_back_to_default(self, domain, scales):
        user, client = _student("ana@uni.test.mx")
        response = client.patch(PROFILE_URL, {"grade_scale": None}, format="json")
        assert response.status_code == 200, response.content
        assert Profile.objects.get(user=user).grade_scale_id == scales[0].pk

    def test_unlocked_domain_only_suggests_default(self, domain, scales):
        domain.lock_grade_scale = False
        domain.save()
        user, client = _student("ana@uni.test.mx")
        policy = client.get(PROFILE_URL).json()["grade_scale_policy"]
        assert policy["locked"] is False
        assert policy["default_grade_scale"] == str(scales[0].pk)
        response = client.patch(
            PROFILE_URL, {"grade_scale": str(scales[1].pk), "gpa": 3.2}, format="json"
        )
        assert response.status_code == 200, response.content
        assert Profile.objects.get(user=user).grade_scale_id == scales[1].pk

    def test_other_domains_are_not_locked(self, domain, scales):
        _user, client = _student("bob@elsewhere.test")
        policy = client.get(PROFILE_URL).json()["grade_scale_policy"]
        assert policy["locked"] is False and policy["default_grade_scale"] is None
        response = client.patch(
            PROFILE_URL, {"grade_scale": str(scales[1].pk)}, format="json"
        )
        assert response.status_code == 200, response.content

    def test_staff_can_change_locked_student_scale(self, domain, scales):
        student, _ = _student("ana@uni.test.mx")
        staff = User.objects.create_user(
            username="staffer", email="staff@x.test", password="pw", is_staff=True
        )
        client = APIClient()
        client.force_authenticate(staff)
        profile = Profile.objects.get(user=student)
        response = client.patch(
            f"/api/accounts/api/profiles/{profile.pk}/",
            {"grade_scale": str(scales[1].pk)},
            format="json",
        )
        assert response.status_code == 200, response.content
        profile.refresh_from_db()
        assert profile.grade_scale_id == scales[1].pk


@pytest.mark.django_db
@pytest.mark.unit
class TestPromedioRange:
    def test_promedio_outside_scale_rejected(self, scales):
        _user, client = _student("carl@elsewhere.test")
        response = client.patch(
            PROFILE_URL,
            {"grade_scale": str(scales[1].pk), "gpa": 9.5},
            format="json",
        )
        assert response.status_code == 400
        assert "gpa" in response.json()

    def test_promedio_inside_scale_accepted(self, scales):
        _user, client = _student("carl@elsewhere.test")
        response = client.patch(
            PROFILE_URL,
            {"grade_scale": str(scales[0].pk), "gpa": 9.5},
            format="json",
        )
        assert response.status_code == 200, response.content


@pytest.mark.django_db
@pytest.mark.unit
class TestDomainCatalogApi:
    def test_lock_requires_default_scale(self, scales):
        admin = User.objects.create_superuser(
            username="root", email="root@x.test", password="pw"
        )
        client = APIClient()
        client.force_authenticate(admin)
        url = "/api/accounts/catalogs/allowed-email-domains/"
        bad = client.post(url, {"name": "a.test.mx", "lock_grade_scale": True})
        assert bad.status_code == 400
        assert "lock_grade_scale" in bad.json()
        ok = client.post(
            url,
            {
                "name": "a.test.mx",
                "lock_grade_scale": True,
                "default_grade_scale": str(scales[0].pk),
            },
        )
        assert ok.status_code == 201, ok.content
        assert ok.json()["default_grade_scale_name"] == "MX 0-10"
