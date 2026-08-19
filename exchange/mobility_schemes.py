"""Seed helpers for the two international mobility scheme Programs."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from django.utils import timezone

from exchange.models import Program

MOBILITY_SCHEME_HISPANA = "Movilidad Internacional Habla Hispana"
MOBILITY_SCHEME_INGLESa = "Movilidad Internacional Habla Inglesa"
LEGACY_SCHEME_INGLESa = "Movilidad Internacional"
LEGACY_SCHEME_NACIONAL = "Movilidad Nacional"

MOBILITY_SCHEME_SPECS = (
    {
        "name": MOBILITY_SCHEME_HISPANA,
        "description": (
            "Esquema de movilidad internacional en países de habla hispana. "
            "Promedio mínimo 90 (escala 0–100), TOEFL mínimo 450."
        ),
        "min_gpa": 3.6,
        "min_toefl_score": 450,
        "min_semester": 4,
        "min_credits_approved_percent": Decimal("50.00"),
        "required_language": "Spanish",
        "min_language_level": "B1",
    },
    {
        "name": MOBILITY_SCHEME_INGLESa,
        "description": (
            "Esquema de movilidad internacional en destinos de lengua extranjera. "
            "Promedio mínimo 85 (escala 0–100), TOEFL mínimo 550."
        ),
        "min_gpa": 3.4,
        "min_toefl_score": 550,
        "min_semester": 4,
        "min_credits_approved_percent": Decimal("50.00"),
        "required_language": "English",
        "min_language_level": "B2",
    },
)


def seed_mobility_schemes(*, today: date | None = None) -> list[Program]:
    """
    Ensure the two international mobility scheme programs exist (get_or_create by name).

    Deactivates legacy Nacional scheme and renames legacy Internacional when present.
    Returns the Program instances (created or existing).
    """
    today = today or timezone.localdate()
    start = today + timedelta(days=90)
    end = start + timedelta(days=180)
    open_date = today
    deadline = start - timedelta(days=30)

    # Deactivate removed scheme.
    Program.objects.filter(name=LEGACY_SCHEME_NACIONAL).update(is_active=False)

    # Rename legacy English scheme if it exists under the old name.
    legacy = Program.objects.filter(name=LEGACY_SCHEME_INGLESa).first()
    if legacy and not Program.objects.filter(name=MOBILITY_SCHEME_INGLESa).exists():
        legacy.name = MOBILITY_SCHEME_INGLESa
        legacy.save(update_fields=["name", "updated_at"])

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
                "min_toefl_score": spec["min_toefl_score"],
                "min_semester": spec["min_semester"],
                "min_credits_approved_percent": spec["min_credits_approved_percent"],
                "required_language": spec["required_language"],
                "min_language_level": spec["min_language_level"],
            },
        )
        if not created:
            update_fields: list[str] = []
            for field in (
                "description",
                "min_gpa",
                "min_toefl_score",
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
