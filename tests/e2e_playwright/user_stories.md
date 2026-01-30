# User Story Paths for Video Demos

## Student User Stories

### Story 1: New Student Registration & First Application
**Path**: Registration → Email Verification → Login → Browse Programs → Create Application → Upload Documents → Submit Application

**Steps**:
1. Visit homepage
2. Navigate to registration
3. Complete registration form
4. Verify email (or auto-verify for demo)
5. Login with new account
6. View dashboard
7. Browse available programs
8. Select a program
9. Start new application
10. Fill application form
11. Upload required documents
12. Review application
13. Submit application
14. View application status

### Story 2: Returning Student - Check Status & Update
**Path**: Login → Dashboard → View Applications → Check Status → Update Profile

**Steps**:
1. Login as existing student
2. View dashboard with applications
3. Click on application to view details
4. Check current status
5. View timeline/history
6. Navigate to profile
7. Update profile information
8. Save changes
9. Return to dashboard

### Story 3: Student - Withdraw Draft Application
**Path**: Login → Dashboard → View Draft Application → Withdraw Application

**Steps**:
1. Login as student
2. View dashboard
3. Find draft application
4. Open application details
5. Click withdraw button
6. Confirm withdrawal
7. Verify application status changed

---

## Coordinator User Stories

### Story 4: Coordinator - Review Pending Applications
**Path**: Login → Coordinator Dashboard → View Pending Applications → Review Application → Add Comment → Change Status

**Steps**:
1. Login as coordinator
2. Access coordinator dashboard
3. View pending applications list
4. Filter by status (pending, under_review)
5. Select an application
6. Review application details
7. Review uploaded documents
8. Add internal comment
9. Add public comment (visible to student)
10. Change application status
11. Verify status update
12. Check notification sent

### Story 5: Coordinator - Request Document Resubmission
**Path**: Login → Coordinator Dashboard → Review Application → View Documents → Request Resubmission → Add Comment

**Steps**:
1. Login as coordinator
2. Access coordinator dashboard
3. Select application with documents
4. View document list
5. Review specific document
6. Request document resubmission
7. Add comment explaining why
8. Verify request sent to student
9. Check notification

### Story 6: Coordinator - Approve Application
**Path**: Login → Coordinator Dashboard → Review Complete Application → Validate Documents → Approve Application

**Steps**:
1. Login as coordinator
2. Access coordinator dashboard
3. Find application ready for review
4. Review all application details
5. Validate all required documents
6. Check eligibility criteria
7. Approve application
8. Verify status change
9. Check approval notification

---

## Admin User Stories

### Story 7: Admin - Create New Exchange Program
**Path**: Login → Admin Dashboard → Program Management → Create Program → Configure Settings → Publish Program

**Steps**:
1. Login as admin
2. Access admin dashboard
3. Navigate to program management
4. Click create new program
5. Fill program details (name, description, requirements)
6. Set eligibility criteria (GPA, language)
7. Configure dates (open/close)
8. Set program as active
9. Save program
10. Verify program appears in list
11. View program details

### Story 8: Admin - Manage Users & Roles
**Path**: Login → Admin Dashboard → User Management → View Users → Assign Roles → Update Permissions

**Steps**:
1. Login as admin
2. Access admin dashboard
3. Navigate to user management
4. View user list
5. Filter/search for specific user
6. View user details
7. Assign coordinator role
8. Verify role assignment
9. Check user permissions
10. Update user status

### Story 9: Admin - View Analytics & Reports
**Path**: Login → Admin Dashboard → Analytics → View Metrics → Export Data → Generate Report

**Steps**:
1. Login as admin
2. Access admin dashboard
3. Navigate to analytics
4. View overall statistics
5. View program-specific metrics
6. View application status breakdown
7. View user activity metrics
8. Export data (if available)
9. Generate report

### Story 10: Admin - System Configuration
**Path**: Login → Admin Dashboard → Settings → Configure System → Update Settings → Verify Changes

**Steps**:
1. Login as admin
2. Access admin dashboard
3. Navigate to system settings
4. View current configuration
5. Update notification settings
6. Configure email templates
7. Update system preferences
8. Save changes
9. Verify changes applied

---

## Cross-Role Stories

### Story 11: Complete Application Lifecycle
**Path**: Student Creates → Coordinator Reviews → Coordinator Requests Changes → Student Updates → Coordinator Approves

**Steps**:
1. **Student**: Create and submit application
2. **Coordinator**: Review application, request document resubmission
3. **Student**: Upload new document, resubmit
4. **Coordinator**: Review updated application, add comments
5. **Coordinator**: Approve application
6. **Student**: View approved status and comments

### Story 12: Multi-User Collaboration
**Path**: Multiple Students Apply → Coordinator Reviews All → Admin Views Analytics

**Steps**:
1. **Student 1**: Submit application
2. **Student 2**: Submit application
3. **Coordinator**: View all pending applications
4. **Coordinator**: Review and process applications
5. **Admin**: View analytics showing application trends
6. **Admin**: Generate report

---

## Video Demo Configuration

Each story will be recorded as a separate video with:
- **Video Format**: MP4
- **Resolution**: 1280x720 (HD)
- **Frame Rate**: 30 FPS
- **Audio**: None (silent)
- **Naming**: `demo_{story_number}_{role}_{description}.mp4`

Example: `demo_1_student_registration_first_application.mp4`

