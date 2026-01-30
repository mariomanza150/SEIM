# SEIM Data Models

**Generated:** 2025-01-27  
**Database:** PostgreSQL 15+  
**ORM:** Django ORM

## Core Base Models

### UUIDModel
Abstract base model providing UUID primary keys for global uniqueness.
- **Fields:** `id` (UUID, primary key, auto-generated)
- **Usage:** Extended by all domain models

### TimeStampedModel
Abstract base model providing created/updated timestamps for audit trails.
- **Fields:**
  - `created_at` (DateTime, auto_now_add)
  - `updated_at` (DateTime, auto_now)
- **Usage:** Extended by all models requiring audit trails

## Accounts Models

### User (Custom User Model)
Custom user model extending Django's AbstractUser with email verification and role-based access.

**Fields:**
- `id` (UUID, primary key)
- `username` (CharField, unique)
- `email` (EmailField, unique, required)
- `is_email_verified` (BooleanField, default=False)
- `email_verification_token` (CharField, max_length=64, nullable)
- `failed_login_attempts` (IntegerField, default=0)
- `lockout_until` (DateTimeField, nullable)
- `roles` (ManyToManyField to Role)
- Standard Django user fields (password, is_active, is_staff, is_superuser, etc.)
- `created_at`, `updated_at` (from TimeStampedModel)

**Relationships:**
- Many-to-Many: `roles` → Role
- One-to-One: `profile` → Profile
- One-to-One: `settings` → UserSettings
- One-to-Many: `sessions` → UserSession
- One-to-Many: `uploaded_documents` → Document
- One-to-Many: `notifications` → Notification
- One-to-Many: `reminders` → Reminder
- One-to-Many: `saved_searches` → SavedSearch

**Key Methods:**
- `has_role(role_name)` - Check if user has specific role
- `has_any_role(role_names)` - Check if user has any of specified roles
- `has_all_roles(role_names)` - Check if user has all specified roles
- `primary_role` - Get priority role (admin > coordinator > student)
- `is_locked_out()` - Check if account is locked
- `increment_failed_login_attempts()` - Increment and potentially lock account
- `generate_email_verification_token()` - Generate email verification token

### Profile
Extended user profile with additional information.

**Fields:**
- `id` (UUID, primary key)
- `user` (OneToOneField to User)
- `secondary_email` (EmailField, nullable)
- `gpa` (FloatField, nullable) - Student's GPA in institutional grading scale
- `grade_scale` (ForeignKey to grades.GradeScale, nullable)
- `language` (CharField, max_length=64, nullable)
- `language_level` (CharField, choices: A1-C2, nullable)
- `date_of_birth` (DateField, nullable)
- `created_at`, `updated_at` (from TimeStampedModel)

**Relationships:**
- One-to-One: `user` → User
- Foreign Key: `grade_scale` → grades.GradeScale

**Key Methods:**
- `get_gpa_equivalent()` - Convert GPA to 4.0 scale equivalent

### Role
User roles for role-based access control.

**Fields:**
- `id` (AutoField, primary key)
- `name` (CharField, max_length=50, unique)
- Standard roles: "student", "coordinator", "admin"

**Relationships:**
- Many-to-Many: `users` → User (via User.roles)
- Many-to-Many: `permissions` → Permission

### Permission
Custom permissions associated with roles.

**Fields:**
- `id` (AutoField, primary key)
- `name` (CharField, max_length=100, unique)

**Relationships:**
- Many-to-Many: `roles` → Role

### UserSettings
User preferences and settings.

**Fields:**
- `id` (AutoField, primary key)
- `user` (OneToOneField to User)
- **Appearance:**
  - `theme` (CharField, choices: light/dark/auto, default='auto')
  - `font_size` (CharField, choices: normal/large/x-large, default='normal')
  - `high_contrast` (BooleanField, default=False)
  - `reduce_motion` (BooleanField, default=False)
- **Notifications:**
  - `email_applications`, `email_documents`, `email_programs`, `email_system` (BooleanField)
  - `inapp_applications`, `inapp_documents`, `inapp_comments` (BooleanField)
- **Privacy:**
  - `profile_public` (BooleanField, default=False)
  - `share_analytics` (BooleanField, default=True)
- `created_at`, `updated_at` (from TimeStampedModel)

### UserSession
Track user sessions for security management.

**Fields:**
- `id` (AutoField, primary key)
- `user` (ForeignKey to User)
- `session_key` (CharField, max_length=40, unique)
- `user_agent` (TextField)
- `ip_address` (GenericIPAddressField, nullable)
- `device` (CharField, max_length=100)
- `location` (CharField, max_length=100)
- `is_active` (BooleanField, default=True)
- `last_activity` (DateTimeField, auto_now=True)
- `created_at`, `updated_at` (from TimeStampedModel)

## Exchange Models

### Program
Exchange program definition with eligibility criteria.

**Fields:**
- `id` (UUID, primary key)
- `name` (CharField, max_length=255)
- `description` (TextField)
- `start_date` (DateField)
- `end_date` (DateField)
- `is_active` (BooleanField, default=True)
- **Eligibility Criteria:**
  - `min_gpa` (FloatField, nullable)
  - `required_language` (CharField, max_length=64, nullable)
  - `min_language_level` (CharField, choices: A1-C2, nullable)
  - `min_age` (PositiveIntegerField, nullable)
  - `max_age` (PositiveIntegerField, nullable)
  - `auto_reject_ineligible` (BooleanField, default=False)
- `recurring` (BooleanField, default=False)
- `application_form` (ForeignKey to application_forms.FormType, nullable)
- `created_at`, `updated_at` (from TimeStampedModel)

**Relationships:**
- One-to-Many: `applications` → Application
- One-to-Many: `form_submissions` → application_forms.FormSubmission
- Foreign Key: `application_form` → application_forms.FormType

**Validation:**
- `clean()` - Ensures end_date > start_date

### Application
Student application for an exchange program.

**Fields:**
- `id` (UUID, primary key)
- `program` (ForeignKey to Program)
- `student` (ForeignKey to accounts.User)
- `status` (ForeignKey to ApplicationStatus)
- `submitted_at` (DateTimeField, nullable)
- `withdrawn` (BooleanField, default=False)
- `created_at`, `updated_at` (from TimeStampedModel)

**Relationships:**
- Foreign Key: `program` → Program
- Foreign Key: `student` → accounts.User
- Foreign Key: `status` → ApplicationStatus
- One-to-Many: `comments` → Comment
- One-to-Many: `timeline_events` → TimelineEvent
- One-to-Many: `documents` → Document
- One-to-Many: `form_submissions` → application_forms.FormSubmission

**Indexes:**
- `app_student_status_idx` - (student, status)
- `app_program_status_idx` - (program, status)
- `app_student_withdrawn_idx` - (student, withdrawn)
- `app_submitted_idx` - (submitted_at)
- `app_created_desc_idx` - (-created_at)

### ApplicationStatus
Status values for application workflow state machine.

**Fields:**
- `id` (AutoField, primary key)
- `name` (CharField, max_length=50, unique)
- `order` (PositiveIntegerField, default=0)

**Standard Statuses:**
- draft → submitted → under_review → approved/rejected → completed/cancelled

### Comment
Comments on applications (internal or visible to students).

**Fields:**
- `id` (UUID, primary key)
- `application` (ForeignKey to Application)
- `author` (ForeignKey to accounts.User)
- `text` (TextField)
- `is_private` (BooleanField, default=False)
- `created_at`, `updated_at` (from TimeStampedModel)

### TimelineEvent
Audit trail for application status changes and key events.

**Fields:**
- `id` (UUID, primary key)
- `application` (ForeignKey to Application)
- `event_type` (CharField, max_length=100)
- `description` (TextField)
- `created_by` (ForeignKey to accounts.User, nullable)
- `created_at`, `updated_at` (from TimeStampedModel)

### SavedSearch
Saved search filters for users (coordinators/admins).

**Fields:**
- `id` (UUID, primary key)
- `user` (ForeignKey to accounts.User)
- `name` (CharField, max_length=100)
- `search_type` (CharField, choices: program/application)
- `filters` (JSONField, default=dict)
- `is_default` (BooleanField, default=False)
- `created_at`, `updated_at` (from TimeStampedModel)

**Indexes:**
- `savedsearch_user_type_idx` - (user, search_type)
- `savedsearch_user_default_idx` - (user, is_default)

**Validation:**
- `save()` - Ensures only one default search per type per user

## Documents Models

### DocumentType
Types of documents (transcript, ID, recommendation letter, etc.).

**Fields:**
- `id` (AutoField, primary key)
- `name` (CharField, max_length=100, unique)
- `description` (TextField, blank=True)

**Relationships:**
- One-to-Many: `documents` → Document

### Document
Uploaded document for an application.

**Fields:**
- `id` (UUID, primary key)
- `application` (ForeignKey to exchange.Application)
- `type` (ForeignKey to DocumentType)
- `file` (FileField, upload_to="documents/")
- `uploaded_by` (ForeignKey to accounts.User)
- `is_valid` (BooleanField, default=False)
- `validated_at` (DateTimeField, nullable)
- `created_at`, `updated_at` (from TimeStampedModel)

**Relationships:**
- Foreign Key: `application` → exchange.Application
- Foreign Key: `type` → DocumentType
- Foreign Key: `uploaded_by` → accounts.User
- One-to-Many: `validations` → DocumentValidation
- One-to-Many: `resubmission_requests` → DocumentResubmissionRequest
- One-to-Many: `comments` → DocumentComment

**Indexes:**
- `doc_app_type_idx` - (application, type)
- `doc_uploaded_by_idx` - (uploaded_by)
- `doc_is_valid_idx` - (is_valid)
- `doc_validated_at_idx` - (validated_at)
- `doc_created_desc_idx` - (-created_at)

### DocumentValidation
Validation record for documents (virus scan, integrity check).

**Fields:**
- `id` (UUID, primary key)
- `document` (ForeignKey to Document)
- `validator` (ForeignKey to accounts.User, nullable)
- `result` (CharField, max_length=100)
- `details` (TextField, blank=True)
- `validated_at` (DateTimeField, auto_now_add=True)
- `created_at`, `updated_at` (from TimeStampedModel)

### DocumentResubmissionRequest
Request for student to resubmit a document.

**Fields:**
- `id` (UUID, primary key)
- `document` (ForeignKey to Document)
- `requested_by` (ForeignKey to accounts.User)
- `reason` (TextField)
- `resolved` (BooleanField, default=False)
- `requested_at` (DateTimeField, auto_now_add=True)
- `created_at`, `updated_at` (from TimeStampedModel)

### DocumentComment
Comments on documents (internal or visible to students).

**Fields:**
- `id` (UUID, primary key)
- `document` (ForeignKey to Document)
- `author` (ForeignKey to accounts.User)
- `text` (TextField)
- `is_private` (BooleanField, default=False)
- `created_at` (DateTimeField, auto_now_add=True)

## Notifications Models

### NotificationType
Types of notifications (status change, comment, reminder, etc.).

**Fields:**
- `id` (AutoField, primary key)
- `name` (CharField, max_length=100, unique)

**Relationships:**
- One-to-Many: `notification_preferences` → NotificationPreference

### Notification
Notification instance sent to a user.

**Fields:**
- `id` (UUID, primary key)
- `recipient` (ForeignKey to accounts.User, nullable)
- `title` (CharField, max_length=255, nullable, default="Untitled")
- `message` (TextField, nullable, default="")
- `notification_type` (CharField, choices: in_app/email/both, default='in_app')
- `category` (CharField, choices: info/success/warning/error, default='info')
- `is_read` (BooleanField, default=False)
- `action_url` (CharField, max_length=500, nullable) - Direct link to related resource
- `action_text` (CharField, max_length=100, nullable, default="View Details")
- `data` (JSONField, default=dict)
- `sent_at` (DateTimeField, auto_now_add=True)
- `created_at`, `updated_at` (from TimeStampedModel)

**Indexes:**
- `notif_recipient_read_idx` - (recipient, is_read)
- `notif_recipient_sent_idx` - (recipient, -sent_at)
- `notif_type_idx` - (notification_type)
- `notif_category_idx` - (category)
- `notif_sent_desc_idx` - (-sent_at)

### NotificationPreference
User preferences for notification types.

**Fields:**
- `id` (UUID, primary key)
- `user` (ForeignKey to accounts.User)
- `type` (ForeignKey to NotificationType)
- `enabled` (BooleanField, default=True)
- `created_at`, `updated_at` (from TimeStampedModel)

### Reminder
Reminder for events like deadlines.

**Fields:**
- `id` (UUID, primary key)
- `user` (ForeignKey to accounts.User)
- `event_type` (CharField, choices: application_deadline/document_deadline/program_start/program_end/custom)
- `event_id` (UUIDField) - ID of related object (Program, Application, etc.)
- `event_title` (CharField, max_length=255)
- `remind_at` (DateTimeField)
- `sent` (BooleanField, default=False)
- `notification` (ForeignKey to Notification, nullable)
- `created_at`, `updated_at` (from TimeStampedModel)

**Indexes:**
- `reminder_user_sent_idx` - (user, sent)
- `reminder_time_sent_idx` - (remind_at, sent)
- `reminder_event_idx` - (event_type, event_id)

## Grades Models

### GradeScale
Represents a grading system used by an institution or country.

**Fields:**
- `id` (UUID, primary key)
- `name` (CharField, max_length=255)
- `code` (CharField, max_length=50, unique)
- `description` (TextField, blank=True)
- `country` (CharField, max_length=100, blank=True)
- `min_value` (FloatField)
- `max_value` (FloatField)
- `passing_value` (FloatField)
- `is_active` (BooleanField, default=True)
- `is_reverse_scale` (BooleanField, default=False) - True if lower values are better
- `created_at`, `updated_at` (from TimeStampedModel)

**Relationships:**
- One-to-Many: `grade_values` → GradeValue
- One-to-Many: `student_profiles` → accounts.Profile

**Indexes:**
- `grade_scale_code_idx` - (code)
- `grade_scale_active_idx` - (is_active)

**Supported Scales:**
- US GPA 4.0
- ECTS
- UK (First Class, Upper Second, etc.)
- German (1.0-5.0, reverse scale)
- French (0-20)
- Canadian (0-4.33)

### GradeValue
Individual grade values within a scale with numeric equivalents.

**Fields:**
- `id` (UUID, primary key)
- `grade_scale` (ForeignKey to GradeScale)
- `label` (CharField, max_length=50) - e.g., 'A', '1.0', 'First Class'
- `numeric_value` (FloatField)
- `gpa_equivalent` (FloatField, validators: 0.0-4.0) - Normalized 4.0 GPA equivalent
- `min_percentage` (FloatField, nullable, validators: 0.0-100.0)
- `max_percentage` (FloatField, nullable, validators: 0.0-100.0)
- `description` (TextField, blank=True)
- `order` (PositiveIntegerField, default=0)
- `is_passing` (BooleanField, default=True)
- `created_at`, `updated_at` (from TimeStampedModel)

**Relationships:**
- Foreign Key: `grade_scale` → GradeScale
- One-to-Many: `translations_from` → GradeTranslation
- One-to-Many: `translations_to` → GradeTranslation

**Unique Together:**
- (grade_scale, label)
- (grade_scale, numeric_value)

**Indexes:**
- `grade_val_gpa_idx` - (grade_scale, gpa_equivalent)
- `grade_val_num_idx` - (grade_scale, numeric_value)

### GradeTranslation
Direct translation mappings between specific grades in different scales.

**Fields:**
- `id` (UUID, primary key)
- `source_grade` (ForeignKey to GradeValue)
- `target_grade` (ForeignKey to GradeValue)
- `confidence` (FloatField, validators: 0.0-1.0, default=1.0)
- `notes` (TextField, blank=True)
- `created_by` (ForeignKey to accounts.User, nullable)
- `created_at`, `updated_at` (from TimeStampedModel)

**Relationships:**
- Foreign Key: `source_grade` → GradeValue
- Foreign Key: `target_grade` → GradeValue
- Foreign Key: `created_by` → accounts.User

**Unique Together:**
- (source_grade, target_grade)

**Indexes:**
- `grade_trans_src_idx` - (source_grade)
- `grade_trans_tgt_idx` - (target_grade)

**Validation:**
- `clean()` - Ensures source and target grades are from different scales

## Application Forms Models

### FormType
Defines the structure and configuration of a dynamic form.

**Fields:**
- `id` (AutoField, primary key)
- `name` (CharField, max_length=200)
- `form_type` (CharField, choices: application/survey/feedback/custom, default='application')
- `description` (TextField, blank=True)
- `schema` (JSONField, default=dict) - JSON schema defining field structure
- `ui_schema` (JSONField, default=dict) - UI schema for form rendering
- `created_by` (ForeignKey to accounts.User, nullable)
- `created_at` (DateTimeField, auto_now_add=True)
- `updated_at` (DateTimeField, auto_now=True)
- `is_active` (BooleanField, default=True)

**Relationships:**
- Foreign Key: `created_by` → accounts.User
- One-to-Many: `submissions` → FormSubmission
- One-to-Many: `programs` → exchange.Program

**Key Methods:**
- `get_field_count()` - Return number of fields in schema
- `get_required_fields()` - Return list of required field names

### FormSubmission
Stores individual form submissions with responses.

**Fields:**
- `id` (AutoField, primary key)
- `form_type` (ForeignKey to FormType)
- `submitted_by` (ForeignKey to accounts.User, nullable)
- `responses` (JSONField, default=dict) - JSON object containing form responses
- `submitted_at` (DateTimeField, auto_now_add=True)
- `updated_at` (DateTimeField, auto_now=True)
- `program` (ForeignKey to exchange.Program, nullable)
- `application` (ForeignKey to exchange.Application, nullable)

**Relationships:**
- Foreign Key: `form_type` → FormType
- Foreign Key: `submitted_by` → accounts.User
- Foreign Key: `program` → exchange.Program
- Foreign Key: `application` → exchange.Application

**Key Methods:**
- `get_response_count()` - Return number of fields with responses

## Database Indexes Summary

The application uses strategic indexes for performance:
- User/Application relationships (student, status, withdrawn)
- Document lookups (application, type, uploaded_by, validation status)
- Notification queries (recipient, read status, sent date)
- Saved searches (user, type, default)
- Grade lookups (scale, code, active status, GPA equivalents)
- Timeline/audit queries (created_at descending)

---

_Generated using BMAD Method `document-project` workflow (Exhaustive Scan)_
