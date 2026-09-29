"""CGRI partner universities for international mobility schemes."""

from __future__ import annotations

import json
from pathlib import Path

MOBILITY_SCHEME_HISPANA = "Movilidad Internacional Habla Hispana"
MOBILITY_SCHEME_INGLESa = "Movilidad Internacional Habla Inglesa"

SCHEME_CODE_TO_NAME = {
    "hispana": MOBILITY_SCHEME_HISPANA,
    "inglesa": MOBILITY_SCHEME_INGLESa,
}

SPANISH_SPEAKING_COUNTRIES = frozenset(
    {
        "españa",
        "spain",
        "mexico",
        "méxico",
        "colombia",
        "ecuador",
        "argentina",
        "bolivia",
        "chile",
        "peru",
        "perú",
        "costa rica",
        "panama",
        "panamá",
        "uruguay",
        "paraguay",
        "venezuela",
        "guatemala",
        "honduras",
        "nicaragua",
        "el salvador",
        "cuba",
        "dominican republic",
        "república dominicana",
        "puerto rico",
    }
)

CGRI_PARTNER_SPECS: tuple[dict[str, str], ...] = (
    # Habla Hispana — España
    {"scheme": MOBILITY_SCHEME_HISPANA, "country": "España", "name": "Universidad de León"},
    {"scheme": MOBILITY_SCHEME_HISPANA, "country": "España", "name": "Universidad de Cádiz"},
    {"scheme": MOBILITY_SCHEME_HISPANA, "country": "España", "name": "Universidad de Salamanca"},
    {"scheme": MOBILITY_SCHEME_HISPANA, "country": "España", "name": "Universidad Politécnica de Cartagena"},
    {"scheme": MOBILITY_SCHEME_HISPANA, "country": "España", "name": "Universidad Internacional de Cataluña"},
    {"scheme": MOBILITY_SCHEME_HISPANA, "country": "España", "name": "Universidad de Burgos"},
    {"scheme": MOBILITY_SCHEME_HISPANA, "country": "España", "name": "Universidad de Granada"},
    # Habla Hispana — Colombia
    {"scheme": MOBILITY_SCHEME_HISPANA, "country": "Colombia", "name": "Pontificia Universidad Javeriana"},
    {"scheme": MOBILITY_SCHEME_HISPANA, "country": "Colombia", "name": "Universidad de Córdoba"},
    {"scheme": MOBILITY_SCHEME_HISPANA, "country": "Colombia", "name": "Universidad Militar Nueva Granada"},
    # Habla Hispana — Ecuador
    {"scheme": MOBILITY_SCHEME_HISPANA, "country": "Ecuador", "name": "Universidad Internacional del Ecuador"},
    # Habla Inglesa — Italia
    {"scheme": MOBILITY_SCHEME_INGLESa, "country": "Italia", "name": "Università degli Studi di Firenze"},
    {"scheme": MOBILITY_SCHEME_INGLESa, "country": "Italia", "name": "Università degli Studi di Torino"},
    {"scheme": MOBILITY_SCHEME_INGLESa, "country": "Italia", "name": "Università degli Studi di Siena"},
    # Habla Inglesa — Alemania
    {
        "scheme": MOBILITY_SCHEME_INGLESa,
        "country": "Alemania",
        "name": "Duale Hochschule Baden-Württemberg (Stuttgart/Mosbach)",
    },
    # Habla Inglesa — Brasil
    {"scheme": MOBILITY_SCHEME_INGLESa, "country": "Brasil", "name": "Universidade de Ouro Preto"},
    {"scheme": MOBILITY_SCHEME_INGLESa, "country": "Brasil", "name": "Universidade Cruzeiro do Sul (São Paulo)"},
    {"scheme": MOBILITY_SCHEME_INGLESa, "country": "Brasil", "name": "Universidade de Passo Fundo"},
    # Habla Inglesa — China
    {"scheme": MOBILITY_SCHEME_INGLESa, "country": "China", "name": "Beijing Institute of Technology"},
)

PLACEHOLDER_SCHOOL = "Facultad / Escuela general"
PLACEHOLDER_PROGRAM = "Programa académico general"
PLACEHOLDER_SUBJECT = ("GEN101", "Asignatura general de movilidad", "6.00")

_DATA_DIR = Path(__file__).resolve().parent / "data"
_UNIVERSITY_LIST_FILES = (
    "universidades_por_convenio.json",
    "universidades_por_conahec.json",
)


def _resolve_scheme_name(entry: dict) -> str:
    code = (entry.get("scheme") or "").strip().lower()
    if code in SCHEME_CODE_TO_NAME:
        return SCHEME_CODE_TO_NAME[code]
    country = (entry.get("country") or "").strip().lower()
    if country in SPANISH_SPEAKING_COUNTRIES:
        return MOBILITY_SCHEME_HISPANA
    return MOBILITY_SCHEME_INGLESa


def _load_official_university_entries() -> list[dict]:
    rows: list[dict] = []
    for filename in _UNIVERSITY_LIST_FILES:
        path = _DATA_DIR / filename
        if not path.is_file():
            continue
        with path.open(encoding="utf-8") as handle:
            payload = json.load(handle)
        if isinstance(payload, list):
            rows.extend(payload)
    return rows


def seed_cgri_partner_destinations(*, program_model=None, host_models=None) -> dict[str, int]:
    """
    Seed HostInstitution trees and ExchangeAgreement rows for CGRI partners.

    Returns counts: institutions, agreements.
    """
    if program_model is None or host_models is None:
        from exchange.models import (
            ExchangeAgreement,
            HostAcademicProgram,
            HostInstitution,
            HostSchool,
            HostSubject,
            Program,
        )

        program_model = Program
        host_models = {
            "institution": HostInstitution,
            "school": HostSchool,
            "academic": HostAcademicProgram,
            "subject": HostSubject,
            "agreement": ExchangeAgreement,
        }

    HostInstitution = host_models["institution"]
    HostSchool = host_models["school"]
    HostAcademicProgram = host_models["academic"]
    HostSubject = host_models["subject"]
    ExchangeAgreement = host_models["agreement"]

    inst_count = 0
    agr_count = 0
    schemes_seen: set[str] = set()

    for spec in CGRI_PARTNER_SPECS:
        program = program_model.objects.filter(name=spec["scheme"], is_active=True).first()
        if program is None:
            continue

        institution, created = HostInstitution.objects.get_or_create(
            program=program,
            name=spec["name"],
            defaults={"country": spec["country"], "is_active": True},
        )
        if not created and institution.country != spec["country"]:
            institution.country = spec["country"]
            institution.save(update_fields=["country", "updated_at"])

        inst_count += 1

        # Full destination tree for the first partner per scheme (demo/application flows).
        if spec["scheme"] not in schemes_seen:
            schemes_seen.add(spec["scheme"])
            school, _ = HostSchool.objects.get_or_create(
                institution=institution,
                name=PLACEHOLDER_SCHOOL,
                defaults={"is_active": True},
            )
            academic, _ = HostAcademicProgram.objects.get_or_create(
                school=school,
                name=PLACEHOLDER_PROGRAM,
                defaults={"code": "GEN", "is_active": True},
            )
            code, subj_name, credits = PLACEHOLDER_SUBJECT
            HostSubject.objects.get_or_create(
                academic_program=academic,
                code=code,
                defaults={"name": subj_name, "credits": credits, "is_active": True},
            )

        ref = f"CGRI-{spec['country'][:3].upper()}-{institution.name[:20].replace(' ', '')}"
        _, agr_created = ExchangeAgreement.objects.get_or_create(
            partner_institution_name=spec["name"],
            partner_country=spec["country"],
            defaults={
                "title": f"Convenio CGRI — {spec['name']}",
                "internal_reference": ref[:64],
                "agreement_type": "bilateral",
                "status": "active",
                "notes": f"Convenio CGRI — {spec['scheme']}",
            },
        )
        if agr_created:
            agr_count += 1

    list_counts = seed_official_university_lists(
        program_model=program_model,
        host_models=host_models,
    )
    return {
        "institutions": inst_count + list_counts["institutions"],
        "agreements": agr_count + list_counts["agreements"],
    }


def seed_official_university_lists(
    *, program_model=None, host_models=None
) -> dict[str, int]:
    """
    Upsert HostInstitution + ExchangeAgreement from official convenio/CONAHEC JSON lists.

    Institution-only (no placeholder schools). Idempotent by program+name /
    partner_institution_name+partner_country.
    """
    if program_model is None or host_models is None:
        from exchange.models import ExchangeAgreement, HostInstitution, Program

        program_model = Program
        host_models = {
            "institution": HostInstitution,
            "agreement": ExchangeAgreement,
        }

    HostInstitution = host_models["institution"]
    ExchangeAgreement = host_models["agreement"]

    inst_count = 0
    agr_count = 0

    for entry in _load_official_university_entries():
        name = (entry.get("name") or "").strip()
        country = (entry.get("country") or "").strip()
        if not name:
            continue
        scheme_name = _resolve_scheme_name(entry)
        program = program_model.objects.filter(name=scheme_name, is_active=True).first()
        if program is None:
            continue

        institution, created = HostInstitution.objects.get_or_create(
            program=program,
            name=name,
            defaults={"country": country, "is_active": True},
        )
        if not created and country and institution.country != country:
            institution.country = country
            institution.save(update_fields=["country", "updated_at"])
        inst_count += 1

        source = (entry.get("source") or "convenio").strip().lower()
        agreement_type = "conahec" if source == "conahec" else "bilateral"
        title_prefix = "CONAHEC" if agreement_type == "conahec" else "Convenio CGRI"
        ref_prefix = "CONAHEC" if agreement_type == "conahec" else "CGRI"
        ref = f"{ref_prefix}-{(country or 'XX')[:3].upper()}-{name[:20].replace(' ', '')}"

        existing = ExchangeAgreement.objects.filter(
            partner_institution_name=name,
            partner_country=country,
        ).first()
        if existing is None:
            ExchangeAgreement.objects.create(
                partner_institution_name=name,
                partner_country=country,
                title=f"{title_prefix} — {name}",
                internal_reference=ref[:64],
                agreement_type=agreement_type,
                status="active",
                notes=f"{title_prefix} — {scheme_name}",
            )
            agr_count += 1

    return {"institutions": inst_count, "agreements": agr_count}
