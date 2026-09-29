# UX themes and good-to-haves

_Captured 2026-08-20 from the polish backlog (not a rebuild). Updated 2026-08-31 after Tier 0+1 remaining polish. Canonical product state: [`gap-audit-2026-08-20.md`](gap-audit-2026-08-20.md), [`feature-tracking.md`](feature-tracking.md), [`ui-audit/`](ui-audit/). April UI audit is stale in places (dark-mode page bg, PDF preview recovery); re-verify before treating old P0/P1 as open. Admin console (`/seim/admin/*`) was never in that audit._

Core (apply, review, documents, partner portal, admin catalogs/forms/workflows) is **Implemented**. Open MQ list is empty. Treat this as **polish + expansion**, not MVP.

**Out of scope here:** Calendar OAuth, communication hub, warehouse, i18n beyond en/es, rewriting Oct-2025 [`docs/roadmap.md`](../roadmap.md) / [`docs/backlog.md`](../backlog.md).

## Themes

1. **Results first.** One row of primary filters; advanced + presets collapsed by default.
2. **One surface per job.** SPA is canonical for authenticated work. Leftover SSR bookmarks redirect or are documented as leftover — no dual theming.
3. **Wayfinding that survives long names.** Shared breadcrumb: ellipsis + tooltip, theme tokens.
4. **Empty and blocked states that say what to do.** Primary CTA + why (eligibility, waitlist, missing docs, unpublished workflow).
5. **Admin tools are first-class SPA.** Same tokens as student/staff. Form builder focus, BPMN overlay vs toasts, catalogs IA.
6. **A11y as a pass, not a foundation.** Skip link, `lang`, focus rings, en/es exist. Remaining is a manual WCAG sweep.
7. **Staff speed.** Bulk actions, keyboard in queues, optional split view — after density, not instead of it.

## Ranked backlog

**Tier 0 — cheap UX wins**

- ~~Collapsible/sticky compact filters on Applications, Documents, Notifications, Review queue, Agreements, Agreement documents~~ — shipped (`CompactFilterBar`).
- ~~Breadcrumb truncation + shared styling (application detail program name)~~ — shipped (`PageBreadcrumb` truncate).
- ~~Re-verify workflow editor Validate overlay + form-builder label focus~~ — re-verified 2026-08-31; overlay z-index + label focus already fixed; no further change.
- ~~Empty-state copy on workload, nominations, admin catalogs~~ — shipped 2026-08-31 (CTAs + create form visible when catalogs empty).
- ~~Admin console pass: `AdminWorkflowEditor.vue`, `AdminDynformEditor.vue`, catalogs hub~~ — overlay/focus/save already in place; catalogs empty CTA shipped 2026-08-31.
- ~~Confirm dialog i18n defaults + focus trap~~ — shipped 2026-08-31.
- ~~ToeflPractice on `PageStateShell`~~ — shipped 2026-08-31.

**Tier 1 — daily use**

- ~~**SSR vs SPA:** Preferences → Settings; leftover sessions / coordinator overview / analytics bookmarks → SPA~~ — shipped (Vue redirects + `core/legacy_spa_urls.py` + analytics HTML views redirect to forecasts/dashboard).
- ~~Student apply: collapse program filters so program select is above the fold~~ — shipped (program select first; filters in collapsed advanced).
- ~~Eligibility “fix list”: ordered gaps with links to Profile / upload~~ — shipped (`EligibilityFixList`).
- ~~Document checklist as a persistent progress rail on application detail~~ — shipped (`DocumentProgressRail`).
- ~~Staff review: multi-select + next/prev~~ — multi-select shipped earlier; detail prev/next via `sessionStorage` queue nav shipped 2026-08-31.
- ~~Scholarship ruleset editor~~ — shipped 2026-08-20 (factor max weights MVP; formula/workflow hooks deferred).

**Tier 2 — already in tracker**

- ~~Eligibility rulesets: richer JSON schema / versioning~~ — shipped 2026-08-20 (document schema v2 + apply-time ruleset snapshot freeze).
- Full manual a11y audit (P2 Remaining).
- ~~Richer partner document workflows — applicant checklist visibility~~ — shipped 2026-08-20 (supersede/version + checklist). Staff review of partner uploads remains P3 Remaining.
- ~~Eligibility step-level document gates in preview~~ — shipped 2026-08-20.
- Cross-institution communication hub (P3 — large; not “UX polish”).
- Google Calendar OAuth2 (P2) — skip unless explicit product bet; ICS/webcal is enough.
- Predictive warehouse (P3) — skip; SPA forecasts exist.

**Tier 3 — later / optional**

- ~~Command palette for staff/admin.~~ — shipped (Ctrl/Cmd+K + navbar search; role-filtered routes/actions).
- ~~Review-queue split pane.~~ — shipped (desktop `lg+` list + embedded detail via `?selected=`; mobile keeps full-page open).
- ~~First-run tours.~~ — shipped (role-based ProductTour; Settings replay; `localStorage` completion).
- CMS ↔ SPA token alignment; unlinked `ProgramPage` Compare already known.
- Mobile native app — reject; PWA/responsive SPA is enough.
- Deprecated (stay rejected): e-sign, document intelligence, BI warehouse.

**Quality (not UX)**

- ~~Admin-console Vitest + smoke~~ — shipped 2026-08-20.
- Production ASGI if realtime toasts matter in prod.

## Canonical authenticated surface

SPA under `/seim/` is canonical. Do not add Django HTML dashboards or a second theme. Mapping (also [`SPA_VS_LEGACY.md`](SPA_VS_LEGACY.md), `core/legacy_spa_urls.py`):

| Leftover | Canonical |
| --- | --- |
| `/preferences/`, `/seim/preferences` | `/seim/settings/` |
| `/sessions/`, `/seim/sessions` | `/seim/settings/` (staff session console: `/seim/admin/sessions`) |
| `/coordinator-dashboard/`, `/seim/coordinator-dashboard` | `/seim/dashboard/` (review: `/seim/review-queue/`; workload: `/seim/coordinator-workload/`) |
| `/dashboard/analytics/`, `/seim/analytics` | `/seim/analytics-forecasts/` |
| `/analytics/dashboard/` | `/seim/dashboard/` |
| `/analytics/*-statistics/`, `/analytics/user-activity/`, `/analytics/export-data/` | `/seim/analytics-forecasts/` |

There is no student sessions SPA page (old SSR is unmounted). Bookmarks go to Settings rather than a new page. Admin session list already lives at `/seim/admin/sessions`.

## Suggested next increment

**Tier 2:** full manual a11y audit (WCAG), then staff review of partner-uploaded documents (P3 Remaining). Skip Calendar OAuth / hub / warehouse unless an explicit product bet. Tier 3 command palette, review-queue split pane, and first-run tours are shipped.
