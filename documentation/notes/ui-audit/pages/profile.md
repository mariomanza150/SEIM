# Profile

## Audit status
- **Status**: Complete
- **Owner**: _TBD_
- **Updated**: 2026-04-15

## Test matrix
- **Themes**: Dark (via Settings → Theme)
- **Viewport(s)**: Desktop-ish
- **Browser(s)**: Cursor embedded Chromium
- **Role(s) used for screenshots**: Student (`student@test.com`)
- **Screenshots**:
  - Dark: `ui-audit-profile-dark.png`

## Page
- **Route(s)**: `/seim/profile` (Vue), legacy `/profile/` (Django)
- **Role(s) tested**: Student (Vue)

## Breadcrumb
- **Observed**: Breadcrumb shows `Dashboard > Profile`.
- **Issues**:
  - Breadcrumb bar styling should be re-checked now that page-level Dark mode backgrounds are fixed.

## Layout
- **Observed**: Form split into “Account” and “Eligibility” sections, with a “Tip” card.
- **Issues**:
  - On narrower widths, long forms may benefit from sticky section nav or clearer save/cancel placement (verify).

## Theme
- **Observed**: Dark mode now applies at the page level after replacing hardcoded view backgrounds with `var(--seim-app-bg)`.
- **Issues**:
  - Re-check form control contrast (inputs/selects) and help text in Dark mode.

## Top issues (P0/P1/P2)
- **P0**: None observed that block editing/saving.
- **P1**:
  - None specific beyond cross-page contrast verification.
- **P2**:
  - Consider improving long-form ergonomics (section anchors, save/cancel visibility).

## Quick wins
- Done: page-level background now respects Dark mode (verify contrast).
- Verify mobile UX for long eligibility section and additional languages controls.

