# Generated manually for Phase 1 mobility schemes seed

from datetime import timedelta
from decimal import Decimal

from django.db import migrations
from django.utils import timezone


SCHEME_SPECS = (
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


def seed_schemes(apps, schema_editor):
    Program = apps.get_model("exchange", "Program")
    today = timezone.localdate()
    start = today + timedelta(days=90)
    end = start + timedelta(days=180)
    open_date = today
    deadline = start - timedelta(days=30)

    for spec in SCHEME_SPECS:
        Program.objects.get_or_create(
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


def unseed_schemes(apps, schema_editor):
    Program = apps.get_model("exchange", "Program")
    Program.objects.filter(name__in=[spec["name"] for spec in SCHEME_SPECS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("exchange", "0021_mobility_eligibility_phase1"),
    ]

    operations = [
        migrations.RunPython(seed_schemes, unseed_schemes),
    ]
