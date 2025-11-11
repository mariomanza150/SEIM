# SEIM Admin Guide

## Overview
This guide is for administrators managing the SEIM (Student Exchange Information Manager) system. It covers user management, program configuration, application review, and system administration.

---

## 🚀 **Quick Start for Admins**

### **Initial Setup:**
1. **Access Admin Interface**: http://localhost:8000/admin/
2. **Default Credentials**: 
   - Username: `admin`
   - Password: `admin123`
3. **Change Default Password**: Immediately after first login

### **Essential Admin Tasks:**
- [ ] Create exchange programs
- [ ] Set up user roles and permissions
- [ ] Configure email notifications
- [ ] Review and approve applications
- [ ] Monitor system health

---

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
   - **Email**: Primary contact method
   - **Role**: Student, Coordinator, or Admin
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
- **GPA**: Current grade point average
- **Language**: Primary language(s)
- **Academic Level**: Undergraduate/Graduate
- **Department**: Academic department

#### **Coordinator Profiles:**
- **Department**: Responsible department
- **Programs**: Assigned exchange programs
- **Contact Information**: Phone, office location

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

### **Program Workflow Configuration**

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