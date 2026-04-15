# UI stabilization fix queue (P0/P1 summary)

_Source: per-page audits under `docs\\ui-audit\\pages\\`._

## P0 (must-fix)

### Documents
- **Document detail: inline PDF preview fails** (`/seim/documents/:id`)
  - **Observed**: Preview shows “Failed to load PDF document.”
  - **Screenshots**: `ui-audit-document-detail-light.png`, `ui-audit-document-detail-dark.png`
  - **Impact**: Blocks staff/student document review in-page (forces download-only workflow).

## P1 (high-priority stabilization)

### Theme / surfaces
- **Dark mode parity inconsistent across SPA routes**: _Resolved (2026-04-15)_
  - Fix: removed per-page hardcoded `background-color: #f8f9fa` overrides in SPA views; now uses `var(--seim-app-bg)` driven by `html[data-theme]`.
  - Verification: `ui-audit-applications-dark-afterthemefix.png`, `ui-audit-settings-dark-afterthemefix.png`

### Breadcrumbs / wayfinding
- **Breadcrumb bar styling inconsistent**
  - SPA breadcrumb bar often appears dark regardless of theme; SSR pages use different breadcrumb conventions.
- **Long breadcrumb segment risk**
  - Application detail breadcrumb includes full program name; likely needs truncation/ellipsis on narrow widths.

### Filters / density (list pages)
- **Filter cards are tall and push results below fold**
  - Applications list, documents list, notifications, staff agreements/docs, review queue.
  - “Clear” action often far from inputs; presets UI increases height.

### SSR vs SPA parity
- **Multiple legacy SSR pages duplicate SPA concepts**
  - Preferences (`/preferences/`) overlaps with SPA Settings.
  - Sessions, coordinator dashboard, admin dashboard/analytics use different design language than SPA.

