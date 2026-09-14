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
        "key": "solicitud_participacion_entrante",
        "filename": "AF_Solicitud de Participacion.pdf",
        "title": "Solicitud de Participación (Entrante)",
        "document_type_slug": None,
    },
    {
        "key": "solicitud_participacion_saliente",
        "filename": "FS-SP Solicitud de Participacion Saliente.pdf",
        "title": "Solicitud de Participación (Saliente)",
        "document_type_slug": "solicitud_participacion",
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
        "key": "homologacion",
        "filename": "FS-HM Homologacion de Materias.pdf",
        "title": "Homologación de Materias",
        "document_type_slug": "carta_homologacion",
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


def samples_dir() -> Path:
    return Path(settings.BASE_DIR) / "SAMPLES"


def key_tag(key: str) -> str:
    return f"{CGRI_KEY_TAG_PREFIX}{key}"
