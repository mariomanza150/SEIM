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
        assert "host_school" in errors
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
            result = ApplicationService.submit_application(
                app, mobility_app["student"]
            )
        result.refresh_from_db()
        assert result.status.name == "submitted"
        assert result.submitted_at is not None
