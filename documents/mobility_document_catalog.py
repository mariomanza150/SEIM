"""
Mexican mobility document catalog seeds (Phase 4).

Maps legacy English DocumentType.name seeds to Spanish display names + stable slugs.
"""

from __future__ import annotations

from documents.models import DocumentType
from exchange.models import Program, ProgramDocumentRequirement

# Legacy English seed name → new slug (overlapping types are renamed in place).
LEGACY_NAME_TO_SLUG = {
    "transcript": "kardex_oficial",
    "passport": "pasaporte_vigente",
    "recommendation": "cartas_recomendacion",
    "language_certificate": "constancia_idioma",
    "cv": "cv_actualizado",
}

MOBILITY_DOCUMENT_TYPES = (
    {
        "slug": "solicitud_participacion",
        "name": "Solicitud de Participación",
        "description": "Formato de solicitud de participación en movilidad (generado por el sistema).",
        "submission_mode": DocumentType.SubmissionMode.SYSTEM_GENERATED,
        "instructions": (
            "Descargue el PDF prellenado, fírmelo y súbalo escaneado en formato PDF."
        ),
        "accepted_extensions": "pdf",
    },
    {
        "slug": "pasaporte_vigente",
        "name": "Pasaporte Vigente",
        "description": "Pasaporte vigente (páginas de datos).",
        "submission_mode": DocumentType.SubmissionMode.UPLOAD,
        "accepted_extensions": "pdf,jpg,jpeg,png",
        "legacy_names": ("passport",),
    },
    {
        "slug": "carta_homologacion",
        "name": "Carta de Homologación",
        "description": "Carta de homologación de asignaturas.",
        "submission_mode": DocumentType.SubmissionMode.SYSTEM_GENERATED,
        "instructions": (
            "Genere o complete la carta de homologación según las asignaturas seleccionadas, "
            "fórmela y súbala firmada."
        ),
        "accepted_extensions": "pdf",
    },
    {
        "slug": "kardex_oficial",
        "name": "Kardex Oficial",
        "description": "Kardex / historial académico oficial.",
        "submission_mode": DocumentType.SubmissionMode.UPLOAD,
        "accepted_extensions": "pdf",
        "legacy_names": ("transcript",),
    },
    {
        "slug": "carta_postulacion",
        "name": "Carta de Postulación",
        "description": "Carta de postulación emitida por la facultad (instrucciones).",
        "submission_mode": DocumentType.SubmissionMode.INSTRUCTIONS_ONLY,
        "instructions": (
            "Solicite la carta de postulación a la dirección de su facultad. "
            "No se carga en esta plataforma; conserve el original para trámites externos."
        ),
    },
    {
        "slug": "seguro_gastos_medicos",
        "name": "Seguro de gastos médicos mayores",
        "description": "Póliza de seguro de gastos médicos mayores con cobertura internacional.",
        "submission_mode": DocumentType.SubmissionMode.UPLOAD,
        "accepted_extensions": "pdf",
    },
    {
        "slug": "credencial_estudiante",
        "name": "Credencial de estudiante",
        "description": "Credencial vigente de estudiante.",
        "submission_mode": DocumentType.SubmissionMode.UPLOAD,
        "accepted_extensions": "pdf,jpg,jpeg,png",
    },
    {
        "slug": "caratula_cuenta_santander",
        "name": "Carátula cuenta Bancaria Santander",
        "description": "Carátula de cuenta bancaria Santander a nombre del estudiante.",
        "submission_mode": DocumentType.SubmissionMode.UPLOAD,
        "accepted_extensions": "pdf,jpg,jpeg,png",
    },
    {
        "slug": "carta_aceptacion",
        "name": "Carta de Aceptación",
        "description": "Carta de aceptación de la institución anfitriona (cuando aplique).",
        "submission_mode": DocumentType.SubmissionMode.UPLOAD,
        "accepted_extensions": "pdf",
    },
    {
        "slug": "carta_exposicion_motivos",
        "name": "Carta de Exposición de motivos",
        "description": "Carta de exposición de motivos del estudiante.",
        "submission_mode": DocumentType.SubmissionMode.UPLOAD,
        "accepted_extensions": "pdf",
    },
    {
        "slug": "carta_compromiso",
        "name": "Carta compromiso",
        "description": "Carta compromiso firmada por el estudiante.",
        "submission_mode": DocumentType.SubmissionMode.TEMPLATE_DOWNLOAD,
        "instructions": "Descargue la plantilla, fírmela y súbala en PDF.",
        "accepted_extensions": "pdf",
    },
    {
        "slug": "reglamento_movilidad",
        "name": "Reglamento de Movilidad",
        "description": "Acuse de conocimiento del reglamento de movilidad.",
        "submission_mode": DocumentType.SubmissionMode.INSTRUCTIONS_ONLY,
        "instructions": (
            "Lea el Reglamento de Movilidad institucional. "
            "Su participación implica aceptación de las disposiciones vigentes."
        ),
    },
    {
        # Stable legacy slug; display name is branded at seed time.
        "slug": "inscripcion_uadec",
        "name": "Inscripción {short_name}",
        "description": "Comprobante de inscripción vigente en {short_name}.",
        "submission_mode": DocumentType.SubmissionMode.UPLOAD,
        "accepted_extensions": "pdf",
    },
    {
        "slug": "cartas_recomendacion",
        "name": "2 Cartas de Recomendación",
        "description": "Dos cartas de recomendación académicas.",
        "submission_mode": DocumentType.SubmissionMode.UPLOAD,
        "allows_multiple": True,
        "accepted_extensions": "pdf",
        "instructions": "Suba ambas cartas (puede cargar más de un archivo).",
        "legacy_names": ("recommendation",),
    },
    {
        "slug": "cv_actualizado",
        "name": "CV Actualizado",
        "description": "Curriculum vitae actualizado.",
        "submission_mode": DocumentType.SubmissionMode.UPLOAD,
        "accepted_extensions": "pdf",
        "legacy_names": ("cv",),
    },
    {
        "slug": "ine_credencial_elector",
        "name": "INE/Credencial de Elector",
        "description": "Identificación oficial (INE) por ambos lados.",
        "submission_mode": DocumentType.SubmissionMode.UPLOAD,
        "accepted_extensions": "pdf,jpg,jpeg,png",
    },
    {
        "slug": "constancia_idioma",
        "name": "Constancia de Idioma",
        "description": "Constancia o certificado de dominio de idioma.",
        "submission_mode": DocumentType.SubmissionMode.UPLOAD,
        "accepted_extensions": "pdf",
        "legacy_names": ("language_certificate",),
    },
    {
        "slug": "carta_beca",
        "name": "Carta Beca",
        "description": "Carta de beca (solo cuando aplique apoyo económico).",
        "submission_mode": DocumentType.SubmissionMode.UPLOAD,
        "accepted_extensions": "pdf",
    },
    {
        "slug": "oficio_asignacion_beca",
        "name": "Oficio de Asignación de Beca",
        "description": "Oficio de asignación de beca.",
        "submission_mode": DocumentType.SubmissionMode.UPLOAD,
        "accepted_extensions": "pdf",
    },
    {
        "slug": "recibo_beca",
        "name": "Recibo de Beca",
        "description": "Recibo o comprobante de beca.",
        "submission_mode": DocumentType.SubmissionMode.UPLOAD,
        "accepted_extensions": "pdf",
    },
    {
        "slug": "comprobante_no_adeudo",
        "name": "Comprobante de No adeudo (SIIA)",
        "description": "Comprobante de no adeudo emitido por SIIA.",
        "submission_mode": DocumentType.SubmissionMode.UPLOAD,
        "accepted_extensions": "pdf",
    },
)

# Core required docs for all three mobility schemes (sort_order, slug).
CORE_SCHEME_REQUIREMENTS = (
    (10, "solicitud_participacion"),
    (20, "kardex_oficial"),
    (30, "cv_actualizado"),
    (40, "carta_exposicion_motivos"),
    (50, "cartas_recomendacion"),
    (60, "credencial_estudiante"),
    (70, "ine_credencial_elector"),
    (80, "inscripcion_uadec"),
    (90, "comprobante_no_adeudo"),
    (100, "carta_compromiso"),
    (110, "reglamento_movilidad"),
    (120, "carta_postulacion"),
)

# Additional for international schemes.
INTERNATIONAL_EXTRA = (
    (130, "pasaporte_vigente"),
    (140, "constancia_idioma"),
    (150, "seguro_gastos_medicos"),
    (160, "carta_homologacion"),
    (170, "caratula_cuenta_santander"),
)

# Optional scholarship docs (international schemes only).
SCHOLARSHIP_OPTIONAL = (
    (200, "carta_beca"),
    (210, "oficio_asignacion_beca"),
    (220, "recibo_beca"),
)

# Nacional-only extras (domestic ID already covered; homologación optional).
NACIONAL_EXTRA = (
    (150, "carta_homologacion"),
    (160, "caratula_cuenta_santander"),
    (170, "carta_aceptacion"),
)


def _branded_document_spec(spec: dict) -> dict:
    """Resolve {short_name} placeholders from INSTITUTION_SHORT_NAME."""
    from django.conf import settings

    short_name = getattr(settings, "INSTITUTION_SHORT_NAME", "UAdeC")
    branded = dict(spec)
    for key in ("name", "description", "instructions"):
        value = branded.get(key)
        if isinstance(value, str):
            branded[key] = value.format(short_name=short_name)
    return branded


def seed_mobility_document_types() -> list[DocumentType]:
    """Create/update Mexican mobility DocumentType rows; map legacy English names."""
    by_slug: dict[str, DocumentType] = {}
    for spec in MOBILITY_DOCUMENT_TYPES:
        spec = _branded_document_spec(spec)
        slug = spec["slug"]
        legacy_names = spec.get("legacy_names") or ()
        existing = DocumentType.objects.filter(slug=slug).first()
        if not existing:
            for legacy in legacy_names:
                existing = DocumentType.objects.filter(
                    name=legacy, slug__isnull=True
                ).first()
                if existing:
                    break
            if not existing:
                for legacy in legacy_names:
                    existing = DocumentType.objects.filter(name=legacy).first()
                    if existing:
                        break

        defaults = {
            "name": spec["name"],
            "slug": slug,
            "description": spec.get("description", ""),
            "submission_mode": spec.get(
                "submission_mode", DocumentType.SubmissionMode.UPLOAD
            ),
            "instructions": spec.get("instructions", ""),
            "faq": spec.get("faq", ""),
            "accepted_extensions": spec.get("accepted_extensions", ""),
            "allows_multiple": spec.get("allows_multiple", False),
        }
        if existing:
            for key, value in defaults.items():
                setattr(existing, key, value)
            existing.save()
            dt = existing
        else:
            dt, _ = DocumentType.objects.update_or_create(slug=slug, defaults=defaults)
        by_slug[slug] = dt
    return list(by_slug.values())


def assign_scheme_document_requirements(
    program_model=None,
    requirement_model=None,
    document_type_model=None,
) -> int:
    """
    Attach ProgramDocumentRequirement rows to mobility schemes.

    Scholarship docs are optional and only on international schemes.
    Returns number of requirement rows ensured.

    Optional model args exist so migrations can pass historical models whose
    columns match the schema at that point (live models may already include
    later fields such as deadline_days_after_program_start).
    """
    program_cls = program_model or Program
    requirement_cls = requirement_model or ProgramDocumentRequirement
    document_type_cls = document_type_model or DocumentType

    seed_mobility_document_types()
    schemes = {
        "Movilidad Internacional Habla Hispana": "intl_es",
        "Movilidad Internacional Habla Inglesa": "intl",
        "Movilidad Internacional": "intl",
        "Movilidad Maestría": "maestria",
    }
    created = 0
    for program_name, kind in schemes.items():
        program = program_cls.objects.filter(name=program_name).first()
        if not program:
            continue
        rows: list[tuple[int, str, bool]] = [
            (order, slug, True) for order, slug in CORE_SCHEME_REQUIREMENTS
        ]
        if kind in ("intl_es", "intl", "maestria"):
            rows.extend((order, slug, True) for order, slug in INTERNATIONAL_EXTRA)
            rows.extend((order, slug, False) for order, slug in SCHOLARSHIP_OPTIONAL)

        for sort_order, slug, is_required in rows:
            dt = document_type_cls.objects.filter(slug=slug).first()
            if not dt:
                continue
            _, was_created = requirement_cls.objects.update_or_create(
                program=program,
                document_type=dt,
                defaults={
                    "is_required": is_required,
                    "sort_order": sort_order,
                    "deadline_days_before_program_deadline": 0 if is_required else None,
                },
            )
            if was_created:
                created += 1
    return created
