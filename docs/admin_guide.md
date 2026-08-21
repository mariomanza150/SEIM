# SEIM Admin Guide

## Overview
This guide is for administrators managing the SEIM (Student Exchange Information Manager) system. It covers user management, program configuration, application review, and system administration.

---

## 🚀 **Quick Start for Admins**

### **Initial Setup:**
1. **Django Admin** (ORM, users, system config): http://localhost:8001/seim/django-admin/ (root `/admin/` redirects here)
2. **Vue Staff UI** (programs, forms, workflows): http://localhost:8001/seim/admin/
3. **CMS Admin** (Wagtail content): http://localhost:8001/cms/
4. **Demo credentials** (from `seed_demo_readiness`): `admin@test.com` / `admin123`
5. **Change default passwords** after first login

### **Essential Admin Tasks:**
- [ ] Create exchange programs
- [ ] Set up user roles and permissions
- [ ] Configure email notifications
- [ ] Review and approve applications
- [ ] Monitor system health

---


## SPA Help Center

In-app help at `/seim/help` is edited in Wagtail (`/cms/`) as FAQ pages (same `FAQPage` model as the public FAQ site):

1. Put SPA-only articles under the SPA help index (`index_kind = spa_help`, slug typically `ayuda-seim`).
2. Set **Surfaces** to include `spa` (omit `public` for coordinator/partner/admin-only copy).
3. Set **Audiences** for the roles that may see the article (`student`, `coordinator`, `partner`, `admin`, `all`). SPA role `responsible` maps to coordinator.
4. Set **Topic** for hub grouping and optionally **Contextual keys** to Vue route names so the `?` on that screen filters help.
5. Publish the page. Seed/refresh the default catalog: `python manage.py seed_spa_help`.

Do not rely on public `/api/cms/pages/` for SPA help (spa-only pages are hidden there). The SPA uses authenticated `/api/help/articles/`. Field details: `docs/cms_guide.md`.

## 👥 **User Management**

### **User Roles and Permissions**

SEIM supports three main user roles:

#### **1. Students**
- **Permissions**: View programs, submit applications, upload documents
- **Access**: Personal dashboard, application forms, document upload
- **Restrictions**: Cannot view other users' data

#### **2. Coordinators**
- **Permissions**: Review applications, manage programs, send notifications
- **Access**: Application review dashboard, program management, user management
- **Restrictions**: Cannot modify system settings

#### **3. Administrators**
- **Permissions**: Full system access, user management, system configuration
- **Access**: Django admin interface, all system features
- **Restrictions**: None

### **Creating and Managing Users**

#### **Via Django Admin:**
1. Navigate to **Admin** → **Accounts** → **Users**
2. Click **"Add User"**
3. Fill in required fields:
   - **Username**: Unique identifier
   - **Email**: Unique institutional login and security address
   - **First name, middle name, paternal last name, maternal last name**
   - **Roles**: One or more of Student, Coordinator, or Admin
   - **Password**: Secure password
4. Click **"Save"**

#### **Via Management Commands:**
```bash
# Create admin user
docker-compose exec web python manage.py createsuperuser

# Assign user roles
docker-compose exec web python manage.py assign_user_roles

# Create missing profiles
docker-compose exec web python manage.py create_missing_profiles
```

### **User Profile Management**

#### **Student Profiles:**
- **Required before starting an application**: matrícula, academic level, school/faculty, home academic program, unidad, gender, date of birth, birthplace, postal code, mobile phone, secondary email, GPA, grade scale, primary language, credits approved %, and program ingress date or current semester. Middle name, maternal last name, passport number, and RFC are optional.
- **Eligibility information** (GPA, grade scale, language, credits, semester) is required to apply, not optional.
- **Optional banking information**: bank institution and 18-digit CLABE.
- The profile API exposes `is_personal_academic_complete`, `is_eligibility_complete`, `is_ready_to_apply`, `missing_apply_fields`, `apply_start_field_keys`, and `due_profile_fields`. Application creation is rejected until apply-start fields are complete (program extras apply when a program is selected).
- Document type editor: per-program **Required from** (optional throughout, or a pipeline status from submitted onward). Program editor: **Field requirements** table. Django admin inlines match. Do not change Santander carátula seed off submit-required without an explicit policy decision.
- Notification email is delivered to `secondary_email` when present; otherwise it uses the account email.

#### **Student Profile Catalogs:**
Manage these under **Admin** → **Accounts**:
- **Allowed email domains**: Active domains accepted during registration. The default seed includes `uanl.edu.mx`.
- **Academic levels**
- **School faculties**
- **Unidades**
- **Home academic programs**: Each program belongs to one school/faculty.
- **Bank institutions**

Only active catalog entries are shown in the student UI. Allowed email domains are publicly readable so the registration page can display and validate them; all other profile catalogs require authentication.

### **Account Security**

#### **Password Policies:**
- Minimum 8 characters
- Must include uppercase, lowercase, number
- Cannot be common passwords
- Expires every 90 days

#### **Account Lockout:**
- 5 failed login attempts
- 30-minute lockout period
- Automatic unlock after timeout

#### **Email Verification:**
- Required for all new accounts
- Verification token expires in 24 hours
- Resend verification available

---

## 🎓 **Program Management**

### **Creating Exchange Programs**

#### **Program Configuration:**
1. Navigate to **Admin** → **Exchange** → **Programs**
2. Click **"Add Program"**
3. Fill in program details:

**Basic Information:**
- **Name**: Program title
- **Description**: Detailed description
- **Institution**: Host institution
- **Country**: Host country
- **Start/End Dates**: Program duration
- **Application Deadline**: Submission cutoff

**Eligibility Criteria:**
- **Minimum GPA**: Required grade point average
- **Language Requirements**: Required language proficiency
- **Max Participants**: Maximum number of students
- **Academic Level**: Undergraduate/Graduate

**Program Settings:**
- **Is Active**: Enable/disable program
- **Is Recurring**: Annual/semester programs
- **Application Fee**: Cost to apply (if any)

#### **Program Workflow Configuration**

Document and field **lifecycle requirements** (when an item becomes mandatory) are configured on the program / document type, not via `ApplicationStatus.order`. Staff can still advance status when later-stage items are missing; students see Due now / Required from on the checklist.

**Field requirements (SPA Programs editor and Django inline):** source can be profile, application, or form. Form keys are the JSON Schema `properties` of the program's `application_form`. Cloning a program (SPA API or Django admin clone action) copies document and field requirement rows.

When staff (or a workflow action) moves an application onto a pipeline status and items are still missing, the student receives a requirements-due notification. Repeating the same status with the same missing items does not send another copy.

#### **Application Statuses:**
1. **Draft**: Student working on application
2. **Submitted**: Application submitted for review
3. **Under Review**: Coordinator reviewing
4. **Approved**: Application approved
5. **Rejected**: Application rejected
6. **Completed**: Program completed
7. **Cancelled**: Application withdrawn

#### **Status Transitions:**
- **Draft** → **Submitted** (Student action)
- **Submitted** → **Under Review** (Automatic)
- **Under Review** → **Approved/Rejected** (Coordinator action)
- **Approved** → **Completed** (After program ends)
- **Any Status** → **Cancelled** (Student withdrawal)

### **Dynamic Forms**

#### **Form Builder:**
1. Navigate to **Admin** → **Exchange** → **Dynamic Forms**
2. Create custom application forms
3. Configure required fields
4. Set validation rules

#### **Form Fields:**
- **Text**: Short text input
- **Textarea**: Long text input
- **Number**: Numeric input
- **Date**: Date picker
- **File Upload**: Document upload
- **Dropdown**: Selection from options
- **Checkbox**: Boolean selection

---

## 📋 **Application Management**

### **Application Review Process**

#### **Review Dashboard:**
1. Navigate to **Admin** → **Exchange** → **Applications**
2. Filter by status, program, or date
3. Click on application to review details

#### **Review Criteria:**
- **Eligibility**: GPA, language requirements
- **Documents**: Required documents uploaded
- **Application Quality**: Form completeness
- **Academic Standing**: Student performance

#### **Review Actions:**
- **Approve**: Accept application
- **Reject**: Decline with reason
- **Request Changes**: Ask for modifications
- **Add Comments**: Internal notes

### **Bulk Operations**

#### **Bulk Approval:**
1. Select multiple applications
2. Choose **"Bulk Actions"**
3. Select **"Approve Selected"**
4. Confirm action

#### **Bulk Status Update:**
1. Select applications
2. Choose new status
3. Add optional comment
4. Apply changes

### **Application Timeline**

#### **Audit Trail:**
- All status changes logged
- User actions tracked
- Comments and notes preserved
- Timestamp for all events

#### **Notifications:**
- Email notifications for status changes
- In-app notifications for updates
- Coordinator alerts for new submissions

---

## 📄 **Document Management**

### **Document Types**

#### **Required Documents:**
- **Transcript**: Academic records
- **Language Certificate**: Proficiency proof
- **Personal Statement**: Motivation letter
- **Recommendation Letter**: Academic reference
- **Passport Copy**: Identity verification

#### **Optional Documents:**
- **CV/Resume**: Professional background
- **Portfolio**: Creative work samples
- **Financial Documents**: Funding proof

### **Document Validation**

#### **Validation Process:**
1. **Upload**: Student uploads document
2. **Virus Scan**: Automatic security check
3. **Format Check**: File type validation
4. **Size Check**: File size limits
5. **Manual Review**: Coordinator review

#### **Validation Status:**
- **Pending**: Awaiting review
- **Valid**: Document approved
- **Invalid**: Document rejected
- **Resubmission Required**: Needs new upload

### **Document Workflow**

#### **Resubmission Process:**
1. Coordinator marks document as invalid
2. Student receives notification
3. Student uploads new document
4. Process repeats until valid

#### **Document Comments:**
- Coordinators can add notes
- Internal comments for review
- Student-visible feedback

---

## 🔔 **Notification System**

### **Email Configuration**

#### **SMTP Setup:**
1. Navigate to **Admin** → **Core** → **Settings**
2. Configure email settings:
   - **SMTP Host**: smtp.gmail.com
   - **SMTP Port**: 587
   - **Username**: your-email@gmail.com
   - **Password**: App-specific password
   - **Use TLS**: Enabled

#### **Email Templates:**
- **Application Submitted**: Confirmation to student
- **Application Approved**: Approval notification
- **Application Rejected**: Rejection with reason
- **Document Required**: Missing document alert
- **Program Reminder**: Deadline reminders

### **Notification Preferences**

#### **User Preferences:**
- **Email Notifications**: Enable/disable
- **In-App Notifications**: Enable/disable
- **Notification Types**: Select specific types
- **Frequency**: Immediate or digest

#### **System Notifications:**
- **Admin Alerts**: System issues
- **Coordinator Notifications**: New applications
- **Student Updates**: Status changes

---

## 📊 **Analytics and Reporting**

### **Dashboard Metrics**

#### **Program Analytics:**
- **Application Count**: Total applications
- **Approval Rate**: Percentage approved
- **Completion Rate**: Program completion
- **Popular Programs**: Most applied programs

#### **User Analytics:**
- **Active Users**: Recent activity
- **User Growth**: New registrations
- **Role Distribution**: User types
- **Engagement**: Feature usage

### **Report Generation**

#### **Available Reports:**
- **Program Summary**: Program statistics
- **Application Status**: Status distribution
- **User Activity**: User engagement
- **Document Status**: Document completion

#### **Export Options:**
- **CSV Export**: Data analysis
- **PDF Reports**: Formal documentation
- **Excel Export**: Detailed analysis

---

## ⚙️ **System Configuration**

### **General Settings**

#### **Site Configuration:**
- **Site Name**: SEIM
- **Site Description**: Student Exchange Information Manager
- **Contact Email**: admin@seim.local
- **Support Email**: support@seim.local

#### **Application Settings:**
- **Max File Size**: Document upload limits
- **Allowed File Types**: Supported formats
- **Session Timeout**: User session duration
- **Password Policy**: Security requirements

### **Security Settings**

#### **Authentication:**
- **JWT Expiration**: Token lifetime
- **Password Reset**: Reset token expiration
- **Email Verification**: Verification token expiration
- **Account Lockout**: Failed attempt limits

#### **Data Protection:**
- **Data Retention**: How long to keep data
- **Backup Schedule**: Automatic backups
- **Privacy Policy**: Data handling
- **GDPR Compliance**: European regulations

### **Performance Settings**

#### **Caching:**
- **Redis Configuration**: Cache settings
- **Page Caching**: Static page caching
- **Database Caching**: Query caching
- **Session Storage**: Session management

#### **Monitoring:**
- **Error Logging**: Error tracking
- **Performance Monitoring**: Response times
- **Health Checks**: System status
- **Alert Configuration**: Notification rules

---

## 🔧 **Maintenance and Troubleshooting**

### **Regular Maintenance**

#### **Daily Tasks:**
- [ ] Check system logs for errors
- [ ] Monitor application submissions
- [ ] Review pending document validations
- [ ] Check email delivery status

#### **Weekly Tasks:**
- [ ] Review user activity reports
- [ ] Check system performance
- [ ] Update program deadlines
- [ ] Review notification settings

#### **Monthly Tasks:**
- [ ] Database backup verification
- [ ] Security audit
- [ ] Performance optimization
- [ ] User feedback review

### **Common Issues**

#### **Email Not Sending:**
1. Check SMTP configuration
2. Verify email credentials
3. Check spam filters
4. Review email logs

#### **File Upload Issues:**
1. Check file size limits
2. Verify file type restrictions
3. Check disk space
4. Review upload logs

#### **User Access Problems:**
1. Verify user role permissions
2. Check account lockout status
3. Verify email verification
4. Review user logs

### **Backup and Recovery**

#### **Database Backup:**
```bash
# Create backup
docker-compose exec db pg_dump -U postgres seim_db > backup.sql

# Restore backup
docker-compose exec db psql -U postgres seim_db < backup.sql
```

#### **File Backup:**
```bash
# Backup media files
tar -czf media_backup.tar.gz media/

# Restore media files
tar -xzf media_backup.tar.gz
```

---

## 📞 **Support and Contact**

### **Getting Help:**
- **Documentation**: Check this guide first
- **System Logs**: Review error logs
- **Community**: GitHub issues
- **Direct Contact**: admin@seim.local

### **Emergency Procedures:**
1. **System Down**: Check Docker containers
2. **Data Loss**: Restore from backup
3. **Security Breach**: Reset passwords, review logs
4. **Performance Issues**: Check resource usage

---

## 🔗 **Related Documentation**

- [Installation Guide](installation.md)
- [Developer Guide](developer_guide.md)
- [API Documentation](api_documentation.md)
- [Troubleshooting Guide](troubleshooting.md)
- [Frontend Guide](frontend_guide.md)

---

**Last Updated**: December 2024  
**Version**: 1.0 