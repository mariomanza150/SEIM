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

# English / alternate spellings for searchable selectors (values stay Spanish CGRI names).
CGRI_COUNTRY_ALIASES: dict[str, tuple[str, ...]] = {
    "Alemania": ("Germany",),
    "Brasil": ("Brazil",),
    "Canadá": ("Canada",),
    "Corea del Sur": ("South Korea", "Korea"),
    "España": ("Spain",),
    "EUA": ("USA", "United States", "US", "EEUU", "U.S.A.", "U.S."),
    "Finlandia": ("Finland",),
    "Francia": ("France",),
    "Italia": ("Italy",),
    "Panamá": ("Panama",),
    "Perú": ("Peru",),
    "Taiwán": ("Taiwan",),
}


def country_options() -> list[dict]:
    """Return read-only country catalog entries for API consumers."""
    options: list[dict] = []
    for name in CGRI_COUNTRY_NAMES:
        entry: dict = {"value": name, "label": name}
        aliases = CGRI_COUNTRY_ALIASES.get(name)
        if aliases:
            entry["aliases"] = list(aliases)
        options.append(entry)
    return options
