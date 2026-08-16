"""Institution branding helpers. UAdeC is the packaged default theme."""

from __future__ import annotations

import json
import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any

DEFAULT_SLUG = "uadec"

DEFAULT_INSTITUTION: dict[str, str] = {
    "INSTITUTION_SLUG": DEFAULT_SLUG,
    "INSTITUTION_NAME": "Universidad Autónoma de Coahuila",
    "INSTITUTION_SHORT_NAME": "UAdeC",
    "INSTITUTION_TAGLINE": "Intercambio Académico",
    "INSTITUTION_DEPARTMENT": "Dirección de Intercambio Académico",
    "INSTITUTION_LOCATION": "Saltillo, Coahuila, México",
    "INSTITUTION_WEBSITE": "https://www.uadec.mx/",
    "INSTITUTION_EMAIL": "intercambio@uadec.edu.mx",
    "INSTITUTION_PHONE": "+52 (844) 412-8800 ext. 2345",
    "INSTITUTION_ADDRESS": (
        "Boulevard V. Carranza y González Lobo s/n<br>"
        "Col. República Oriente<br>Saltillo, Coahuila, México<br>C.P. 25280"
    ),
    "INSTITUTION_LOGO_URL": "",
    "INSTITUTION_NAV_BRAND": "",
    "INSTITUTION_SOCIAL_FACEBOOK": "https://facebook.com/uadec",
    "INSTITUTION_SOCIAL_TWITTER": "https://twitter.com/uadec",
    "INSTITUTION_SOCIAL_INSTAGRAM": "https://instagram.com/uadec",
    "INSTITUTION_THEME_CSS": "uadec/theme.css",
    "BRAND_PRIMARY": "#2E5090",
    "BRAND_PRIMARY_LIGHT": "#3B5FA5",
    "BRAND_PRIMARY_DARK": "#1E3A5F",
    "BRAND_ACCENT": "#C7A162",
    "BRAND_ACCENT_LIGHT": "#D4B177",
    "BRAND_ACCENT_DARK": "#B08D4D",
    "BRAND_NAVY": "#1E3A5F",
    "BRAND_ORANGE": "#E67E22",
    "BRAND_TEXT": "#2C3E50",
}

_DEFAULT_ADDRESS = DEFAULT_INSTITUTION["INSTITUTION_ADDRESS"]

_CONFIG_TO_BRAND = {
    "INSTITUTION_SLUG": "slug",
    "INSTITUTION_NAME": "name",
    "INSTITUTION_SHORT_NAME": "short_name",
    "INSTITUTION_TAGLINE": "tagline",
    "INSTITUTION_DEPARTMENT": "department",
    "INSTITUTION_LOCATION": "location",
    "INSTITUTION_WEBSITE": "website",
    "INSTITUTION_EMAIL": "email",
    "INSTITUTION_PHONE": "phone",
    "INSTITUTION_ADDRESS": "address",
    "INSTITUTION_LOGO_URL": "logo_url",
    "INSTITUTION_NAV_BRAND": "nav_brand",
    "INSTITUTION_SOCIAL_FACEBOOK": "social_facebook",
    "INSTITUTION_SOCIAL_TWITTER": "social_twitter",
    "INSTITUTION_SOCIAL_INSTAGRAM": "social_instagram",
    "INSTITUTION_THEME_CSS": "theme_css",
}


def default_pack_config_path(base_dir: Path) -> Path:
    return pack_config_path(base_dir, DEFAULT_SLUG)


def pack_config_path(base_dir: Path, slug: str | None = None) -> Path:
    return Path(base_dir) / "branding" / (slug or DEFAULT_SLUG) / "config.json"


def default_override_config_path(base_dir: Path) -> Path:
    return Path(base_dir) / "branding" / "institution.json"


def default_tenant_config_path(base_dir: Path) -> Path:
    return Path(base_dir) / "tenant_config.json"


def resolve_tenant_config_path(
    base_dir: Path,
    tenant_path: Path | str | None = None,
) -> Path:
    """TENANT_CONFIG_FILE env, explicit path, then repo-root tenant_config.json."""
    if tenant_path:
        path = Path(tenant_path)
        return path if path.is_absolute() else Path(base_dir) / path
    env_path = (os.environ.get("TENANT_CONFIG_FILE") or "").strip()
    if env_path:
        path = Path(env_path)
        return path if path.is_absolute() else Path(base_dir) / path
    return default_tenant_config_path(base_dir)


def _nonempty_mapping(data: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in data.items() if value not in (None, "")}


def resolve_institution_slug(
    base_dir: Path,
    override_path: Path | str | None = None,
    tenant_path: Path | str | None = None,
) -> str:
    """Env INSTITUTION_SLUG, then tenant_config.json, then institution.json, then UAdeC."""
    env_slug = (os.environ.get("INSTITUTION_SLUG") or "").strip()
    if env_slug:
        return env_slug
    tenant_slug = str(
        load_json_object(resolve_tenant_config_path(base_dir, tenant_path)).get(
            "INSTITUTION_SLUG"
        )
        or ""
    ).strip()
    if tenant_slug:
        return tenant_slug
    path = (
        Path(override_path) if override_path else default_override_config_path(base_dir)
    )
    file_slug = str(load_json_object(path).get("INSTITUTION_SLUG") or "").strip()
    return file_slug or DEFAULT_SLUG


def load_json_object(path: Path | str | None) -> dict[str, Any]:
    """Load a JSON object from disk. Missing or invalid files yield {}."""
    if not path:
        return {}
    file_path = Path(path)
    if not file_path.is_file():
        return {}
    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def merge_institution_config(
    base_dir: Path,
    override_path: Path | str | None = None,
    tenant_path: Path | str | None = None,
) -> dict[str, str]:
    """Defaults ← pack ← institution.json ← tenant_config.json.

    Missing overlays are skipped. Env vars still win in Django settings.
    UAdeC remains the packaged fallback when no tenant file is present.
    """
    resolved_tenant = resolve_tenant_config_path(base_dir, tenant_path)
    slug = resolve_institution_slug(base_dir, override_path, resolved_tenant)
    merged = dict(DEFAULT_INSTITUTION)
    merged["INSTITUTION_SLUG"] = slug
    pack_path = pack_config_path(base_dir, slug)
    if not pack_path.is_file() and slug != DEFAULT_SLUG:
        pack_path = default_pack_config_path(base_dir)
    merged.update(_nonempty_mapping(load_json_object(pack_path)))
    overlay = (
        Path(override_path) if override_path else default_override_config_path(base_dir)
    )
    overlay_key = overlay.resolve() if overlay.exists() else overlay
    tenant_key = (
        resolved_tenant.resolve() if resolved_tenant.exists() else resolved_tenant
    )
    if overlay_key != tenant_key:
        merged.update(_nonempty_mapping(load_json_object(overlay)))
    merged.update(_nonempty_mapping(load_json_object(resolved_tenant)))
    if not merged.get("INSTITUTION_SLUG"):
        merged["INSTITUTION_SLUG"] = slug
    return merged


def default_brand() -> dict[str, Any]:
    return brand_from_config(DEFAULT_INSTITUTION)


def brand_from_config(config: Mapping[str, Any]) -> dict[str, Any]:
    brand = {
        field: config.get(key, DEFAULT_INSTITUTION.get(key, ""))
        for key, field in _CONFIG_TO_BRAND.items()
    }
    brand["theme"] = {
        "primary": config.get("BRAND_PRIMARY", DEFAULT_INSTITUTION["BRAND_PRIMARY"]),
        "primary_light": config.get(
            "BRAND_PRIMARY_LIGHT", DEFAULT_INSTITUTION["BRAND_PRIMARY_LIGHT"]
        ),
        "primary_dark": config.get(
            "BRAND_PRIMARY_DARK", DEFAULT_INSTITUTION["BRAND_PRIMARY_DARK"]
        ),
        "accent": config.get("BRAND_ACCENT", DEFAULT_INSTITUTION["BRAND_ACCENT"]),
        "accent_light": config.get(
            "BRAND_ACCENT_LIGHT", DEFAULT_INSTITUTION["BRAND_ACCENT_LIGHT"]
        ),
        "accent_dark": config.get(
            "BRAND_ACCENT_DARK", DEFAULT_INSTITUTION["BRAND_ACCENT_DARK"]
        ),
        "navy": config.get("BRAND_NAVY", DEFAULT_INSTITUTION["BRAND_NAVY"]),
        "orange": config.get("BRAND_ORANGE", DEFAULT_INSTITUTION["BRAND_ORANGE"]),
        "text": config.get("BRAND_TEXT", DEFAULT_INSTITUTION["BRAND_TEXT"]),
    }
    if not brand.get("nav_brand"):
        brand["nav_brand"] = " ".join(
            part for part in (brand.get("short_name"), brand.get("tagline")) if part
        )
    return brand


def brand_from_settings(settings: Any) -> dict[str, Any]:
    """Build the runtime brand dict from Django settings."""
    theme = getattr(settings, "INSTITUTION_THEME", {}) or {}
    short_name = getattr(
        settings,
        "INSTITUTION_SHORT_NAME",
        DEFAULT_INSTITUTION["INSTITUTION_SHORT_NAME"],
    )
    tagline = getattr(settings, "INSTITUTION_TAGLINE", "")
    nav_brand = getattr(settings, "INSTITUTION_NAV_BRAND", "") or " ".join(
        part for part in (short_name, tagline) if part
    )
    return {
        "slug": getattr(
            settings, "INSTITUTION_SLUG", DEFAULT_INSTITUTION["INSTITUTION_SLUG"]
        ),
        "name": getattr(
            settings, "INSTITUTION_NAME", DEFAULT_INSTITUTION["INSTITUTION_NAME"]
        ),
        "short_name": short_name,
        "tagline": tagline,
        "department": getattr(settings, "INSTITUTION_DEPARTMENT", ""),
        "location": getattr(settings, "INSTITUTION_LOCATION", ""),
        "website": getattr(settings, "INSTITUTION_WEBSITE", ""),
        "email": getattr(settings, "INSTITUTION_EMAIL", ""),
        "phone": getattr(settings, "INSTITUTION_PHONE", ""),
        "address": getattr(settings, "INSTITUTION_ADDRESS", ""),
        "logo_url": getattr(settings, "INSTITUTION_LOGO_URL", ""),
        "nav_brand": nav_brand,
        "social_facebook": getattr(settings, "INSTITUTION_SOCIAL_FACEBOOK", ""),
        "social_twitter": getattr(settings, "INSTITUTION_SOCIAL_TWITTER", ""),
        "social_instagram": getattr(settings, "INSTITUTION_SOCIAL_INSTAGRAM", ""),
        "theme_css": getattr(settings, "INSTITUTION_THEME_CSS", "uadec/theme.css"),
        "theme": theme,
    }


def apply_institution_tokens(text: str, brand: Mapping[str, Any]) -> str:
    """Replace packaged UAdeC example tokens with the active institution."""
    if not isinstance(text, str):
        return text
    replacements = (
        (_DEFAULT_ADDRESS, brand.get("address") or ""),
        (
            "Boulevard V. Carranza y González Lobo s/n, Saltillo, Coahuila, México",
            brand.get("address") or "",
        ),
        ("Universidad Autónoma de Coahuila", brand.get("name") or ""),
        (
            "UNIVERSIDAD AUTÓNOMA DE COAHUILA",
            (brand.get("name") or "").upper(),
        ),
        ("intercambio@uadec.edu.mx", brand.get("email") or ""),
        ("relaciones.internacionales@uadec.edu.mx", brand.get("email") or ""),
        ("cgri@uadec.mx", brand.get("email") or ""),
        ("+52 (844) 412-8800 ext. 2345", brand.get("phone") or ""),
        ("Saltillo, Coahuila, México", brand.get("location") or ""),
        ("UAdeC", brand.get("short_name") or ""),
        ("UADEC", brand.get("short_name") or ""),
    )
    for old, new in replacements:
        if old and new and old != new:
            text = text.replace(old, new)
    return text


def apply_institution_tokens_deep(value: Any, brand: Mapping[str, Any]) -> Any:
    if isinstance(value, str):
        return apply_institution_tokens(value, brand)
    if isinstance(value, list):
        return [apply_institution_tokens_deep(item, brand) for item in value]
    if isinstance(value, dict):
        return {
            key: apply_institution_tokens_deep(item, brand)
            for key, item in value.items()
        }
    return value
