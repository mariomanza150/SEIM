# SEIM API Contracts

**Generated:** 2025-01-27  
**API Version:** 1.0.0  
**Base URL:** `http://localhost:8000/api/` (development)  
**Documentation:** `http://localhost:8000/api/docs/` (Swagger UI)

## Authentication

SEIM uses JWT (JSON Web Token) authentication for API access.

### Get Access Token

```http
POST /api/token/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Refresh Access Token

```http
POST /api/token/refresh/
Content-Type: application/json

{
  "refresh": "your_refresh_token"
}
```

### Using Tokens

Include the access token in the Authorization header:
```http
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## Rate Limiting

- **Anonymous users:** 100 requests/hour
- **Authenticated users:** 1000 requests/hour
- **Burst rate (login/register):** 10 requests/minute

## API Endpoints

### Authentication & User Management

#### Registration
- `POST /api/register/` - Register new user (with burst rate limiting)
  - **Body:** `{username, email, password, ...}`
  - **Response:** `{detail: "Registration successful. Please check your email..."}`

#### Email Verification
- `POST /api/email-verification/` - Verify email address
  - **Body:** `{token: "verification_token"}`
  - **Response:** `{detail: "Email verified successfully..."}`

#### Login
- `POST /api/login/` - User login (with burst rate limiting)
  - **Body:** `{username, password}`
  - **Response:** `{access, refresh, user: {...}}`

#### Password Reset
- `POST /api/password-reset-request/` - Request password reset
- `POST /api/password-reset-confirm/` - Confirm password reset with token

### Accounts

#### Users (Admin Only)
- `GET /api/users/` - List all users
- `GET /api/users/{id}/` - Get user details
- `PUT /api/users/{id}/` - Update user
- `DELETE /api/users/{id}/` - Delete user

#### Profiles
- `GET /api/profiles/` - List profiles (filtered by user permissions)
- `GET /api/profiles/{id}/` - Get profile details
- `PUT /api/profiles/{id}/` - Update profile

#### Roles
- `GET /api/roles/` - List all roles
- `POST /api/roles/` - Create role (admin only)
- `GET /api/roles/{id}/` - Get role details

#### Permissions
- `GET /api/permissions/` - List all permissions
- `GET /api/permissions/{id}/` - Get permission details

#### User Sessions
- `GET /api/user-sessions/` - List user sessions
- `DELETE /api/user-sessions/{id}/` - Revoke session

#### User Settings
- `GET /api/accounts/user-settings/` - Get current user settings
- `PATCH /api/accounts/user-settings/` - Update user settings
  - Appearance settings (theme, font_size, high_contrast, reduce_motion)
  - Notification settings (`email_*`, `inapp_*`) — these gates are enforced server-side for transactional notifications (applications, documents, public document comments, program reminders, agreement-expiration staff alerts). Account-security and verification emails and notification digests do not use this matrix.
  - Privacy settings (profile_public, share_analytics)

#### Dashboard stats
- `GET /api/accounts/dashboard/stats/` - Authenticated. JSON: `{ applications, documents, notifications, pending }`.
  - **Student:** `applications` / `pending` are scoped to the current user (`pending` counts `draft` and `under_review`). `documents` counts documents the student uploaded or that belong to their applications.
  - **Coordinator or admin:** `applications` and `documents` are global totals; `notifications` is still unread for the current user; `pending` counts non-withdrawn applications that are `submitted` or `under_review`, or have at least one unresolved `DocumentResubmissionRequest`.

#### Coordinator workload (staff)
- `GET /api/accounts/dashboard/coordinator-workload/` — **Coordinator or admin** only. JSON:
  - **`you`:** `assigned_pending_review`, `coordinated_programs_pending` (submitted/under_review on programs the user coordinates), `assigned_with_open_resubmit`, `avg_days_in_queue_assigned` (mean days since `submitted_at` for assigned pending apps, or `null`).
  - **`global`** (admins only): `pending_review_total`, `unassigned_pending_review`, `stale_under_review_14d` (still `under_review` with `updated_at` older than 14 days).
  - **`distribution`** (admins only): list of `{ coordinator_id, display_name, assigned_pending_review }` for users with the coordinator role (up to 40, sorted by load).

#### Analytics exports (authenticated)
- `GET /api/analytics/export/` — Download dashboard export. **Query:** same date/program filters as `GET /api/analytics/dashboard/` (`date_start`, `date_end`, `program`). **`export_format`:** omit or `csv` → `text/csv; charset=utf-8` (`analytics-report.csv`); `xlsx` or `excel` → Excel workbook (`analytics-report.xlsx`) with sheets *Metrics*, *Application status*, *Program performance*; `pdf` → `application/pdf` (`analytics-report.pdf`, landscape letter, same three sections as tables). (Do not use query name `format` — reserved by DRF.)

### Exchange Programs

#### Programs
- `GET /api/programs/` - List programs (cached 10min, supports filtering/search)
  - **Filters (django-filter):** `is_active`, `search` (name/description via `ProgramFilter`), `name`, `description`, `start_date_after`, `start_date_before`, `end_date_after`, `end_date_before`, `min_gpa_min`, `min_gpa_max` (match programs by required minimum GPA bounds), `required_language`, `min_language_level` (CEFR), `min_age_min`, `max_age_max`, `recurring`, `auto_reject_ineligible`, `accepting_applications=true` (open date null or ≤ today, deadline null or ≥ today), `ordering`.
  - **Search (DRF):** `?search=` also matches `name` and `description` when used with list view.
  - **Ordering:** `name`, `start_date`, `end_date`, `created_at`
- `GET /api/programs/{id}/` - Get program details (cached 10min)
- `POST /api/programs/` - Create program (admin only)
- `PUT /api/programs/{id}/` - Update program (admin only)
- `DELETE /api/programs/{id}/` - Delete program (admin only)
- `GET /api/programs/active/` - Get only active programs (cached 10min)
- `POST /api/programs/{id}/clone/` - Clone existing program (admin only)
  - Creates copy with " (Copy)" appended to name, marked inactive
- `GET /api/programs/{id}/check_eligibility/` - Check if current user is eligible
  - Returns detailed eligibility status with requirement checks
- **Vue program comparison:** the SPA route `/programs/compare` aggregates fields from repeated list calls (`is_active=true`, paginated) for side-by-side display; no separate comparison API.

#### Applications
- `GET /api/applications/` - List applications (filtered by user role)
  - **Staff / coordinator queue filters (query params, combinable):** `pending_review=true` (status `submitted` or `under_review`), `needs_document_resubmit=true` (open `DocumentResubmissionRequest` on any application document), `assigned_to_me=true` (assigned coordinator is the current user). Existing filters such as `search`, `status`, and `ordering` still apply.
  - **List/detail extras:** `student_display_name`, `student_email`, `program_name` on each application for display in staff views.
  - **`readiness`** (each item): `{ score, level, headline, window_open, deadline_days, document_counts }`. Levels: `done` (non-draft), `blocked` (draft + window closed), `ready`, `attention`, `ok`. List responses omit dynamic-form DB lookups (`include_dynamic_form=False`); detail includes program form completion in the score.
- `GET /api/applications/{id}/` - Get application details
- `POST /api/applications/` - Create application (students only)
  - Validates eligibility before creation
  - Supports dynamic form data (fields prefixed with `df_`)
- `PUT /api/applications/{id}/` - Update application
- `DELETE /api/applications/{id}/` - Delete application
- `POST /api/applications/{id}/submit/` - Submit application (changes status to "submitted")
- `POST /api/applications/{id}/withdraw/` - Withdraw application

#### Exchange agreements (staff)
- `GET /api/exchange-agreements/` - List operational agreements (coordinator/admin). **Filters:** `status`, `agreement_type`, `program` (UUID, linked program), `partner` (icontains on partner institution), `end_date_before`, `end_date_after`, `expiring_within_days` (active agreements with `end_date` within N days), `ordering`, plus `search` across title/partner/notes.
- `POST /api/exchange-agreements/` - Create agreement
- `GET /api/exchange-agreements/{id}/` - Retrieve
- `PUT/PATCH/DELETE /api/exchange-agreements/{id}/` - Update/delete

#### Application Statuses
- `GET /api/application-statuses/` - List all application statuses
- **Statuses:** draft, submitted, under_review, approved, rejected, completed, cancelled

#### Comments
- `GET /api/comments/` - List comments (filtered by user permissions)
- `POST /api/comments/` - Create comment on application
- `GET /api/comments/{id}/` - Get comment details
- `PUT /api/comments/{id}/` - Update comment
- `DELETE /api/comments/{id}/` - Delete comment

#### Timeline Events
- `GET /api/timeline-events/` - List timeline events for applications
- `GET /api/timeline-events/{id}/` - Get timeline event details

#### Saved Searches
- `GET /api/saved-searches/` - List user's saved searches
- `POST /api/saved-searches/` - Create saved search
  - **Types:** `program`, `application`, `exchange_agreement`, `document`, `agreement_document`
  - **Body:** `{name, search_type, filters: {...}, is_default}`
- `GET /api/saved-searches/{id}/` - Get saved search
- `PUT /api/saved-searches/{id}/` - Update saved search
- `DELETE /api/saved-searches/{id}/` - Delete saved search
- `POST /api/saved-searches/{id}/apply/` - Returns `{ search_type, filters, name }` for the client to apply (Vue review queue uses `filters` from the list/detail payload directly).
- `POST /api/saved-searches/{id}/set_default/` - Marks this preset as default for its `search_type` (clears other defaults of that type for the same user).
- **Review queue (`search_type=application`)** — `filters` keys used by the SPA: `search`, `status`, `ordering`, `pending_review`, `needs_document_resubmit`, `assigned_to_me` (booleans). Legacy `status_name` is accepted when loading.
- **`search_type=exchange_agreement`** — SPA keys: `search`, `status`, `agreement_type`, `program`, `partner`, `end_date_before`, `end_date_after`, `expiring_within_days`, `ordering`.
- **`search_type=document`** — application document list: `application`, `type` (document type id), `valid` (`""` | `"true"` | `"false"`, maps to `is_valid`), `ordering`.
- **`search_type=agreement_document`** — agreement repository list: `search`, `agreement`, `category`, `current_only` (boolean), `ordering`.
- **`search_type=program`** — new-application program list filters: `search`, `required_language`, `min_language_level`, `start_date_after`, `start_date_before`, `min_gpa_max` (number or empty), `accepting_applications` (boolean), `ordering` (e.g. `name`, `-start_date`). Used by the Vue application form presets; same keys as `GET /api/programs/` filter params except `is_active` (always applied client-side).

#### Calendar events (read-only)
- `GET /api/calendar/events/` — Authenticated. Returns a JSON **array** of FullCalendar-style events: `id`, `title`, `start` (ISO datetime), optional `end`, `allDay`, `className`, `backgroundColor`, `borderColor`, optional `spa_path` (path for Vue `router.push`, e.g. `/applications/<uuid>/`).
  - **Query:** `start`, `end` (ISO range). **`type`:** `program` (program run dates only), `deadline` (program application open/close dates), `application` (student’s apps, or all apps for staff; date uses program apply-by when status is draft/submitted/under_review and deadline exists, else program start), `agreement` (staff: agreement `end_date` in range; coordinators limited to agreements linked to their programs), `all` (union of applicable types).
  - **Default** (omit `type`): `program` + `deadline` + `application` + `agreement` (staff only).
- `GET /api/calendar/events/subscribe-token/` — Authenticated (JWT). Returns `{ ics_url, webcal_url }` absolute URLs embedding a signed `token` query param for the personal feed below.
- `GET /api/calendar/subscribe.ics` — **No JWT.** Query `token` (from `subscribe-token`). Returns `text/calendar` (iCalendar) for ~90 days past through 730 days future with `type=all` visibility rules for that user. Treat the URL as a secret.

### Documents

#### Document Types
- `GET /api/document-types/` - List document types
- `POST /api/document-types/` - Create document type (admin only)
- `GET /api/document-types/{id}/` - Get document type details

#### Documents
- `GET /api/documents/` - List documents (filtered by user permissions). **Query filters:** `application` (UUID), `type` (document type id), `is_valid` (boolean), `ordering` (`created_at`, `validated_at`).
- `POST /api/documents/` - Upload document
  - **Body:** `{application, type, file, ...}`
  - Supports file upload with validation
- `GET /api/documents/{id}/` - Get document details
- `GET /api/documents/{id}/preview/` - Stream the stored file for inline preview (JWT/session auth; same access rules as detail; `Content-Disposition: inline`)
- `PUT /api/documents/{id}/` - Update document
- `DELETE /api/documents/{id}/` - Delete document

#### Agreement documents (staff repository)
- `GET /api/agreement-documents/` - List files linked to exchange agreements (coordinator/admin). **Filters:** `agreement`, `category`, `current_only=true` (exclude superseded), `ordering`, plus `search`.

#### Document Validation
- `GET /api/document-validations/` - List document validations
- `POST /api/documents/{id}/validate/` - Validate document (coordinator/admin only)
  - Triggers virus scan and integrity check

#### Document Resubmissions
- `GET /api/document-resubmissions/` - List resubmission requests
- `POST /api/document-resubmissions/` - Request document resubmission
- `PUT /api/document-resubmissions/{id}/resolve/` - Mark resubmission as resolved

#### Document Comments
- `GET /api/document-comments/` - List comments on documents
- `POST /api/document-comments/` - Add comment to document
- `GET /api/document-comments/{id}/` - Get comment details
- `PUT /api/document-comments/{id}/` - Update comment
- `DELETE /api/document-comments/{id}/` - Delete comment

### Notifications

#### Notifications
- `GET /api/notifications/` - List user's notifications
  - **Filters:** `is_read`, `category`, `notification_type`
  - **Ordering:** `-sent_at` (newest first)
- `GET /api/notifications/{id}/` - Get notification details
- `PUT /api/notifications/{id}/mark-read/` - Mark notification as read
- `DELETE /api/notifications/{id}/` - Delete notification

**Notification Categories:**
- `info` - Information
- `success` - Success
- `warning` - Warning
- `error` - Error

**Notification Types:**
- `in_app` - In-app only
- `email` - Email only
- `both` - Both in-app and email

#### Notification Types
- `GET /api/notification-types/` - List notification types
- `GET /api/notification-types/{id}/` - Get notification type details

#### Notification Preferences
- `GET /api/notification-preferences/` - List user's notification preferences
- `POST /api/notification-preferences/` - Create/update preference
- `PUT /api/notification-preferences/{id}/` - Update preference
- **Optional opt-out by type name:** internal sends may pass a `NotificationType` key (`preference_key`) so `enabled=false` suppresses that category entirely (in addition to the UserSettings email/in-app matrix).

#### Reminders
- `GET /api/reminders/` - List user's reminders
- `POST /api/reminders/` - Create reminder
  - **Event Types:** `application_deadline`, `document_deadline`, `program_start`, `program_end`, `custom`
- `GET /api/reminders/{id}/` - Get reminder details
- `PUT /api/reminders/{id}/` - Update reminder
- `DELETE /api/reminders/{id}/` - Delete reminder

### Analytics

#### Reports
- `GET /api/reports/` - List reports
- `POST /api/reports/` - Generate report (admin only)
- `GET /api/reports/{id}/` - Get report details

#### Metrics
- `GET /api/metrics/` - List metrics
- `GET /api/metrics/{id}/` - Get metric details

#### Dashboard Configs
- `GET /api/dashboard-configs/` - List dashboard configurations
- `POST /api/dashboard-configs/` - Create dashboard config
- `GET /api/dashboard-configs/{id}/` - Get dashboard config
- `PUT /api/dashboard-configs/{id}/` - Update dashboard config

#### Admin Dashboard
- `GET /api/admin/dashboard/` - Get admin dashboard metrics (admin only)
  - Returns real-time system metrics, application statistics, etc.

### Application Forms

#### Form Types
- `GET /api/form-types/` - List form types
- `POST /api/form-types/` - Create form type
- `GET /api/form-types/{id}/` - Get form type details
- `PUT /api/form-types/{id}/` - Update form type

#### Form Submissions
- `GET /api/submissions/` - List form submissions
- `POST /api/submissions/` - Submit form
- `GET /api/submissions/{id}/` - Get submission details

## Pagination

All list endpoints support pagination:
- Default page size: 20 items per page
- Query parameters: `page`, `page_size`

**Example:**
```http
GET /api/programs/?page=2&page_size=50
```

**Response:**
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/programs/?page=3",
  "previous": "http://localhost:8000/api/programs/?page=1",
  "results": [...]
}
```

## Filtering

Many endpoints support filtering using Django Filter Backend:
- Use query parameters to filter results
- Example: `GET /api/programs/?is_active=true&start_date_after=2025-01-01&accepting_applications=true`

## Search

Endpoints with search support:
- **Programs:** `?search=term` (searches name, description)
- Use `search` query parameter

## Ordering

Endpoints with ordering support:
- Use `ordering` query parameter
- Example: `GET /api/programs/?ordering=-created_at,name`
- Prefix with `-` for descending order

## Error Responses

Standard error response format:
```json
{
  "detail": "Error message",
  "code": "error_code"
}
```

**Status Codes:**
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (authentication required)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error

## Response Caching

Some endpoints have response caching enabled:
- **Programs list/retrieve:** 10 minutes
- Cache is invalidated on mutations (create/update/delete)

## WebSocket Support

Real-time notifications via WebSocket:
- Connection: `ws://localhost:8000/ws/notifications/`
- Requires JWT authentication in connection header
- Sends notification updates in real-time
- **Server → client message types:**
  - `notification.new` — `{ notification: { id, title, message, category, action_url, action_text, sent_at, is_read, data? } }`
  - `application.sync` — `{ application_id, change_type, document_id? }` — hints the SPA to refetch the open application/document detail (no DB row); used for comments, status changes, document validation, etc.

---

_Generated using BMAD Method `document-project` workflow (Exhaustive Scan)_
