"""
Test utilities for SEIM.

This module provides helper functions, utilities, and common testing patterns
that can be used across all test modules.
"""

import json
import os
import tempfile
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone
from faker import Faker
from rest_framework.test import APIClient

from accounts.models import AcademicLevel, HomeAcademicProgram, Role, SchoolFaculty, Unidad
from documents.models import Document
from exchange.models import Application, ApplicationStatus, Program
from grades.models import GradeScale

User = get_user_model()
fake = Faker()


def complete_apply_profile(user: User) -> None:
    """Fill personal, academic, and eligibility fields required to start an application."""
    updates = {}
    if not (user.first_name or "").strip():
        updates["first_name"] = "Test"
    if not (user.middle_name or "").strip():
        updates["middle_name"] = "Q"
    if not (user.last_name or "").strip():
        updates["last_name"] = "User"
    if not (user.mothers_last_name or "").strip():
        updates["mothers_last_name"] = "Garcia"
    if updates:
        for field, value in updates.items():
            setattr(user, field, value)
        user.save(update_fields=list(updates))

    school, _ = SchoolFaculty.objects.get_or_create(name="Engineering")
    home_program, _ = HomeAcademicProgram.objects.get_or_create(
        name="Computer Science",
        defaults={"school": school},
    )
    if home_program.school_id != school.id:
        home_program.school = school
        home_program.save(update_fields=["school"])
    level, _ = AcademicLevel.objects.get_or_create(name="Undergraduate")
    unidad, _ = Unidad.objects.get_or_create(name="Ciudad Universitaria")
    scale, _ = GradeScale.objects.get_or_create(
        code="US_GPA_4",
        defaults={
            "name": "US GPA 4.0 Scale",
            "min_value": 0.0,
            "max_value": 4.0,
            "passing_value": 2.0,
        },
    )

    profile = user.profile
    digits = "".join(ch for ch in str(user.pk) if ch.isdigit())
    if len(digits) < 7:
        digits = f"{abs(hash(str(user.pk))) % 10_000_000:07d}"
    profile.matricula = digits[:12]
    profile.academic_level = level
    profile.school = school
    profile.unidad = unidad
    profile.home_academic_program = home_program
    profile.gender = profile.gender or "prefer_not_to_say"
    profile.gpa = 3.5 if profile.gpa is None else profile.gpa
    profile.language = (profile.language or "").strip() or "English"
    profile.language_level = (profile.language_level or "").strip() or "B2"
    profile.date_of_birth = profile.date_of_birth or date(2000, 1, 1)
    profile.birthplace = (profile.birthplace or "").strip() or "Monterrey"
    profile.postal_code = (profile.postal_code or "").strip() or "64000"
    profile.passport_number = (profile.passport_number or "").strip() or "P1234567"
    profile.mobile_phone = (profile.mobile_phone or "").strip() or "8112345678"
    profile.secondary_email = (profile.secondary_email or "").strip() or (
        f"alt-{user.username}@example.net"
    )
    profile.rfc = (profile.rfc or "").strip() or "XAXX010101000"
    profile.grade_scale = profile.grade_scale or scale
    if profile.credits_approved_percent is None:
        profile.credits_approved_percent = Decimal("70.00")
    profile.ingress_date = profile.ingress_date or date(2022, 8, 1)
    profile.save()


class TestUtils:
    """Utility class for common testing operations."""

    @staticmethod
    def create_test_user(
        username: str = None,
        email: str = None,
        role: str = "student",
        password: str = "testpass123",
        is_email_verified: bool = True,
        **kwargs,
    ) -> User:
        """Create a test user with specified role."""
        if username is None:
            username = fake.user_name()
        if email is None:
            email = fake.email()

        kwargs.setdefault("first_name", "Test")
        kwargs.setdefault("middle_name", "Q")
        kwargs.setdefault("last_name", "User")
        kwargs.setdefault("mothers_last_name", "Garcia")
        user = User.objects.create_user(
            username=username, email=email, password=password, **kwargs
        )
        user.is_email_verified = is_email_verified
        if not is_email_verified:
            from django.utils.crypto import get_random_string

            user.email_verification_token = get_random_string(32)
        user.save()
        # Assign role
        role_obj, _ = Role.objects.get_or_create(name=role)
        user.roles.add(role_obj)
        complete_apply_profile(user)
        return user

    @staticmethod
    def create_test_program(**kwargs) -> Program:
        """Create a test program."""
        defaults = {
            "name": fake.sentence(nb_words=3),
            "description": fake.paragraph(),
            "start_date": fake.future_date(end_date="+1y"),
            "end_date": fake.future_date(end_date="+2y"),
            "is_active": True,
            "min_gpa": 2.0,  # Low minimum for testing
            "required_language": "English",  # Default language
            "recurring": fake.boolean(),
        }
        defaults.update(kwargs)

        return Program.objects.create(**defaults)

    @staticmethod
    def create_test_application(
        student: User = None,
        program: Program = None,
        status_name: str = "draft",
        **kwargs,
    ) -> Application:
        """Create a test application."""
        if student is None:
            student = TestUtils.create_test_user(role="student")
        if program is None:
            program = TestUtils.create_test_program()

        status_obj, _ = ApplicationStatus.objects.get_or_create(name=status_name)

        defaults = {
            "student": student,
            "program": program,
            "status": status_obj,
            "submitted_at": None if status_name == "draft" else timezone.now(),
        }
        defaults.update(kwargs)

        application = Application.objects.create(**defaults)
        from tests.unit.exchange.host_destination_helpers import (
            apply_host_destination,
            attach_host_destination,
        )

        if application.host_institution_id is None:
            tree = attach_host_destination(program)
            apply_host_destination(application, tree)
        return application

    @staticmethod
    def create_test_document(
        application: Application = None, uploaded_by: User = None, **kwargs
    ) -> Document:
        """Create a test document."""
        if application is None:
            application = TestUtils.create_test_application()
        if uploaded_by is None:
            uploaded_by = application.student

        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        temp_file.write(b"Test PDF content")
        temp_file.close()

        defaults = {
            "application": application,
            "uploaded_by": uploaded_by,
            "file_name": fake.file_name(extension="pdf"),
            "file_type": "application/pdf",
            "file_size": fake.random_int(min=1000, max=10000000),
            "is_required": fake.boolean(),
            "is_validated": False,
        }
        defaults.update(kwargs)

        # Create the document
        document = Document.objects.create(**defaults)

        # Attach the file
        document.file = SimpleUploadedFile(
            name=document.file_name,
            content=open(temp_file.name, "rb").read(),
            content_type=document.file_type,
        )
        document.save()

        # Clean up temporary file
        os.unlink(temp_file.name)

        return document

    @staticmethod
    def create_test_file(
        filename: str = None,
        content: bytes = b"Test content",
        content_type: str = "text/plain",
    ) -> SimpleUploadedFile:
        """Create a test file for uploads."""
        if filename is None:
            filename = fake.file_name()

        return SimpleUploadedFile(
            name=filename, content=content, content_type=content_type
        )

    @staticmethod
    def get_auth_headers(user: User) -> dict[str, str]:
        """Get authentication headers for API requests."""
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(user)
        return {
            "HTTP_AUTHORIZATION": f"Bearer {refresh.access_token}",
            "content_type": "application/json",
        }


class APITestCase(TestCase):
    """Base test case for API tests with common utilities."""

    def setUp(self):
        """Set up test case."""
        self.client = APIClient()
        self.fake = Faker()
        self._create_required_status_objects()
        from accounts.models import AllowedEmailDomain

        AllowedEmailDomain.objects.get_or_create(
            name="example.com",
            defaults={"code": "example", "is_active": True},
        )

    def _create_required_status_objects(self):
        """Create required ApplicationStatus objects for tests."""
        required_statuses = [
            ("draft", 1),
            ("submitted", 2),
            ("under_review", 3),
            ("approved", 4),
            ("rejected", 5),
            ("withdrawn", 6),
        ]

        for status_name, order in required_statuses:
            ApplicationStatus.objects.get_or_create(
                name=status_name, defaults={"order": order}
            )

    def create_user(self, role: str = "student", **kwargs) -> User:
        """Create a test user."""
        return TestUtils.create_test_user(role=role, **kwargs)

    def create_program(self, **kwargs) -> Program:
        """Create a test program."""
        return TestUtils.create_test_program(**kwargs)

    def create_application(self, **kwargs) -> Application:
        """Create a test application."""
        return TestUtils.create_test_application(**kwargs)

    def create_document(self, **kwargs) -> Document:
        """Create a test document."""
        return TestUtils.create_test_document(**kwargs)

    def authenticate_user(self, user: User):
        """Authenticate a user for API requests."""
        self.client.force_authenticate(user=user)

    def assert_response_success(self, response, status_code: int = 200):
        """Assert that the response is successful."""
        self.assertEqual(response.status_code, status_code)
        if hasattr(response, "data"):
            self.assertIsNotNone(response.data)

    def assert_response_error(self, response, status_code: int = 400):
        """Assert that the response is an error."""
        self.assertEqual(response.status_code, status_code)

    def assert_response_unauthorized(self, response):
        """Assert that the response indicates unauthorized access."""
        self.assertIn(response.status_code, [401, 403])

    def assert_response_not_found(self, response):
        """Assert that the response indicates not found."""
        self.assertEqual(response.status_code, 404)

    def assert_model_exists(self, model_class, **filters):
        """Assert that a model instance exists."""
        self.assertTrue(model_class.objects.filter(**filters).exists())

    def assert_model_not_exists(self, model_class, **filters):
        """Assert that a model instance does not exist."""
        self.assertFalse(model_class.objects.filter(**filters).exists())


class WorkflowTestCase(APITestCase):
    """Test case for testing business workflows."""

    def setUp(self):
        """Set up workflow test case."""
        super().setUp()

        # Create common test data
        self.student = self.create_user(role="student")
        self.coordinator = self.create_user(role="coordinator")
        self.admin = self.create_user(role="admin")
        self.program = self.create_program()

    def create_application_workflow(self, status_name: str = "draft") -> Application:
        """Create an application with specific status."""
        return self.create_application(
            student=self.student, program=self.program, status_name=status_name
        )

    def submit_application(self, application: Application) -> Application:
        """Submit an application."""
        application.status = ApplicationStatus.objects.get(name="submitted")
        application.submitted_at = timezone.now()
        application.save()
        return application

    def approve_application(self, application: Application) -> Application:
        """Approve an application."""
        application.status = ApplicationStatus.objects.get(name="approved")
        application.save()
        return application

    def reject_application(self, application: Application) -> Application:
        """Reject an application."""
        application.status = ApplicationStatus.objects.get(name="rejected")
        application.save()
        return application


class PerformanceTestCase(APITestCase):
    """Test case for performance testing."""

    def setUp(self):
        """Set up performance test case."""
        super().setUp()
        self.start_time = datetime.now()

    def assert_response_time(self, response, max_time: float = 1.0):
        """Assert that the response time is within acceptable limits."""
        end_time = datetime.now()
        response_time = (end_time - self.start_time).total_seconds()
        self.assertLess(
            response_time,
            max_time,
            f"Response time {response_time}s exceeded limit {max_time}s",
        )

    def create_bulk_data(self, count: int = 100):
        """Create bulk test data for performance testing."""
        programs = []
        for i in range(count):
            program = self.create_program(
                name=f"Test Program {i}", description=f"Description for program {i}"
            )
            programs.append(program)
        return programs


# Common test data generators
def generate_test_data():
    """Generate comprehensive test data."""
    data = {
        "users": {
            "student": TestUtils.create_test_user(role="student"),
            "coordinator": TestUtils.create_test_user(role="coordinator"),
            "admin": TestUtils.create_test_user(role="admin"),
        },
        "programs": [
            TestUtils.create_test_program(name=f"Program {i}") for i in range(5)
        ],
        "applications": [],
    }

    # Create applications for each program
    for program in data["programs"]:
        for status in ["draft", "submitted", "under_review", "approved", "rejected"]:
            app = TestUtils.create_test_application(
                student=data["users"]["student"], program=program, status_name=status
            )
            data["applications"].append(app)

    return data


# Assertion helpers
def assert_valid_json_response(response):
    """Assert that the response contains valid JSON."""
    try:
        json.loads(response.content.decode("utf-8"))
    except json.JSONDecodeError as e:
        raise AssertionError("Response is not valid JSON") from e


def assert_contains_required_fields(
    response_data: dict[str, Any], required_fields: list[str]
):
    """Assert that the response contains all required fields."""
    for field in required_fields:
        assert field in response_data, f"Missing required field: {field}"


def assert_valid_date_format(date_string: str, format: str = "%Y-%m-%d"):
    """Assert that a date string is in the correct format."""
    try:
        datetime.strptime(date_string, format)
    except ValueError as e:
        raise AssertionError(
            f"Date string '{date_string}' is not in format '{format}'"
        ) from e


# Mock helpers
def mock_external_service(service_name: str, return_value: Any = None):
    """Create a mock for external services."""
    import unittest.mock as mock

    def decorator(func):
        @mock.patch(service_name, return_value=return_value)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator
