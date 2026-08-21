> **Snapshot at test time** � ports/URLs reflect the environment when this QA run was recorded.

# Manual QA — 2026-08-18 (checking, actions, statuses, documents)

**Stack:** Compose `seim-localprod` @ `http://localhost:8020`  
**Do not recreate** `seim-web-local-prod`.

Coordinator walked Vienna application `0e4c6efc-206a-4bb6-a203-c569a542a0de` (DEMO-SEED Resubmit - University of Vienna). Student then verified visibility. Admin opened workflow editor.

## Coordinator (pass)

- Status **Submitted → Under review** via sidebar Update status. Badge **Under review**.
- Public comment posted; private internal rank note posted (staff-only badge).
- Transcript `b73ce5b0-7290-4557-acb4-b05b3a3fd784` PDF preview, type **Academic transcript**, **Mark valid** succeeded.

## Student (pass)

- Public application comment visible; private rank note hidden (no Staff only).
- Status/timeline **Under review** (not `under_review`).
- Transcript preview; public document comment visible; no coordinator actions.
- Passport still **Resubmission needed**.

## Admin workflow (pass, no executable actions)

- Vienna: **No workflow configured for this program.**
- DAAD nominated `68696218-040f-4fa2-8259-0b1527547451`: definition **Demo Application Workflow**, state **Nominated**, **No workflow actions available** (seed `engine_state` stub, `available_actions: []`).

## Defects fixed this pass

- **MQ-037** review history slug `valid` → **Valid**
- **MQ-038** comment/uploader usernames → **Coordinator User** / **Student User**
- **MQ-039** mark invalid: checklist **Invalid** (not Pending review); student can replace without a separate resubmission request; document page status **Invalid** (not Pending)
