# Application detail

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
  - Light: `ui-audit-application-detail-light.png`
  - Dark: `ui-audit-application-detail-dark.png`

## Page
- **Route(s)**: `/applications/<uuid>/` (Django template), `/seim/applications/:id` (Vue)
- **Role(s) tested**: Student (Vue)

## Breadcrumb
- **Observed**: Breadcrumb shows deep trail (`Dashboard > Applications > <Program name>`).
- **Issues**:
  - Breadcrumb bar remains dark while the page background is bright (theme mismatch).
  - Program name in breadcrumb can be long; truncation/overflow needs verification on narrow widths.

## Layout
- **Observed**: Card-based sections (readiness, program info, timeline, comments, quick actions, document upload/checklist).
- **Issues**:
  - Program information shows multiple `N/A` fields; visual hierarchy makes the empty data prominent.
  - Document section lists items as “Invalid” without clear next action on the detail view (may be expected, but UX is harsh).

## Theme
- **Observed**: Light/Dark preference does not switch the page background to a dark surface; the cards are dark on a bright page in both screenshots.
- **Issues**:
  - Mixed surfaces reduce perceived cohesion and can affect contrast expectations (especially around badges/pills).

## Top issues (P0/P1/P2)
- **P0**: None observed that block page use (navigation, reading status, posting comment, document upload form visible).
- **P1**:
  - Theme mismatch (breadcrumb + card surfaces vs page background).
  - Long breadcrumb segment (program name) likely needs truncation/ellipsis on narrow widths.
- **P2**:
  - Consider de-emphasizing empty program metadata (group empty fields or hide absent sections).

## Quick wins
- Confirm intended theming model (full-page theme vs mixed card surfaces) and apply consistently.
- Add breadcrumb truncation rules for long program names.

