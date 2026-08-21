"""Seed helpers for student profile School / Program / Bank catalogs."""

from __future__ import annotations

from typing import Any

from accounts.uadec_catalog_data import UADEC_CATALOG

BANK_SPECS: tuple[tuple[str, str], ...] = (
    ("BBVA", "bbva"),
    ("Banorte", "banorte"),
    ("Santander", "santander"),
    ("Citibanamex", "citibanamex"),
    ("HSBC", "hsbc"),
)

# Legacy flat specs used when SchoolFaculty has no unidad FK (historical migrations).
LEGACY_SCHOOL_SPECS: tuple[dict[str, Any], ...] = (
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


def _model_has_field(model, field_name: str) -> bool:
    try:
        model._meta.get_field(field_name)
    except Exception:
        return False
    return True


def _seed_banks(bank_model) -> list:
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
    return banks


def _seed_legacy_schools(school_model, program_model) -> tuple[list, list]:
    schools: list = []
    programs: list = []
    for ordering, spec in enumerate(LEGACY_SCHOOL_SPECS):
        defaults = {
            "code": spec["code"],
            "is_active": True,
            "ordering": ordering,
        }
        school, _ = school_model.objects.update_or_create(
            name=spec["name"],
            defaults=defaults,
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
    return schools, programs


def seed_profile_catalogs(
    *,
    school_model=None,
    program_model=None,
    bank_model=None,
    unidad_model=None,
):
    """
    Ensure School/Program/Bank catalog rows exist (update_or_create by name).

    Optional model classes allow migrations to pass historical models.
    Returns (schools, programs, banks).
    """
    if school_model is None or program_model is None or bank_model is None:
        from accounts.models import BankInstitution, HomeAcademicProgram, SchoolFaculty, Unidad

        school_model = school_model or SchoolFaculty
        program_model = program_model or HomeAcademicProgram
        bank_model = bank_model or BankInstitution
        unidad_model = unidad_model or Unidad

    if not _model_has_field(school_model, "unidad") or unidad_model is None:
        schools, programs = _seed_legacy_schools(school_model, program_model)
        return schools, programs, _seed_banks(bank_model)

    schools: list = []
    programs: list = []
    global_order = 0
    for unidad_name, faculty_specs in UADEC_CATALOG.items():
        unidad, _ = unidad_model.objects.get_or_create(
            name=unidad_name,
            defaults={
                "code": unidad_name.lower(),
                "is_active": True,
                "ordering": list(UADEC_CATALOG.keys()).index(unidad_name),
            },
        )
        for spec in faculty_specs:
            school, _ = school_model.objects.update_or_create(
                unidad=unidad,
                name=spec["name"],
                defaults={
                    "code": spec["code"],
                    "is_active": True,
                    "ordering": global_order,
                },
            )
            global_order += 1
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

    if unidad_model is not None and school_model is not None:
        for unidad in unidad_model.objects.filter(is_active=True):
            has_schools = school_model.objects.filter(
                unidad_id=unidad.id, is_active=True
            ).exists()
            if not has_schools:
                unidad.is_active = False
                unidad.save(update_fields=["is_active"])

    return schools, programs, _seed_banks(bank_model)


# Legacy alias kept for tests referencing SCHOOL_SPECS count expectations.
SCHOOL_SPECS: tuple[dict[str, Any], ...] = tuple(
    spec for specs in UADEC_CATALOG.values() for spec in specs
)
