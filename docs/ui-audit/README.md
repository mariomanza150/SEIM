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
| `pages\dashboard.md` | In progress |  | Fill **Observed/Issues** + top P0/P1/P2; capture 1 screenshot per theme |  | 2026-04-10 |
| `pages\programs.md` | In progress |  | Audit `/programs/` and `/seim/programs/compare`; capture breadcrumb + layout notes |  | 2026-04-10 |
| `pages\applications-list.md` | In progress |  | Audit both Django + Vue list; note table density + responsive behavior |  | 2026-04-10 |
| `pages\application-detail.md` | Not started |  |  |  |  |
| `pages\application-form.md` | Not started |  |  |  |  |
| `pages\documents-list.md` | Not started |  |  |  |  |
| `pages\document-detail.md` | Not started |  |  |  |  |
| `pages\calendar.md` | Not started |  |  |  |  |
| `pages\notifications.md` | Not started |  |  |  |  |
| `pages\profile.md` | Not started |  |  |  |  |
| `pages\settings.md` | Not started |  |  |  |  |
| `pages\preferences.md` | Not started |  |  |  |  |
| `pages\sessions.md` | Not started |  |  |  |  |
| `pages\admin-dashboard.md` | Not started |  |  |  |  |
| `pages\admin-analytics.md` | Not started |  |  |  |  |
| `pages\coordinator-dashboard.md` | Not started |  |  |  |  |
| `pages\coordinator-review-queue.md` | Not started |  |  |  |  |
| `pages\coordinator-workload.md` | Not started |  |  |  |  |
| `pages\notification-routing.md` | Not started |  |  |  |  |
| `pages\exchange-agreements.md` | Not started |  |  |  |  |
| `pages\agreement-documents.md` | Not started |  |  |  |  |

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

