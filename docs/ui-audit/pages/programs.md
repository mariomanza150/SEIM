# Programs

## Audit status
- **Status**: Complete
- **Owner**: _TBD_
- **Updated**: 2026-04-15

## Test matrix
- **Themes**: Light + Dark (via Settings → Theme; SSR page appears theme-styled independently)
- **Viewport(s)**: Mobile-ish (narrow) + Desktop-ish
- **Browser(s)**: Cursor embedded Chromium
- **Role(s) used for screenshots**: Student (`student@test.com`)
- **Screenshots**:
  - Light (SSR): `ui-audit-programs-ssr-light.png`
  - Dark (SSR): `ui-audit-programs-ssr-dark.png`

## Page
- **Route(s)**: `/programs/` (Django template), `/seim/programs/compare` (Vue compare)
- **Role(s) tested**: Student (logged in)

## Breadcrumb
- **Observed**: SSR page uses top nav wayfinding, not SPA breadcrumb trail.
- **Issues**:
  - Header/nav patterns differ from SPA pages (visual + interaction inconsistency).

## Layout
- **Observed**: Desktop layout shows filters as a horizontal bar above program cards.
- **Issues**:
  - Responsive behavior differs from SPA list pages (filters + cards spacing rhythm not aligned).

## Theme
- **Observed**: SSR page visually renders as “dark” themed in both screenshots; overall styling appears Bootstrap-dark-ish.
- **Issues**:
  - Potential mismatch between SSR theming and SPA theme preference (Light/Dark toggle in SPA may not affect SSR pages).

## Top issues (P0/P1/P2)
- **P0**: None observed that block browsing/apply CTAs.
- **P1**:
  - SSR `/programs/` navigation + styling not aligned with SPA (theme, spacing, breadcrumb/wayfinding).
  - Theme preference may not apply across SSR pages.
- **P2**:
  - Consider aligning filter UX (labels, density, card rhythm) with SPA program discovery surfaces.

## Quick wins
- Define expected theme behavior for SSR pages (follow SPA preference vs fixed theme).
- Align header/breadcrumb conventions between SSR and SPA where feasible.

