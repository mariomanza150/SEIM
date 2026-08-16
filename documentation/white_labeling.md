# White-labeling / institution branding

SEIM ships with Universidad Autónoma de Coahuila (UAdeC) as the **default example theme**. Chrome, colors, logos, PDF headers, and CMS seed tokens are configurable so another institution can run the same product without forking templates.

## Quick start for another school

1. Copy `branding\uadec\` to `branding\<your-slug>\` (for example `branding\myuni\`).
2. Edit `branding\<your-slug>\config.json` (name, short name, email, colors).
3. Put logos in `branding\<your-slug>\logos\` (PNG/SVG). After `collectstatic` they are served as `/static/<your-slug>/logos/...`.
4. Copy `branding\institution.json.example` to `branding\institution.json` **or** set `INSTITUTION_CONFIG_FILE` to your pack’s `config.json`.
5. Optionally set the same keys in `.env` (env vars win).
6. Point `INSTITUTION_THEME_CSS` at `<your-slug>\theme.css` (copy and recolor `uadec\theme.css`).
7. Set `INSTITUTION_LOGO_URL=/static/<your-slug>/logos/institution-logo.png`.
8. Re-seed CMS if you want example pages to use the new name: `python manage.py populate_institution_content`.

Existing UAdeC deployments keep working if you change nothing.

## Precedence

1. Environment variables (`INSTITUTION_*`, `BRAND_*`, `INSTITUTION_SLUG`)
2. `INSTITUTION_CONFIG_FILE` (default `branding\institution.json`)
3. Packaged defaults in `branding\<slug>\config.json` (slug from env / overlay, default `uadec`)
4. Built-in Python defaults in `core\branding.py`

## What is configurable

Set these in `.env` (see `env.example`) or in the JSON config:

| Variable | Role |
| --- | --- |
| `INSTITUTION_SLUG` | Pack folder under `branding\` (default `uadec`) |
| `INSTITUTION_NAME` | Legal / footer name |
| `INSTITUTION_SHORT_NAME` | Navbar, titles, CMS seed headings, document labels |
| `INSTITUTION_TAGLINE` | Title suffix (default: Intercambio Académico) |
| `INSTITUTION_DEPARTMENT` | Footer, homepage hero, PDF header |
| `INSTITUTION_LOCATION` | Footer address line |
| `INSTITUTION_WEBSITE` | Footer link and asset-download source |
| `INSTITUTION_EMAIL` | Seed / contact / PDF footer email |
| `INSTITUTION_PHONE` | Seed / contact / PDF footer phone |
| `INSTITUTION_ADDRESS` | Seed postal address (HTML allowed) |
| `INSTITUTION_LOGO_URL` | Optional navbar logo |
| `INSTITUTION_NAV_BRAND` | Navbar label (falls back to short name + tagline) |
| `INSTITUTION_SOCIAL_*` | Footer social links |
| `INSTITUTION_THEME_CSS` | CMS stylesheet (default `uadec/theme.css`) |
| `INSTITUTION_CONFIG_FILE` | Path to a JSON overlay |
| `BRAND_PRIMARY` / `BRAND_ACCENT` (and light/dark/navy/orange/text) | CMS CSS variables |
| `WAGTAIL_SITE_NAME` | Wagtail admin site name |

Templates read these through `core.context_processors.institution`. CSS keeps the historical `--uadec-*` names and aliases them to `--brand-*` so existing CMS templates keep working.

## Logos and theme files

| Path | Purpose |
| --- | --- |
| `branding\uadec\theme.css` | Default CMS theme (moved from `static\css\uadec-styles.css`) |
| `branding\uadec\logos\` | Default / downloaded logo directory |
| `static\css\uadec-styles.css` | Compatibility stub that imports the pack theme |
| `static\css\institution-styles.css` | Compatibility stub for older templates |

`branding\` is on `STATICFILES_DIRS`, so `branding\uadec\theme.css` is `/static/uadec/theme.css`.

## Asset download

```powershell
python scripts\download_institution_assets.py
```

`download_uadec_assets.py` (repo root and `scripts\`) is a compatibility wrapper. Environment:

- `INSTITUTION_SLUG` — branding pack folder (default `uadec`)
- `INSTITUTION_WEBSITE` — homepage to scrape (from branding config, UAdeC default)
- `INSTITUTION_ASSET_DIR` — output directory (default `branding\<slug>\logos`)
- `INSTITUTION_LOGO_FILENAME` — primary file name (default `institution-logo.png`)
- `INSTITUTION_LOGO_COMPAT_FILENAME` — extra copy (default `uadec-logo.png` only for the UAdeC slug)
- `INSTITUTION_ASSET_PATHS` — comma-separated logo paths to try
- `INSTITUTION_ASSET_SSL_VERIFY` — `true` to enable TLS verify (default off)

Do not commit downloaded logos. Keep `branding\<slug>\logos\.gitkeep`.

You can skip the downloader and drop files into `branding\<slug>\logos\` yourself.

## CMS seed content

`manage.py populate_institution_content` (alias: `populate_uadec_content`) and `restore_cms` still install the Spanish **example pages**. Name, email, phone, address, and “UAdeC” tokens are replaced from `INSTITUTION_*` at seed time.

PDF mobility forms stamp `INSTITUTION_NAME` / short name in the header. The document catalog slug `inscripcion_uadec` is stable for existing databases; the display name becomes `Inscripción {short_name}`.

## Still example-specific (by design)

- Spanish narrative in seed FAQs/programs (tokens replaced; stories are still the UAdeC sample set)
- Named CGRI staff and scraped copy in `populate_internacional_content` (demo/CMS content)
- `documentation\notes\INTERNACIONAL_*` hostnames (`uadec.mx`) — banners note they are examples
- Default `branding\uadec\theme.css` palette file (do not delete; copy it)
- Legacy document slug `inscripcion_uadec`
- `/cgri/` and `/movilidad/` URL redirects in `internacional\` (UAdeC site compatibility)

Do not delete those assets; override or replace them per institution.
