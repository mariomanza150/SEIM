"""Propose / confirm / reject host-course grades and persist Carta PDFs."""

from __future__ import annotations

from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone

from exchange.models import (
    SUBJECT_GRADE_ELIGIBLE_STATUS_NAMES,
    ApplicationSubjectPlanVersion,
    ApplicationSubjectSelection,
    TimelineEvent,
)
from exchange.subject_plan_versions import snapshot_subject_plan


def _application_status_name(application) -> str | None:
    return getattr(application.status, "name", None)


def assert_gradeable_status(application) -> None:
    status_name = _application_status_name(application)
    if status_name not in SUBJECT_GRADE_ELIGIBLE_STATUS_NAMES:
        allowed = ", ".join(sorted(SUBJECT_GRADE_ELIGIBLE_STATUS_NAMES))
        raise ValueError(
            f"Subject grades can only be managed when the application status "
            f"is one of: {allowed}."
        )


def persist_carta_homologacion(application, user) -> bytes:
    """Render Carta de Homologación and attach/refresh the checklist Document."""
    from documents.models import Document, DocumentType
    from documents.pdf_generation import render_carta_homologacion_pdf

    pdf_bytes = render_carta_homologacion_pdf(application)
    filename = f"carta_homologacion_{application.id}.pdf"
    doc_type = DocumentType.objects.filter(slug="carta_homologacion").first()
    if doc_type is None:
        doc_type, _ = DocumentType.objects.get_or_create(
            slug="carta_homologacion",
            defaults={
                "name": "Carta de Homologación",
                "description": "Carta de homologación de asignaturas.",
                "submission_mode": getattr(
                    DocumentType.SubmissionMode,
                    "SYSTEM_GENERATED",
                    "system_generated",
                ),
                "accepted_extensions": "pdf",
            },
        )

    existing = (
        Document.objects.filter(application=application, type=doc_type)
        .order_by("-created_at")
        .first()
    )
    uploaded_by = user if getattr(user, "is_authenticated", False) else application.student
    if existing is None:
        document = Document(
            application=application,
            type=doc_type,
            uploaded_by=uploaded_by,
        )
        document.file.save(filename, ContentFile(pdf_bytes), save=True)
    else:
        existing.file.save(filename, ContentFile(pdf_bytes), save=True)
    return pdf_bytes


def propose_subject_grades(application, user) -> int:
    """Mark selections that have a proposed host grade as ``proposed``."""
    assert_gradeable_status(application)
    now = timezone.now()
    qs = application.subject_selections.all()
    to_update = [
        row
        for row in qs
        if row.proposed_host_grade_id
        and row.grade_status != ApplicationSubjectSelection.GradeStatus.CONFIRMED
    ]
    if not to_update:
        raise ValueError("No subject selections have a proposed host grade.")

    status_changing = any(
        row.grade_status != ApplicationSubjectSelection.GradeStatus.PROPOSED
        for row in to_update
    )
    with transaction.atomic():
        if status_changing:
            snapshot_subject_plan(
                application,
                user,
                trigger=ApplicationSubjectPlanVersion.Trigger.GRADES_PROPOSED,
            )
        for row in to_update:
            row.grade_status = ApplicationSubjectSelection.GradeStatus.PROPOSED
            row.proposed_at = now
            row.proposed_by = user
            row.save(
                update_fields=[
                    "grade_status",
                    "proposed_at",
                    "proposed_by",
                    "updated_at",
                ]
            )
        TimelineEvent.objects.create(
            application=application,
            event_type="subject_grades_proposed",
            description="Student submitted host subject grades for confirmation.",
            created_by=user,
        )
    return len(to_update)


def confirm_subject_grades(application, user, notes: str = "") -> int:
    """Translate proposed host grades, lock them, and regenerate the carta."""
    from grades.services import GradeTranslationService

    assert_gradeable_status(application)
    host_institution = application.host_institution
    if host_institution is None or not host_institution.grade_scale_id:
        raise ValueError(
            "Host institution must have a grade scale before grades can be confirmed."
        )
    profile = getattr(application.student, "profile", None)
    home_scale_id = getattr(profile, "grade_scale_id", None) if profile else None
    if not home_scale_id:
        raise ValueError(
            "Student profile must have a grade scale before grades can be confirmed."
        )

    rows = list(
        application.subject_selections.select_related(
            "proposed_host_grade", "host_subject"
        )
    )
    if not rows:
        raise ValueError("This application has no subject selections to confirm.")

    missing = [row for row in rows if not row.proposed_host_grade_id]
    if missing:
        raise ValueError(
            "Every subject selection must have a proposed host grade before confirmation."
        )
    not_proposed = [
        row
        for row in rows
        if row.grade_status != ApplicationSubjectSelection.GradeStatus.PROPOSED
    ]
    if not_proposed:
        raise ValueError(
            "Every subject selection must be submitted for confirmation before "
            "grades can be confirmed."
        )
    wrong_scale = [
        row
        for row in rows
        if row.proposed_host_grade.grade_scale_id != host_institution.grade_scale_id
    ]
    if wrong_scale:
        raise ValueError(
            "Proposed grades must belong to the host institution grade scale."
        )

    now = timezone.now()
    notes = notes or ""
    status_changing = any(
        row.grade_status != ApplicationSubjectSelection.GradeStatus.CONFIRMED
        for row in rows
    )

    with transaction.atomic():
        if status_changing:
            snapshot_subject_plan(
                application,
                user,
                trigger=ApplicationSubjectPlanVersion.Trigger.GRADES_CONFIRMED,
            )
        for row in rows:
            try:
                home_grade = GradeTranslationService.translate_grade(
                    row.proposed_host_grade_id,
                    home_scale_id,
                    fallback_to_gpa=True,
                )
            except ObjectDoesNotExist as exc:
                raise ValueError(str(exc)) from exc
            if home_grade is None:
                label = row.host_course_display
                raise ValueError(
                    f"No grade translation mapping for '{label}'. "
                    "Add a translation or ensure both scales have GPA equivalents."
                )
            row.confirmed_host_grade = row.proposed_host_grade
            row.home_grade = home_grade
            row.grade_status = ApplicationSubjectSelection.GradeStatus.CONFIRMED
            row.confirmed_at = now
            row.confirmed_by = user
            row.confirmation_notes = notes
            row.save(
                update_fields=[
                    "confirmed_host_grade",
                    "home_grade",
                    "grade_status",
                    "confirmed_at",
                    "confirmed_by",
                    "confirmation_notes",
                    "updated_at",
                ]
            )
        TimelineEvent.objects.create(
            application=application,
            event_type="subject_grades_confirmed",
            description="Coordinator confirmed host subject grades and locked translations.",
            created_by=user,
        )
        persist_carta_homologacion(application, user)
    return len(rows)


def reject_subject_grades(application, user, notes: str = "") -> int:
    """Reopen subject mappings/grades for student edits."""
    notes = notes or ""
    now = timezone.now()
    rows = list(application.subject_selections.all())
    if not rows:
        raise ValueError("This application has no subject selections to reject.")

    status_changing = any(
        row.grade_status != ApplicationSubjectSelection.GradeStatus.REJECTED
        for row in rows
    )
    with transaction.atomic():
        if status_changing:
            snapshot_subject_plan(
                application,
                user,
                trigger=ApplicationSubjectPlanVersion.Trigger.GRADES_REJECTED,
            )
        for row in rows:
            row.grade_status = ApplicationSubjectSelection.GradeStatus.REJECTED
            row.confirmed_host_grade = None
            row.home_grade = None
            row.confirmed_at = now
            row.confirmed_by = user
            row.confirmation_notes = notes
            row.save(
                update_fields=[
                    "grade_status",
                    "confirmed_host_grade",
                    "home_grade",
                    "confirmed_at",
                    "confirmed_by",
                    "confirmation_notes",
                    "updated_at",
                ]
            )
        TimelineEvent.objects.create(
            application=application,
            event_type="subject_grades_rejected",
            description=notes or "Coordinator rejected host subject grades.",
            created_by=user,
        )
    return len(rows)
