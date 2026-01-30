# Vue.js Manual Test Flow – Results

**Date:** 2026-01-29  
**Branch:** feature/vue-migration  
**Backend:** Django on http://localhost:8001 (Docker)  
**Frontend:** Vue dev server on http://localhost:5173  

---

## API Flow (Automated)

The following steps were run via PowerShell against the Django API with JWT.

| Step | Endpoint | Result |
|------|----------|--------|
| 1. Login | POST /api/token/ (email + password) | OK – access token received |
| 2. Profile | GET /api/accounts/profile/ | OK – User: Student User, email: student@test.com |
| 3. Dashboard stats | GET /api/accounts/dashboard/stats/ | OK – Applications: 0, Documents: 0, Notifications: 2, Pending: 0 |
| 4. Applications list | GET /api/applications/ | OK – Count: 0 |
| 5. Programs list | GET /api/programs/ | OK – Count: 6 |
| 6. Documents list | GET /api/documents/ | OK – Count: 0 |
| 7. Notifications list | GET /api/notifications/ | OK – Count: 3 |

**Conclusion:** All API steps passed.

---

## Fixes Applied During Test

### 1. JWT login with email

- **Issue:** Vue sends `email` + `password`; default simplejwt expects `username` + `password`, so login failed with “username required”.
- **Change:** Custom JWT view that accepts `email` + `password`.
  - Added `accounts/jwt_views.py`: `CustomTokenObtainPairSerializer`, `CustomTokenObtainPairView`.
  - In `api/urls.py`, token endpoint now uses `CustomTokenObtainPairView`.
- **Result:** Login with `student@test.com` / `student123` works.

### 2. Dashboard stats FieldError

- **Issue:** GET /api/accounts/dashboard/stats/ returned `FieldError` (wrong field name).
- **Cause:** `Application` model uses `student`, not `user`, for the applicant.
- **Change:** In `accounts/views_dashboard.py`, `Application.objects.filter(user=user)` → `Application.objects.filter(student=user)` (and same for `pending`).
- **Result:** Dashboard stats endpoint returns 200 and correct counts.

---

## Browser Manual Test (You Can Run)

1. **Start backend (if not already):**  
   `docker-compose up -d`

2. **Start frontend:**  
   `cd frontend-vue` then `npm run dev`  
   App: http://localhost:5173

3. **Login:**  
   Email: `student@test.com`  
   Password: `student123`  
   → Should redirect to dashboard with welcome and stats.

4. **Dashboard:**  
   - Four stat cards (Applications, Documents, Notifications, Pending).  
   - Sidebar: Dashboard, Applications, Documents, Notifications.  
   - Navbar: bell icon (unread count), user dropdown.  
   - Click Applications → list (empty or with data).  
   - Click Documents → list.  
   - Click Notifications → list (e.g. 3 items); try “Mark as read” / “Mark all read”.

5. **Applications:**  
   - “New Application” → select program, optional statement, Create.  
   - Open an application → detail with timeline; upload document if draft/submitted.

6. **Logout:**  
   User menu → Logout → redirect to login; visiting /dashboard should redirect to login.

---

## Summary

- **API flow:** All 7 steps passed after the two fixes above.
- **Vue app:** Login now works with email; dashboard stats load correctly.
- **Next:** Run the browser steps above and use `docs/VUE_TEST_CHECKLIST.md` for a full checklist.
