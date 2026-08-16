# Preferences

## Audit status
- **Status**: Complete
- **Owner**: _TBD_
- **Updated**: 2026-04-15

## Test matrix
- **Themes**: N/A (SSR page renders its own appearance controls)
- **Viewport(s)**: Desktop-ish
- **Browser(s)**: Cursor embedded Chromium
- **Role(s) used for screenshots**: Student (`student@test.com`)
- **Screenshots**:
  - SSR: `ui-audit-preferences-ssr.png`

## Page
- **Route(s)**: `/seim/preferences` → redirects to Settings (Vue), legacy `/preferences/` (Django)
- **Role(s) tested**: Student (Django `/preferences/`)

## Breadcrumb
- **Observed**: SSR page has its own nav + breadcrumb behavior; not aligned with SPA breadcrumb styling.
- **Issues**:
  - Duplicated concept vs SPA Settings (two different places to configure appearance/accessibility).

## Layout
- **Observed**: Two-column layout with Appearance/Accessibility controls and a preview panel.
- **Issues**:
  - Potential user confusion: SSR page provides controls that overlap with SPA Settings but may not map 1:1.

## Theme
- **Observed**: SSR page appears consistently styled (dark-ish layout) and includes its own theme controls.
- **Issues**:
  - Theme preference parity between SSR Preferences and SPA Settings needs explicit product decision.

## Top issues (P0/P1/P2)
- **P0**: None observed that block use.
- **P1**:
  - Duplicate preferences surfaces (SSR Preferences vs SPA Settings) can cause inconsistency and user confusion.
- **P2**:
  - Consider consolidating or clearly labeling legacy vs SPA preference paths.

## Quick wins
- Decide whether to deprecate SSR `/preferences/` or make it a thin redirect to `/seim/settings`.
- Align the SSR page’s controls to the same backing settings (or explicitly mark as legacy).

