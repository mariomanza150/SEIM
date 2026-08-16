# Notifications

## Audit status
- **Status**: Complete
- **Owner**: _TBD_
- **Updated**: 2026-04-15

## Test matrix
- **Themes**: Dark (via Settings → Theme)
- **Viewport(s)**: Desktop-ish
- **Browser(s)**: Cursor embedded Chromium
- **Role(s) used for screenshots**: Student (`student@test.com`)
- **Screenshots**:
  - Dark: `ui-audit-notifications-dark.png`

## Page
- **Route(s)**: `/seim/notifications` (Vue)
- **Role(s) tested**: Student

## Breadcrumb
- **Observed**: Breadcrumb shows `Dashboard > Notifications`.
- **Issues**:
  - Breadcrumb bar appears dark while the page background is bright (same mismatch as other SPA list pages).

## Layout
- **Observed**: Actions row includes “Mark all as read”, filter card (status/category), then notification cards with per-item actions.
- **Issues**:
  - Filter card is tall; “Clear filters” is distant from the select controls.
  - The primary “Mark all as read” action sits above the filter card; hierarchy might be unclear on narrow screens.

## Theme
- **Observed**: Dark mode now applies at the page level after replacing hardcoded view backgrounds with `var(--seim-app-bg)`.
- **Issues**:
  - Re-check notification card contrast and focus rings in Dark mode.

## Top issues (P0/P1/P2)
- **P0**: None observed that block reading or marking notifications.
- **P1**:
  - Filter layout could be more compact and consistent with other list views.
- **P2**:
  - Consider sticky filter header and clearer action grouping (bulk vs per-item).

## Quick wins
- Done: page-level background now respects Dark mode (verify other surfaces).
- Compact filters and move “Clear filters” adjacent to filter inputs.

