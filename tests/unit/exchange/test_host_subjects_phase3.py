"""Light unit tests for Phase 3 host subjects + Carta de Homologación."""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Role
from documents.pdf_generation import render_carta_homologacion_pdf
from exchange.models import (
    Application,
    ApplicationStatus,
    ApplicationSubjectSelection,
    HostAcademicProgram,
    HostInstitution,
    HostSchool,
    HostSubject,
    Program,
)

User = get_user_model()


@pytest.fixture
def student_client(db):
    student = User.objects.create_user(
        username="subj_student",
        email="subj_student@university.edu",
        password="testpass123",
        first_name="Sub",
        last_name="Student",
    )
    role, _ = Role.objects.get_or_create(name="student")
    student.roles.add(role)
    client = APIClient()
    token = RefreshToken.for_user(student)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return student, client


@pytest.fixture
def host_tree(db):
    today = date.today()
    program = Program.objects.create(
        name="Movilidad Test Subjects",
        description="Phase 3 test scheme",
        start_date=today + timedelta(days=60),
        end_date=today + timedelta(days=200),
        application_open_date=today - timedelta(days=10),
        application_deadline=today + timedelta(days=30),
        is_active=True,
    )
    institution = HostInstitution.objects.create(
        program=program, name="Host U", country="MX", is_active=True
    )
    school = HostSchool.objects.create(
        institution=institution, name="Engineering", is_active=True
    )
    academic = HostAcademicProgram.objects.create(
        school=school, name="Computer Science", code="CS", is_active=True
    )
    subject = HostSubject.objects.create(
        institution=institution,
        school=school,
        academic_program=academic,
        code="CS101",
        name="Algorithms",
        credits=Decimal("6.00"),
        is_active=True,
    )
    return {
        "program": program,
        "institution": institution,
        "school": school,
        "academic": academic,
        "subject": subject,
    }


@pytest.mark.django_db
@pytest.mark.unit
class TestHostSubjectsPhase3:
    def test_list_subjects_for_academic_program(self, student_client, host_tree):
        _, client = student_client
        academic = host_tree["academic"]
        url = f"/api/academic-programs/{academic.id}/subjects/"
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["code"] == "CS101"
        assert response.data[0]["name"] == "Algorithms"

    def test_subject_selection_crud_own_draft(self, student_client, host_tree):
        student, client = student_client
        draft, _ = ApplicationStatus.objects.get_or_create(
            name="draft", defaults={"order": 0}
        )
        application = Application.objects.create(
            student=student,
            program=host_tree["program"],
            status=draft,
            host_institution=host_tree["institution"],
            host_school=host_tree["school"],
            host_academic_program=host_tree["academic"],
        )
        subject = host_tree["subject"]

        create_resp = client.post(
            "/api/application-subject-selections/",
            {
                "application": str(application.id),
                "host_subject": str(subject.id),
                "home_course_code": "MAT101",
                "home_course_label": "Algoritmos",
            },
            format="json",
        )
        assert create_resp.status_code == status.HTTP_201_CREATED
        selection_id = create_resp.data["id"]
        assert create_resp.data["credits"] == "6.00"

        list_resp = client.get(
            "/api/application-subject-selections/",
            {"application": str(application.id)},
        )
        assert list_resp.status_code == status.HTTP_200_OK
        rows = (
            list_resp.data
            if isinstance(list_resp.data, list)
            else list_resp.data["results"]
        )
        assert len(rows) == 1

        del_resp = client.delete(f"/api/application-subject-selections/{selection_id}/")
        assert del_resp.status_code == status.HTTP_204_NO_CONTENT
        assert ApplicationSubjectSelection.objects.filter(pk=selection_id).count() == 0

    def test_other_student_cannot_manage_selections(self, student_client, host_tree):
        owner, _ = student_client
        draft, _ = ApplicationStatus.objects.get_or_create(
            name="draft", defaults={"order": 0}
        )
        application = Application.objects.create(
            student=owner,
            program=host_tree["program"],
            status=draft,
            host_institution=host_tree["institution"],
            host_school=host_tree["school"],
            host_academic_program=host_tree["academic"],
        )
        other = User.objects.create_user(
            username="other_subj",
            email="other_subj@university.edu",
            password="testpass123",
        )
        role, _ = Role.objects.get_or_create(name="student")
        other.roles.add(role)
        other_client = APIClient()
        token = RefreshToken.for_user(other)
        other_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")

        resp = other_client.post(
            "/api/application-subject-selections/",
            {
                "application": str(application.id),
                "host_subject": str(host_tree["subject"].id),
            },
            format="json",
        )
        assert resp.status_code in (
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
        )

    def test_carta_homologacion_pdf_empty_and_with_selections(
        self, student_client, host_tree
    ):
        student, client = student_client
        draft, _ = ApplicationStatus.objects.get_or_create(
            name="draft", defaults={"order": 0}
        )
        application = Application.objects.create(
            student=student,
            program=host_tree["program"],
            status=draft,
            host_institution=host_tree["institution"],
            host_school=host_tree["school"],
            host_academic_program=host_tree["academic"],
        )

        empty_pdf = render_carta_homologacion_pdf(application)
        assert empty_pdf[:4] == b"%PDF"
        assert len(empty_pdf) > 200

        ApplicationSubjectSelection.objects.create(
            application=application,
            host_subject=host_tree["subject"],
            home_course_code="MAT101",
            home_course_label="Algoritmos",
            credits=Decimal("6.00"),
        )
        filled_pdf = render_carta_homologacion_pdf(application)
        assert filled_pdf[:4] == b"%PDF"
        # With selections the PDF should be larger than the empty notice version.
        assert len(filled_pdf) >= len(empty_pdf)

        dl = client.get(f"/api/applications/{application.id}/carta-homologacion/")
        assert dl.status_code == status.HTTP_200_OK
        assert dl["Content-Type"] == "application/pdf"
        assert dl.content[:4] == b"%PDF"
        assert dl["X-Subject-Selection-Count"] == "1"
