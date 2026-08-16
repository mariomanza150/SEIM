# Institution branding packs

SEIM is white-labelable. **UAdeC** (`branding\uadec\`) is the packaged default example, not the only supported institution.

## Add another school

1. Copy `branding\uadec\` to `branding\<slug>\` (for example `branding\myuni\`).
2. Edit `branding\<slug>\config.json` — set `INSTITUTION_SLUG`, name, colors, website.
3. Recolor `theme.css`. After `collectstatic`, it is served as `/static/<slug>/theme.css`.
4. Put your own logos in `branding\<slug>\logos\` (PNG/SVG). Do **not** commit copyrighted university marks; keep `.gitkeep`.
5. Point SEIM at the pack:
   - Copy `tenant_config.json.example` to `tenant_config.json` (gitignored), or
   - Copy `institution.json.example` to `institution.json` (gitignored), or
   - Set `INSTITUTION_SLUG=myuni` and/or `INSTITUTION_CONFIG_FILE=branding\myuni\config.json`.
6. Optional: set the same `INSTITUTION_*` / `BRAND_*` keys in `.env` (env wins).
7. Re-seed CMS example pages if needed: `python manage.py populate_institution_content`.

Full guide: `docs\white_labeling.md`.

## Asset download (optional)

```powershell
python scripts\download_institution_assets.py
```

Reads `branding\<slug>\config.json` / `institution.json` plus env vars (`INSTITUTION_SLUG`, `INSTITUTION_WEBSITE`, `INSTITUTION_ASSET_DIR`, …). `download_uadec_assets.py` is a compatibility wrapper. Downloaded files stay local — do not add them to git.

## Precedence

1. Environment variables
2. `tenant_config.json` (or `TENANT_CONFIG_FILE`)
3. `branding\institution.json` (or `INSTITUTION_CONFIG_FILE`)
4. `branding\<slug>\config.json` (`INSTITUTION_SLUG`, default `uadec`)
5. Built-in defaults in `core\branding.py`
