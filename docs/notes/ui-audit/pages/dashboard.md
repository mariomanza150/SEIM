# Dashboard

## Audit status
- **Status**: Complete
- **Owner**: _TBD_
- **Updated**: 2026-04-15

## Test matrix
- **Themes**: Light + Dark (via Settings → Theme)
- **Viewport(s)**: Mobile-ish (narrow) + Desktop (1280×800)
- **Browser(s)**: Cursor embedded Chromium
- **Role(s) used for screenshots**: Student (`student@test.com`)
- **Screenshots**:
  - Light: `ui-audit-dashboard-light.png`, `ui-audit-dashboard-light-desktop-navclosed.png`
  - Dark: `ui-audit-dashboard-dark.png`

## Page
- **Route(s)**: `/seim/dashboard` (Vue), legacy redirect `/dashboard/` → `/seim/dashboard/`
- **Role(s) tested**: Student

## Breadcrumb
- **Observed**: No breadcrumb on the dashboard; left navigation is the primary wayfinding element.
- **Issues**:
  - Theme feels inconsistent with other pages that have breadcrumb trails (contrast/spacing mismatch between pages).

## Layout
- **Observed**: On narrow view, the nav drawer dominates the viewport and hides the dashboard content until toggled.
- **Issues**:
  - Nav overlay behavior on desktop-sized viewport still appears “mobile-first” (drawer takes full vertical space and blocks content).

## Theme
- **Observed**: Light/Dark theme toggle does not appear to materially change the dashboard page background (still bright background with dark cards).
- **Issues**:
  - Theme preference may not be applied consistently across the SPA shell (dashboard looks visually identical between Light/Dark screenshots).

## Top issues (P0/P1/P2)
- **P0**: None observed that block task completion.
- **P1**:
  - Theme preference not reliably reflected on the page (Light vs Dark looks the same).
  - Navigation overlay/layout feels “mobile” even at desktop width (content discoverability).
- **P2**: Dashboard lacks breadcrumb parity with the rest of the app (may be intentional; confirm).

## Quick wins
- Ensure theme preference updates body/background + card surfaces consistently.
- Re-check responsive breakpoint logic for the nav drawer so desktop shows content-first layout.

