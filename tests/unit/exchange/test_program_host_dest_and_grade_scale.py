"""Program host-destination settings and outgoing grade-scale overrides."""

from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APIRequestFactory

from accounts.models import AllowedEmailDomain, Profile, Role
from exchange.models import (
    Application,
    ApplicationStatus,
    Program,
    application_host_institution_display,
    program_grade_scale_policy,
    program_requires_host_destination,
    validate_application_host_destination,
)
from exchange.serializers import ApplicationSerializer, ProgramSerializer
from grades.models import GradeScale

User = get_user_model()


@pytest.fixture
def scales(db):
    ten = GradeScale.objects.create(
        name="MX 0-10", code="MX_P_10", min_value=0, max_value=10, passing_value=6
    )
    four = GradeScale.objects.create(
        name="US 0-4", code="US_P_4", min_value=0, max_value=4, passing_value=2
    )
    return ten, four


@pytest.fixture
def program(db):
    today = date.today()
    return Program.objects.create(
        name="Host Dest Program",
        description="Settings tests",
        start_date=today + timedelta(days=60),
        end_date=today + timedelta(days=200),
        application_open_date=today - timedelta(days=5),
        application_deadline=today + timedelta(days=30),
        is_active=True,
        mobility_direction=Program.MobilityDirection.OUTGOING,
    )


@pytest.mark.django_db
@pytest.mark.unit
class TestProgramHostDestinationSettings:
    def test_defaults_preserve_catalog_required_behavior(self, program):
        assert program.host_destination_required is True
        assert program.host_destination_mode == Program.HostDestinationMode.CATALOG
        assert program_requires_host_destination(program) is False  # no hosts yet

    def test_required_false_skips_requirement(self, program):
        from exchange.models import HostInstitution

        HostInstitution.objects.create(
            program=program, name="U", country="MX", is_active=True
        )
        program.host_destination_required = False
        program.save(update_fields=["host_destination_required"])
        assert program_requires_host_destination(program) is False

    def test_free_text_mode_required_without_catalog(self, program):
        program.host_destination_mode = Program.HostDestinationMode.FREE_TEXT
        program.save(update_fields=["host_destination_mode"])
        assert program_requires_host_destination(program) is True

        app = Application(
            program=program,
            student=User.objects.create_user(
                username="ft", email="ft@example.com", password="x"
            ),
            status=ApplicationStatus.objects.get_or_create(
                name="draft", defaults={"order": 1}
            )[0],
        )
        errors = validate_application_host_destination(app, require_complete=True)
        assert "host_institution" in errors

        app.host_institution_text = "Typed University"
        app.host_school_text = "Arts"
        app.host_academic_program_text = "BA"
        errors = validate_application_host_destination(app, require_complete=True)
        assert errors == {}
        assert application_host_institution_display(app) == "Typed University"

    def test_serializer_stores_free_text_in_free_text_mode(self, program):
        program.host_destination_mode = Program.HostDestinationMode.FREE_TEXT
        program.save(update_fields=["host_destination_mode"])
        student = User.objects.create_user(
            username="ft2", email="ft2@example.com", password="x"
        )
        role, _ = Role.objects.get_or_create(name="student")
        student.roles.add(role)
        Profile.objects.get_or_create(user=student)
        factory = APIRequestFactory()
        request = factory.post("/api/applications/")
        request.user = student
        serializer = ApplicationSerializer(
            data={
                "program": program.id,
                "host_institution_text": "Free U",
                "host_school_text": "Free School",
                "host_academic_program_text": "Free Program",
            },
            context={"request": request},
        )
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data.get("host_institution") in (None,)
        assert serializer.validated_data["host_institution_text"] == "Free U"
        assert serializer.validated_data["host_school_text"] == "Free School"
        assert (
            application_host_institution_display(
                type(
                    "P",
                    (),
                    {
                        "host_institution": None,
                        "host_institution_text": "Free U",
                    },
                )()
            )
            == "Free U"
        )


@pytest.mark.django_db
@pytest.mark.unit
class TestProgramGradeScaleSettings:
    def test_program_policy_overrides_domain_for_outgoing(self, program, scales):
        ten, four = scales
        AllowedEmailDomain.objects.create(
            name="uni.test.mx", default_grade_scale=ten, lock_grade_scale=True
        )
        program.default_grade_scale = four
        program.lock_grade_scale = True
        program.save()
        policy = program_grade_scale_policy(program)
        assert policy["default_grade_scale"] == str(four.pk)
        assert policy["locked"] is True

        user = User.objects.create_user(
            username="ana", email="ana@uni.test.mx", password="pw-123456!"
        )
        role, _ = Role.objects.get_or_create(name="student")
        user.roles.add(role)
        Profile.objects.get_or_create(user=user)
        client = APIClient()
        client.force_authenticate(user)
        # Without program: domain policy
        domain_policy = client.get("/api/accounts/profile/").json()[
            "grade_scale_policy"
        ]
        assert domain_policy["default_grade_scale"] == str(ten.pk)
        # With program: outgoing program overrides
        program_policy = client.get(
            f"/api/accounts/profile/?program={program.id}"
        ).json()["grade_scale_policy"]
        assert program_policy["default_grade_scale"] == str(four.pk)
        assert program_policy["locked"] is True

        bad = client.patch(
            f"/api/accounts/profile/?program={program.id}",
            {"grade_scale": str(ten.pk)},
            format="json",
        )
        assert bad.status_code == 400
        assert "grade_scale" in bad.json()

        ok = client.patch(
            f"/api/accounts/profile/?program={program.id}",
            {"gpa": 3.1},
            format="json",
        )
        assert ok.status_code == 200, ok.content
        assert Profile.objects.get(user=user).grade_scale_id == four.pk

    def test_incoming_program_does_not_override_domain(self, program, scales):
        ten, four = scales
        program.mobility_direction = Program.MobilityDirection.INCOMING
        program.default_grade_scale = four
        program.lock_grade_scale = True
        program.save()
        assert program_grade_scale_policy(program) is None

    def test_program_serializer_rejects_lock_without_default(self, program):
        serializer = ProgramSerializer(
            instance=program,
            data={"lock_grade_scale": True, "default_grade_scale": None},
            partial=True,
        )
        assert not serializer.is_valid()
        assert "lock_grade_scale" in serializer.errors
