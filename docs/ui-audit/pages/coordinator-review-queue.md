# Coordinator review queue

## Audit status
- **Status**: Complete
- **Owner**: _TBD_
- **Updated**: 2026-04-15

## Test matrix
- **Themes**: Mixed (page background bright; dark filter card)
- **Viewport(s)**: Desktop-ish
- **Browser(s)**: Cursor embedded Chromium
- **Role(s) used for screenshots**: Coordinator (`coordinator@test.com`)
- **Screenshots**:
  - `ui-audit-coordinator-review-queue.png`

## Page
- **Route(s)**: `/seim/review-queue` (Vue)
- **Role(s) tested**: Coordinator

## Breadcrumb
- **Observed**: Breadcrumb shows `Dashboard > Review queue`.
- **Issues**:
  - Breadcrumb bar appears dark while page background is bright (theme mismatch).

## Layout
- **Observed**: Large filter card (search + quick filters + status/sort + presets) above results table/list.
- **Issues**:
  - Quick filters are checkboxes but appear visually like “off” controls; needs clear affordance that they are filters.
  - “Clear” button is far down and may be below the fold depending on preset section height.

## Theme
- **Observed**: Dark card surfaces on a bright background.
- **Issues**:
  - Cross-page theme inconsistency; Dark mode preference does not make the shell consistently dark.

## Top issues (P0/P1/P2)
- **P0**: None observed that block filtering or opening items.
- **P1**:
  - Theme mismatch (breadcrumb + cards vs background).
  - Filter card density/height reduces scanability (especially with presets UI).
- **P2**:
  - Consider sticky compact filter bar; collapse presets UI by default.

## Quick wins
- Compact the filter card and place “Clear” adjacent to filter controls.
- Apply consistent page-level theme/background behavior across staff pages.

