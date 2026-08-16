# Application form (new/edit)

## Audit status
- **Status**: Complete
- **Owner**: _TBD_
- **Updated**: 2026-04-15

## Test matrix
- **Themes**: Light + Dark (via Settings → Theme)
- **Viewport(s)**: Desktop-ish
- **Browser(s)**: Cursor embedded Chromium
- **Role(s) used for screenshots**: Student (`student@test.com`)
- **Screenshots**:
  - Light: `ui-audit-application-form-light.png`
  - Dark: `ui-audit-application-form-dark.png`

## Page
- **Route(s)**: `/applications/create/` (Django), `/seim/applications/new`, `/seim/applications/:id/edit` (Vue)
- **Role(s) tested**: Student (Vue, new application)

## Breadcrumb
- **Observed**: Breadcrumb shows `Dashboard > Applications > New application`.
- **Issues**:
  - Breadcrumb bar appears dark while the page background is bright (theme mismatch).

## Layout
- **Observed**: Program-selection section embeds a filter panel (search/sort/language/date/GPA) inside the “Exchange program” card; tips appear as a sidebar card.
- **Issues**:
  - The embedded filter panel is visually heavy and tall; primary “Exchange program” select is far below the fold on narrower view.
  - “Clear filters” link inside the card header can be easy to miss (low contrast and small target).

## Theme
- **Observed**: Light and Dark screenshots look very similar; page background remains bright while the inner filter surfaces are dark.
- **Issues**:
  - Theme preference does not appear to drive an overall page-level background/surface change.

## Top issues (P0/P1/P2)
- **P0**: None observed that block starting an application (controls render, required field clearly marked).
- **P1**:
  - Above-the-fold density: key selection control is pushed down by filters; may slow task completion on small screens.
  - Theme mismatch (dark card surfaces on bright page; breadcrumb dark in Light).
- **P2**:
  - Consider collapsing advanced filters by default (progressive disclosure) and surfacing “accepting now” prominently.

## Quick wins
- Make advanced filters collapsible; keep “program select” and primary actions near top.
- Standardize breadcrumb styling across themes and match page background/surface expectations.

