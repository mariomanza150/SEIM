"""Rank applications and allocate program seats (nomination matching)."""

from __future__ import annotations

from django.db import transaction
from django.db.models import Case, IntegerField, Value, When
from django.db.models.functions import Coalesce
from django.utils import timezone as dj_tz

from exchange.models import (
    Application,
    ApplicationStatus,
    NominationCycle,
    NominationPartnerAllocation,
    Program,
    TimelineEvent,
)
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
        .select_related("student", "status", "nomination_cycle")
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
        "nomination_cycle_id": str(app.nomination_cycle_id)
        if app.nomination_cycle_id
        else None,
        "partner_nomination_acknowledged_at": (
            app.partner_nomination_acknowledged_at.isoformat()
            if app.partner_nomination_acknowledged_at
            else None
        ),
    }


def active_nomination_cycle(program: Program) -> NominationCycle | None:
    """Prefer an open active cycle; fall back to any active cycle for the program."""
    today = dj_tz.localdate()
    cycles = list(
        NominationCycle.objects.filter(program=program, is_active=True).order_by(
            "-opens_at", "-created_at"
        )
    )
    for cycle in cycles:
        if cycle.is_open_on(today):
            return cycle
    return cycles[0] if cycles else None


def serialize_cycle(cycle: NominationCycle | None) -> dict | None:
    if cycle is None:
        return None
    return {
        "id": str(cycle.id),
        "name": cycle.name,
        "opens_at": cycle.opens_at.isoformat() if cycle.opens_at else None,
        "closes_at": cycle.closes_at.isoformat() if cycle.closes_at else None,
        "seat_quota": cycle.seat_quota,
        "is_active": cycle.is_active,
        "is_open": cycle.is_open_on(),
    }


def serialize_partner_allocations(cycle: NominationCycle | None) -> list[dict]:
    if cycle is None:
        return []
    rows = (
        NominationPartnerAllocation.objects.filter(cycle=cycle)
        .select_related("agreement")
        .order_by("agreement__partner_institution_name")
    )
    return [
        {
            "id": str(row.id),
            "agreement_id": str(row.agreement_id),
            "partner_institution_name": row.agreement.partner_institution_name,
            "agreement_title": row.agreement.title,
            "seat_quota": row.seat_quota,
        }
        for row in rows
    ]


def locked_seat_count(program: Program, cycle: NominationCycle | None = None) -> int:
    """Seats already taken by terminal statuses (not the matching pool)."""
    qs = program.application_set.filter(
        withdrawn=False, status__name__in=LOCKED_STATUSES
    )
    if cycle is not None:
        qs = qs.filter(nomination_cycle=cycle)
    return qs.count()


def match_slot_count(
    program: Program, cycle: NominationCycle | None = None
) -> int | None:
    """Slots Match will allocate. Pool apps (submitted/under_review) do not consume these.

    When an active cycle defines ``seat_quota``, that overrides program enrollment capacity
    for this Match run (multi-cycle windows).
    """
    if cycle is not None and cycle.seat_quota is not None:
        return max(0, cycle.seat_quota - locked_seat_count(program, cycle=cycle))
    if program.enrollment_capacity is None:
        return None
    return max(0, program.enrollment_capacity - locked_seat_count(program))


def program_nomination_payload(program: Program) -> dict:
    cycle = active_nomination_cycle(program)
    rows = [serialize_nomination_row(a) for a in nomination_queryset(program)]
    return {
        "program_id": str(program.id),
        "program_name": program.name,
        "enrollment_capacity": program.enrollment_capacity,
        "slots_remaining": match_slot_count(program, cycle=cycle),
        "active_cycle": serialize_cycle(cycle),
        "partner_allocations": serialize_partner_allocations(cycle),
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


def _set_status(
    application: Application,
    status_name: str,
    user,
    *,
    cycle: NominationCycle | None = None,
) -> bool:
    if application.status.name == status_name:
        return False
    application.status = ApplicationStatus.objects.get(name=status_name)
    update_fields = ["status", "updated_at"]
    if cycle is not None and application.nomination_cycle_id != cycle.id:
        application.nomination_cycle = cycle
        update_fields.append("nomination_cycle")
    application.save(update_fields=update_fields)
    TimelineEvent.objects.create(
        application=application,
        event_type=f"status_{status_name}",
        description=f"Nomination matching set status to {status_name}.",
        created_by=user,
    )
    NotificationService.broadcast_application_sync(
        str(application.id), "application_status_changed"
    )
    try:
        from workflows.runtime import WorkflowRuntimeService

        WorkflowRuntimeService.sync_with_application(application)
    except Exception:
        pass
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
    cycle = active_nomination_cycle(program)
    if cycle is not None and not cycle.is_open_on():
        raise ValueError(
            f"Active nomination cycle '{cycle.name}' is outside its open window."
        )

    pool = list(nomination_queryset(program))
    if cycle is not None and cycle.seat_quota is not None:
        slots = match_slot_count(program, cycle=cycle)
    elif program.enrollment_capacity is None:
        slots = sum(1 for a in pool if a.nomination_rank is not None) or len(pool)
    else:
        slots = match_slot_count(program, cycle=cycle)

    nominated = 0
    waitlisted = 0
    for index, app in enumerate(pool):
        if index < slots:
            if _set_status(app, "nominated", user, cycle=cycle):
                nominated += 1
        elif program.waitlist_when_full:
            if app.status.name == "nominated":
                continue
            if _set_status(app, "waitlist", user, cycle=cycle):
                waitlisted += 1
    payload = program_nomination_payload(program)
    payload["matched"] = {
        "nominated": nominated,
        "waitlisted": waitlisted,
        "slots": slots,
        "cycle_id": str(cycle.id) if cycle else None,
    }
    return payload
