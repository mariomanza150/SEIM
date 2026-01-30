# SEIM Architecture Documentation

## Overview
SEIM (Student Exchange Information Manager) is a Django-based web application designed to manage student exchange programs. The system follows a modular, service-oriented architecture with clear separation of concerns.

---

## System Architecture

### **High-Level Architecture:**
```
┌────────────────────────────────────────────────────────────────────┐
│                          Frontend Layer                            │
│  ┌──────────────────────┐         ┌───────────────────────────┐  │
│  │  Public Pages        │         │  Authenticated Pages      │  │
│  │  (Wagtail CMS)       │         │  (Django Templates +      │  │
│  │  - Home, Blog        │         │   Bootstrap 5 +           │  │
│  │  - Program Pages     │         │   ES6+ JavaScript)        │  │
│  │  - Info Pages        │         │  - Dashboard              │  │
│  └──────────────────────┘         │  - Applications           │  │
│                                    │  - Documents              │  │
│                                    └───────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌────────────────────────────────────────────────────────────────────┐
│                     Admin Interfaces                               │
│  ┌──────────────────────┐         ┌───────────────────────────┐  │
│  │  Wagtail CMS Admin   │         │  Django Admin             │  │
│  │  - Content Pages     │         │  - System Config          │  │
│  │  - Blog Management   │         │  - User Management        │  │
│  │  - Forms             │         │  - Exchange Workflows     │  │
│  └──────────────────────┘         └───────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌────────────────────────────────────────────────────────────────────┐
│   API Layer (DRF) ◄──────────────────────────────────────┐        │
│   - REST API                                              │        │
│   - JWT Authentication                                    │        │
│   - OpenAPI Documentation                                 │        │
└───────────────────────────────────────────────────────────┼────────┘
                                     │                      │
                                     ▼                      ▼
┌────────────────────────────────────────┐   ┌──────────────────────┐
│   Business Logic Layer (Services)      │   │  External Services   │
│   - WorkflowService                    │   │  - Email (Celery)    │
│   - ApplicationService                 │   │  - Redis (Cache)     │
│   - DocumentService                    │   │  - File Storage      │
└────────────────────────────────────────┘   └──────────────────────┘
                                     │
                                     ▼
                       ┌──────────────────────────┐
                       │   Data Layer (ORM)       │
                       │   - Django Models        │
                       │   - Wagtail Pages        │
                       └──────────────────────────┘
                                     │
                                     ▼
                       ┌──────────────────────────┐
                       │   Database               │
                       │   (PostgreSQL)           │
                       └──────────────────────────┘
```

---

## Application Structure

### **Django Apps:**

#### **1. Core Apps:**
- **`accounts/`**: User management and authentication
  - Custom User model with email verification
  - JWT authentication
  - Role-based permissions (Student, Coordinator, Admin)
  - Password reset functionality

- **`exchange/`**: Core exchange program logic
  - Program management with eligibility criteria
  - Application workflow and state management
  - Dynamic forms using django-dynforms
  - Application comments and audit logging

- **`documents/`**: Document management system
  - File upload and validation
  - Document type configuration
  - Resubmission workflow
  - Document comments from coordinators

- **`notifications/`**: Communication system
  - Email notifications for key events
  - Async email processing via Celery
  - User notification preferences
  - Support for SMTP and AWS SES

#### **2. Supporting Apps:**
- **`analytics/`**: Reporting and metrics
  - Dashboard metrics calculation
  - Program-specific analytics
  - User activity tracking

- **`grades/`**: Grade translation system
  - International grade scale conversion
  - GPA equivalency calculations
  - Support for multiple grading systems

- **`cms/`**: Wagtail CMS for content management
  - HomePage, StandardPage, BlogPost pages
  - Program pages with rich content
  - Dynamic form builder (replacing django-dynforms)
  - StreamField blocks for flexible content
  - SEO optimization
  - Publishing workflows and moderation
  - Integration with exchange.Program model

- **`application_forms/`**: Dynamic form builder (DEPRECATED)
  - Being replaced by Wagtail FormPage
  - Historical data preserved
  - Migration command available
  - Will be removed in future version

- **`api/`**: REST API endpoints
  - DRF-based API with OpenAPI documentation
  - JWT authentication
  - Pagination and filtering

- **`dashboard/`**: Admin and user interfaces
  - Django admin customization
  - User dashboard views

- **`core/`**: Shared utilities and base classes
  - Base models and mixins
  - Common utilities and helpers

- **`plugins/`**: Extensibility system
  - Plugin architecture for custom workflows

---

## Data Models

### **Core Models:**

#### **User Management:**
```python
class User(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(choices=ROLE_CHOICES)
    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, null=True)
    failed_login_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True)
```

#### **Exchange Programs:**
```python
class Program(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    institution = models.CharField(max_length=200)
    country = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    application_deadline = models.DateField()
    max_participants = models.IntegerField()
    min_gpa = models.DecimalField(max_digits=3, decimal_places=2)
    language_requirements = models.JSONField()
    is_recurring = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
```

#### **Applications:**
```python
class Application(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS_CHOICES, default='draft')
    submitted_at = models.DateTimeField(null=True)
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### **Documents:**
```python
class Document(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    document_type = models.ForeignKey(DocumentType, on_delete=models.CASCADE)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_validated = models.BooleanField(default=False)
    validation_notes = models.TextField(blank=True)
```

#### **Dynamic Forms:**
```python
class FormType(models.Model):
    name = models.CharField(max_length=200)
    schema = models.JSONField()  # JSON Schema format
    ui_schema = models.JSONField(default=dict)  # UI hints
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class FormSubmission(models.Model):
    form_type = models.ForeignKey(FormType, on_delete=models.CASCADE)
    application = models.ForeignKey('exchange.Application', on_delete=models.CASCADE)
    data = models.JSONField()  # Submitted form data
    submitted_at = models.DateTimeField(auto_now_add=True)
```

#### **Grade Translation:**
```python
class GradeScale(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    min_grade = models.DecimalField(max_digits=5, decimal_places=2)
    max_grade = models.DecimalField(max_digits=5, decimal_places=2)
    passing_grade = models.DecimalField(max_digits=5, decimal_places=2)

class GradeTranslation(models.Model):
    from_scale = models.ForeignKey(GradeScale, related_name='from_translations')
    to_scale = models.ForeignKey(GradeScale, related_name='to_translations')
    from_grade = models.DecimalField(max_digits=5, decimal_places=2)
    to_grade = models.DecimalField(max_digits=5, decimal_places=2)
```

#### **Audit Logging:**
```python
class TimelineEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=50)
    description = models.TextField()
    related_object_type = models.CharField(max_length=50)
    related_object_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
```

---

## Service Layer Architecture

### **Service Classes:**

#### **1. WorkflowService:**
- Manages application state transitions
- Enforces business rules for status changes
- Handles bulk operations
- Triggers notifications for workflow events

#### **2. DocumentService:**
- Handles document upload and validation
- Manages document replacement rules
- Processes resubmission requests
- Integrates with virus scanning (stub)

#### **3. NotificationService:**
- Sends email notifications
- Manages notification preferences
- Handles async email processing
- Supports multiple email backends

#### **4. AccountService:**
- Manages user registration and verification
- Handles password reset workflow
- Implements account lockout policy
- Manages user roles and permissions

#### **5. AnalyticsService:**
- Calculates dashboard metrics
- Generates program-specific reports
- Tracks user activity
- Provides data for admin dashboards

---

## API Design

### **RESTful Endpoints:**

#### **Authentication:**
- `POST /api/accounts/register/` - User registration
- `POST /api/accounts/verify-email/` - Email verification
- `POST /api/token/` - JWT token generation
- `POST /api/token/refresh/` - Token refresh
- `POST /api/accounts/password-reset/` - Password reset

#### **Programs:**
- `GET /api/programs/` - List programs
- `POST /api/programs/` - Create program
- `GET /api/programs/{id}/` - Get program details
- `PUT /api/programs/{id}/` - Update program
- `DELETE /api/programs/{id}/` - Delete program

#### **Applications:**
- `GET /api/applications/` - List applications
- `POST /api/applications/` - Create application
- `GET /api/applications/{id}/` - Get application details
- `PUT /api/applications/{id}/` - Update application
- `POST /api/applications/{id}/withdraw/` - Withdraw application
- `POST /api/applications/{id}/transition_status/` - Change status

#### **Documents:**
- `GET /api/documents/` - List documents
- `POST /api/documents/` - Upload document
- `GET /api/documents/{id}/` - Get document details
- `PUT /api/documents/{id}/` - Update document
- `DELETE /api/documents/{id}/` - Delete document

### **API Features:**
- JWT authentication
- Role-based permissions
- Pagination (20 items per page)
- Filtering and search
- OpenAPI documentation
- Rate limiting (planned)

---

## Security Architecture

### **Authentication & Authorization:**
- JWT-based authentication
- Role-based access control (RBAC)
- Email verification workflow
- Account lockout after failed attempts
- Password reset functionality

### **Data Protection:**
- CSRF protection
- XSS prevention
- SQL injection protection (Django ORM)
- File upload validation
- Environment variable configuration

### **Audit & Compliance:**
- Comprehensive audit logging via TimelineEvent
- All critical actions logged
- User activity tracking
- Data retention policies

---

## Background Processing

### **Celery Integration:**
- Async email sending
- Document processing
- Analytics calculation
- Scheduled tasks

### **Redis Configuration:**
- Celery broker and result backend
- Session storage
- Caching layer

---

## Database Design

### **Database Schema:**
- PostgreSQL (production) / SQLite (development)
- Normalized design with proper relationships
- Indexes on frequently queried fields
- Foreign key constraints for data integrity

### **Migrations:**
- Django migrations for schema changes
- Data migrations for business logic changes
- Backward compatibility maintained

---

## Deployment Architecture

### **Development:**
- Docker Compose for local development
- SQLite database
- Console email backend
- Debug mode enabled

### **Production:**
- Docker containers for scalability
- PostgreSQL database
- Redis for caching and background tasks
- Nginx for static file serving
- SSL/TLS encryption
- Environment-based configuration

---

## Monitoring & Logging

### **Application Monitoring:**
- Django debug toolbar (development)
- Application logs
- Error tracking (planned)
- Performance monitoring (planned)

### **Infrastructure Monitoring:**
- Container health checks
- Database monitoring
- Redis monitoring
- Email delivery tracking

---

## Scalability Considerations

### **Horizontal Scaling:**
- Stateless application design
- Database connection pooling
- Redis for session storage
- Load balancer ready

### **Performance Optimization:**
- Database query optimization
- Caching strategies
- Static file optimization
- Background task processing

---

## CMS Integration (Wagtail)

### **Content Management System:**

The SEIM platform now includes a comprehensive CMS powered by Wagtail:

#### **Architecture:**
- **Dual Admin Interface**: Wagtail CMS admin for content, Django admin for system configuration
- **Shared Authentication**: Single user model (accounts.User) for both interfaces
- **URL Routing**: Wagtail catch-all at the end of URL patterns, preserving all API and app routes

#### **Page Types:**
1. **HomePage**: Main landing page with hero section and flexible content blocks
2. **StandardPage**: General information pages (About, Contact, Help)
3. **BlogIndexPage & BlogPostPage**: Full-featured blog with categories, tags, and SEO
4. **ProgramIndexPage & ProgramPage**: Rich program pages linked to exchange.Program model
5. **FormPage**: Dynamic forms replacing django-dynforms
6. **FAQIndexPage & FAQPage**: Frequently Asked Questions with accordion UI

#### **StreamField Blocks:**
- Rich Text, Images, Videos
- Call-to-Action blocks
- Card Grids, Testimonials
- FAQ Sections, Process Steps
- Two-column layouts
- Embedded forms

#### **Features:**
- **SEO Optimization**: wagtail-seo integration for meta tags, Open Graph, Twitter Cards
- **Media Library**: Centralized image and document management
- **Publishing Workflows**: Draft → Review → Approve → Publish
- **Revision History**: Full version control with rollback capability
- **Multi-language Support**: Wagtail's internationalization framework
- **Responsive Design**: Bootstrap 5 integration for all page templates

#### **Integration Points:**
- **exchange.Program**: ProgramPage.program OneToOneField for rich program content
- **accounts.User**: Shared authentication and permissions
- **FormPage → Exchange Applications**: Forms can be linked to programs for applications

#### **Migration from django-dynforms:**
- Management command: `migrate_forms_to_wagtail.py`
- Preserves historical FormSubmission data
- Maps JSON schema fields to Wagtail form fields
- Command: `remove_old_form_system.py` for cleanup after verification

## Future Enhancements

### **Planned Features:**
- Real-time notifications (WebSockets) - Implemented
- Advanced analytics and reporting - In Progress
- Mobile API endpoints
- Enhanced CMS features (A/B testing, personalization)
- Multi-language content management via Wagtail
- Advanced form logic and conditional fields
- Third-party integrations
- Plugin system expansion

### **Technical Improvements:**
- GraphQL API
- Microservices architecture
- Event-driven architecture
- Advanced caching strategies

---

## Development Workflow

### **Code Organization:**
- Modular app structure
- Service layer for business logic
- Thin controllers (views)
- Comprehensive test coverage (planned)

### **Quality Assurance:**
- Code linting and formatting
- Type hints and documentation
- Code review process
- Automated testing (planned)

---

### Dynamic Program Application Forms

- Each `Program` can be linked to a `DynamicForm` (from django-dynforms) via the `application_form` field.
- Admins manage and design forms using the visual builder at `/dynforms/`.
- This enables multi-stage, customizable application forms per program, supporting complex eligibility and workflow logic.

This architecture provides a solid foundation for the SEIM application, with clear separation of concerns, scalability considerations, and maintainable code structure. 