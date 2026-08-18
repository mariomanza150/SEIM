"""Rank applications and allocate program seats (nomination matching)."""

from __future__ import annotations

from django.db import transaction
from django.db.models import Case, IntegerField, Value, When
from django.db.models.functions import Coalesce

from exchange.models import Application, ApplicationStatus, Program, TimelineEvent
from notifications.services import NotificationService

POOL_STATUSES = ("submitted", "under_review", "waitlist", "nominated")
LOCKED_STATUSES = ("approved", "completed", "nominated")


def nomination_queryset(program: Program):
    return (
        Application.objects.filter(
            program=program,
            withdrawn=False,
            status__name__in=POOL_STATUSES,
        )
        .select_related("student", "status")
        .annotate(
            _rank_sort=Coalesce(
                "nomination_rank",
                Value(10**9),
                output_field=IntegerField(),
            ),
            _has_rank=Case(
                When(nomination_rank__isnull=True, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            ),
        )
        .order_by("_has_rank", "_rank_sort", "submitted_at", "created_at")
    )


def serialize_nomination_row(app: Application) -> dict:
    student = app.student
    name = student.get_full_name().strip() or student.username or student.email
    return {
        "id": str(app.id),
        "student_display_name": name,
        "status": app.status.name,
        "nomination_rank": app.nomination_rank,
        "submitted_at": app.submitted_at.isoformat() if app.submitted_at else None,
    }


def locked_seat_count(program: Program) -> int:
    """Seats already taken by terminal statuses (not the matching pool)."""
    return program.application_set.filter(
        withdrawn=False, status__name__in=LOCKED_STATUSES
    ).count()


def match_slot_count(program: Program) -> int | None:
    """Slots Match will allocate. Pool apps (submitted/under_review) do not consume these.

    ``Program.enrollment_slots_remaining`` counts seat-holding statuses including
    under_review, which made DAAD look full (0) while Match still had a slot.
    """
    if program.enrollment_capacity is None:
        return None
    return max(0, program.enrollment_capacity - locked_seat_count(program))


def program_nomination_payload(program: Program) -> dict:
    rows = [serialize_nomination_row(a) for a in nomination_queryset(program)]
    return {
        "program_id": str(program.id),
        "program_name": program.name,
        "enrollment_capacity": program.enrollment_capacity,
        "slots_remaining": match_slot_count(program),
        "applications": rows,
    }


def set_nomination_ranks(program: Program, items: list[dict]) -> dict:
    by_id = {str(row.get("id") or ""): row for row in items if row.get("id")}
    updated = 0
    for app in nomination_queryset(program):
        payload = by_id.get(str(app.id))
        if payload is None:
            continue
        raw = payload.get("rank", payload.get("nomination_rank"))
        rank = None if raw in (None, "") else int(raw)
        if rank is not None and rank < 1:
            raise ValueError("Rank must be a positive integer.")
        if app.nomination_rank != rank:
            app.nomination_rank = rank
            app.save(update_fields=["nomination_rank", "updated_at"])
            updated += 1
    return program_nomination_payload(program) | {"updated": updated}


def _set_status(application: Application, status_name: str, user) -> bool:
    if application.status.name == status_name:
        return False
    application.status = ApplicationStatus.objects.get(name=status_name)
    application.save(update_fields=["status", "updated_at"])
    TimelineEvent.objects.create(
        application=application,
        event_type=f"status_{status_name}",
        description=f"Nomination matching set status to {status_name}.",
        created_by=user,
    )
    NotificationService.broadcast_application_sync(
        str(application.id), "application_status_changed"
    )
    return True


@transaction.atomic
def match_nominations(program: Program, user) -> dict:
    ApplicationStatus.objects.get_or_create(
        name="nominated",
        defaults={"order": 16},
    )
    ApplicationStatus.objects.get_or_create(
        name="waitlist",
        defaults={"order": 15},
    )
    pool = list(nomination_queryset(program))
    if program.enrollment_capacity is None:
        slots = sum(1 for a in pool if a.nomination_rank is not None) or len(pool)
    else:
        slots = match_slot_count(program)

    nominated = 0
    waitlisted = 0
    for index, app in enumerate(pool):
        if index < slots:
            if _set_status(app, "nominated", user):
                nominated += 1
        elif program.waitlist_when_full:
            if app.status.name == "nominated":
                continue
            if _set_status(app, "waitlist", user):
                waitlisted += 1
    payload = program_nomination_payload(program)
    payload["matched"] = {
        "nominated": nominated,
        "waitlisted": waitlisted,
        "slots": slots,
    }
    return payload
