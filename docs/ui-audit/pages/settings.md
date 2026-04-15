# Settings

## Audit status
- **Status**: Complete
- **Owner**: _TBD_
- **Updated**: 2026-04-15

## Test matrix
- **Themes**: Light + Dark (Theme select on this page)
- **Viewport(s)**: Mobile-ish (narrow)
- **Browser(s)**: Cursor embedded Chromium
- **Role(s) used for screenshots**: Student (`student@test.com`)
- **Screenshots**:
  - Light: `ui-audit-settings-light.png`
  - Dark: `ui-audit-settings-dark.png`

## Page
- **Route(s)**: `/seim/settings` (Vue), legacy `/settings/` (Django)
- **Role(s) tested**: Student (Vue)

## Breadcrumb
- **Observed**: Breadcrumb shows `Dashboard > Settings`.
- **Issues**:
  - Breadcrumb styling should be re-checked now that page-level Dark mode backgrounds are fixed.

## Layout
- **Observed**: Long form with grouped sections: Appearance, Notifications, Privacy; includes Cancel + Save actions.
- **Issues**:
  - On narrow view, the form is long; primary action placement at bottom can require lots of scrolling (consider sticky footer actions).

## Theme
- **Observed**: Theme selector works and Dark mode now applies at the page level after replacing hardcoded view backgrounds with `var(--seim-app-bg)`.
- **Issues**:
  - Re-check contrast for checkboxes/help text and breadcrumb styling in Dark mode.

## Top issues (P0/P1/P2)
- **P0**: None observed.
- **P1**:
  - None specific beyond contrast verification across routes.
- **P2**:
  - Consider sticky bottom action bar for long forms (Save/Cancel) on mobile.

## Quick wins
- Done: removed per-view hardcoded backgrounds to restore theme parity; verify remaining SSR routes separately.
- Add sticky actions on mobile (optional) and confirm focus/scroll behavior after save.

