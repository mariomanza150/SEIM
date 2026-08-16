# Deferred P1 items (UI stabilization)

_These are P1 issues identified during the UI audit that were **not** addressed in the current implementation pass._

## Filters / density (list pages)
- **Tall filter cards push results below the fold**
  - Affected: Applications list, Documents list, Notifications, Review queue, Exchange agreements, Agreement documents.
  - Suggestion: collapse “advanced” filters + presets UI by default; move “Clear” near primary filters; consider sticky compact filter header.

## Breadcrumb behavior
- **Long breadcrumb segment truncation**
  - Affected: Application detail (`Dashboard > Applications > <Program name>`).
  - Suggestion: CSS ellipsis with max-width + tooltip, preserve accessible name.

## SSR vs SPA duplication/parity
- **Legacy SSR pages overlapping SPA surfaces**
  - Preferences (`/preferences/`) overlaps with SPA Settings.
  - Sessions/coordinator/admin dashboards use different visual language and theming.
  - Suggestion: decide canonical surface per feature; redirect legacy pages or align styling tokens.

