# SEIM UI audit

This folder contains a **per-page UI audit** focused on:
- theme (light/dark consistency, tokens, contrast)
- layout (spacing rhythm, container widths, responsiveness)
- breadcrumbs (placement, clarity, overflow/truncation, contrast)

## How to use
- Each page has a dedicated file under `docs\ui-audit\pages\`.
- Use the tracker below to record **audit status** and a single next action per page.
- Items are prioritized:
  - **P0**: breaks task completion / severe accessibility / severe visual bug
  - **P1**: significant usability/consistency issues
  - **P2**: polish / nice-to-have improvements

## Tracker
Statuses:
- **Not started**: page file exists, audit not written yet
- **In progress**: actively auditing / capturing issues
- **Complete**: audit written and issues captured
- **Follow-up**: needs re-check after UI changes land

Legend:
- **Next action**: the single most important next step for that page (keep it short)
- **Owner**: optional (name/handle)
- **Updated**: optional (YYYY-MM-DD)

| Page | Status | Top priority | Next action | Owner | Updated |
| --- | --- | --- | --- | --- | --- |
| `pages\dashboard.md` | Complete | P1 | Verify theme application + nav breakpoints during P0 fix sweep |  | 2026-04-15 |
| `pages\programs.md` | Complete | P1 | Decide SSR vs SPA theme parity expectations; align nav/wayfinding |  | 2026-04-15 |
| `pages\applications-list.md` | Complete | P1 | Standardize breadcrumb + light/dark surfaces; compact filter layout |  | 2026-04-15 |
| `pages\application-detail.md` | Complete | P1 | Breadcrumb truncation + theme surface consistency; de-emphasize N/A fields |  | 2026-04-15 |
| `pages\application-form.md` | Complete | P1 | Reduce above-the-fold density (collapse advanced filters) + theme parity |  | 2026-04-15 |
| `pages\documents-list.md` | Complete | P1 | Theme parity + compact filters; verify table behavior on narrow widths |  | 2026-04-15 |
| `pages\document-detail.md` | Complete | P0 | Fix inline PDF preview failing; then improve error-state recovery actions |  | 2026-04-15 |
| `pages\calendar.md` | Complete | P1 | Align Dark mode parity across SPA pages; consider sticky/compact filters |  | 2026-04-15 |
| `pages\notifications.md` | Complete | P1 | Theme parity + compact filters; clarify action hierarchy (bulk vs item) |  | 2026-04-15 |
| `pages\profile.md` | Complete | P1 | Theme parity; verify long-form mobile ergonomics |  | 2026-04-15 |
| `pages\settings.md` | Complete | P1 | Fix theme application consistency across routes; consider sticky actions on mobile |  | 2026-04-15 |
| `pages\preferences.md` | Complete | P1 | Decide SSR Preferences vs SPA Settings consolidation/redirect |  | 2026-04-15 |
| `pages\sessions.md` | Complete | P1 | Decide SSR vs SPA ownership; align breadcrumb/theme conventions |  | 2026-04-15 |
| `pages\admin-dashboard.md` | Complete | P1 | Decide SSR vs SPA admin surface; align nav/theme conventions |  | 2026-04-15 |
| `pages\admin-analytics.md` | Complete | P1 | Decide SSR vs SPA analytics surface; verify responsive behavior |  | 2026-04-15 |
| `pages\coordinator-dashboard.md` | Complete | P1 | Decide SSR vs SPA coordinator overview; align wayfinding/theme |  | 2026-04-15 |
| `pages\coordinator-review-queue.md` | Complete | P1 | Compact filters + fix theme parity/background consistency |  | 2026-04-15 |
| `pages\coordinator-workload.md` | Complete | P1 | Align theme parity across staff pages; add empty-state guidance |  | 2026-04-15 |
| `pages\notification-routing.md` | Complete | P1 | Verify responsive table behavior; add anchors/TOC if needed |  | 2026-04-15 |
| `pages\exchange-agreements.md` | Complete | P1 | Collapse advanced filters; fix theme parity/background consistency |  | 2026-04-15 |
| `pages\agreement-documents.md` | Complete | P1 | Compact filters; fix theme parity/background consistency |  | 2026-04-15 |

## Page index (files)
- `pages\dashboard.md`
- `pages\programs.md`
- `pages\applications-list.md`
- `pages\application-detail.md`
- `pages\application-form.md`
- `pages\documents-list.md`
- `pages\document-detail.md`
- `pages\calendar.md`
- `pages\notifications.md`
- `pages\profile.md`
- `pages\settings.md`
- `pages\preferences.md`
- `pages\sessions.md`
- `pages\admin-dashboard.md`
- `pages\admin-analytics.md`
- `pages\coordinator-dashboard.md`
- `pages\coordinator-review-queue.md`
- `pages\coordinator-workload.md`
- `pages\notification-routing.md`
- `pages\exchange-agreements.md`
- `pages\agreement-documents.md`

