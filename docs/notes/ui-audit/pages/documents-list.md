# Documents (list)

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
  - Light: `ui-audit-documents-list-light.png`
  - Dark: `ui-audit-documents-list-dark.png`

## Page
- **Route(s)**: `/seim/documents` (Vue), legacy placeholder `/documents/` (Django)
- **Role(s) tested**: Student (Vue)

## Breadcrumb
- **Observed**: Breadcrumb shows `Dashboard > Documents`.
- **Issues**:
  - Breadcrumb bar appears dark even when the page background is bright.

## Layout
- **Observed**: Filter card above a table/list of documents with per-row actions (view/download).
- **Issues**:
  - Filter card consumes significant vertical space; “Clear” is separated from inputs.
  - Table headers are visible but on smaller widths, the table likely needs horizontal scroll (verify).

## Theme
- **Observed**: Dark mode now applies at the page level after replacing hardcoded view backgrounds with `var(--seim-app-bg)`.
- **Issues**:
  - Re-check table/link contrast in Dark mode (esp. action icons).

## Top issues (P0/P1/P2)
- **P0**: None observed that block filtering, viewing, or downloading.
- **P1**:
  - Filters could be more compact, especially on small screens.
- **P2**:
  - Consider sticky filter header or condensed filter layout for frequent use.

## Quick wins
- Standardize breadcrumb + page surface theme application.
- Compress filter card spacing and improve “Clear” placement near filter controls.

