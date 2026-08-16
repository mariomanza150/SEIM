# Admin analytics

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
  - SSR: `ui-audit-admin-analytics-ssr.png`

## Page
- **Route(s)**: `/dashboard/analytics/` (Django template)
- **Role(s) tested**: Admin

## Breadcrumb
- **Observed**: SSR navigation/wayfinding; no SPA breadcrumb bar.
- **Issues**:
  - Parity mismatch vs SPA analytics-style screens (if added later) and staff SPA pages.

## Layout
- **Observed**: Refresh + Export menu, date filters, report type selector, KPI cards, charts/sections, and “Detailed Reports” cards.
- **Issues**:
  - Dense page; on smaller widths charts/controls may require responsive tuning (verify).
  - Export menu placement is good, but ensure keyboard/focus behavior is solid.

## Theme
- **Observed**: Light-themed SSR page.
- **Issues**:
  - Not aligned with SPA theme preference and staff SPA screens.

## Top issues (P0/P1/P2)
- **P0**: None observed.
- **P1**:
  - SSR vs SPA parity issues (theme/wayfinding).
- **P2**:
  - Consider sticky filters or a compact header on mobile.

## Quick wins
- Confirm export menu accessibility (focus order, aria labels) during a11y pass.
- Align container widths/typography with SPA if SSR remains a primary surface.

