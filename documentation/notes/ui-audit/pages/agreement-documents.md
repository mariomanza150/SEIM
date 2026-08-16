# Agreement documents (staff)

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
  - `ui-audit-agreement-documents.png`

## Page
- **Route(s)**: `/seim/agreement-documents` (Vue)
- **Role(s) tested**: Coordinator

## Breadcrumb
- **Observed**: Breadcrumb shows `Dashboard > Agreement documents`.
- **Issues**:
  - Breadcrumb bar appears dark while page background is bright (theme mismatch).

## Layout
- **Observed**: Filter card (search/agreement/category/current-only/sort/presets) then results (not visible in screenshot due to filter height).
- **Issues**:
  - Filter card is tall and pushes results below the fold; “Current only” toggle is separated from related selects.

## Theme
- **Observed**: Dark filter surface on bright background.
- **Issues**:
  - Dark mode parity inconsistent across staff routes.

## Top issues (P0/P1/P2)
- **P0**: None observed.
- **P1**:
  - Filter density/height and theme mismatch.
- **P2**:
  - Consider collapsing “preset save” UI by default to reduce height.

## Quick wins
- Compact the filter card and keep at least the first results row visible on desktop.
- Align theme background behavior across staff pages.

