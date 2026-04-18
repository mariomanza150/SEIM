# Feature Correction Plan: Enhancing Exchange and Application Management

This document outlines the plan to implement several key feature enhancements across the codebase, focusing on refining the structure of Convenios/Agreements, managing student application limits, and standardizing the application start process.

## Phase 1: Data Model Updates (Core & Agreements)

The primary goal is to update the data models to support the new fields and relationships.

### 1. Convenios/Agreements Enhancement
*   **Location:** Define a dedicated `Country` model (e.g., in `accounts/`).
*   **Action:** Add the following fields to the Agreement model:
    *   `university`: CharField.
    *   `country`: ForeignKey to Country model.
    *   `required_gpa`: FloatField.
    *   `language_requirements`: JSONField.
    *   `custom_tags`: ManyToManyField/JSONField for restricted tag selection.
    *   `application_limit`: IntegerField.
    *   `notify_on_limit_reached`: BooleanField.
*   **Dependency Check:** Migration for `Country` model (now in `accounts/`) must be run first.
*   **Action:** Update `Agreement` model (in `exchange/models.py`) to include: `university` (CharField), `country` (ForeignKey to Country model), `required_gpa` (FloatField), `language_requirements` (JSONField), `custom_tags` (ManyToManyField/JSONField for restricted tag selection), `application_limit` (IntegerField), and `notify_on_limit_reached` (BooleanField).
*   **Implementation Detail:** Ensure the `ForeignKey` from `Agreement` -> `Country` correctly links to the `Country` model defined in `accounts/`.
...
*   **Testing:** Create dedicated test files in `tests/unit/` for granular testing of the new constraints, especially for `Agreement` limit checking (N-1, N, N+1).

### 2. Exchange Program Structure Definition
*   **Location:** Review the `ExchangeProgram` model and its relationships.
*   **Action:** Ensure the architecture clearly separates:
    *   **Program-Related Agreements:** Agreements directly linked via a ForeignKey/OneToOne to an `ExchangeProgram`.
    *   **Standalone Agreements:** Agreements not tied to a specific program, retaining their existing structure but being queried separately.
*   **Implementation:** Review/Update the `ExchangeProgram` model to manage a collection of related agreements while maintaining the ability to query standalone agreements.

## Phase 2: Business Logic Implementation

This phase focuses on the complex validation and constraint enforcement.

### 3. Student Application Constraint Enforcement
*   **Location:** Services/Views related to Student Applications (e.g., in `application_forms/` or `exchange/`).
*   **Rule:** Implement logic to check `Semester` and `Student` against the application records.
*   **Action:**
    *   By default, the system must prevent creating a new application if an active record exists for the same student in the same semester.
    *   **Admin Override:** Create an explicit permission/flag check (`is_admin_override: Boolean`) on the Application model. If this flag is true, the check must pass, allowing the creation regardless of existing applications.

### 4. Agreement Limit & Notification System
*   **Location:** Service layer processing application submissions against an Agreement.
*   **Action:**
    *   Before an application is successfully linked to an Agreement, the system must check: `current_applications >= agreement.application_limit`.
    *   If the limit is reached, the transaction must fail, and a notification must be queued/triggered for Coordinators and Admins.
*   **Dependency Check:** Ensure the `notifications` module is used correctly to dispatch these alerts.

## Phase 3: Workflow and UI Updates

### 5. Standardized Application Start Step (Document Generation)
*   **Location:** The frontend/backend flow responsible for initiating a new application (likely involving `application_forms/` and PDF generation utilities).
*   **Goal:** The first, mandatory step must be document upload/submission corresponding to `sample_format_documents\FS-SP.pdf`.
*   **Backend Action:** Update the initial step API endpoint to:
    1.  Accept the file upload for `FS-SP.pdf`.
    2.  Process/store this PDF file as the *generated document* for the application record.
    3.  Validate the presence and correct format of this document before allowing progression to Step 2.

## Testing Strategy (To be updated in Tests/ folder)

*   Update unit tests in `tests/unit/exchange/` and `tests/unit/application_forms/` to cover:
    *   Boundary condition testing for application limits (N-1, N, N+1).
    *   Successful and blocked application submissions based on the new GPA, Country, and Tag constraints on Agreements.
    *   The mandatory validation that the initial application step requires the `FS-SP.pdf` document.


*   **New Loop Prompt:** When a user mentions "follow up" or "check status," redirect them to check the Jira status board or the designated task tracker (e.g., Trello board: `https://trello.com/SEIM-tasks`).
