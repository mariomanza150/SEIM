# Calendar / deadlines

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
  - Dark: `ui-audit-calendar-dark.png`

## Page
- **Route(s)**: `/seim/calendar` (Vue), legacy `/calendar/` (Django)
- **Role(s) tested**: Student (Vue)

## Breadcrumb
- **Observed**: Breadcrumb shows `Dashboard > Deadlines and calendar`.
- **Issues**:
  - Breadcrumb bar appears dark while some pages still render bright backgrounds in “dark” mode (cross-page inconsistency).

## Layout
- **Observed**: Page contains (1) ICS/webcal subscribe card with copy warnings, (2) date range inputs + toggles, (3) long list of event rows.
- **Issues**:
  - ICS/webcal URLs are long and can overflow; copy controls exist but the fields can still dominate the viewport.
  - Long event list likely benefits from stronger grouping/sticky filters (verify on narrow widths).

## Theme
- **Observed**: This page reads as consistently dark-themed.
- **Issues**:
  - Theme parity differs vs other SPA pages (some appear “mixed”/bright even when Dark is selected).

## Top issues (P0/P1/P2)
- **P0**: None observed that block filtering, refreshing, or subscribing.
- **P1**:
  - Cross-page theme inconsistency (calendar looks correctly dark; other pages often look mixed/bright).
- **P2**:
  - Consider a compact/sticky filter header for long lists and narrow screens.

## Quick wins
- Add truncation + “Copy” affordance alignment for long subscribe URLs (responsive).
- Align theme application across SPA pages so Dark mode is consistent.

