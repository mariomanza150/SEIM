"""Curated CGRI destination country list for admin selectors and partner seeding."""

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


def country_options() -> list[dict[str, str]]:
    """Return read-only country catalog entries for API consumers."""
    return [{"value": name, "label": name} for name in CGRI_COUNTRY_NAMES]
