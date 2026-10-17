"""Static birth-place catalog (Country → State → City) for student profiles.

Countries come from ``data/geo_countries.json`` (CLDR names, Spanish label plus
English alias). States and cities are curated for Mexico only
(``data/geo_mx.json``: all 32 states, every Coahuila municipality and the main
cities elsewhere). Anything not listed is entered freehand on the profile form,
so the stored profile values are plain strings, never foreign keys.
"""

from __future__ import annotations

import json
import unicodedata
from functools import lru_cache
from pathlib import Path

_DATA_DIR = Path(__file__).resolve().parent / "data"


def _norm(value: str | None) -> str:
    text = unicodedata.normalize("NFKD", str(value or "").strip().casefold())
    return "".join(ch for ch in text if not unicodedata.combining(ch))


@lru_cache(maxsize=1)
def _countries() -> tuple[dict, ...]:
    with open(_DATA_DIR / "geo_countries.json", encoding="utf-8") as fh:
        return tuple(json.load(fh))


@lru_cache(maxsize=1)
def _states_by_country() -> dict[str, dict]:
    with open(_DATA_DIR / "geo_mx.json", encoding="utf-8") as fh:
        return {"MX": json.load(fh)}


def resolve_country_code(value: str | None) -> str | None:
    """Return the ISO alpha-2 code for a country code or (es/en) name."""
    key = _norm(value)
    if not key:
        return None
    for row in _countries():
        if key in (_norm(row["code"]), _norm(row["name"]), _norm(row.get("name_en"))):
            return row["code"]
    return None


def resolve_state_code(country: str | None, value: str | None) -> str | None:
    code = resolve_country_code(country)
    states = _states_by_country().get(code or "")
    key = _norm(value)
    if not states or not key:
        return None
    for state_code, spec in states.items():
        names = [state_code, spec["name"], *spec.get("aliases", [])]
        if key in {_norm(n) for n in names}:
            return state_code
    return None


def country_options() -> list[dict]:
    rows = []
    for row in _countries():
        entry = {
            "code": row["code"],
            "value": row["name"],
            "label": row["name"],
            "has_states": row["code"] in _states_by_country(),
        }
        if row.get("name_en") and row["name_en"] != row["name"]:
            entry["aliases"] = [row["name_en"]]
        rows.append(entry)
    return rows


def state_options(country: str | None) -> list[dict]:
    code = resolve_country_code(country)
    states = _states_by_country().get(code or "", {})
    rows = []
    for state_code, spec in sorted(states.items(), key=lambda kv: _norm(kv[1]["name"])):
        entry = {"code": state_code, "value": spec["name"], "label": spec["name"]}
        if spec.get("aliases"):
            entry["aliases"] = list(spec["aliases"])
        rows.append(entry)
    return rows


def city_options(country: str | None, state: str | None) -> list[dict]:
    country_code = resolve_country_code(country)
    state_code = resolve_state_code(country, state)
    if not country_code or not state_code:
        return []
    spec = _states_by_country()[country_code][state_code]
    return [
        {"value": city, "label": city} for city in sorted(spec["cities"], key=_norm)
    ]


def compose_birthplace(city: str | None, state: str | None, country: str | None) -> str:
    """Legacy single-string birthplace, e.g. ``"Saltillo, Coahuila, México"``."""
    parts = [str(p).strip() for p in (city, state, country) if p and str(p).strip()]
    return ", ".join(parts)[:150]
