# SEIM Backlog

This backlog tracks actionable development tasks, prioritized for sprint planning. Each item is linked to a user story, phase, and acceptance criteria. Update status and sprint as work progresses.

| ID    | User Story / Task (summary)                                 | Phase   | Priority | Acceptance Criteria (summary)                                 | Status   | Sprint |
|-------|------------------------------------------------------------|---------|----------|--------------------------------------------------------------|----------|--------|
| US1   | Student can apply to exchange programs                     | 1/MVP   | High     | Student can view/apply, fill forms, upload docs, track status | Done     | 1      |
| US1.1 | Implement student registration and login                    | 1/MVP   | High     | Student can register, verify email, and log in                | Done     | 1      |
| US1.2 | Build student dashboard (list available programs)           | 1/MVP   | High     | Student sees available programs after login                   | Done     | 1      |
| US1.3 | Application form: create, edit, save as draft               | 1/MVP   | High     | Student can fill and save application as draft                | Done     | 1      |
| US1.4 | Application submission and status tracking                  | 1/MVP   | High     | Student submits, sees status updates                          | Done     | 1      |
| US2   | Coordinator reviews and manages applications                | 1/MVP   | High     | Coordinator can view/review, comment, change status           | Done     | 1      |
| US2.1 | Coordinator dashboard: list/review applications             | 1/MVP   | High     | Coordinator sees all assigned applications                    | Done     | 1      |
| US2.2 | Application review: add comments, change status             | 1/MVP   | High     | Coordinator can comment, approve/reject, request changes      | Done     | 1      |
| US3   | Admin configures programs, forms, and document types        | 1/MVP   | High     | Admin can create/edit programs, forms, doc types              | Done     | 1      |
| US3.1 | Program management UI (CRUD)                                | 1/MVP   | High     | Admin can add/edit/delete programs                            | Done     | 1      |
| US3.2 | Form builder integration (django-dynforms)                  | 1/MVP   | High     | Admin can build/edit forms                                    | Done     | 2      |
| US3.3 | Document type management                                    | 1/MVP   | High     | Admin can define allowed document types                       | Done     | 2      |
| US4   | Application workflow: draft → submitted → review → result   | 1/MVP   | High     | State machine enforced, status/history visible                | Done     | 1      |
| US4.1 | Implement application state machine                         | 1/MVP   | High     | Only valid transitions allowed                                | Done     | 1      |
| US4.2 | Application history/audit log                               | 1/MVP   | Medium   | All status changes/comments logged                            | Done     | 2      |
| US5   | Document upload, replace, delete (pre/post submission)      | 1/MVP   | High     | Students can upload/replace/delete docs as per rules          | Done     | 1      |
| US5.1 | Document upload UI and backend                              | 1/MVP   | High     | Drag-and-drop/file select, upload to server                   | Done     | 1      |
| US5.2 | Document validation (type, integrity, virus scan)           | 1/MVP   | High     | Only valid, safe files accepted                               | Done     | 1      |
| US5.3 | Document resubmission flow                                  | 1/MVP   | Medium   | Coordinator can request resubmission, student notified        | Done     | 2      |
| US6   | Email verification and login for students                   | 1/MVP   | High     | Registration, email verify, login, password reset             | Done     | 1      |
| US7   | Admin dashboard for program/application overview            | 1/MVP   | Medium   | Admin dashboard displays key metrics                          | Done     | 2      |
| US8   | Visual form builder for dynamic application forms           | 1/MVP   | Medium   | Admin can build/edit forms with validation                    | Done     | 2      |
| US9   | Notifications for workflow events                           | 2/Future| Medium   | Email/in-app notifications for key events                     | Done     | 3      |
| US10  | Analytics dashboard and exportable reports                  | 3/Future| Low      | Admin/coordinator can view/export analytics                   | Done     | 4      |
| US11  | Internationalization support                                | 5/Future| Low      | Users can select preferred language                           | Planned  | 5      |
| T1    | Set up CI/CD pipeline (lint, test, deploy)                  | 1/MVP   | High     | Automated build, test, deploy on push/PR                      | To Do    | 1      |
| T2    | Write unit and integration tests for all major features     | 1/MVP   | High     | 80%+ coverage, all critical paths tested                      | To Do    | 2      |
| T3    | Update and maintain documentation as features are added     | 1/MVP   | High     | Docs reflect current state, onboarding is up to date          | Done     | 1-5    |

---

**Legend:**
- **Phase:** Roadmap phase (see [roadmap.md](roadmap.md))
- **Priority:** High/Medium/Low (business value, MVP first)
- **Status:** To Do, In Progress, Done, Planned
- **Sprint:** Target sprint (update as needed)

**Current Status Summary:**
- **MVP Features:** 22/22 completed (100%)
- **Future Features:** 4/4 completed (100%)
  - Program Cloning ✅
  - Enhanced Eligibility Criteria ✅
  - Direct Notification Links ✅
  - Enhanced Analytics (previous) ✅
- **Technical Tasks:** 1/3 completed (33%)

**Remaining Work for Production:**
1. **Testing:** Comprehensive test suite (T2)
2. **CI/CD:** Automated deployment pipeline (T1)
3. **Optional:** Internationalization support (US11)

Expand this backlog as new stories/tasks are identified. For full user stories and requirements, see [user_stories.md](user_stories.md). 