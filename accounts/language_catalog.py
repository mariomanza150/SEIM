"""Spoken-language catalog seeds and alias-aware matching for eligibility."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from accounts.models import SpokenLanguage

LANGUAGE_SPECS: tuple[dict[str, object], ...] = (
    {
        "name": "English",
        "code": "english",
        "aliases": ["Ingles", "Inglés", "ingles", "inglés", "EN"],
    },
    {
        "name": "Spanish",
        "code": "spanish",
        "aliases": ["Español", "Espanol", "español", "espanol", "ES"],
    },
    {
        "name": "French",
        "code": "french",
        "aliases": ["Francés", "Frances", "frances", "francés", "FR"],
    },
    {
        "name": "German",
        "code": "german",
        "aliases": ["Alemán", "Aleman", "alemán", "aleman", "DE"],
    },
    {
        "name": "Portuguese",
        "code": "portuguese",
        "aliases": ["Portugués", "Portugues", "portugués", "portugues", "PT"],
    },
    {
        "name": "Italian",
        "code": "italian",
        "aliases": ["Italiano", "italiano", "IT"],
    },
)


def _norm(value: str | None) -> str:
    return (value or "").strip().casefold()


def _language_index(
    languages: list | None = None,
) -> dict[str, str]:
    """Map normalized labels (name + aliases) to canonical catalog names."""
    if languages is None:
        from accounts.models import SpokenLanguage

        languages = list(
            SpokenLanguage.objects.filter(is_active=True).values("name", "aliases")
        )

    index: dict[str, str] = {}
    for row in languages:
        canonical = (row.get("name") or "").strip()
        if not canonical:
            continue
        index[_norm(canonical)] = canonical
        for alias in row.get("aliases") or []:
            alias_text = str(alias or "").strip()
            if alias_text:
                index[_norm(alias_text)] = canonical
    return index


def seed_spoken_languages(*, spoken_language_model=None) -> list:
    """Ensure default spoken-language catalog rows exist."""
    if spoken_language_model is None:
        from accounts.models import SpokenLanguage

        spoken_language_model = SpokenLanguage

    rows: list = []
    for ordering, spec in enumerate(LANGUAGE_SPECS):
        language, _ = spoken_language_model.objects.update_or_create(
            name=spec["name"],
            defaults={
                "code": spec["code"],
                "aliases": list(spec.get("aliases") or []),
                "is_active": True,
                "ordering": ordering,
            },
        )
        rows.append(language)
    return rows


def resolve_spoken_language(raw: str | None) -> SpokenLanguage | None:
    """Return the catalog row for a free-text language label, if recognized."""
    canonical = canonical_language_name(raw)
    if not canonical:
        return None
    from accounts.models import SpokenLanguage

    return SpokenLanguage.objects.filter(name=canonical, is_active=True).first()


def canonical_language_name(raw: str | None) -> str | None:
    """Resolve any catalog name or alias to the canonical spoken-language name."""
    text = (raw or "").strip()
    if not text:
        return None
    return _language_index().get(_norm(text))


def languages_match(student: str | None, required: str | None) -> bool:
    """True when both labels refer to the same catalog language (or required is empty)."""
    if not (required or "").strip():
        return True
    student_canonical = canonical_language_name(student)
    required_canonical = canonical_language_name(required)
    if student_canonical and required_canonical:
        return student_canonical == required_canonical
    return _norm(student) == _norm(required)


def canonicalize_additional_languages(rows: list | None) -> list[dict[str, str]]:
    """Normalize additional-language names to catalog canonical labels."""
    cleaned: list[dict[str, str]] = []
    for item in rows or []:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        if not name:
            continue
        canonical = canonical_language_name(name) or name
        level = str(item.get("level", "")).strip() or ""
        cleaned.append({"name": canonical, "level": level})
    return cleaned
