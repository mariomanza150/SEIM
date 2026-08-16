# Admin dashboard

## Audit status
- **Status**: Complete
- **Owner**: _TBD_
- **Updated**: 2026-04-15

## Test matrix
- **Themes**: Light (SSR page)
- **Viewport(s)**: Desktop-ish
- **Browser(s)**: Cursor embedded Chromium
- **Role(s) used for screenshots**: Admin (`admin@test.com`)
- **Screenshots**:
  - SSR: `ui-audit-admin-dashboard-ssr.png`

## Page
- **Route(s)**: `/admin-dashboard/` (Django), `/seim/admin-dashboard` (Vue entry may vary by role)
- **Role(s) tested**: Admin (Django `/admin-dashboard/`)

## Breadcrumb
- **Observed**: SSR nav uses top navigation links, not the SPA breadcrumb bar.
- **Issues**:
  - Wayfinding and layout differ from SPA routes; users switching between `/seim/*` and SSR admin pages will notice inconsistency.

## Layout
- **Observed**: Status tiles (DB/Redis/Celery/Static), KPI cards, recent activity, quick actions, and sections for alerts/system info.
- **Issues**:
  - Mixed density: some sections show “loading…” placeholders; ensure loading states are visually consistent.
  - Tile colors are vivid; verify contrast and dark-mode expectations if SSR pages later support it.

## Theme
- **Observed**: Light-themed SSR page.
- **Issues**:
  - Not aligned with SPA theme preference and SPA staff screens.

## Top issues (P0/P1/P2)
- **P0**: None observed that block use.
- **P1**:
  - SSR vs SPA parity issues (nav/breadcrumb, theme, spacing rhythm).
- **P2**:
  - Consider aligning typography and container widths to SPA design tokens if SSR remains.

## Quick wins
- Define canonical admin surface (SSR vs SPA) and align styling/wayfinding accordingly.
- Ensure SSR “loading…” placeholders don’t persist unnecessarily (or show skeletons).

