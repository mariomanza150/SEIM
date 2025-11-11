# SEIM User Stories

> **Note:** Each user story is tagged with its corresponding roadmap phase and whether it is part of the MVP or planned for a future release.

## Roles [Phase 1, MVP]
- **Student**: Can view available exchange programs, apply, fill forms, upload documents, and track applications. [MVP]
- **Coordinator**: Can view/review applications and documents, change application status, leave comments, and submit new programs in draft. [MVP]
- **Admin**: Has all coordinator permissions, plus can configure exchange programs, application forms, document types, allowed formats, and override application status. Can view analytics dashboard. [MVP, Analytics dashboard: Future]

---

## Application Detail & Status Flow [Phase 1, MVP]
- As a coordinator/admin, I want to view a text timeline/history of all status changes and comments for each application. [MVP]
- As a student, I want to withdraw my application if it is still in draft status. [MVP]
- As a coordinator, I want to view cancelled/withdrawn applications. [MVP]
- As a coordinator/admin, I want to add comments to applications, with the option to mark them as private (internal-only) or visible to students. [MVP]
- As a student, I want to respond once to coordinator/admin comments for clarification, but not engage in a chat. [MVP]

## Document Upload & Review [Phase 1, MVP]
- As a student, I want to upload documents using drag-and-drop or file selection. [MVP]
- As a student, I can replace or delete documents before submission, but after submission, I can only replace a document if a coordinator requests resubmission. [MVP]
- As a coordinator/admin, I want to request specific document resubmissions and leave comments on documents. [MVP]
- As a coordinator/admin, I do not need document versioning; only the latest version is kept. [MVP]

## Program Management (Admin/Coordinator) [Phase 1, MVP]
- As an admin, I want to set application open/close dates and configure recurring programs (e.g., each semester). [MVP]
- As an admin, I want to copy details from an existing program to speed up creation. [Future]
- As an admin, I want to define eligibility criteria (e.g., GPA, language) tied to form answers, so the system can auto-reject ineligible students. [Future]
- As a coordinator, I want to submit new programs in draft mode for later approval. [MVP]

## Application Form Builder (Admin) [Phase 1, MVP]
- As an admin, I want to use a visual form builder (powered by django-dynforms) to create/edit dynamic application forms with a wide range of field types. [MVP]
- As an admin, I want to set comprehensive validation rules (required, min/max, regex, etc.) for each field. [MVP]
- As an admin, I want to define conditional logic for fields (e.g., show/hide fields based on answers). [Future]
- As an admin, I want to reuse field definitions and copy forms between programs. [Future]

## Notifications [Phase 2, Future]
- As a user, I want notifications to include direct links to the relevant application or program. [Future]
- As a coordinator/admin, I want to receive notifications for new applications and status changes, with summaries for multiple events. [Future]

## Analytics [Phase 3, Future]
- As an admin, I want to view analytics with filters (by program, date, status) and see key metrics (students, ongoing, approved, rejected). [Future]
- As a coordinator, I want analytics for only the programs I manage. [Future]

## Technology [Phase 1, MVP]
- The application form builder will use [django-dynforms](https://github.com/michel4j/django-dynforms) for dynamic form creation and management. [MVP]

## Internationalization [Phase 5, Future]
- As a user, I want to use the system in my preferred language from the start. [Future]

---

## Authentication & Account Management [Phase 1, MVP]
- As a student, I want to register using my institutional email so I can access SEIM for my university. [MVP]
- As a student, I want to receive an email verification link and only be able to log in after verifying my email. [MVP]
- As a user, I want to log in using email and password (no social login or SSO in MVP). [MVP]
- As a user, I want to reset my password via email if I forget it. [MVP]
- As a user, I want password strength requirements enforced for security. [MVP]
- As a user, I want my account to be locked after 10 failed login attempts in an hour, and be able to reactivate via email or admin intervention. [Future]
- As an admin, I want to create coordinator/admin accounts and reactivate locked accounts. [Future]
- As a user, I want to update my profile info (name, password, secondary email) after registration, but my primary email must remain institutional. [MVP]
- As a user, I want to select my preferred language on authentication screens. [Future]

## Technology & Future Plans [Phase 4/5, Future]
- Social login (Google, Microsoft, etc.) and MFA are desired for future versions, but not included in the MVP. [Future]
- No SSO support is planned due to institutional system diversity. [Future]

These user stories will guide the development and UX of SEIM. 