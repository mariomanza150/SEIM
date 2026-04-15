# Coordinator workload

## Audit status
- **Status**: Complete
- **Owner**: _TBD_
- **Updated**: 2026-04-15

## Test matrix
- **Themes**: Dark (this page reads consistently dark)
- **Viewport(s)**: Desktop-ish
- **Browser(s)**: Cursor embedded Chromium
- **Role(s) used for screenshots**: Coordinator (`coordinator@test.com`)
- **Screenshots**:
  - `ui-audit-coordinator-workload.png`

## Page
- **Route(s)**: `/seim/coordinator-workload` (Vue)
- **Role(s) tested**: Coordinator

## Breadcrumb
- **Observed**: Breadcrumb shows `Dashboard > Coordinator workload`.
- **Issues**:
  - Breadcrumb styling differs from SSR staff pages; cross-surface parity issue.

## Layout
- **Observed**: KPI cards (“Assigned to you”, “Your programs”, etc.) plus table/distribution (if populated).
- **Issues**:
  - When values are empty/zero, cards can feel repetitive; consider empty-state guidance.

## Theme
- **Observed**: This page appears properly dark-themed (unlike several list views).
- **Issues**:
  - Inconsistency vs other SPA pages where Dark mode still yields bright backgrounds.

## Top issues (P0/P1/P2)
- **P0**: None observed.
- **P1**:
  - Cross-page theme inconsistency (workload reads dark; lists often read mixed/bright).
- **P2**:
  - Add empty-state copy when workload metrics are zero to guide next actions.

## Quick wins
- Align theme behavior across staff pages to reduce “random dark vs bright” feel.
- Add simple empty-state guidance (e.g., link to review queue / agreements).

