"""Tests for read-only audit_clean_scan_approvals management command."""

from datetime import date
from io import StringIO

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.utils import timezone

from documents.management.commands.audit_clean_scan_approvals import (
    EQUIVALENT_SQL,
    queryset_likely_clean_scan_approvals,
)
from documents.models import Document, DocumentType, DocumentValidation
from exchange.models import Application, ApplicationStatus, Program

User = get_user_model()


@pytest.fixture
def base_doc(db):
    user = User.objects.create_user(
        username="audit_student", email="audit.student@example.com", password="x"
    )
    staff = User.objects.create_user(
        username="audit_coord", email="audit.coord@example.com", password="x"
    )
    program = Program.objects.create(
        name="Audit Program",
        description="x",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 6, 30),
        is_active=True,
    )
    status, _ = ApplicationStatus.objects.get_or_create(
        name="draft", defaults={"order": 1}
    )
    application = Application.objects.create(
        student=user, program=program, status=status
    )
    doc_type = DocumentType.objects.create(name="AuditDocType", description="")
    file = SimpleUploadedFile("a.pdf", b"%PDF-1.4", content_type="application/pdf")
    doc = Document.objects.create(
        application=application,
        type=doc_type,
        file=file,
        uploaded_by=user,
        is_valid=False,
    )
    return {"doc": doc, "user": user, "staff": staff}


def _make_sibling(base_doc, *, name_suffix: str) -> Document:
    file = SimpleUploadedFile(
        f"{name_suffix}.pdf", b"%PDF-1.4", content_type="application/pdf"
    )
    return Document.objects.create(
        application=base_doc["doc"].application,
        type=base_doc["doc"].type,
        file=file,
        uploaded_by=base_doc["user"],
        is_valid=False,
    )


@pytest.mark.django_db
def test_queryset_counts_only_clean_scan_auto_approvals(base_doc):
    scan_only = base_doc["doc"]
    scan_only.is_valid = True
    scan_only.validated_at = timezone.now()
    scan_only.save(update_fields=["is_valid", "validated_at"])
    DocumentValidation.objects.create(
        document=scan_only,
        validator=base_doc["user"],
        result="valid",
        details="Scanned by async task",
    )

    staff_approved = _make_sibling(base_doc, name_suffix="staff")
    staff_approved.is_valid = True
    staff_approved.validated_at = timezone.now()
    staff_approved.save(update_fields=["is_valid", "validated_at"])
    DocumentValidation.objects.create(
        document=staff_approved,
        validator=base_doc["staff"],
        result="valid",
        details="Looks good",
    )

    both = _make_sibling(base_doc, name_suffix="both")
    both.is_valid = True
    both.validated_at = timezone.now()
    both.save(update_fields=["is_valid", "validated_at"])
    DocumentValidation.objects.create(
        document=both,
        validator=base_doc["user"],
        result="valid",
        details="Scanned by async task",
    )
    DocumentValidation.objects.create(
        document=both,
        validator=base_doc["staff"],
        result="valid",
        details="Coordinator approved after scan",
    )

    orphan = _make_sibling(base_doc, name_suffix="orphan")
    orphan.is_valid = True
    orphan.validated_at = timezone.now()
    orphan.save(update_fields=["is_valid", "validated_at"])

    ids = set(queryset_likely_clean_scan_approvals().values_list("id", flat=True))
    assert ids == {scan_only.id}


@pytest.mark.django_db
def test_command_prints_count_and_is_read_only(base_doc):
    doc = base_doc["doc"]
    doc.is_valid = True
    doc.validated_at = timezone.now()
    doc.save(update_fields=["is_valid", "validated_at"])
    DocumentValidation.objects.create(
        document=doc,
        validator=base_doc["user"],
        result="valid",
        details="Scanned by async task. Threat: None",
    )

    out = StringIO()
    call_command("audit_clean_scan_approvals", sample=5, stdout=out)
    text = out.getvalue()
    assert "READ-ONLY" in text
    assert "likely clean-scan auto-approvals:      1" in text
    assert str(doc.id) in text
    assert "No data was modified" in text

    doc.refresh_from_db()
    assert doc.is_valid is True


@pytest.mark.django_db
def test_command_sql_only_skips_query():
    out = StringIO()
    call_command("audit_clean_scan_approvals", sql_only=True, stdout=out)
    text = out.getvalue()
    assert EQUIVALENT_SQL.strip() in text
    assert "is_valid=True total" not in text
