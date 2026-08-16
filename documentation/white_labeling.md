# White-labeling / institution branding

SEIM ships with Universidad Autónoma de Coahuila (UAdeC) as the **default example theme**. Chrome, colors, and asset download are configurable so another institution can run the same product.

## What is configurable today

Set these in `.env` (see `env.example`):

| Variable | Role |
| --- | --- |
| `INSTITUTION_NAME` | Legal / footer name |
| `INSTITUTION_SHORT_NAME` | Navbar, titles, CMS seed headings |
| `INSTITUTION_TAGLINE` | Title suffix (default: Intercambio Académico) |
| `INSTITUTION_DEPARTMENT` | Footer and homepage hero |
| `INSTITUTION_LOCATION` | Footer address line |
| `INSTITUTION_WEBSITE` | Footer link and asset-download source |
| `INSTITUTION_LOGO_URL` | Optional navbar logo |
| `INSTITUTION_NAV_BRAND` | Navbar label (falls back to short name + tagline) |
| `INSTITUTION_SOCIAL_*` | Footer social links |
| `BRAND_PRIMARY` / `BRAND_ACCENT` (and light/dark/navy/orange/text) | CMS CSS variables |
| `WAGTAIL_SITE_NAME` | Wagtail admin site name |

Templates read these through `core.context_processors.institution`. CSS keeps the historical `--uadec-*` names and aliases them to `--brand-*` so existing CMS templates keep working.

## Asset download

```powershell
python scripts\download_institution_assets.py
```

`download_uadec_assets.py` (repo root and `scripts\`) is a compatibility wrapper. Environment:

- `INSTITUTION_WEBSITE` — homepage to scrape (default `https://www.uadec.mx/`)
- `INSTITUTION_ASSET_DIR` — output directory (default `staticfiles\images`)
- `INSTITUTION_LOGO_FILENAME` — primary file name (default `institution-logo.png`)
- `INSTITUTION_LOGO_COMPAT_FILENAME` — extra copy (default `uadec-logo.png`)
- `INSTITUTION_ASSET_PATHS` — comma-separated logo paths to try
- `INSTITUTION_ASSET_SSL_VERIFY` — `true` to enable TLS verify (default off for the legacy UAdeC fetch)

## CMS seed content

`manage.py populate_uadec_content` and `restore_cms` still install the UAdeC **example pages** (Spanish copy, programs, FAQs). Homepage title/hero use `INSTITUTION_*`. Replacing the rest of the seed copy is a follow-up (GitHub issue), not a requirement to change colors or chrome.

## Still institution-specific

- Remaining Spanish UAdeC body copy in `populate_uadec_content`
- PDF mobility forms and some `docs/` UAdeC deployment notes
- CSS file name `static/css/uadec-styles.css` (content is now theme-overridable)

Do not delete those assets; override or replace them per institution.
