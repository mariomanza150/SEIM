# SEIM Business Rules

## Overview
This document outlines the business rules and logic implemented in the SEIM (Student Exchange Information Manager) system. These rules govern how the application behaves and ensure data integrity and proper workflow management.

---

## User Management Rules

### **User Registration:**
- Users must register with a valid institutional email address
- Email addresses must be unique across the system
- Usernames must be unique and alphanumeric
- Passwords must meet minimum security requirements
- Users are assigned a default role of "Student" upon registration

### **Email Verification:**
- Users must verify their email address before accessing the system
- Verification tokens expire after 24 hours
- Users can request a new verification token if needed
- Unverified users cannot submit applications or upload documents

### **Account Security:**
- Accounts are locked after 5 failed login attempts
- Locked accounts remain locked for 30 minutes
- Users can reset their password via email
- Password reset tokens expire after 1 hour

### **Role-Based Access:**
- **Students**: Can manage their own applications and documents
- **Coordinators**: Can review applications, change status, request resubmissions
- **Admins**: Full access to all features, analytics, and user management

---

## Program Management Rules

### **Program Creation:**
- Only admins can create new exchange programs
- Programs must have a unique name within the institution
- Start date must be before end date
- Application deadline must be before program start date
- Maximum participants must be a positive integer

### **Eligibility Criteria:**
- Minimum GPA must be between 0.00 and 4.00
- Language requirements are stored as JSON with required proficiency levels
- Programs can be marked as recurring for annual offerings
- Only active programs are visible to students

### **Program Lifecycle:**
- Programs can be deactivated but not deleted (for audit purposes)
- Deactivated programs cannot accept new applications
- Existing applications for deactivated programs remain accessible

---

## Application Workflow Rules

### **Application Creation:**
- Students can only have one active application per program
- Applications start in "draft" status
- Students must be verified users to create applications
- Applications are linked to specific programs and students

### **Application Status Transitions:**
```
draft → submitted → under_review → nominated → approved → completed
```
Side statuses: `waitlist`, `rejected`, `cancelled`, `withdrawn` (they do not inherit later pipeline requirements).

#### **Status Transition Rules:**
- **draft → submitted**: Student can submit when items due at **submitted** are complete (documents + scheduled fields + existing host/form/eligibility). Documents required from a later status (e.g. approved) do **not** block submit.
- Staff `PATCH` of status is **not** blocked by the lifecycle schedule; missing later-stage items remain due on the student checklist.
- After a staff or workflow status change, if items are due now and still missing, the student gets an in-app/email reminder (`lifecycle_requirements_due`). The same application + status + missing-item set is not sent twice.
- **draft → cancelled / withdrawn**: Student workflow actions do not require pipeline items.

### **Application Withdrawal:**
- Only draft applications can be withdrawn
- Withdrawn applications cannot be reactivated
- Withdrawal is logged in the audit trail

### **Application Comments:**
- Students can add private comments to their applications
- Coordinators and admins can add public comments
- Comments are preserved throughout the application lifecycle

---

## Document Management Rules

### **Document Upload:**
- Only verified users can upload documents
- Documents must be associated with a specific application
- File size limit: 10MB per document
- Allowed file types: PDF, DOC, DOCX, JPG, PNG
- Documents are scanned for viruses (stub implementation)

### **Document Types:**
- Document types are configured by admins in the SPA admin console (`/seim/admin/documents`)
- Each type can have student instructions, FAQ, an optional Word template, accepted extensions, and a per-type size cap
- Each program can request different document types. `is_required=False` is optional throughout; `is_required=True` with no `required_from_status` is required from submitted; otherwise required from the chosen success-pipeline status (not `draft`).
- Submission deadlines can be an absolute date, N days after program start, or N days before the application deadline
- Profile/application/form fields can be scheduled per program via `ProgramFieldRequirement` (admin: program editor Field requirements table, including `source=form` keys from the program's application form schema). Student PATCH of a due field cannot clear it; staff profile edits are unrestricted.
- Word `.docx` templates use MERGEFIELD names (e.g. `FirstName`, `Matricula`, `ProgramName`); student downloads are prefilled for the selected application

### **Document Replacement Rules:**
- **Before Submission**: Students can freely replace documents
- **After Submission**: Documents can only be replaced if resubmission is requested
- **Admin Override**: Admins can override replacement restrictions
- **Maximum Resubmissions**: Maximum 3 resubmission requests per document

### **Document Validation:**
- Documents are marked as validated by coordinators/admins
- Validation includes checking file integrity and content
- Validation notes can be added by reviewers
- Invalid documents can be flagged for resubmission

### **Document Comments:**
- Coordinators and admins can add comments to documents
- Comments are visible to students
- Comments can be used to request changes or provide feedback

---

## Notification Rules

### **Email Notifications:**
- Notifications are sent for all critical workflow events
- Emails are sent asynchronously via Celery
- Failed email deliveries are logged but don't block workflows
- Users can configure notification preferences

### **Notification Events:**
- **User Registration**: Welcome email with verification link
- **Email Verification**: Confirmation email
- **Application Submission**: Notification to student and coordinators
- **Status Change**: Notification to student about application status
- **Document Resubmission Request**: Notification to student
- **Password Reset**: Reset link sent to user's email

### **Email Configuration:**
- Development: Emails printed to console
- Production: SMTP or AWS SES backend
- Email templates are customizable
- Support for HTML and plain text emails

---

## Analytics and Reporting Rules

### **Dashboard Metrics:**
- Metrics are calculated in real-time
- Admin dashboard shows system-wide statistics
- Program-specific metrics available for coordinators
- User activity is tracked for audit purposes

### **Data Privacy:**
- Personal information is anonymized in reports
- Access to analytics is role-based
- Historical data is preserved for compliance

---

## Audit and Compliance Rules

### **Audit Logging:**
- All critical actions are logged via TimelineEvent
- Log entries include user, action type, description, and timestamp
- Related objects are referenced for traceability
- Audit logs cannot be modified or deleted

### **Data Retention:**
- User data is retained for compliance purposes
- Deleted applications are soft-deleted (marked as inactive)
- Document files are retained for audit trail
- Timeline events are permanently stored

### **Access Control:**
- All API endpoints require authentication
- Role-based permissions enforced at view level
- Sensitive operations require admin privileges
- Session management with automatic timeout

---

## System Configuration Rules

### **Environment Configuration:**
- Development and production settings are separated
- Sensitive data stored in environment variables
- Database configuration supports multiple backends
- Email configuration supports multiple providers

### **Security Configuration:**
- CSRF protection enabled for all forms
- XSS prevention through Django's built-in protection
- SQL injection prevention through ORM
- File upload validation and sanitization

---

## Error Handling Rules

### **Validation Errors:**
- Form validation errors are returned to users
- API validation errors include detailed field information
- Business rule violations are clearly communicated
- Graceful degradation for non-critical errors

### **System Errors:**
- Critical errors are logged for debugging
- User-friendly error messages for common issues
- Fallback mechanisms for external service failures
- Health checks for system monitoring

---

## Performance and Scalability Rules

### **Database Optimization:**
- Queries are optimized for common use cases
- Indexes are created on frequently queried fields
- Database connections are pooled
- Read replicas supported for scaling

### **Caching Strategy:**
- Frequently accessed data is cached
- Cache invalidation on data updates
- Session data stored in Redis
- Static files served efficiently

---

## Integration Rules

### **External Services:**
- Email services (SMTP, AWS SES) are configurable
- File storage supports local and cloud providers
- Virus scanning integration (stub implementation)
- Third-party authentication support (planned)

### **API Integration:**
- RESTful API design with consistent patterns
- JWT authentication for API access
- Rate limiting to prevent abuse
- Comprehensive API documentation

---

## Future Business Rules

### **Planned Enhancements:**
- Real-time notifications via WebSockets
- Advanced workflow customization
- Multi-language support
- Mobile application support
- Advanced analytics and reporting
- Third-party system integrations

---

## Compliance and Legal Rules

### **Data Protection:**
- User consent required for data processing
- Right to data portability
- Right to data deletion (with audit trail preservation)
- Data breach notification procedures

### **Regulatory Compliance:**
- Educational institution data protection requirements
- International student exchange regulations
- Audit trail requirements for accreditation
- Privacy policy and terms of service compliance

---

This document serves as the authoritative source for all business rules in the SEIM system. Any changes to these rules should be documented and communicated to all stakeholders. 