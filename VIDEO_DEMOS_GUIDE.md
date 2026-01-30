# 🎬 Video Demo Walkthroughs Guide

## Overview

This guide explains how to generate comprehensive video demos of user workflows for review and issue spotting. Each video demonstrates a complete user story path through the SEIM application.

## Quick Start

### Generate All Video Demos
```bash
make e2e-video-demos
```

Or using Docker directly:
```bash
docker-compose -f docker-compose.e2e.yml run --rm e2e_playwright pytest tests/e2e_playwright/test_video_demos.py -v -m video_demo
```

### Generate Specific Demo
```bash
docker-compose -f docker-compose.e2e.yml run --rm e2e_playwright pytest tests/e2e_playwright/test_video_demos.py::TestStudentVideoDemos::test_demo_1_new_student_registration_first_application -v -m video_demo
```

## Available Video Demos

### Student Demos (3 videos)

1. **Demo 1: New Student Registration & First Application**
   - Registration → Email Verification → Login → Browse Programs → Create Application → Upload Documents → Submit Application
   - File: `demo_1_new_student_registration_first_application.webm`

2. **Demo 2: Returning Student - Check Status & Update**
   - Login → Dashboard → View Applications → Check Status → Update Profile
   - File: `demo_2_returning_student_check_status.webm`

3. **Demo 3: Student - Withdraw Draft Application**
   - Login → Dashboard → View Draft Application → Withdraw Application
   - File: `demo_3_student_withdraw_draft.webm`

### Coordinator Demos (3 videos)

4. **Demo 4: Coordinator - Review Pending Applications**
   - Login → Coordinator Dashboard → View Pending Applications → Review Application → Add Comment → Change Status
   - File: `demo_4_coordinator_review_pending.webm`

5. **Demo 5: Coordinator - Request Document Resubmission**
   - Login → Coordinator Dashboard → Review Application → View Documents → Request Resubmission → Add Comment
   - File: `demo_5_coordinator_request_resubmission.webm`

6. **Demo 6: Coordinator - Approve Application**
   - Login → Coordinator Dashboard → Review Complete Application → Validate Documents → Approve Application
   - File: `demo_6_coordinator_approve_application.webm`

### Admin Demos (4 videos)

7. **Demo 7: Admin - Create New Exchange Program**
   - Login → Admin Dashboard → Program Management → Create Program → Configure Settings → Publish Program
   - File: `demo_7_admin_create_program.webm`

8. **Demo 8: Admin - Manage Users & Roles**
   - Login → Admin Dashboard → User Management → View Users → Assign Roles → Update Permissions
   - File: `demo_8_admin_manage_users.webm`

9. **Demo 9: Admin - View Analytics & Reports**
   - Login → Admin Dashboard → Analytics → View Metrics → Export Data → Generate Report
   - File: `demo_9_admin_view_analytics.webm`

10. **Demo 10: Admin - System Configuration**
    - Login → Admin Dashboard → Settings → Configure System → Update Settings → Verify Changes
    - File: `demo_10_admin_system_configuration.webm`

### Cross-Role Demos (2 videos)

11. **Demo 11: Complete Application Lifecycle**
    - Student Creates → Coordinator Reviews → Coordinator Requests Changes → Student Updates → Coordinator Approves
    - File: `demo_11_complete_application_lifecycle.webm`

12. **Demo 12: Multi-User Collaboration**
    - Multiple Students Apply → Coordinator Reviews All → Admin Views Analytics
    - File: `demo_12_multi_user_collaboration.webm`

## Video Specifications

- **Format**: WebM (VP8/VP9 codec)
- **Resolution**: 1280x720 (HD)
- **Frame Rate**: 30 FPS
- **Audio**: None (silent videos)
- **Location**: `tests/e2e_playwright/videos/`

## Viewing Videos

### On Windows
```powershell
# Open videos folder
explorer tests\e2e_playwright\videos

# Or play specific video
Start-Process tests\e2e_playwright\videos\demo_1_new_student_registration_first_application.webm
```

### On Mac/Linux
```bash
# Open videos folder
open tests/e2e_playwright/videos  # Mac
xdg-open tests/e2e_playwright/videos  # Linux

# Play specific video
vlc tests/e2e_playwright/videos/demo_1_new_student_registration_first_application.webm
```

### Recommended Players
- **VLC Media Player** (cross-platform, free)
- **Windows Media Player** (Windows)
- **QuickTime** (Mac)
- **MPV** (Linux)

## Review Checklist

When reviewing videos, check for:

### ✅ Functionality
- [ ] All steps in the user story complete successfully
- [ ] No unexpected errors or redirects
- [ ] Forms submit correctly
- [ ] Navigation works as expected
- [ ] Status changes reflect properly

### 🎨 UI/UX Issues
- [ ] Page layouts are correct
- [ ] Buttons and links are visible and clickable
- [ ] Forms are properly formatted
- [ ] Error messages display correctly
- [ ] Success messages appear
- [ ] Loading states are shown

### 🐛 Bugs to Spot
- [ ] Broken links or 404 errors
- [ ] JavaScript errors (check browser console)
- [ ] Missing or incorrect data
- [ ] Permission issues
- [ ] Race conditions or timing issues
- [ ] Responsive design problems

### 📱 Responsive Design
- [ ] Elements are properly sized
- [ ] Text is readable
- [ ] Forms are usable
- [ ] Navigation is accessible
- [ ] No horizontal scrolling

## Customizing Videos

### Change Video Resolution
Edit `tests/e2e_playwright/conftest.py`:
```python
config["record_video"] = {
    "dir": str(videos_dir),
    "size": {"width": 1920, "height": 1080}  # Full HD
}
```

### Add Slow Motion
Add `--slowmo=500` to pytest command:
```bash
docker-compose -f docker-compose.e2e.yml run --rm e2e_playwright pytest tests/e2e_playwright/test_video_demos.py -v -m video_demo --slowmo=500
```

### Run in Headed Mode (See Browser)
Add `--headed` flag:
```bash
docker-compose -f docker-compose.e2e.yml run --rm e2e_playwright pytest tests/e2e_playwright/test_video_demos.py -v -m video_demo --headed
```

## Troubleshooting

### Videos Not Generated
1. Check that `tests/e2e_playwright/videos/` directory exists
2. Verify test has `@pytest.mark.video_demo` marker
3. Check Docker volume mounts in `docker-compose.e2e.yml`

### Videos Are Empty
1. Tests might be failing - check test output
2. Verify web service is running and accessible
3. Check browser is launching correctly

### Videos Too Large
1. Reduce video resolution in `conftest.py`
2. Shorten test duration (reduce `time.sleep()` calls)
3. Use video compression tools

### Can't Play Videos
1. Install VLC Media Player (recommended)
2. Convert to MP4 if needed: `ffmpeg -i input.webm output.mp4`
3. Check video codec support in your player

## Converting Videos

### Convert WebM to MP4
```bash
# Using ffmpeg
ffmpeg -i tests/e2e_playwright/videos/demo_1.webm tests/e2e_playwright/videos/demo_1.mp4

# Batch convert all
for file in tests/e2e_playwright/videos/*.webm; do
    ffmpeg -i "$file" "${file%.webm}.mp4"
done
```

## Sharing Videos

### For Team Review
1. Upload to shared drive (OneDrive, Google Drive, etc.)
2. Share link in project documentation
3. Add to project wiki or documentation site

### For Documentation
1. Convert to MP4 for better compatibility
2. Add to documentation site
3. Embed in user guides

## Next Steps

After reviewing videos:
1. Document any issues found
2. Create bug reports for critical issues
3. Update user stories if workflows don't match expectations
4. Refine tests based on findings
5. Re-record videos after fixes

---

**Generated**: 2025-11-26  
**Total Demos**: 12 videos  
**Coverage**: All major user workflows  
**Status**: Ready for review

