# Sessions

## Audit status
- **Status**: Complete
- **Owner**: _TBD_
- **Updated**: 2026-04-15

## Test matrix
- **Themes**: Light (SSR page)
- **Viewport(s)**: Desktop-ish
- **Browser(s)**: Cursor embedded Chromium
- **Role(s) used for screenshots**: Student (`student@test.com`)
- **Screenshots**:
  - SSR: `ui-audit-sessions-ssr.png`

## Page
- **Route(s)**: `/sessions/` (Django)
- **Role(s) tested**: Student

## Breadcrumb
- **Observed**: SSR breadcrumb shows `Dashboard / Settings / Sessions` with a pill-style container.
- **Issues**:
  - Breadcrumb styling differs significantly from SPA breadcrumb bar (inconsistent wayfinding).

## Layout
- **Observed**: Security tip banner, session list card, and security actions (revoke other sessions, change password).
- **Issues**:
  - Visual language is clearly “SSR/Bootstrap default” and does not match SPA cards/controls.

## Theme
- **Observed**: Page renders as light-themed.
- **Issues**:
  - Not clear whether SPA theme preference should apply to this SSR page; currently looks independent.

## Top issues (P0/P1/P2)
- **P0**: None observed.
- **P1**:
  - SSR page styling and breadcrumb conventions do not match SPA.
- **P2**:
  - Consider redirecting sessions management into the SPA or aligning styles for consistency.

## Quick wins
- Decide SSR vs SPA ownership for sessions UI. If staying SSR, align breadcrumb + spacing/token usage with SPA conventions.

