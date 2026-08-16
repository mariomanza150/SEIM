# Notification routing

## Audit status
- **Status**: Complete
- **Owner**: _TBD_
- **Updated**: 2026-04-15

## Test matrix
- **Themes**: Dark
- **Viewport(s)**: Desktop-ish
- **Browser(s)**: Cursor embedded Chromium
- **Role(s) used for screenshots**: Coordinator (`coordinator@test.com`)
- **Screenshots**:
  - `ui-audit-notification-routing.png`

## Page
- **Route(s)**: `/seim/notification-routing` (Vue)
- **Role(s) tested**: Coordinator

## Breadcrumb
- **Observed**: Breadcrumb shows `Dashboard > Notification routing`.
- **Issues**:
  - Breadcrumb bar styling is consistent with other SPA pages but differs from SSR admin/staff pages.

## Layout
- **Observed**: Large table-based documentation view (category → settings fields → triggers → recipients).
- **Issues**:
  - Table is wide; on smaller widths this likely requires horizontal scrolling (verify).
  - High-density content could benefit from section anchors or collapsible groups.

## Theme
- **Observed**: Page reads consistently dark-themed.
- **Issues**:
  - Cross-page theme parity issues remain (some list pages render bright backgrounds even in Dark mode).

## Top issues (P0/P1/P2)
- **P0**: None observed.
- **P1**:
  - Wide table responsiveness risk on mobile.
- **P2**:
  - Consider navigation aids (TOC, jump links) for long documentation pages.

## Quick wins
- Add responsive table handling (horizontal scroll + sticky first column/header if needed).
- Consider a “copy schema version / API link” affordance near the title for staff workflows.

