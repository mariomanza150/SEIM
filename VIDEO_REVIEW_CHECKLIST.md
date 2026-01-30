# 🎬 Video Demo Review Checklist

## Overview

This checklist helps you systematically review all 12 video demos to spot issues, verify functionality, and ensure workflows match expectations.

**Location**: `tests/e2e_playwright/videos/`  
**Format**: WebM (VP8/VP9 codec)  
**Total Videos**: 12 demos covering all user roles

---

## Quick Access

### Open Videos Folder
```powershell
# Windows
explorer tests\e2e_playwright\videos

# Or use the helper script
.\scripts\review_videos.ps1
```

### Recommended Video Player
- **VLC Media Player** (free, cross-platform) - Best for WebM files
- **Windows Media Player** (built-in, may need codec)
- **Chrome/Edge** (can play WebM directly)

---

## Review Checklist Template

For each video, check the following:

### ✅ Functionality
- [ ] All steps complete successfully
- [ ] No unexpected errors or 404s
- [ ] Forms submit correctly
- [ ] Navigation works smoothly
- [ ] Status changes reflect properly
- [ ] Data persists correctly

### 🎨 UI/UX
- [ ] Page layouts are correct
- [ ] Buttons/links are visible and clickable
- [ ] Forms are properly formatted
- [ ] Error messages display correctly
- [ ] Success messages appear
- [ ] Loading states are shown
- [ ] No broken images or missing assets

### 🐛 Bugs & Issues
- [ ] No JavaScript console errors
- [ ] No broken links
- [ ] No missing data
- [ ] No permission issues
- [ ] No race conditions
- [ ] No responsive design problems

### 📱 Responsive Design
- [ ] Elements properly sized
- [ ] Text is readable
- [ ] Forms are usable
- [ ] Navigation accessible
- [ ] No horizontal scrolling

---

## Video-by-Video Review

### Student Demos (3 videos)

#### Demo 1: New Student Registration & First Application
**Expected Path**: Registration → Email Verification → Login → Browse Programs → Create Application → Upload Documents → Submit Application

**Checkpoints**:
- [ ] Homepage loads correctly
- [ ] Registration link is accessible
- [ ] Login page displays properly
- [ ] Student can log in successfully
- [ ] Dashboard shows after login
- [ ] Programs page displays available programs
- [ ] Application creation form is accessible
- [ ] Form fields are visible and usable
- [ ] Documents page is accessible
- [ ] Application list shows created applications
- [ ] Application details page displays correctly

**Issues Found**:
```
[Document any issues here]
```

---

#### Demo 2: Returning Student - Check Status & Update
**Expected Path**: Login → Dashboard → View Applications → Check Status → Update Profile

**Checkpoints**:
- [ ] Student logs in successfully
- [ ] Dashboard displays with applications
- [ ] Applications list is accessible
- [ ] Application details page loads
- [ ] Status information is visible
- [ ] Timeline/history section displays (if present)
- [ ] Profile page is accessible
- [ ] Edit profile functionality works (if available)
- [ ] Save button is visible (if edit form exists)

**Issues Found**:
```
[Document any issues here]
```

---

#### Demo 3: Student - Withdraw Draft Application
**Expected Path**: Login → Dashboard → View Draft Application → Withdraw Application

**Checkpoints**:
- [ ] Student logs in successfully
- [ ] Dashboard displays
- [ ] Applications list shows draft applications
- [ ] Application details page loads
- [ ] Withdraw button is visible (if draft status)
- [ ] Withdrawal flow is accessible

**Issues Found**:
```
[Document any issues here]
```

---

### Coordinator Demos (3 videos)

#### Demo 4: Coordinator - Review Pending Applications
**Expected Path**: Login → Coordinator Dashboard → View Pending Applications → Review Application → Add Comment → Change Status

**Checkpoints**:
- [ ] Coordinator logs in successfully
- [ ] Coordinator dashboard is accessible
- [ ] Applications list displays
- [ ] Filter options are visible (if present)
- [ ] Application details page loads
- [ ] Application details are scrollable
- [ ] Documents section is visible
- [ ] Comment form is accessible (if present)
- [ ] Public comment toggle is visible (if present)
- [ ] Status dropdown is accessible (if present)

**Issues Found**:
```
[Document any issues here]
```

---

#### Demo 5: Coordinator - Request Document Resubmission
**Expected Path**: Login → Coordinator Dashboard → Review Application → View Documents → Request Resubmission → Add Comment

**Checkpoints**:
- [ ] Coordinator logs in successfully
- [ ] Coordinator dashboard is accessible
- [ ] Applications list displays
- [ ] Application details page loads
- [ ] Documents section is visible and scrollable
- [ ] Individual document links are accessible
- [ ] Resubmission request button is visible (if present)
- [ ] Comment area is accessible

**Issues Found**:
```
[Document any issues here]
```

---

#### Demo 6: Coordinator - Approve Application
**Expected Path**: Login → Coordinator Dashboard → Review Complete Application → Validate Documents → Approve Application

**Checkpoints**:
- [ ] Coordinator logs in successfully
- [ ] Coordinator dashboard is accessible
- [ ] Applications list displays
- [ ] Application details page loads
- [ ] Full application details are scrollable
- [ ] Eligibility section is visible (if present)
- [ ] Approve button is visible (if application is ready)

**Issues Found**:
```
[Document any issues here]
```

---

### Admin Demos (4 videos)

#### Demo 7: Admin - Create New Exchange Program
**Expected Path**: Login → Admin Dashboard → Program Management → Create Program → Configure Settings → Publish Program

**Checkpoints**:
- [ ] Admin logs in successfully
- [ ] Admin dashboard is accessible
- [ ] Program creation page is accessible
- [ ] Create button is visible (if present)
- [ ] Form fields are visible and scrollable
- [ ] Save button is accessible
- [ ] Programs list displays after navigation

**Issues Found**:
```
[Document any issues here]
```

---

#### Demo 8: Admin - Manage Users & Roles
**Expected Path**: Login → Admin Dashboard → User Management → View Users → Assign Roles → Update Permissions

**Checkpoints**:
- [ ] Admin logs in successfully
- [ ] Admin dashboard is accessible
- [ ] User management page is accessible
- [ ] User list is scrollable
- [ ] Search/filter input is visible (if present)
- [ ] User detail links are accessible
- [ ] Role assignment section is visible (if present)

**Issues Found**:
```
[Document any issues here]
```

---

#### Demo 9: Admin - View Analytics & Reports
**Expected Path**: Login → Admin Dashboard → Analytics → View Metrics → Export Data → Generate Report

**Checkpoints**:
- [ ] Admin logs in successfully
- [ ] Admin dashboard displays metrics
- [ ] Analytics page is accessible
- [ ] Statistics section is visible
- [ ] Metrics are scrollable
- [ ] Status breakdown section is visible (if present)
- [ ] Activity metrics section is visible (if present)
- [ ] Export button is visible (if present)

**Issues Found**:
```
[Document any issues here]
```

---

#### Demo 10: Admin - System Configuration
**Expected Path**: Login → Admin Dashboard → Settings → Configure System → Update Settings → Verify Changes

**Checkpoints**:
- [ ] Admin logs in successfully
- [ ] Admin dashboard is accessible
- [ ] Settings page is accessible
- [ ] Configuration sections are scrollable
- [ ] Notification settings section is visible (if present)
- [ ] Email template section is visible (if present)
- [ ] System preferences section is visible (if present)

**Issues Found**:
```
[Document any issues here]
```

---

### Cross-Role Demos (2 videos)

#### Demo 11: Complete Application Lifecycle
**Expected Path**: Student Creates → Coordinator Reviews → Coordinator Requests Changes → Student Updates → Coordinator Approves

**Checkpoints**:
- [ ] Student login works
- [ ] Application creation page is accessible
- [ ] Role switch (logout/login) works smoothly
- [ ] Coordinator login works
- [ ] Applications list displays for coordinator
- [ ] Application details are accessible
- [ ] Review workflow is visible

**Issues Found**:
```
[Document any issues here]
```

---

#### Demo 12: Multi-User Collaboration
**Expected Path**: Multiple Students Apply → Coordinator Reviews All → Admin Views Analytics

**Checkpoints**:
- [ ] Student view displays applications
- [ ] Role switch to coordinator works
- [ ] Coordinator dashboard displays
- [ ] Role switch to admin works
- [ ] Admin analytics page is accessible
- [ ] Multi-role navigation is smooth

**Issues Found**:
```
[Document any issues here]
```

---

## Summary Section

### Overall Assessment

**Total Videos Reviewed**: ___ / 12

**Critical Issues Found**: ___
- [List critical issues]

**Major Issues Found**: ___
- [List major issues]

**Minor Issues Found**: ___
- [List minor issues]

**UI/UX Improvements Needed**: ___
- [List UI/UX issues]

**Functionality Issues**: ___
- [List functionality issues]

### Priority Actions

1. **High Priority**:
   - [Issue 1]
   - [Issue 2]

2. **Medium Priority**:
   - [Issue 1]
   - [Issue 2]

3. **Low Priority**:
   - [Issue 1]
   - [Issue 2]

### Next Steps

- [ ] Create bug reports for critical issues
- [ ] Update user stories if workflows don't match
- [ ] Refine tests based on findings
- [ ] Re-record videos after fixes
- [ ] Update documentation with findings

---

## Video File Mapping

The videos are named with hash identifiers. To identify which video corresponds to which demo, check the creation time:

| Demo # | Description | Approx. Creation Time | File Size Range |
|--------|-------------|----------------------|-----------------|
| 1 | New Student Registration | 7:41-7:42 AM | ~1.4 MB |
| 2 | Returning Student Check Status | 7:42-7:43 AM | ~1.4 MB |
| 3 | Student Withdraw Draft | 7:43 AM | ~0.7 MB |
| 4 | Coordinator Review Pending | 7:43-7:44 AM | ~0.8 MB |
| 5 | Coordinator Request Resubmission | 7:44 AM | ~0.7 MB |
| 6 | Coordinator Approve | 7:44 AM | ~0.8 MB |
| 7 | Admin Create Program | 7:44-7:45 AM | ~1.3 MB |
| 8 | Admin Manage Users | 7:45 AM | ~1.0 MB |
| 9 | Admin View Analytics | 7:45 AM | ~0.5 MB |
| 10 | Admin System Config | 7:45-7:46 AM | ~0.9 MB |
| 11 | Complete Lifecycle | 7:46-7:47 AM | ~1.7 MB |
| 12 | Multi-User Collaboration | 7:47 AM | ~2.5 MB |

**Note**: The largest video (2.5 MB) is Demo 12 (Multi-User Collaboration) as it involves multiple role switches.

---

**Review Date**: _______________  
**Reviewed By**: _______________  
**Status**: ⬜ In Progress | ⬜ Complete | ⬜ Needs Re-review

