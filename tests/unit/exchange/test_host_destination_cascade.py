"""Unit tests for host destination cascade validation and optional subjects skip."""

from datetime import date, timedelta
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model

from accounts.models import Profile, Role
from exchange.models import (
    Application,
    ApplicationStatus,
    HostInstitution,
    HostSchool,
    Program,
    validate_application_host_destination,
)
from exchange.services import ApplicationService
from tests.unit.exchange.host_destination_helpers import (
    apply_host_destination,
    attach_host_destination,
)

User = get_user_model()


@pytest.fixture
def mobility_app(db):
    student = User.objects.create_user(
        username="cascade_student",
        email="cascade@example.com",
        password="testpass123",
    )
    role, _ = Role.objects.get_or_create(name="student")
    student.roles.add(role)
    Profile.objects.update_or_create(
        user=student,
        defaults={"gpa": 3.5, "language": "English", "language_level": "B2"},
    )
    today = date.today()
    program = Program.objects.create(
        name="Cascade Scheme",
        description="Host cascade tests",
        start_date=today + timedelta(days=60),
        end_date=today + timedelta(days=200),
        application_open_date=today - timedelta(days=5),
        application_deadline=today + timedelta(days=30),
        is_active=True,
    )
    host_tree = attach_host_destination(program, with_subject=True)
    draft, _ = ApplicationStatus.objects.get_or_create(
        name="draft", defaults={"order": 1}
    )
    ApplicationStatus.objects.get_or_create(name="submitted", defaults={"order": 2})
    application = Application.objects.create(
        student=student, program=program, status=draft
    )
    return {
        "student": student,
        "program": program,
        "application": application,
        "host_tree": host_tree,
        "draft": draft,
    }


@pytest.mark.django_db
@pytest.mark.unit
class TestHostDestinationCascade:
    def test_require_complete_reports_missing_fields(self, mobility_app):
        app = mobility_app["application"]
        errors = validate_application_host_destination(app, require_complete=True)
        assert "host_institution" in errors
        assert "host_school" not in errors

        tree = mobility_app["host_tree"]
        app.host_institution = tree["institution"]
        errors = validate_application_host_destination(app, require_complete=True)
        assert "host_school" in errors

        app.host_school = tree["school"]
        errors = validate_application_host_destination(app, require_complete=True)
        assert "host_academic_program" in errors

    def test_inconsistent_school_rejected(self, mobility_app):
        app = mobility_app["application"]
        tree = mobility_app["host_tree"]
        other_inst = HostInstitution.objects.create(
            program=mobility_app["program"],
            name="Other U",
            country="ES",
            is_active=True,
        )
        other_school = HostSchool.objects.create(
            institution=other_inst, name="Other Faculty", is_active=True
        )
        app.host_institution = tree["institution"]
        app.host_school = other_school
        app.host_academic_program = tree["academic"]
        errors = validate_application_host_destination(app, require_complete=True)
        assert "host_school" in errors
        assert "belong" in str(errors["host_school"]).lower()

    def test_institution_must_belong_to_scheme(self, mobility_app):
        today = date.today()
        other_program = Program.objects.create(
            name="Other Scheme",
            description="x",
            start_date=today,
            end_date=today + timedelta(days=30),
            is_active=True,
        )
        foreign = HostInstitution.objects.create(
            program=other_program, name="Foreign U", country="US", is_active=True
        )
        app = mobility_app["application"]
        tree = mobility_app["host_tree"]
        app.host_institution = foreign
        app.host_school = tree["school"]
        app.host_academic_program = tree["academic"]
        errors = validate_application_host_destination(app, require_complete=False)
        assert "host_institution" in errors

    def test_submit_succeeds_without_subject_selections(self, mobility_app):
        """Subjects are optional — empty selections must not block submit."""
        app = mobility_app["application"]
        apply_host_destination(app, mobility_app["host_tree"])
        assert app.subject_selections.count() == 0
        with (
            patch("exchange.services.NotificationService.send_notification"),
            patch("exchange.services.NotificationService.broadcast_application_sync"),
        ):
            result = ApplicationService.submit_application(app, mobility_app["student"])
        result.refresh_from_db()
        assert result.status.name == "submitted"
        assert result.submitted_at is not None

    def test_require_complete_skipped_when_scheme_has_no_hosts(self, mobility_app):
        app = mobility_app["application"]
        mobility_app["program"].host_institutions.all().delete()
        errors = validate_application_host_destination(app, require_complete=True)
        assert errors == {}

    def test_institution_without_catalog_requires_school_and_program(self, mobility_app):
        app = mobility_app["application"]
        bare = HostInstitution.objects.create(
            program=mobility_app["program"],
            name="Bare University",
            country="MX",
            is_active=True,
        )
        mobility_app["program"].host_institutions.exclude(pk=bare.pk).delete()
        app.host_institution = bare
        app.host_school = None
        app.host_academic_program = None
        errors = validate_application_host_destination(app, require_complete=True)
        assert "host_school" in errors
        assert "host_academic_program" in errors

    def test_resolve_host_destination_names_creates_catalog_rows(self, mobility_app):
        from exchange.models import HostAcademicProgram, resolve_host_destination_names

        bare = HostInstitution.objects.create(
            program=mobility_app["program"],
            name="Typed Host U",
            country="MX",
            is_active=True,
        )
        school, academic, errors = resolve_host_destination_names(
            institution=bare,
            school_name="Faculty of Arts",
            academic_program_name="Fine Arts",
        )
        assert errors == {}
        assert school is not None
        assert school.name == "Faculty of Arts"
        assert school.institution_id == bare.id
        assert academic is not None
        assert academic.name == "Fine Arts"
        assert academic.school_id == school.id
        assert HostAcademicProgram.objects.filter(pk=academic.pk).exists()

        school2, academic2, errors2 = resolve_host_destination_names(
            institution=bare,
            school_name="Faculty of Arts",
            academic_program_name="Fine Arts",
        )
        assert errors2 == {}
        assert school2.pk == school.pk
        assert academic2.pk == academic.pk

    def test_serializer_accepts_free_text_host_names(self, mobility_app):
        from rest_framework.test import APIRequestFactory

        from exchange.serializers import ApplicationSerializer

        bare = HostInstitution.objects.create(
            program=mobility_app["program"],
            name="API Bare U",
            country="MX",
            is_active=True,
        )
        mobility_app["program"].host_institutions.exclude(pk=bare.pk).delete()
        factory = APIRequestFactory()
        request = factory.post("/api/applications/")
        request.user = mobility_app["student"]
        serializer = ApplicationSerializer(
            data={
                "program": mobility_app["program"].id,
                "host_institution": bare.id,
                "host_school_name": "Law Faculty",
                "host_academic_program_name": "LLB",
            },
            context={"request": request},
        )
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data["host_school"].name == "Law Faculty"
        assert serializer.validated_data["host_academic_program"].name == "LLB"
        assert "host_school_name" not in serializer.validated_data
        assert "host_academic_program_name" not in serializer.validated_data

    def test_serializer_rejects_free_text_without_institution(self, mobility_app):
        from rest_framework.test import APIRequestFactory

        from exchange.serializers import ApplicationSerializer

        factory = APIRequestFactory()
        request = factory.post("/api/applications/")
        request.user = mobility_app["student"]
        serializer = ApplicationSerializer(
            data={
                "program": mobility_app["program"].id,
                "host_school_name": "Orphan Faculty",
            },
            context={"request": request},
        )
        assert not serializer.is_valid()
        assert "host_school_name" in serializer.errors

    def test_submit_succeeds_when_scheme_has_no_host_tree(self, mobility_app):
        app = mobility_app["application"]
        mobility_app["program"].host_institutions.all().delete()
        app.host_institution = None
        app.host_school = None
        app.host_academic_program = None
        app.save()
        with (
            patch("exchange.services.NotificationService.send_notification"),
            patch("exchange.services.NotificationService.broadcast_application_sync"),
        ):
            result = ApplicationService.submit_application(app, mobility_app["student"])
        result.refresh_from_db()
        assert result.status.name == "submitted"

    def test_submit_still_requires_hosts_when_tree_exists(self, mobility_app):
        app = mobility_app["application"]
        with pytest.raises(ValueError, match="Host destination incomplete"):
            ApplicationService.submit_application(app, mobility_app["student"])
