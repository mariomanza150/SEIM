import pytest
from django.contrib.auth.models import Group
from django.utils import timezone
from django.core.exceptions import ValidationError

from exchange.models import StudentProfile
from exchange.models import University  # Adjust import if needed

pytestmark = pytest.mark.django_db  # Applies to all tests in this module


class TestStudentProfile:

    def test_create_student_profile(self):
        university = University.objects.create(name="Test University")
        student = StudentProfile.objects.create_user(
            username="student1",
            password="strongpass",
            email="student@example.com",
            first_name="Ana",
            last_name="Santos",
            student_id="STU123456",
            institution="Faculty of Engineering",
            degree="BSc Computer Science",
            university=university,
        )
        assert student.username == "student1"
        assert student.university.name == "Test University"
        assert student.student_id == "STU123456"

    def test_gender_choices(self):
        student = StudentProfile.objects.create_user(
            username="gendered",
            password="pass",
            gender="M",
        )
        assert student.gender == "M"

    def test_profile_completeness(self):
        student = StudentProfile.objects.create_user(
            username="completeuser",
            password="pass",
            email="user@example.com",
            first_name="Alice",
            last_name="Doe",
            student_id="1234",
            institution="Tech U",
            degree="CS"
        )
        # All required fields filled
        assert student.get_profile_completeness() == 100

        # Remove one field and check again
        student.degree = ""
        student.save()
        assert student.get_profile_completeness() < 100

    def test_profile_completeness_zero(self):
        student = StudentProfile.objects.create_user(username="empty")
        assert student.get_profile_completeness() == 0

    def test_optional_fields_blank(self):
        student = StudentProfile.objects.create_user(
            username="optionaluser",
            password="pass",
        )
        student.phone = ""
        student.city = ""
        student.address = None
        student.save()
        assert student.phone == ""
        assert student.address is None
