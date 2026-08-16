# Applications (list)

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
  - Light: `ui-audit-applications-list-light.png`
  - Dark: `ui-audit-applications-list-dark.png`

## Page
- **Route(s)**: `/applications/` (Django template), `/seim/applications` (Vue)
- **Role(s) tested**: Student (Vue)

## Breadcrumb
- **Observed**: Breadcrumb exists (`Dashboard > Applications`) and stays pinned at top.
- **Issues**:
  - Breadcrumb bar appears dark even under Light theme (visual mismatch with page background).

## Layout
- **Observed**: Filter card + CTA buttons above list; application cards below.
- **Issues**:
  - Filters section takes significant vertical space; “Clear” button appears low-emphasis and separated from inputs.
  - Card header density is tight; status pill + title compete on narrow widths.

## Theme
- **Observed**: Dark mode now applies at the page level after replacing hardcoded view backgrounds with `var(--seim-app-bg)`.
- **Issues**:
  - Re-check contrast on badges/buttons/inputs in Dark mode.

## Top issues (P0/P1/P2)
- **P0**: None observed that block listing, filtering, or navigation.
- **P1**:
  - Filter layout/spacing could be more compact and consistent with other list views.
- **P2**:
  - Consider making “Clear” action more discoverable (placement near filters / sticky filter header).

## Quick wins
- Standardize breadcrumb background + spacing across themes.
- Reduce filter card vertical footprint on small screens; align “Clear” placement with common patterns.

