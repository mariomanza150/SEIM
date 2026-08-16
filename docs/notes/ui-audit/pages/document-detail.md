# Document detail

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
  - Light: `ui-audit-document-detail-light.png`
  - Dark: `ui-audit-document-detail-dark.png`

## Page
- **Route(s)**: `/seim/documents/:id` (Vue)
- **Role(s) tested**: Student (Vue)

## Breadcrumb
- **Observed**: Breadcrumb shows `Dashboard > Documents > <document type>`.
- **Issues**:
  - Breadcrumb bar appears dark while page background is bright (theme mismatch).

## Layout
- **Observed**: Top “Preview” area followed by document metadata, replace flow, review history, comments, and quick actions.
- **Issues**:
  - Preview occupies significant space; error state overlay can dominate the page.

## Theme
- **Observed**: Cards/surfaces are dark while page background stays bright in both Light/Dark theme screenshots.
- **Issues**:
  - Theme preference does not appear to apply consistently to the overall page background.

## Top issues (P0/P1/P2)
- **P0**: _Resolved (2026-04-15)_ — demo PDFs now render inline.
  - Verification: `ui-audit-document-detail-preview-fixed.png`
- **P1**:
  - Theme mismatch (breadcrumb + card surfaces vs page background).
  - Error state UX could provide clearer recovery path (e.g., try download/open in new tab, show status details).
- **P2**:
  - Consider collapsing preview by default after failure and surfacing alternate actions prominently.

## Quick wins
- Done: demo-seeded PDFs are now valid (reportlab-based seed) and preview loads; keep frontend guardrails for non-PDF error payloads.
- Improve preview error state to offer “Download” / “Open in new tab” as primary actions.

