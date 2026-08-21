"""Lifecycle requirement schedule: pipeline due dates and submit filtering."""

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from documents.models import DocumentType
from exchange.eligibility_rules import evaluate_eligibility
from exchange.lifecycle_requirements import (
    is_due,
    missing_submit_documents,
    pipeline_index,
)
from exchange.models import (
    Application,
    ApplicationStatus,
    ProgramDocumentRequirement,
    ProgramFieldRequirement,
)
from tests.utils import TestUtils


def _status(name, order=0):
    obj, _ = ApplicationStatus.objects.get_or_create(
        name=name, defaults={"order": order}
    )
    return obj


@pytest.mark.django_db
class TestPipelineIsDue:
    def test_approved_gate_not_due_at_submitted(self):
        assert is_due("approved", "submitted") is False

    def test_approved_gate_due_at_approved_and_completed(self):
        assert is_due("approved", "approved") is True
        assert is_due("approved", "completed") is True

    def test_not_due_on_rejected_or_waitlist(self):
        assert is_due("submitted", "rejected") is False
        assert is_due("submitted", "waitlist") is False
        assert is_due("approved", "waitlist") is False

    def test_pipeline_index_ignores_status_order(self):
        assert pipeline_index("approved") is not None
        assert pipeline_index("rejected") is None
        assert pipeline_index("waitlist") is None


@pytest.mark.django_db
class TestSubmitDocumentGate:
    def _app(self, status_name="draft"):
        student = TestUtils.create_test_user(role="student")
        program = TestUtils.create_test_program()
        st = _status(status_name)
        return TestUtils.create_test_application(
            student=student, program=program, status_name=status_name
        ), program, student

    def test_required_from_approved_does_not_fail_submit_rule(self):
        app, program, student = self._app()
        dt = DocumentType.objects.create(name="Santander cover")
        ProgramDocumentRequirement.objects.create(
            program=program,
            document_type=dt,
            is_required=True,
            required_from_status=_status("approved", 4),
        )
        ev = evaluate_eligibility(student, program, application=app)
        rd = next(r for r in ev.rules if r.rule_id == "required_documents")
        assert rd.passed is True
        assert missing_submit_documents(app) == []

    def test_required_from_submitted_still_fails_submit_rule(self):
        app, program, student = self._app()
        dt = DocumentType.objects.create(name="Transcript")
        ProgramDocumentRequirement.objects.create(
            program=program,
            document_type=dt,
            is_required=True,
            required_from_status=_status("submitted", 2),
        )
        ev = evaluate_eligibility(student, program, application=app)
        rd = next(r for r in ev.rules if r.rule_id == "required_documents")
        assert rd.passed is False
        assert missing_submit_documents(app)

    def test_legacy_null_required_from_is_submitted(self):
        app, program, student = self._app()
        dt = DocumentType.objects.create(name="Passport")
        ProgramDocumentRequirement.objects.create(
            program=program,
            document_type=dt,
            is_required=True,
            required_from_status=None,
        )
        ev = evaluate_eligibility(student, program, application=app)
        rd = next(r for r in ev.rules if r.rule_id == "required_documents")
        assert rd.passed is False


@pytest.mark.django_db
class TestStaffStatusPatchIgnoresLaterDocs:
    def test_coordinator_can_approve_with_missing_approved_document(self):
        student = TestUtils.create_test_user(role="student")
        coordinator = TestUtils.create_test_user(role="coordinator")
        program = TestUtils.create_test_program()
        under_review = _status("under_review", 3)
        approved = _status("approved", 4)
        app = Application.objects.create(
            student=student, program=program, status=under_review
        )
        dt = DocumentType.objects.create(name="Santander cover")
        ProgramDocumentRequirement.objects.create(
            program=program,
            document_type=dt,
            is_required=True,
            required_from_status=approved,
        )
        client = APIClient()
        refresh = RefreshToken.for_user(coordinator)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        response = client.patch(
            f"/api/applications/{app.id}/",
            {"status": "approved"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK, response.data
        app.refresh_from_db()
        assert app.status.name == "approved"


@pytest.mark.django_db
class TestStudentProfileDueFields:
    def test_empty_clabe_ok_when_not_due(self):
        student = TestUtils.create_test_user(role="student")
        client = APIClient()
        refresh = RefreshToken.for_user(student)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        response = client.patch(
            "/api/accounts/profile/",
            {"clabe": ""},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK, response.data

    def test_empty_clabe_fails_when_application_crossed_gate(self):
        student = TestUtils.create_test_user(role="student")
        program = TestUtils.create_test_program()
        approved = _status("approved", 4)
        Application.objects.create(
            student=student, program=program, status=approved
        )
        ProgramFieldRequirement.objects.create(
            program=program,
            source="profile",
            field_key="clabe",
            required_from_status=approved,
        )
        client = APIClient()
        refresh = RefreshToken.for_user(student)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        response = client.patch(
            "/api/accounts/profile/",
            {"clabe": ""},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "clabe" in response.data


@pytest.mark.django_db
class TestFieldRequirementFormCatalog:
    def test_catalog_includes_application_form_schema_keys(self):
        from application_forms.models import FormType
        from exchange.lifecycle_requirements import field_requirement_catalog

        ft = FormType.objects.create(
            name="Exchange form",
            form_type="application",
            schema={"properties": {"motivation_letter": {"type": "string"}}},
        )
        program = TestUtils.create_test_program()
        program.application_form = ft
        program.save(update_fields=["application_form"])
        catalog = field_requirement_catalog(program)
        assert "motivation_letter" in catalog["form"]
        assert "clabe" in catalog["profile"]


@pytest.mark.django_db
class TestDueNowReminder:
    def test_notify_dedupes_same_status_and_items(self):
        from exchange.lifecycle_requirements import notify_due_now_after_status_change
        from notifications.models import Notification

        student = TestUtils.create_test_user(role="student")
        program = TestUtils.create_test_program()
        approved = _status("approved", 4)
        app = Application.objects.create(
            student=student, program=program, status=approved
        )
        dt = DocumentType.objects.create(name="Santander cover")
        ProgramDocumentRequirement.objects.create(
            program=program,
            document_type=dt,
            is_required=True,
            required_from_status=approved,
        )
        first = notify_due_now_after_status_change(app)
        second = notify_due_now_after_status_change(app)
        assert first is not None
        assert second is None
        assert (
            Notification.objects.filter(
                recipient=student, title="Requirements due"
            ).count()
            == 1
        )

    def test_staff_status_patch_sends_due_reminder(self):
        from notifications.models import Notification

        student = TestUtils.create_test_user(role="student")
        coordinator = TestUtils.create_test_user(role="coordinator")
        program = TestUtils.create_test_program()
        under_review = _status("under_review", 3)
        approved = _status("approved", 4)
        app = Application.objects.create(
            student=student, program=program, status=under_review
        )
        dt = DocumentType.objects.create(name="Santander cover")
        ProgramDocumentRequirement.objects.create(
            program=program,
            document_type=dt,
            is_required=True,
            required_from_status=approved,
        )
        client = APIClient()
        refresh = RefreshToken.for_user(coordinator)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        response = client.patch(
            f"/api/applications/{app.id}/",
            {"status": "approved"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK, response.data
        due = Notification.objects.filter(
            recipient=student, title="Requirements due"
        )
        assert due.count() == 1
        assert "Santander cover" in due.get().message


@pytest.mark.django_db
class TestAdminProgramCloneRequirements:
    def test_admin_clone_copies_document_and_field_requirements(self):
        from django.contrib.admin.sites import AdminSite
        from django.contrib.messages.storage.fallback import FallbackStorage
        from django.test import RequestFactory

        from exchange.admin import ProgramAdmin
        from exchange.models import Program

        admin_user = TestUtils.create_test_user(role="admin")
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        program = TestUtils.create_test_program(name="Clone Source")
        dt = DocumentType.objects.create(name="Transcript clone")
        submitted = _status("submitted", 2)
        ProgramDocumentRequirement.objects.create(
            program=program,
            document_type=dt,
            is_required=True,
            required_from_status=submitted,
            sort_order=3,
        )
        ProgramFieldRequirement.objects.create(
            program=program,
            source="profile",
            field_key="clabe",
            required_from_status=submitted,
        )
        request = RequestFactory().post("/")
        request.user = admin_user
        request.session = {}
        request._messages = FallbackStorage(request)
        ProgramAdmin(Program, AdminSite()).clone_programs(
            request, Program.objects.filter(pk=program.pk)
        )
        clone = Program.objects.get(name=f"{program.name} (Copy)")
        copied_doc = clone.program_document_requirements.get()
        assert copied_doc.document_type_id == dt.id
        assert copied_doc.sort_order == 3
        assert copied_doc.is_required is True
        copied_field = clone.field_requirements.get()
        assert copied_field.source == "profile"
        assert copied_field.field_key == "clabe"
        assert copied_field.required_from_status_id == submitted.id
