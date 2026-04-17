## SPA Admin Console (Vue)

This project now includes an **admin-only** section inside the Vue SPA for managing:

- **Programs** (CRUD + clone + attach dynamic form + bind workflow version)
- **Forms** (`FormType` CRUD with JSON schema / UI schema / step definitions editing)
- **Workflows** (BPMN modeler with versioning, validate, publish)
- **Applications (admin view)** (edit assignment/withdrawn + view workflow actions + trigger actions)

### Routes

All routes are served under the SPA base (`/seim/`):

- **Programs**: `/seim/admin/programs`
- **Forms**: `/seim/admin/forms`
- **Workflows**: `/seim/admin/workflows`
- **Workflow editor**: `/seim/admin/workflows/<workflow_id>`
- **Application admin view**: `/seim/admin/applications/<application_id>`

Routes are guarded via router meta `adminOnly` and require the authenticated user to be **SEIM admin**.

### Backend APIs used

- Programs: `/api/programs/`
- Forms: `/api/application-forms/form-types/`
- Workflows: `/api/workflows/`, `/api/workflow-versions/`
- Application workflow runtime:
  - Snapshot: `/api/applications/<id>/workflow/`
  - Action: `/api/applications/<id>/workflow/action/`

### Notes on workflow enforcement (MVP)

- Programs may bind to a **published** workflow version via `Program.workflow_version`.
- The runtime surfaces **READY manual tasks** as `available_actions`.
- The application status is derived when a manual task name matches an `ApplicationStatus.name` (convention).

### Running tests

- Vue unit tests:

```powershell
npm --prefix frontend-vue run test:run
```

- Backend tests:
  - The test suite expects a working database configuration per `seim\settings\test.py`.
  - In Docker-based setups, run tests inside the `web` container (recommended).

