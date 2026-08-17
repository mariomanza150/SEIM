"""API and model tests for host-subject visibility, custom XOR, and grade workflow."""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Profile, Role
from documents.pdf_generation import render_carta_homologacion_pdf
from exchange.models import (
    Application,
    ApplicationStatus,
    ApplicationSubjectSelection,
    HostSubject,
    Program,
    visible_host_subjects_queryset,
)
from grades.models import GradeScale, GradeValue
from tests.unit.exchange.host_destination_helpers import attach_host_destination

User = get_user_model()


def _auth_client(user):
    client = APIClient()
    token = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return client


@pytest.fixture
def student_client(db):
    student = User.objects.create_user(
        username="grade_student",
        email="grade_student@university.edu",
        password="testpass123",
        first_name="Grade",
        last_name="Student",
    )
    role, _ = Role.objects.get_or_create(name="student")
    student.roles.add(role)
    return student, _auth_client(student)


@pytest.fixture
def host_tree(db):
    today = date.today()
    program = Program.objects.create(
        name="Movilidad Grade Subjects",
        description="Grade workflow test scheme",
        start_date=today + timedelta(days=60),
        end_date=today + timedelta(days=200),
        application_open_date=today - timedelta(days=10),
        application_deadline=today + timedelta(days=30),
        is_active=True,
    )
    tree = attach_host_destination(program, with_subject=True)
    tree["program"] = program
    return tree


@pytest.fixture
def admin_client(db):
    admin = User.objects.create_user(
        username="subj_admin",
        email="subj_admin@university.edu",
        password="testpass123",
    )
    role, _ = Role.objects.get_or_create(name="admin")
    admin.roles.add(role)
    return admin, _auth_client(admin)


@pytest.fixture
def coordinator_client(db):
    coord = User.objects.create_user(
        username="subj_coord",
        email="subj_coord@university.edu",
        password="testpass123",
    )
    role, _ = Role.objects.get_or_create(name="coordinator")
    coord.roles.add(role)
    return coord, _auth_client(coord)


def _draft_application(student, host_tree):
    draft, _ = ApplicationStatus.objects.get_or_create(
        name="draft", defaults={"order": 0}
    )
    return Application.objects.create(
        student=student,
        program=host_tree["program"],
        status=draft,
        host_institution=host_tree["institution"],
        host_school=host_tree["school"],
        host_academic_program=host_tree["academic"],
    )


def _make_scales():
    host_scale = GradeScale.objects.create(
        name="Host ECTS",
        code="HOST_ECTS_SUBJ",
        min_value=0,
        max_value=4,
        passing_value=1,
    )
    home_scale = GradeScale.objects.create(
        name="Home GPA",
        code="HOME_GPA_SUBJ",
        min_value=0,
        max_value=4,
        passing_value=2,
    )
    host_a = GradeValue.objects.create(
        grade_scale=host_scale,
        label="HostA",
        numeric_value=4.0,
        gpa_equivalent=4.0,
        order=1,
    )
    home_a = GradeValue.objects.create(
        grade_scale=home_scale,
        label="HomeA",
        numeric_value=4.0,
        gpa_equivalent=4.0,
        order=1,
    )
    return host_scale, home_scale, host_a, home_a


@pytest.mark.django_db
@pytest.mark.unit
class TestHostSubjectVisibility:
    def test_visibility_includes_institution_school_and_program_levels(
        self, host_tree
    ):
        inst = host_tree["institution"]
        school = host_tree["school"]
        academic = host_tree["academic"]
        HostSubject.objects.create(
            institution=inst, name="Uni Seminar", code="UNI1", is_active=True
        )
        HostSubject.objects.create(
            institution=inst,
            school=school,
            name="School Lab",
            code="SCH1",
            is_active=True,
        )
        ids = set(
            visible_host_subjects_queryset(
                institution_id=inst.id,
                school_id=school.id,
                academic_program_id=academic.id,
            ).values_list("code", flat=True)
        )
        assert ids == {"UNI1", "SCH1", "CS101"}

        school_only = set(
            visible_host_subjects_queryset(
                institution_id=inst.id, school_id=school.id
            ).values_list("code", flat=True)
        )
        assert school_only == {"UNI1", "SCH1"}

        inst_only = set(
            visible_host_subjects_queryset(institution_id=inst.id).values_list(
                "code", flat=True
            )
        )
        assert inst_only == {"UNI1"}

    def test_available_subjects_endpoint(self, student_client, host_tree):
        student, client = student_client
        application = _draft_application(student, host_tree)
        HostSubject.objects.create(
            institution=host_tree["institution"],
            name="Uni Seminar",
            code="UNI1",
            is_active=True,
        )
        resp = client.get(f"/api/applications/{application.id}/available-subjects/")
        assert resp.status_code == status.HTTP_200_OK
        codes = {row["code"] for row in resp.data}
        assert "CS101" in codes
        assert "UNI1" in codes


@pytest.mark.django_db
@pytest.mark.unit
class TestCustomSubjectXor:
    def test_custom_create_without_catalog(self, student_client, host_tree):
        student, client = student_client
        application = _draft_application(student, host_tree)
        resp = client.post(
            "/api/application-subject-selections/",
            {
                "application": str(application.id),
                "custom_code": "CUST1",
                "custom_name": "Custom Algorithms",
                "custom_credits": "4.00",
                "home_course_code": "H101",
                "home_course_label": "Algoritmos",
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data["custom_name"] == "Custom Algorithms"
        assert resp.data["host_subject"] is None
        assert resp.data["credits"] == "4.00"

    def test_catalog_and_custom_rejected(self, student_client, host_tree):
        student, client = student_client
        application = _draft_application(student, host_tree)
        resp = client.post(
            "/api/application-subject-selections/",
            {
                "application": str(application.id),
                "host_subject": str(host_tree["subject"].id),
                "custom_name": "Nope",
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@pytest.mark.unit
class TestAdminHostCrud:
    def test_student_cannot_create_host_subject(self, student_client, host_tree):
        _, client = student_client
        resp = client.post(
            "/api/host-subjects/",
            {
                "institution": str(host_tree["institution"].id),
                "name": "Forbidden",
                "code": "F1",
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_create_institution_level_subject(self, admin_client, host_tree):
        _, client = admin_client
        resp = client.post(
            f"/api/host-institutions/{host_tree['institution'].id}/subjects/",
            {"name": "Uni Elective", "code": "UE1", "credits": "3.00"},
            format="json",
        )
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data["school"] is None
        assert resp.data["academic_program"] is None
        assert str(resp.data["institution"]) == str(host_tree["institution"].id)


@pytest.mark.django_db
@pytest.mark.unit
class TestSubjectGradeWorkflow:
    def test_propose_confirm_reject_and_carta_grades(
        self, student_client, coordinator_client, host_tree
    ):
        student, student_api = student_client
        _, coord_api = coordinator_client
        host_scale, home_scale, host_a, home_a = _make_scales()
        host_tree["institution"].grade_scale = host_scale
        host_tree["institution"].save(update_fields=["grade_scale"])
        Profile.objects.update_or_create(
            user=student, defaults={"grade_scale": home_scale, "gpa": 3.5}
        )

        approved, _ = ApplicationStatus.objects.get_or_create(
            name="approved", defaults={"order": 5}
        )
        application = _draft_application(student, host_tree)
        application.status = approved
        application.save(update_fields=["status"])

        selection = ApplicationSubjectSelection.objects.create(
            application=application,
            host_subject=host_tree["subject"],
            home_course_code="H101",
            home_course_label="Algoritmos",
            credits=Decimal("6.00"),
        )

        patch = student_api.patch(
            f"/api/application-subject-selections/{selection.id}/",
            {"proposed_host_grade": str(host_a.id)},
            format="json",
        )
        assert patch.status_code == status.HTTP_200_OK

        propose = student_api.post(
            f"/api/applications/{application.id}/propose-subject-grades/"
        )
        assert propose.status_code == status.HTTP_200_OK
        selection.refresh_from_db()
        assert selection.grade_status == ApplicationSubjectSelection.GradeStatus.PROPOSED

        student_delete = student_api.delete(
            f"/api/application-subject-selections/{selection.id}/"
        )
        assert student_delete.status_code == status.HTTP_400_BAD_REQUEST

        confirm = coord_api.post(
            f"/api/applications/{application.id}/confirm-subject-grades/",
            {"notes": "Looks good"},
            format="json",
        )
        assert confirm.status_code == status.HTTP_200_OK, confirm.data
        selection.refresh_from_db()
        assert selection.grade_status == ApplicationSubjectSelection.GradeStatus.CONFIRMED
        assert selection.confirmed_host_grade_id == host_a.id
        assert selection.home_grade_id == home_a.id

        pdf = render_carta_homologacion_pdf(application)
        assert pdf[:4] == b"%PDF"
        assert b"HostA" in pdf
        assert b"HomeA" in pdf

        student_propose_again = student_api.post(
            f"/api/applications/{application.id}/propose-subject-grades/"
        )
        assert student_propose_again.status_code == status.HTTP_400_BAD_REQUEST

        reject = coord_api.post(
            f"/api/applications/{application.id}/reject-subject-grades/",
            {"notes": "Please revise"},
            format="json",
        )
        assert reject.status_code == status.HTTP_200_OK
        selection.refresh_from_db()
        assert selection.grade_status == ApplicationSubjectSelection.GradeStatus.REJECTED
        assert selection.home_grade_id is None

    def test_student_cannot_confirm(self, student_client, host_tree):
        student, client = student_client
        approved, _ = ApplicationStatus.objects.get_or_create(
            name="approved", defaults={"order": 5}
        )
        application = _draft_application(student, host_tree)
        application.status = approved
        application.save(update_fields=["status"])
        resp = client.post(
            f"/api/applications/{application.id}/confirm-subject-grades/"
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN
