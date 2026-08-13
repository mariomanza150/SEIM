"""Seed helpers for student profile School / Program / Bank catalogs."""

from __future__ import annotations

from typing import Any

# Faculties aligned with UANL/UAdeC-style names; Unidades (Sureste / Laguna / Norte)
# are seeded separately in migration 0013.
SCHOOL_SPECS: tuple[dict[str, Any], ...] = (
    {
        "name": "Ingeniería",
        "code": "ingenieria",
        "programs": (
            ("Ingeniería Civil", "ing_civil"),
            ("Ingeniería en Sistemas Computacionales", "ing_sistemas"),
            ("Ingeniería Mecánica", "ing_mecanica"),
            ("Ingeniería Industrial", "ing_industrial"),
        ),
    },
    {
        "name": "Contaduría y Administración",
        "code": "contaduria",
        "programs": (
            ("Contador Público", "contador_publico"),
            ("Licenciatura en Administración", "lic_admin"),
            ("Licenciatura en Negocios Internacionales", "lic_negocios"),
        ),
    },
    {
        "name": "Derecho",
        "code": "derecho",
        "programs": (
            ("Licenciatura en Derecho", "lic_derecho"),
            ("Maestría en Derecho", "mae_derecho"),
        ),
    },
    {
        "name": "Medicina",
        "code": "medicina",
        "programs": (
            ("Médico Cirujano", "medico_cirujano"),
            ("Licenciatura en Enfermería", "lic_enfermeria"),
        ),
    },
)

BANK_SPECS: tuple[tuple[str, str], ...] = (
    ("BBVA", "bbva"),
    ("Banorte", "banorte"),
    ("Santander", "santander"),
    ("Citibanamex", "citibanamex"),
    ("HSBC", "hsbc"),
)


def seed_profile_catalogs(
    *,
    school_model=None,
    program_model=None,
    bank_model=None,
):
    """
    Ensure School/Program/Bank catalog rows exist (update_or_create by name).

    Optional model classes allow migrations to pass historical models.
    Returns (schools, programs, banks).
    """
    if school_model is None or program_model is None or bank_model is None:
        from accounts.models import BankInstitution, HomeAcademicProgram, SchoolFaculty

        school_model = school_model or SchoolFaculty
        program_model = program_model or HomeAcademicProgram
        bank_model = bank_model or BankInstitution

    schools: list = []
    programs: list = []
    for ordering, spec in enumerate(SCHOOL_SPECS):
        school, _ = school_model.objects.update_or_create(
            name=spec["name"],
            defaults={
                "code": spec["code"],
                "is_active": True,
                "ordering": ordering,
            },
        )
        schools.append(school)
        for prog_ordering, (prog_name, prog_code) in enumerate(spec["programs"]):
            program, _ = program_model.objects.update_or_create(
                name=prog_name,
                school=school,
                defaults={
                    "code": prog_code,
                    "is_active": True,
                    "ordering": prog_ordering,
                },
            )
            programs.append(program)

    banks: list = []
    for ordering, (name, code) in enumerate(BANK_SPECS):
        bank, _ = bank_model.objects.update_or_create(
            name=name,
            defaults={
                "code": code,
                "is_active": True,
                "ordering": ordering,
            },
        )
        banks.append(bank)

    return schools, programs, banks
