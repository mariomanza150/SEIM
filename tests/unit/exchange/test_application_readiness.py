"""Unit tests for exchange.readiness.compute_application_readiness."""

from datetime import timedelta

import pytest
from django.utils import timezone

from documents.models import DocumentType
from exchange.readiness import compute_application_readiness
from tests.utils import TestUtils


@pytest.mark.django_db
class TestApplicationReadiness:
    def test_submitted_is_done(self):
        student = TestUtils.create_test_user(role="student")
        program = TestUtils.create_test_program()
        app = TestUtils.create_test_application(
            student=student, program=program, status_name="submitted"
        )
        r = compute_application_readiness(app, include_dynamic_form=True)
        assert r["level"] == "done"
        assert r["score"] == 100

    def test_draft_window_closed_blocked(self):
        student = TestUtils.create_test_user(role="student")
        today = timezone.localdate()
        program = TestUtils.create_test_program()
        program.application_open_date = today - timedelta(days=60)
        program.application_deadline = today - timedelta(days=1)
        program.save(update_fields=["application_open_date", "application_deadline"])

        app = TestUtils.create_test_application(
            student=student, program=program, status_name="draft"
        )
        r = compute_application_readiness(app, today=today, include_dynamic_form=False)
        assert r["level"] == "blocked"
        assert r["window_open"] is False
        assert r["score"] <= 30

    def test_draft_missing_required_documents_attention(self):
        student = TestUtils.create_test_user(role="student")
        program = TestUtils.create_test_program()
        dt = DocumentType.objects.create(name="Passport")
        program.required_document_types.add(dt)

        app = TestUtils.create_test_application(
            student=student, program=program, status_name="draft"
        )
        r = compute_application_readiness(app, include_dynamic_form=False)
        assert r["level"] == "attention"
        assert r["document_counts"]["missing"] >= 1
        assert "missing" in r["headline"].lower()

    def test_draft_incomplete_host_is_not_ready(self):
        from exchange.models import Application, ApplicationStatus
        from tests.unit.exchange.host_destination_helpers import attach_host_destination

        student = TestUtils.create_test_user(role="student")
        program = TestUtils.create_test_program()
        attach_host_destination(program)
        draft, _ = ApplicationStatus.objects.get_or_create(name="draft")
        app = Application.objects.create(
            student=student, program=program, status=draft
        )
        r = compute_application_readiness(app, include_dynamic_form=False)
        assert r["host_destination"]["required"] is True
        assert r["host_destination"]["complete"] is False
        assert r["level"] != "ready"
        assert "host" in r["headline"].lower()

    def test_draft_without_host_tree_does_not_require_destination(self):
        from exchange.models import Application, ApplicationStatus

        student = TestUtils.create_test_user(role="student")
        program = TestUtils.create_test_program()
        draft, _ = ApplicationStatus.objects.get_or_create(name="draft")
        app = Application.objects.create(
            student=student, program=program, status=draft
        )
        r = compute_application_readiness(app, include_dynamic_form=False)
        assert r["host_destination"]["required"] is False
        assert r["host_destination"]["complete"] is True

    def test_draft_ineligible_language_is_not_ready(self):
        from datetime import date, timedelta

        from accounts.models import Profile, Role
        from django.contrib.auth import get_user_model
        from exchange.models import Application, ApplicationStatus, Program

        User = get_user_model()
        student = User.objects.create(
            username="elig_ready_stu",
            email="elig_ready_stu@test.com",
            password="x",
        )
        role, _ = Role.objects.get_or_create(name="student")
        student.roles.add(role)
        Profile.objects.update_or_create(
            user=student,
            defaults={
                "gpa": 3.7,
                "language": "German",
                "language_level": "A2",
            },
        )
        today = date.today()
        program = Program.objects.create(
            name="Language gate program",
            description="d",
            start_date=today,
            end_date=today + timedelta(days=120),
            application_open_date=today - timedelta(days=7),
            application_deadline=today + timedelta(days=30),
            required_language="English",
            min_language_level="B2",
            is_active=True,
        )
        draft, _ = ApplicationStatus.objects.get_or_create(name="draft")
        app = Application.objects.create(
            student=student, program=program, status=draft
        )
        r = compute_application_readiness(app, include_dynamic_form=False)
        assert r["eligibility"]["complete"] is False
        assert r["eligibility"]["issues"]
        assert r["level"] != "ready"
        assert "eligibility" in r["headline"].lower()

    def test_draft_ignores_stale_eligible_snapshot(self):
        """Draft readiness uses the live profile, not leftover *_at_apply fields."""
        from datetime import date, timedelta

        from accounts.models import Profile, Role
        from django.contrib.auth import get_user_model
        from exchange.models import Application, ApplicationStatus, Program

        User = get_user_model()
        student = User.objects.create(
            username="elig_stale_snap",
            email="elig_stale_snap@test.com",
            password="x",
        )
        role, _ = Role.objects.get_or_create(name="student")
        student.roles.add(role)
        Profile.objects.update_or_create(
            user=student,
            defaults={
                "gpa": 3.7,
                "language": "German",
                "language_level": "A2",
            },
        )
        today = date.today()
        program = Program.objects.create(
            name="Stale snapshot program",
            description="d",
            start_date=today,
            end_date=today + timedelta(days=120),
            application_open_date=today - timedelta(days=7),
            application_deadline=today + timedelta(days=30),
            required_language="English",
            min_language_level="B2",
            is_active=True,
        )
        draft, _ = ApplicationStatus.objects.get_or_create(name="draft")
        app = Application.objects.create(
            student=student,
            program=program,
            status=draft,
            language_at_apply="English",
            language_level_at_apply="C1",
        )
        r = compute_application_readiness(app, include_dynamic_form=False)
        assert r["eligibility"]["complete"] is False
        assert r["level"] != "ready"
        assert any("English" in issue for issue in r["eligibility"]["issues"])
