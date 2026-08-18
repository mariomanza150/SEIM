"""Tests for historic ApplicationSubjectPlanVersion snapshots."""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Profile, Role
from exchange.models import (
    MAX_SUBJECT_PLAN_VERSIONS,
    Application,
    ApplicationStatus,
)
from exchange.subject_plan_versions import snapshot_subject_plan
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
        username="plan_student",
        email="plan_student@university.edu",
        password="testpass123",
        first_name="Plan",
        last_name="Student",
    )
    role, _ = Role.objects.get_or_create(name="student")
    student.roles.add(role)
    return student, _auth_client(student)


@pytest.fixture
def other_student_client(db):
    student = User.objects.create_user(
        username="plan_other",
        email="plan_other@university.edu",
        password="testpass123",
    )
    role, _ = Role.objects.get_or_create(name="student")
    student.roles.add(role)
    return student, _auth_client(student)


@pytest.fixture
def coordinator_client(db):
    coord = User.objects.create_user(
        username="plan_coord",
        email="plan_coord@university.edu",
        password="testpass123",
    )
    role, _ = Role.objects.get_or_create(name="coordinator")
    coord.roles.add(role)
    return coord, _auth_client(coord)


@pytest.fixture
def host_tree(db):
    today = date.today()
    from exchange.models import Program

    program = Program.objects.create(
        name="Plan Version Program",
        description="Subject plan version tests",
        start_date=today + timedelta(days=60),
        end_date=today + timedelta(days=200),
        application_open_date=today - timedelta(days=10),
        application_deadline=today + timedelta(days=30),
        is_active=True,
    )
    tree = attach_host_destination(program, with_subject=True)
    tree["program"] = program
    return tree


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


def _add_selection(client, application, host_tree, *, suffix="1", catalog=False):
    """Add a selection; default is a distinct custom course (suffix must differ)."""
    if catalog:
        return client.post(
            "/api/application-subject-selections/",
            {
                "application": str(application.id),
                "host_subject": str(host_tree["subject"].id),
                "home_course_code": f"H{suffix}",
                "home_course_label": f"Home {suffix}",
            },
            format="json",
        )
    return client.post(
        "/api/application-subject-selections/",
        {
            "application": str(application.id),
            "custom_code": f"C{suffix}",
            "custom_name": f"Custom {suffix}",
            "home_course_code": f"H{suffix}",
            "home_course_label": f"Home {suffix}",
        },
        format="json",
    )


@pytest.mark.django_db
@pytest.mark.unit
class TestSubjectPlanVersionSnapshots:
    def test_first_add_skips_empty_snapshot(self, student_client, host_tree):
        student, client = student_client
        application = _draft_application(student, host_tree)

        resp = _add_selection(client, application, host_tree, suffix="1", catalog=True)
        assert resp.status_code == status.HTTP_201_CREATED
        assert application.subject_plan_versions.count() == 0

    def test_second_add_creates_version_with_prior_row(
        self, student_client, host_tree
    ):
        student, client = student_client
        application = _draft_application(student, host_tree)

        first = _add_selection(client, application, host_tree, suffix="1", catalog=True)
        assert first.status_code == status.HTTP_201_CREATED

        second = _add_selection(client, application, host_tree, suffix="2")
        assert second.status_code == status.HTTP_201_CREATED

        versions = list(
            application.subject_plan_versions.order_by("version_number")
        )
        assert len(versions) == 1
        assert versions[0].version_number == 1
        assert len(versions[0].payload) == 1
        assert versions[0].payload[0]["home_course_code"] == "H1"
        assert versions[0].created_by_id == student.id

    def test_no_duplicate_snapshot_for_identical_payload(
        self, student_client, host_tree
    ):
        student, client = student_client
        application = _draft_application(student, host_tree)
        from exchange.models import ApplicationSubjectSelection

        ApplicationSubjectSelection.objects.create(
            application=application,
            host_subject=host_tree["subject"],
            home_course_code="H1",
            home_course_label="Home 1",
            credits=Decimal("6.00"),
        )
        first = snapshot_subject_plan(application, student)
        assert first is not None
        before = application.subject_plan_versions.count()
        assert snapshot_subject_plan(application, student) is None
        assert application.subject_plan_versions.count() == before

    def test_prune_keeps_at_most_three_versions(self, student_client, host_tree):
        student, client = student_client
        application = _draft_application(student, host_tree)

        for i in range(5):
            resp = _add_selection(
                client, application, host_tree, suffix=str(i)
            )
            assert resp.status_code == status.HTTP_201_CREATED, resp.data

        versions = list(
            application.subject_plan_versions.order_by("version_number")
        )
        assert len(versions) == MAX_SUBJECT_PLAN_VERSIONS
        assert versions[0].version_number == 2
        assert versions[-1].version_number == 4

    def test_destroy_creates_snapshot(self, student_client, host_tree):
        student, client = student_client
        application = _draft_application(student, host_tree)
        create = _add_selection(client, application, host_tree, suffix="1", catalog=True)
        selection_id = create.data["id"]
        _add_selection(client, application, host_tree, suffix="2")

        before = application.subject_plan_versions.count()
        delete = client.delete(f"/api/application-subject-selections/{selection_id}/")
        assert delete.status_code == status.HTTP_204_NO_CONTENT
        assert application.subject_plan_versions.count() == before + 1
        latest = application.subject_plan_versions.order_by("-version_number").first()
        assert len(latest.payload) == 2

    def test_mapping_patch_creates_snapshot(self, student_client, host_tree):
        student, client = student_client
        application = _draft_application(student, host_tree)
        create = _add_selection(client, application, host_tree, suffix="1", catalog=True)
        selection_id = create.data["id"]

        patch = client.patch(
            f"/api/application-subject-selections/{selection_id}/",
            {"home_course_label": "Renamed"},
            format="json",
        )
        assert patch.status_code == status.HTTP_200_OK
        version = application.subject_plan_versions.order_by("-version_number").first()
        assert version is not None
        assert version.payload[0]["home_course_label"] != "Renamed"

    def test_grade_only_patch_does_not_snapshot(
        self, student_client, host_tree
    ):
        student, client = student_client
        application = _draft_application(student, host_tree)
        approved, _ = ApplicationStatus.objects.get_or_create(
            name="approved", defaults={"order": 5}
        )
        application.status = approved
        application.save(update_fields=["status"])

        host_scale = GradeScale.objects.create(
            name="Host Plan",
            code="HOST_PLAN",
            min_value=0,
            max_value=4,
            passing_value=1,
        )
        host_tree["institution"].grade_scale = host_scale
        host_tree["institution"].save(update_fields=["grade_scale"])
        host_grade = GradeValue.objects.create(
            grade_scale=host_scale,
            label="A",
            numeric_value=Decimal("4.00"),
            gpa_equivalent=Decimal("4.00"),
            order=1,
        )

        create = _add_selection(client, application, host_tree, suffix="1", catalog=True)
        selection_id = create.data["id"]
        _add_selection(client, application, host_tree, suffix="2")
        before = application.subject_plan_versions.count()

        patch = client.patch(
            f"/api/application-subject-selections/{selection_id}/",
            {"proposed_host_grade": str(host_grade.id)},
            format="json",
        )
        assert patch.status_code == status.HTTP_200_OK
        assert application.subject_plan_versions.count() == before


@pytest.mark.django_db
@pytest.mark.unit
class TestSubjectPlanVersionApi:
    def test_list_versions_owner_and_coordinator(
        self, student_client, coordinator_client, host_tree
    ):
        student, student_api = student_client
        _, coord_api = coordinator_client
        application = _draft_application(student, host_tree)
        _add_selection(student_api, application, host_tree, suffix="1", catalog=True)
        _add_selection(student_api, application, host_tree, suffix="2")

        url = f"/api/applications/{application.id}/subject-plan-versions/"
        owner = student_api.get(url)
        assert owner.status_code == status.HTTP_200_OK
        assert len(owner.data) == 1
        assert owner.data[0]["version_number"] == 1
        assert owner.data[0]["created_by_name"] == student.get_full_name()

        coord = coord_api.get(url)
        assert coord.status_code == status.HTTP_200_OK
        assert len(coord.data) == 1

    def test_other_student_forbidden(
        self, student_client, other_student_client, host_tree
    ):
        student, student_api = student_client
        _, other_api = other_student_client
        application = _draft_application(student, host_tree)
        _add_selection(student_api, application, host_tree, suffix="1", catalog=True)
        _add_selection(student_api, application, host_tree, suffix="2")

        url = f"/api/applications/{application.id}/subject-plan-versions/"
        resp = other_api.get(url)
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_propose_grades_creates_snapshot(
        self, student_client, coordinator_client, host_tree
    ):
        student, student_api = student_client
        application = _draft_application(student, host_tree)
        approved, _ = ApplicationStatus.objects.get_or_create(
            name="approved", defaults={"order": 5}
        )
        application.status = approved
        application.save(update_fields=["status"])

        host_scale = GradeScale.objects.create(
            name="Host Propose",
            code="HOST_PROP",
            min_value=0,
            max_value=4,
            passing_value=1,
        )
        home_scale = GradeScale.objects.create(
            name="Home Propose",
            code="HOME_PROP",
            min_value=0,
            max_value=4,
            passing_value=2,
        )
        host_tree["institution"].grade_scale = host_scale
        host_tree["institution"].save(update_fields=["grade_scale"])
        Profile.objects.update_or_create(
            user=student, defaults={"grade_scale": home_scale, "gpa": 3.5}
        )
        host_grade = GradeValue.objects.create(
            grade_scale=host_scale,
            label="B",
            numeric_value=Decimal("3.00"),
            gpa_equivalent=Decimal("3.00"),
            order=1,
        )
        GradeValue.objects.create(
            grade_scale=home_scale,
            label="B-home",
            numeric_value=Decimal("3.00"),
            gpa_equivalent=Decimal("3.00"),
            order=1,
        )

        create = _add_selection(student_api, application, host_tree, suffix="1", catalog=True)
        selection_id = create.data["id"]
        _add_selection(student_api, application, host_tree, suffix="2")
        before = application.subject_plan_versions.count()

        patch = student_api.patch(
            f"/api/application-subject-selections/{selection_id}/",
            {"proposed_host_grade": str(host_grade.id)},
            format="json",
        )
        assert patch.status_code == status.HTTP_200_OK

        propose = student_api.post(
            f"/api/applications/{application.id}/propose-subject-grades/"
        )
        assert propose.status_code == status.HTTP_200_OK
        assert application.subject_plan_versions.count() == before + 1
        latest = application.subject_plan_versions.order_by("-version_number").first()
        assert latest.payload[0]["grade_status"] in ("none", "proposed")
