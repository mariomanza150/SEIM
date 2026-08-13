"""Seed helpers for the three mobility scheme Programs (Phase 1)."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from django.utils import timezone

from exchange.models import Program

MOBILITY_SCHEME_SPECS = (
    {
        "name": "Movilidad Nacional",
        "description": (
            "Esquema de movilidad doméstica entre instituciones mexicanas. "
            "Requisitos mínimos configurables por administración."
        ),
        "min_gpa": 3.0,
        "min_semester": 3,
        "min_credits_approved_percent": Decimal("50.00"),
        "required_language": "Spanish",
        "min_language_level": "B1",
    },
    {
        "name": "Movilidad Internacional Habla Hispana",
        "description": (
            "Esquema de movilidad internacional en países de habla hispana. "
            "Requisitos mínimos configurables por administración."
        ),
        "min_gpa": 3.2,
        "min_semester": 4,
        "min_credits_approved_percent": Decimal("60.00"),
        "required_language": "Spanish",
        "min_language_level": "B2",
    },
    {
        "name": "Movilidad Internacional",
        "description": (
            "Esquema de movilidad internacional general (incluye destinos no hispanohablantes). "
            "Requisitos mínimos configurables por administración."
        ),
        "min_gpa": 3.3,
        "min_semester": 4,
        "min_credits_approved_percent": Decimal("60.00"),
        "required_language": "English",
        "min_language_level": "B2",
    },
)


def seed_mobility_schemes(*, today: date | None = None) -> list[Program]:
    """
    Ensure the three mobility scheme programs exist (get_or_create by name).

    Returns the Program instances (created or existing).
    """
    today = today or timezone.localdate()
    start = today + timedelta(days=90)
    end = start + timedelta(days=180)
    open_date = today
    deadline = start - timedelta(days=30)

    programs: list[Program] = []
    for spec in MOBILITY_SCHEME_SPECS:
        program, created = Program.objects.get_or_create(
            name=spec["name"],
            defaults={
                "description": spec["description"],
                "start_date": start,
                "end_date": end,
                "application_open_date": open_date,
                "application_deadline": deadline,
                "is_active": True,
                "recurring": True,
                "min_gpa": spec["min_gpa"],
                "min_semester": spec["min_semester"],
                "min_credits_approved_percent": spec["min_credits_approved_percent"],
                "required_language": spec["required_language"],
                "min_language_level": spec["min_language_level"],
            },
        )
        if not created:
            # Keep windows/dates as configured; refresh eligibility fields for consistency.
            update_fields: list[str] = []
            for field in (
                "description",
                "min_gpa",
                "min_semester",
                "min_credits_approved_percent",
                "required_language",
                "min_language_level",
            ):
                if getattr(program, field) != spec[field]:
                    setattr(program, field, spec[field])
                    update_fields.append(field)
            if not program.is_active:
                program.is_active = True
                update_fields.append("is_active")
            if not program.recurring:
                program.recurring = True
                update_fields.append("recurring")
            if update_fields:
                program.save(update_fields=update_fields)
        programs.append(program)
    return programs
