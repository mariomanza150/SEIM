> **Snapshot at test time** � ports/URLs reflect the environment when this QA run was recorded.

# Manual QA — Section 8 lifecycle retest — 2026-08-17 evening

**Date:** 2026-08-17 (evening, local)  
**App:** `http://localhost:8020` (SPA `/seim/`)  
**Stack:** Compose project `seim-localprod` (`docker-compose.local-prod.yml`)  
**Method:** IDE browser MCP. File picker cannot be driven; required docs uploaded with student JWT (`POST /api/documents/`) then verified in the SPA.  
**Did not:** commit  

Screenshots: [`2026-08-17-lifecycle/`](2026-08-17-lifecycle/). Morning Porto §8 remains in [`2026-08-17-fixtures-lifecycle.md`](2026-08-17-fixtures-lifecycle.md).

Credentials: `student@test.com` / `student123`, `coordinator@test.com` / `coordinator123`.

## Applications this pass

| App | Program | Application id | Outcome |
|-----|---------|----------------|---------|
| **A** | Manual QA Mobility 2026 `1b7900bd-4e5c-4c40-93a1-080bb847df2f` | `d78fc22b-4f1e-43c2-9140-1f3e88d0483b` | Draft saved. Docs uploaded + staff-validated. Public comments both roles. **Submit blocked** — no host tree. |
| **B** | Sciences Po Exchange `8455ccac-d178-4b29-8aca-2c5d24b711e1` | `55dfa4b4-c3c7-441a-9ed4-13484c81ad45` | Full lifecycle: draft → docs valid → **submitted** → **approved**. Student inbox and detail match. |

Host cascade on Sciences Po: Sciences Po (France) `200b0912-…` → School of Public Affairs `86df4eda-…` → International Relations `12e9a97d-…`.

## Section 8 results

| ID | Result | Evidence |
|----|--------|----------|
| **8.1** Draft | **Pass** | Student `/seim/applications/new` → drafts for both programs. `8.1-lifecycle-draft.png`. |
| **8.2** Upload | **Pass** | API upload + SPA checklist pending review. Type dropdown includes Kardex/passport (MQ-001 still fixed). `8.2-uploaded.png`. |
| Comments | **Pass** | Student public comment on App A (`8.2-student-comment.png`). Coordinator public comment (`8.4-public-comment.png`). |
| **8.3** Submit | **Pass** on Sciences Po; **Fail** on Manual QA Mobility | Sciences Po UI submit → status **submitted** (`8.3-submitted.png`). App A: `POST …/submit/` **400** `Host destination incomplete or inconsistent: Select a host university/school/academic program before submitting.` UI still showed ~99% ready and Submit enabled. `8.3-host-gate-error.png`. **MQ-2026-08-17-003**. |
| **8.3b** Validate | **Pass** | Coordinator mark-valid; App A checklist 2/2 approved. `8.3b-coordinator-validate.png`. Sciences Po transcript (22) + passport (23) via `POST /api/documents/{id}/validate_document/`. |
| **8.4** Coord comment | **Pass** | Public comment on App A. Review queue default filter is **Under review**, so a **submitted** Sciences Po row was hidden until the status filter changed. `8.4-review-queue.png`. |
| **8.5** Student update | **Pass** | App A coordinator comment visible after student re-login. Sciences Po inbox: submitted (~7m) and approved (~2m). `8.5-sciences-po-notifications.png`. |
| **8.6** Approve | **Pass** | Coordinator set Sciences Po to **approved**. API `status=approved`. `8.6-coordinator-approved.png`. |
| **8.7** Student approved | **Pass** | Student detail `55dfa4b4-…`: green **Approved**, readiness 100%, “Application approved.” No cache clear needed (MQ-002 still holds). `8.7-sciences-po-approved.png`. |

## New issue

**MQ-2026-08-17-003** — Program with no host destination tree still shows a required host cascade; draft save is allowed; readiness can say complete; Submit stays enabled; API rejects submit. Same pattern likely on UAdeC Law mobility (`bed69f53-…`, 0 hosts). Contrast: Porto / Sciences Po / Movilidad have hosts.

## Notes

- Confirm-dialog clicks often look like no-ops in accessibility snapshots; Vue `v-model` on textarea/select sometimes needs native `input`/`change`.
- Do not use `:8001` for this stack (dev/Taiga). Local-prod is **8020**.
