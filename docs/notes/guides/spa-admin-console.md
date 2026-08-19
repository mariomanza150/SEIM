## SPA Admin Console (Vue)

This project now includes an **admin-only** section inside the Vue SPA for managing:

- **Programs** (CRUD + clone + attach dynamic form + bind workflow version)
- **Catalogs** (home profile lists + host destinations hub)
- **Grade scales** (scales, values, translations)
- **Users and roles**
- **Workflow catalogs** (application status slugs and notification types)
- **Forms** (`FormType` CRUD with JSON schema / UI schema / step definitions editing)
- **Workflows** (BPMN modeler with versioning, validate, publish)
- **Applications (admin view)** (edit assignment/withdrawn + view workflow actions + trigger actions)

### Routes

All routes are served under the SPA base (`/seim/`):

- **Programs**: `/seim/admin/programs`
- **Catalogs**: `/seim/admin/catalogs`
- **Grade scales**: `/seim/admin/grades`
- **Users**: `/seim/admin/users`
- **Workflow catalogs**: `/seim/admin/workflow-catalogs`
- **Forms**: `/seim/admin/forms`
- **Workflows**: `/seim/admin/workflows`
- **Workflow editor**: `/seim/admin/workflows/<workflow_id>`
- **Application admin view**: `/seim/admin/applications/<application_id>`

Routes are guarded via router meta `adminOnly` and require the authenticated user to be **SEIM admin**.

### Backend APIs used

- Programs: `/api/programs/`
- Forms: `/api/application-forms/form-types/`
- Workflows: `/api/workflows/`, `/api/workflow-versions/`
- Application statuses: `/api/application-statuses/`
- Notification types: `/api/notification-types/`
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

