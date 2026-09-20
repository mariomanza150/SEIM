"""Official CGRI sample binaries under SAMPLES/ and their DocumentType / Wagtail keys."""

from __future__ import annotations

from pathlib import Path

from django.conf import settings

# Stable resource keys (also used as Wagtail tag cgri-key:<key>).
CGRI_SAMPLE_SPECS: tuple[dict[str, str | None], ...] = (
    {
        "key": "convocatoria_entrante",
        "filename": "ConvocatoriaMIEntrante.pdf",
        "title": "Convocatoria Movilidad Entrante",
        "document_type_slug": None,
    },
    {
        "key": "convocatoria_saliente",
        "filename": "ConvocatoriaMISaliente.pdf",
        "title": "Convocatoria Movilidad Saliente",
        "document_type_slug": None,
    },
    {
        # Blank AF form for incoming students — CMS/Wagtail only (not a SEIM DocumentType).
        "key": "solicitud_participacion_entrante",
        "filename": "AF_Solicitud de Participacion.pdf",
        "title": "Solicitud de Participación (Entrante)",
        "document_type_slug": None,
    },
    {
        # Official blank FS-SP binary kept in Wagtail for reference / remote fallback.
        # Outgoing applications use system-generated PDFs (slug solicitud_participacion);
        # do not attach this blank file as DocumentType.template_file.
        "key": "solicitud_participacion_saliente",
        "filename": "FS-SP Solicitud de Participacion Saliente.pdf",
        "title": "Solicitud de Participación (Saliente)",
        "document_type_slug": None,
    },
    {
        "key": "lineamientos",
        "filename": "FS-LD Lineamientos y disposiciones.pdf",
        "title": "Lineamientos y Disposiciones",
        "document_type_slug": "reglamento_movilidad",
    },
    {
        "key": "carta_compromiso",
        "filename": "FS-CC Carta Compromiso.docx",
        "title": "Carta Compromiso",
        "document_type_slug": "carta_compromiso",
    },
    {
        "key": "carta_retorno",
        "filename": "FS-PR Carta Compromiso de Adhesion al Programa de Retorno.docx",
        "title": "Carta Compromiso Programa de Retorno",
        "document_type_slug": "carta_retorno_programa",
    },
    {
        "key": "carta_postulacion",
        "filename": "FS-CP Carta de Postulacion.docx",
        "title": "Carta de Postulación",
        "document_type_slug": "carta_postulacion",
    },
    {
        # Official blank FS-HM kept in Wagtail for CMS/reference.
        # Applications use system-generated PDFs (slug carta_homologacion);
        # do not attach this blank file as DocumentType.template_file.
        "key": "homologacion",
        "filename": "FS-HM Homologacion de Materias.pdf",
        "title": "Homologación de Materias",
        "document_type_slug": None,
    },
    {
        "key": "universidades_convenio",
        "filename": "UniversidadesPorConvenio.pdf",
        "title": "Universidades por Convenio 2026-2",
        "document_type_slug": None,
    },
    {
        "key": "universidades_conahec",
        "filename": "UniversidadesPorCONAHEC.pdf",
        "title": "Universidades CONAHEC 2026-2",
        "document_type_slug": None,
    },
)

CGRI_KEY_TAG_PREFIX = "cgri-key:"
CGRI_OFFICIAL_TAG = "cgri-official"
CGRI_COLLECTION_NAME = "CGRI Official"

# Stable ASCII download names for official blank Word forms (no mail-merge fields).
OFFICIAL_DOCX_DOWNLOAD_NAMES: dict[str, str] = {
    "carta_compromiso": "FS-CC_Carta_Compromiso.docx",
    "carta_postulacion": "FS-CP_Carta_de_Postulacion.docx",
    "carta_retorno_programa": (
        "FS-PR_Carta_Compromiso_de_Adhesion_al_Programa_de_Retorno.docx"
    ),
}


def samples_dir() -> Path:
    return Path(settings.BASE_DIR) / "SAMPLES"


def key_tag(key: str) -> str:
    return f"{CGRI_KEY_TAG_PREFIX}{key}"


def sample_spec_for_slug(slug: str) -> dict[str, str | None] | None:
    for spec in CGRI_SAMPLE_SPECS:
        if spec.get("document_type_slug") == slug:
            return spec
    return None


def official_template_download_name(slug: str | None) -> str | None:
    """Return the preferred attachment/download filename for a DocumentType slug."""
    if not slug:
        return None
    if slug in OFFICIAL_DOCX_DOWNLOAD_NAMES:
        return OFFICIAL_DOCX_DOWNLOAD_NAMES[slug]
    spec = sample_spec_for_slug(slug)
    if not spec:
        return None
    return str(spec["filename"]).replace(" ", "_")


def official_sample_path(slug: str | None) -> Path | None:
    """Filesystem path to the official SAMPLES binary for ``slug``, if present."""
    if not slug:
        return None
    spec = sample_spec_for_slug(slug)
    if not spec:
        return None
    path = samples_dir() / str(spec["filename"])
    return path if path.is_file() else None
