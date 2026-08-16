"""Scholarship award state machine, notifications, and cohort export."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from django.http import HttpResponse
from django.utils import timezone

from exchange.models import ScholarshipAward, ScholarshipDisbursement

ALLOWED_TRANSITIONS = {
    ScholarshipAward.Status.NOMINATED: {
        ScholarshipAward.Status.AWARDED,
        ScholarshipAward.Status.DECLINED,
        ScholarshipAward.Status.WITHDRAWN,
    },
    ScholarshipAward.Status.AWARDED: {
        ScholarshipAward.Status.DISBURSING,
        ScholarshipAward.Status.DECLINED,
        ScholarshipAward.Status.WITHDRAWN,
    },
    ScholarshipAward.Status.DISBURSING: {
        ScholarshipAward.Status.DISBURSED,
        ScholarshipAward.Status.WITHDRAWN,
    },
}

SCHOLARSHIP_EVIDENCE_SLUGS = frozenset(
    {"carta_beca", "oficio_asignacion_beca", "recibo_beca"}
)

_NOTIFY_TITLES = {
    ScholarshipAward.Status.NOMINATED: "Scholarship nomination",
    ScholarshipAward.Status.AWARDED: "Scholarship awarded",
    ScholarshipAward.Status.DECLINED: "Scholarship declined",
    ScholarshipAward.Status.DISBURSING: "Scholarship disbursement started",
    ScholarshipAward.Status.DISBURSED: "Scholarship disbursed",
    ScholarshipAward.Status.WITHDRAWN: "Scholarship nomination withdrawn",
}


def evidence_documents_for_application(application) -> list[dict]:
    """Optional scholarship evidence docs on the application (checklist-style)."""
    slugs = SCHOLARSHIP_EVIDENCE_SLUGS
    rows = []
    docs = getattr(application, "document_set", None)
    if docs is None:
        return rows
    qs = docs.select_related("type").all()
    for doc in qs:
        slug = getattr(doc.type, "slug", None) if doc.type_id else None
        if slug not in slugs:
            continue
        rows.append(
            {
                "id": str(doc.id),
                "type_name": doc.type.name if doc.type_id else "",
                "type_slug": slug,
                "is_valid": bool(doc.is_valid),
                "file": doc.file.url if doc.file else None,
            }
        )
    return rows


def serialize_award(award: ScholarshipAward) -> dict:
    application = award.application
    disbursements = [
        {
            "id": str(d.id),
            "label": d.label,
            "amount": str(d.amount) if d.amount is not None else None,
            "due_date": d.due_date.isoformat() if d.due_date else None,
            "paid_at": d.paid_at.isoformat() if d.paid_at else None,
            "notes": d.notes,
            "status": d.status,
            "sort_order": d.sort_order,
        }
        for d in award.disbursements.all()
    ]
    decided_name = None
    if award.decided_by_id:
        decided_name = (
            award.decided_by.get_full_name().strip() or award.decided_by.username
        )
    return {
        "id": str(award.id),
        "application": str(application.id),
        "status": award.status,
        "amount": str(award.amount) if award.amount is not None else None,
        "currency": award.currency,
        "notes": award.notes,
        "decided_by": str(award.decided_by_id) if award.decided_by_id else None,
        "decided_by_name": decided_name,
        "decided_at": award.decided_at.isoformat() if award.decided_at else None,
        "disbursements": disbursements,
        "evidence_documents": evidence_documents_for_application(application),
        "allowed_transitions": sorted(ALLOWED_TRANSITIONS.get(award.status, set())),
        "updated_at": award.updated_at.isoformat() if award.updated_at else None,
    }


def _parse_amount(raw):
    if raw in (None, ""):
        return None
    try:
        return Decimal(str(raw))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError("Invalid amount.") from exc


def _notify_student(award: ScholarshipAward, previous_status: str | None) -> None:
    if previous_status == award.status:
        return
    student = award.application.student
    program_name = award.application.program.name
    title = _NOTIFY_TITLES.get(award.status, "Scholarship update")
    message = (
        f"Your scholarship status for {program_name} is now "
        f"{award.get_status_display()}."
    )
    if award.amount is not None:
        message += f" Amount: {award.amount} {award.currency}."
    try:
        from notifications.services import NotificationService

        NotificationService.send_notification(
            student,
            title,
            message,
            notification_type="both",
            action_url=f"/seim/applications/{award.application_id}",
            action_text="View application",
            category="success"
            if award.status
            in (
                ScholarshipAward.Status.AWARDED,
                ScholarshipAward.Status.DISBURSED,
            )
            else "info",
            settings_category="applications",
            transactional_route_key="scholarship_award_status",
        )
    except Exception:
        pass


def upsert_award(
    application, actor, *, status_value=None, amount=None, currency=None, notes=None
):
    """Create or update the award on *application*. Staff only."""
    award, created = ScholarshipAward.objects.get_or_create(
        application=application,
        defaults={
            "status": status_value or ScholarshipAward.Status.NOMINATED,
            "decided_by": actor,
            "decided_at": timezone.now(),
        },
    )
    previous = None if created else award.status
    if status_value:
        if not created and status_value != award.status:
            allowed = ALLOWED_TRANSITIONS.get(award.status, set())
            if status_value not in allowed:
                raise ValueError(
                    f"Cannot transition from {award.status} to {status_value}."
                )
        award.status = status_value
        award.decided_by = actor
        award.decided_at = timezone.now()
    if amount is not None:
        award.amount = _parse_amount(amount)
    if currency is not None:
        award.currency = str(currency)[:8] or "MXN"
    if notes is not None:
        award.notes = notes
    award.save()
    _notify_student(award, previous)
    return award


def transition_award(
    award: ScholarshipAward, actor, new_status: str
) -> ScholarshipAward:
    allowed = ALLOWED_TRANSITIONS.get(award.status, set())
    if new_status not in allowed:
        raise ValueError(f"Cannot transition from {award.status} to {new_status}.")
    previous = award.status
    award.status = new_status
    award.decided_by = actor
    award.decided_at = timezone.now()
    award.save(update_fields=["status", "decided_by", "decided_at", "updated_at"])
    _notify_student(award, previous)
    return award


def upsert_disbursement(award: ScholarshipAward, payload: dict, disbursement=None):
    if disbursement is None:
        disbursement = ScholarshipDisbursement(award=award)
    if "label" in payload or disbursement.pk is None:
        label = (payload.get("label") or disbursement.label or "").strip()
        if not label:
            raise ValueError("Disbursement label is required.")
        disbursement.label = label
    if "amount" in payload:
        disbursement.amount = _parse_amount(payload.get("amount"))
    if "due_date" in payload:
        raw = payload.get("due_date")
        disbursement.due_date = raw or None
    if "notes" in payload:
        disbursement.notes = payload.get("notes") or ""
    if "sort_order" in payload and payload.get("sort_order") is not None:
        disbursement.sort_order = int(payload["sort_order"])
    new_status = payload.get("status")
    if new_status:
        if new_status not in ScholarshipDisbursement.Status.values:
            raise ValueError("Invalid disbursement status.")
        disbursement.status = new_status
        if (
            new_status == ScholarshipDisbursement.Status.PAID
            and not disbursement.paid_at
        ):
            disbursement.paid_at = timezone.now()
        if new_status != ScholarshipDisbursement.Status.PAID:
            disbursement.paid_at = (
                None
                if new_status == ScholarshipDisbursement.Status.PENDING
                else disbursement.paid_at
            )
    disbursement.save()
    if award.status == ScholarshipAward.Status.AWARDED and award.disbursements.exists():
        try:
            transition_award(
                award, award.decided_by, ScholarshipAward.Status.DISBURSING
            )
        except ValueError:
            pass
    return disbursement


def awards_export_response(program_id, queryset, program_name=""):
    """CSV export of awards for a program cohort."""
    import csv
    import io

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(
        [
            "application_id",
            "student",
            "email",
            "program",
            "award_status",
            "amount",
            "currency",
            "decided_at",
            "notes",
        ]
    )
    for app in queryset:
        award = getattr(app, "scholarship_award", None)
        if not award:
            continue
        student = app.student
        writer.writerow(
            [
                str(app.id),
                student.get_full_name().strip() or student.username,
                student.email,
                program_name or (app.program.name if app.program_id else ""),
                award.status,
                award.amount if award.amount is not None else "",
                award.currency,
                award.decided_at.isoformat() if award.decided_at else "",
                award.notes,
            ]
        )
    body = buf.getvalue()
    response = HttpResponse(body, content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = (
        f'attachment; filename="scholarship-awards-{program_id}.csv"'
    )
    return response
