"""Destination country catalog for admin selectors and partner seeding.

Built from ``accounts/data/geo_countries.json`` (Spanish CLDR names) so admins
can pick any country, e.g. Ecuador or Bolivia. Values are Spanish names, except
legacy CGRI spellings (``EUA``) that existing records already store.
"""

from __future__ import annotations

from functools import lru_cache

from accounts.geo_catalog import _countries, _norm

# Legacy CGRI curated list (kept for reference / ordering of favourites).
CGRI_COUNTRY_NAMES: tuple[str, ...] = (
    "Alemania",
    "Argentina",
    "Brasil",
    "Canadá",
    "Colombia",
    "Corea del Sur",
    "Cuba",
    "Chile",
    "China",
    "España",
    "EUA",
    "Finlandia",
    "Francia",
    "Italia",
    "Panamá",
    "Perú",
    "Taiwán",
)

# Stored values that differ from the geo catalog's Spanish name, by ISO code.
_VALUE_OVERRIDES: dict[str, str] = {"US": "EUA"}

# Extra English / alternate spellings for searchable selectors.
CGRI_COUNTRY_ALIASES: dict[str, tuple[str, ...]] = {
    "Alemania": ("Germany",),
    "Brasil": ("Brazil",),
    "Canadá": ("Canada",),
    "Corea del Sur": ("South Korea", "Korea"),
    "España": ("Spain",),
    "EUA": (
        "Estados Unidos",
        "USA",
        "United States",
        "US",
        "EEUU",
        "U.S.A.",
        "U.S.",
    ),
    "Finlandia": ("Finland",),
    "Francia": ("France",),
    "Italia": ("Italy",),
    "Panamá": ("Panama",),
    "Perú": ("Peru",),
    "Taiwán": ("Taiwan",),
    "República Dominicana": ("Dominican Republic",),
}


@lru_cache(maxsize=1)
def _options() -> tuple[dict, ...]:
    options: list[dict] = []
    for row in _countries():
        value = _VALUE_OVERRIDES.get(row["code"], row["name"])
        aliases: list[str] = []
        for alias in (
            row["name"],
            row.get("name_en"),
            *CGRI_COUNTRY_ALIASES.get(value, ()),
        ):
            if alias and alias != value and alias not in aliases:
                aliases.append(alias)
        entry: dict = {"value": value, "label": value, "code": row["code"]}
        if aliases:
            entry["aliases"] = aliases
        options.append(entry)
    options.sort(key=lambda e: _norm(e["label"]))
    return tuple(options)


def country_options() -> list[dict]:
    """Return read-only country catalog entries for API consumers."""
    return [
        {**e, "aliases": list(e["aliases"])} if "aliases" in e else dict(e)
        for e in _options()
    ]


def resolve_country_option(value: str | None) -> str | None:
    """Return the catalog value matching a name, alias or ISO code (any case/accents)."""
    key = _norm(value)
    if not key:
        return None
    for entry in _options():
        names = [entry["value"], entry["code"], *entry.get("aliases", [])]
        if key in {_norm(n) for n in names}:
            return entry["value"]
    return None
