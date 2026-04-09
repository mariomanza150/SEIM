# SEIM Feature Tracking

_Reconciled into a single canonical tracker on 2026-04-08. Update this file as the source of truth for feature state and priorities._

## 🟢 IMPLEMENTED ✓
| Feature | Module | Status | Last Updated | Notes |
|---------|--------|--------|--------------|-------|
| User authentication and account management | `accounts`, `api` | Implemented | 2026-04-08 | JWT login, registration, profile, permissions, password flows, and account dashboard stats are wired through the API. |
| Role management | `accounts` | Implemented | 2026-04-08 | Student, coordinator, and admin roles are modeled and used across permissions and UI flows. |
| Exchange programs and application workflow | `exchange`, `api` | Implemented | 2026-04-08 | Program catalog, applications, state transitions, timeline events, and coordinator review endpoints exist. |
| Document management | `documents`, `api` | Implemented | 2026-04-08 | Upload, validation, comments, and resubmission APIs are present and used by the application flow. |
| Application comments on detail page | `frontend-vue`, `exchange`, `api` | Implemented | 2026-04-08 | The Vue detail page now shows live comments and can post new comments with author metadata. |
| Notifications center and preferences | `notifications`, `api` | Implemented | 2026-04-08 | Email/in-app notifications, preferences, reminders endpoints, and read-state actions are available. |
| Real-time notification delivery | `notifications`, `seim`, `frontend-vue` | Implemented | 2026-04-08 | WebSocket consumer, JWT middleware, reconnect logic, and Vue toast/dropdown integration are present. |
| Grade translation | `grades` | Implemented | 2026-04-08 | Grade scale and grade value models support international grade conversion logic, and the documented `/grades/api/` endpoints are now exposed and verified. |
| Analytics dashboard core metrics | `analytics` | Implemented | 2026-04-08 | Admin dashboard metrics, activity, alerts, performance, and system info endpoints exist, though some broader analytics/report endpoints remain incomplete. |
| Advanced analytics and report endpoints | `analytics`, `api` | Implemented | 2026-04-08 | Added real `/api/analytics/dashboard/`, detailed report, and CSV export endpoints; replaced remaining analytics stub payloads with service-backed responses. |
| Standalone user settings page | `frontend-vue` | Implemented | 2026-04-08 | Added a dedicated `/settings` page backed by the existing user settings API for appearance, notification, and privacy preferences. |
| Admin export actions | `templates\frontend\admin` | Implemented | 2026-04-08 | Replaced the remaining placeholder admin export actions with working client-side downloads for detailed analytics reports and system info. |
| Vue student/coordinator portal | `frontend-vue` | Implemented | 2026-04-08 | Login, dashboard, applications, documents, notifications, profile, and 404 routes are functional. |
| Wagtail CMS public site | `cms` | Implemented | 2026-04-08 | Public marketing/information pages, navigation, testimonials, programs, movilidad, and convenios templates are present. |
| Dynamic application form builder admin | `application_forms` | Implemented | 2026-04-08 | Form type, submission, schema, and admin-facing builder/list views exist. |
| Dynamic application form consumption in Vue | `application_forms`, `frontend-vue`, `exchange` | Implemented | 2026-04-08 | The SPA now loads program-linked form schemas, renders supported dynamic fields, prefills saved responses on edit, and submits validated `df_*` payloads that persist with the application. |
| Program application windows and deadlines | `exchange`, `cms`, `frontend-vue` | Implemented | 2026-04-08 | Programs now define real open/close dates, the API blocks new applications outside the window, the SPA surfaces window status and disables new submissions, and linked CMS program pages show and respect the operational apply window. |
| Coordinator assignment for programs and applications | `accounts`, `exchange`, `admin UI` | Implemented | 2026-04-08 | Programs can now carry assigned coordinators, applications can carry an explicit coordinator owner, admin/program forms only offer coordinator-role users, and new applications auto-assign when a program has exactly one coordinator. |
| Public program discovery and apply flow | `exchange`, `cms`, `frontend-vue` | Implemented | 2026-04-08 | The public program index now supports search and filtering, renders from linked program data instead of raw child pages, and shows direct apply/sign-in CTAs that preserve the preselected SPA program flow. |
| User settings that visibly change the UI | `frontend-vue`, `accounts` | Implemented | 2026-04-08 | Saved appearance preferences now apply to the SPA shell, including theme, larger font sizes, high contrast, and reduced motion, and the settings page exposes and persists those controls directly. |
| Route and navigation parity across CMS docs and SPA | `docs`, `cms`, `frontend-vue` | Implemented | 2026-04-08 | CMS account navigation now surfaces the active SEIM dashboard/profile/settings routes, the Vue router accepts the legacy `/preferences` path, and the route/docs references now distinguish current SPA paths from legacy Django pages like calendar. |
| Bulk student import workflow | `data_management`, `accounts` | Implemented | 2026-04-08 | Staff data imports now execute a real CSV-backed student import path for `accounts.user`, creating or updating students by email, assigning the student role, updating profile fields, and recording actual import results instead of only queueing a placeholder log. |
| Admin-managed program publishing workflow | `exchange`, `cms`, `admin UI` | Implemented | 2026-04-08 | Program admin: Wagtail edit link, actions to create draft linked `ProgramPage` under the first live program index and to sync operational fields to the CMS (re-publish if already live). Clone-program admin action fixed (assign `cloned_program` before M2M). |
| Exchange agreement lifecycle tracking | `exchange`, `admin UI`, `api` | Implemented | 2026-04-08 | `ExchangeAgreement` model (partner, type, dates, status, notes, optional program links), Django admin with bulk status actions, REST `/api/exchange-agreements/` for coordinators/admins with filters including `expiring_within_days` for active agreements nearing `end_date`. |
| Agreement document repository and classification | `documents`, `exchange`, `admin UI`, `api` | Implemented | 2026-04-08 | `ExchangeAgreementDocument` with category labels, optional `supersedes` chain per agreement/category, staff REST `/api/agreement-documents/` (`current_only`, `agreement`, `category` filters), Django admin list + inline on exchange agreements; uploads reuse application document validation (type/size/virus scan). |
| Agreement expiration reminders for staff | `notifications`, `exchange` | Implemented | 2026-04-08 | Configurable `AGREEMENT_EXPIRATION_REMINDER_DAYS` / `AGREEMENT_EXPIRATION_REMINDER_STATUSES`; daily Celery task `send_agreement_expiration_reminders` + `manage.py send_agreement_expiration_reminders`; in-app + email via `NotificationService` with admin deep link; dedupe via `AgreementExpirationReminderLog`; recipients are admins and coordinators (linked programs when set, else all coordinators). |
| Staff data management tools | `data_management` | Implemented | 2026-04-08 | Staff-only data import/export, cleanup, bulk operations, demo data, and reset-oriented views are present. |
| REST API surface and schema docs | `api`, `seim` | Implemented | 2026-04-08 | Core API routers, JWT endpoints, and OpenAPI documentation are wired and exposed. |
| Configurable multi-step applications | `application_forms`, `exchange`, `frontend-vue` | Implemented | 2026-04-08 | `FormType.step_definitions` + `Application.dynamic_form_current_step`; merged `df_*` saves with per-step validation; full schema validation on submit; `form_schema` / application `dynamic_form_layout` for the Vue wizard (Save & continue, draft save, Back). |
| Required document checklist and completion status | `documents`, `exchange`, `frontend-vue` | Implemented | 2026-04-08 | `Program.required_document_types` (M2M); `document_checklist` on application detail (omitted on list); statuses missing / pending_review / resubmit_requested / approved; submit blocked until all required types are approved; Vue checklist card and disabled submit when incomplete. |
| Real workflow timeline in application detail | `exchange`, `frontend-vue` | Implemented | 2026-04-08 | Application detail loads `/api/timeline-events/?application=&ordering=created_at`; `TimelineEventSerializer` exposes `created_by_name`; default chronological ordering + `OrderingFilter`; list response no longer HTTP-cached so new events show up; Vue maps `event_type` to headings/icons. |
| Rejected document feedback and response notifications | `documents`, `notifications`, `frontend-vue` | Implemented | 2026-04-08 | Resubmission API routes through `DocumentService.request_resubmission` (limits + notify application student); invalid validation and public staff comments notify the student; student file replacement notifies assigned/program coordinators; document detail API returns ordered validations, resubmission requests, and role-filtered comments; Vue document detail shows history, comments, staff actions, and replace-file flow. |
| Coordinator review queue UI | `frontend-vue`, `exchange`, `documents` | Implemented | 2026-04-08 | Staff route `/review-queue` with table view, search/status/sort, and quick filters mapped to `GET /api/applications/?pending_review=true`, `needs_document_resubmit=true`, `assigned_to_me=true`. List serializer adds `student_display_name`, `student_email`, `program_name`. Dashboard link + router guard for coordinator/admin. Unit tests: `tests/unit/exchange/test_filters.py` (`TestApplicationReviewQueueFilters`). |

## 🟡 IN PROGRESS 🔄
| Feature | Module | Status | Started | Assigned |
|---------|--------|--------|---------|----------|
| _None currently assigned_ |  |  |  |  |

## 🔵 PENDING IMPLEMENTATION ⏳
### Priority 1 / MVP

#### Agreements, Programs, and Admin Operations
_All Priority 1 items in this subsection are implemented above._

#### Applications, Documents, and Review Workflow
| Feature | Module | Notes |
|---------|--------|-------|
| Inline document preview and review context | `frontend-vue`, `documents` | Let students and coordinators preview uploaded files in-app and see validation/rejection context without depending on a download-first flow. |
| Live application and document status sync | `exchange`, `notifications`, `frontend-vue`, `documents` | Build application-specific live status UX on top of existing WebSockets so open views refresh and surface status, comments, and document changes without manual reloads. |

#### User Experience, Accessibility, and Engagement
| Feature | Module | Notes |
|---------|--------|-------|
| Action-oriented dashboard with next steps | `frontend-vue`, `exchange`, `documents`, `notifications` | Evolve the dashboard beyond summary counts so students and staff immediately see drafts to finish, missing documents, pending reviews, and unread high-priority updates. |

### Priority 2 / Expansion

#### Applications, Forms, and Eligibility
| Feature | Module | Notes |
|---------|--------|-------|
| Multi-document requirements per application step | `application_forms`, `documents`, `frontend-vue` | Support uploading and validating multiple required documents within each step of an application workflow. |
| Dynamic step builder with reusable templates | `application_forms`, `admin UI`, `exchange` | Let admins compose application flows from reusable step/field templates instead of configuring each application type from scratch. |
| Conditional application logic and branching | `application_forms`, `exchange`, `frontend-vue` | Support conditional fields and step branching based on program type, student answers, or coordinator decisions. |
| Student application readiness scoring | `exchange`, `documents`, `analytics` | Provide a readiness indicator based on missing requirements, document validation state, and deadline proximity. |

#### Programs, Agreements, and Planning
| Feature | Module | Notes |
|---------|--------|-------|
| Program capacity, quotas, and waitlist management | `exchange`, `admin UI`, `frontend-vue` | Track available seats by program and automatically place eligible applicants on a waitlist when capacity is reached. |
| Agreement renewal workflow | `exchange`, `documents`, `notifications`, `admin UI` | Extend agreement tracking with renewal stages, follow-up tasks, and document rollover support for expiring partnerships. |
| Public program comparison experience | `cms`, `exchange`, `frontend-vue` | Let students compare programs side by side by country, dates, language requirements, and deadlines before applying. |
| Advanced program filtering UX | `exchange`, `frontend-vue` | Expand current discovery/search UX once the core application flow is stable. |

#### Staff Operations, Reporting, and Notifications
| Feature | Module | Notes |
|---------|--------|-------|
| Coordinator workload dashboard and SLA tracking | `analytics`, `exchange`, `frontend-vue` | Show review volume, turnaround times, pending bottlenecks, and coordinator workload distribution for operational planning. |
| Advanced notification rules, digests, and reminder scheduling | `notifications`, `accounts`, `admin UI` | Add configurable digest delivery, richer reminder cadences, and role-specific notification rules beyond the current event-based alerts. |
| Saved searches and staff review presets | `frontend-vue`, `exchange`, `documents` | Allow coordinators and admins to save common filters for applications, agreements, and document review queues. |
| Export reports to PDF/Excel | `analytics`, `admin UI` | CSV export is now available through `/api/analytics/export/`; richer PDF/Excel export remains a planned enhancement. |
| Calendar integration for deadlines and milestones | `exchange`, `notifications`, `frontend-vue` | Surface application deadlines, interview dates, and agreement expirations in a calendar view with export/sync options. |

#### User Profile, Localization, and Accessibility
| Feature | Module | Notes |
|---------|--------|-------|
| Multi-language student profile support | `accounts`, `frontend-vue`, `api` | Allow students to record multiple languages and proficiency details instead of a single language value. |
| Internationalization and accessibility pass for Vue UI | `frontend-vue` | Expand language coverage, keyboard accessibility, and inclusive UI patterns across the SPA. |

## 🟠 DESIRED / BACKLOG 💡
### Priority 3 / Advanced Backlog

#### Partner Ecosystem and Collaboration
| Feature | Module | Notes |
|---------|--------|-------|
| Partner institution portal | `accounts`, `exchange`, `documents`, `frontend-vue` | Provide external partner users with limited access to agreements, nominations, required documents, and selected applicant status updates. |
| Cross-institution communication hub | `notifications`, `accounts`, `exchange`, `frontend-vue` | Centralize conversations among students, coordinators, and partner institutions around applications, agreements, and program logistics. |

#### Advanced Workflow Orchestration
| Feature | Module | Notes |
|---------|--------|-------|
| Student nomination and matching workflow | `exchange`, `accounts`, `admin UI` | Support nomination cycles, ranking, partner allocations, and selection matching for institutions with limited slots. |
| Visual workflow designer for applications | `application_forms`, `admin UI` | Give admins a low-code interface to design multi-step application flows, approval paths, and validation gates visually. |
| Electronic signatures for agreements and approvals | `exchange`, `documents`, `admin UI` | Integrate digital signing for agreements, approval letters, and staff sign-off workflows to reduce manual paperwork. |
| Automated eligibility and rules engine | `exchange`, `application_forms`, `accounts` | Evaluate eligibility using configurable academic, language, deadline, and documentation rules before submission or review. |
| Scholarship and funding workflow tracking | `exchange`, `documents`, `analytics`, `frontend-vue` | Track scholarship opportunities, funding applications, required financial documents, and award outcomes alongside exchange applications. |

#### Intelligence, Analytics, and Institutional Reporting
| Feature | Module | Notes |
|---------|--------|-------|
| Advanced document intelligence and extraction | `documents`, `analytics`, `admin UI` | Extract metadata from uploaded documents, flag missing fields, and support smarter classification or duplicate detection. |
| Predictive analytics for demand and bottlenecks | `analytics`, `exchange`, `notifications` | Forecast program demand, review bottlenecks, and likely missed deadlines using historical application and document activity. |
| Institutional reporting warehouse and BI exports | `analytics`, `admin UI`, `api` | Build richer institutional reporting pipelines for trend analysis, accreditation reporting, and external BI tooling integrations. |
## 🔴 DEPRECATED / REJECTED ❌
| Feature | Module | Removed | Reason |
|---------|--------|---------|--------|
| _None recorded_ |  |  |  |

---

*Last updated: 2026-04-08 (coordinator review queue UI)*  
*This file is manually editable; preserve developer changes and update statuses deliberately.*