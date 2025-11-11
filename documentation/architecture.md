# SEIM Architecture Documentation

## Overview
SEIM (Student Exchange Information Manager) is a Django-based web application designed to manage student exchange programs. The system follows a modular, service-oriented architecture with clear separation of concerns.

---

## System Architecture

### **High-Level Architecture:**
```
┌─────────────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend              │    │   API Layer     │    │   Business      │
│   (Django Templates +   │◄──►│   (DRF)         │◄──►│   Logic Layer   │
│   Bootstrap 5 +         │    │                 │    │   (Services)    │
│   ES6+ JavaScript)      │    │                 │    │                 │
└─────────────────────────┘    └─────────────────┘    └─────────────────┘
                                        │                       │
                                        ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────────────┐
                       │   Data Layer    │    │   External Services     │
                       │   (Django ORM)  │    │   (Email, Cache, Queue) │
                       └─────────────────┘    └─────────────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Database      │
                       │   (PostgreSQL)  │
                       └─────────────────┘
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

## Future Enhancements

### **Planned Features:**
- Real-time notifications (WebSockets)
- Advanced analytics and reporting
- Mobile API endpoints
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