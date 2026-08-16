# Exchange agreements (staff)

## Audit status
- **Status**: Complete
- **Owner**: _TBD_
- **Updated**: 2026-04-15

## Test matrix
- **Themes**: Mixed (dark filter card on bright background)
- **Viewport(s)**: Desktop-ish
- **Browser(s)**: Cursor embedded Chromium
- **Role(s) used for screenshots**: Coordinator (`coordinator@test.com`)
- **Screenshots**:
  - `ui-audit-exchange-agreements.png`

## Page
- **Route(s)**: `/seim/exchange-agreements` (Vue)
- **Role(s) tested**: Coordinator

## Breadcrumb
- **Observed**: Breadcrumb shows `Dashboard > Exchange agreements`.
- **Issues**:
  - Breadcrumb bar remains dark while page background is bright (theme mismatch).

## Layout
- **Observed**: Very large filter surface (search, multiple selects, date inputs, expiring days, sort, presets) before results.
- **Issues**:
  - Filter set is long; requires substantial scrolling before results appear on smaller screens.
  - “Clear” button can be far from inputs and below the fold.

## Theme
- **Observed**: Dark cards on bright background; similar to other staff list pages.
- **Issues**:
  - Theme parity not consistent with pages like coordinator workload/calendar which read as fully dark.

## Top issues (P0/P1/P2)
- **P0**: None observed that block filtering.
- **P1**:
  - Filter density/height and theme mismatch.
- **P2**:
  - Consider progressive disclosure for advanced filters (date range, expiring days).

## Quick wins
- Collapse advanced filters by default; keep search/status/type visible.
- Improve “Clear” placement and make filter/results relationship more immediate.

