# Coordinator dashboard

## Audit status
- **Status**: Complete
- **Owner**: _TBD_
- **Updated**: 2026-04-15

## Test matrix
- **Themes**: Light (SSR page)
- **Viewport(s)**: Desktop-ish
- **Browser(s)**: Cursor embedded Chromium
- **Role(s) used for screenshots**: Admin (`admin@test.com`) viewing coordinator dashboard
- **Screenshots**:
  - SSR: `ui-audit-coordinator-dashboard-ssr.png`

## Page
- **Route(s)**: `/coordinator-dashboard/` (Django template), staff screens under `/seim/*` (Vue)
- **Role(s) tested**: Admin (SSR view)

## Breadcrumb
- **Observed**: SSR page does not use the SPA breadcrumb bar; instead it uses SSR navigation patterns.
- **Issues**:
  - Wayfinding and breadcrumb conventions differ from SPA staff routes (review queue/workload).

## Layout
- **Observed**: KPI tiles (pending reviews, documents to validate, recent activity) and simple empty states.
- **Issues**:
  - Visual style differs from SPA staff dashboards; looks like SSR/Bootstrap default.

## Theme
- **Observed**: Light-themed SSR page.
- **Issues**:
  - Not aligned with SPA theme preference and staff SPA routes’ dark styling.

## Top issues (P0/P1/P2)
- **P0**: None observed.
- **P1**:
  - SSR vs SPA mismatch (theme, layout, navigation patterns).
- **P2**:
  - Consider consolidating coordinator staff dashboard into SPA routes or aligning shared styling.

## Quick wins
- Decide which surface is canonical for coordinator staff overview (SSR vs SPA).
- Align breadcrumb/wayfinding and theme conventions across staff pages.

