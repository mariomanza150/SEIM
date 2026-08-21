# UX themes and good-to-haves

_Captured 2026-08-20 from the polish backlog (not a rebuild). Canonical product state: [`gap-audit-2026-08-20.md`](gap-audit-2026-08-20.md), [`feature-tracking.md`](feature-tracking.md), [`ui-audit/`](ui-audit/). April UI audit is stale in places (dark-mode page bg, PDF preview recovery); re-verify before treating old P0/P1 as open. Admin console (`/seim/admin/*`) was never in that audit._

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

- Collapsible/sticky compact filters on Applications, Documents, Notifications, Review queue, Agreements, Agreement documents ([`ui-audit/p1-deferred.md`](ui-audit/p1-deferred.md)).
- Breadcrumb truncation + shared styling (application detail program name).
- Re-verify workflow editor Validate overlay + form-builder label focus ([gap audit unfiled nits](gap-audit-2026-08-20.md)); ship only if still broken.
- Empty-state copy on workload, nominations, admin catalogs.
- Admin console pass: `AdminWorkflowEditor.vue`, `AdminDynformEditor.vue`, catalogs hub — overlay z-index, focus, save affordances.

**Tier 1 — daily use**

- **SSR vs SPA:** Preferences → Settings; leftover sessions / coordinator overview / analytics bookmarks → SPA (see mapping below). Stop dual theming.
- Student apply: collapse program filters so program select is above the fold ([`ui-audit/pages/application-form.md`](ui-audit/pages/application-form.md)).
- Eligibility “fix list”: ordered gaps with links to Profile / upload.
- Document checklist as a persistent progress rail on application detail.
- Staff review: multi-select + next/prev (not in tracker).
- Scholarship ruleset editor ([`feature-tracking.md`](feature-tracking.md) Phase-1 backlog).

**Tier 2 — already in tracker**

- ~~Eligibility rulesets: richer JSON schema / versioning~~ — shipped 2026-08-20 (document schema v2).
- Full manual a11y audit (P2 Remaining).
- Richer partner document workflows — applicant checklist visibility (P3 Remaining; agreement upload/download + supersede/version shipped).
- Eligibility step-level document gates in preview (P3).
- Cross-institution communication hub (P3 — large; not “UX polish”).
- Google Calendar OAuth2 (P2) — skip unless explicit product bet; ICS/webcal is enough.
- Predictive warehouse (P3) — skip; SPA forecasts exist.

**Tier 3 — later / optional**

- Command palette for staff/admin.
- Review-queue split pane.
- First-run tours.
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

One **density + wayfinding** slice: shared compact filter bar + breadcrumb component on the six list pages + application form program panel. No new product features.
