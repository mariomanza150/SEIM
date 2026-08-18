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
