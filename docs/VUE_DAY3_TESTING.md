# Day 3: Authentication Testing Guide

## ✅ Setup Complete

- ✅ Django backend running on `http://localhost:8001`
- ✅ PostgreSQL database (port 5434)
- ✅ Redis cache (port 6379)
- ✅ Test users created

## 🧪 Testing Procedure

### Step 1: Verify Django Backend

Check that Django is accessible:

```powershell
# From project root
curl http://localhost:8001/api/docs/
```

**Expected:** API documentation page loads

Or open in browser: `http://localhost:8001/api/docs/`

### Step 2: Start Vue Dev Server

Open a **NEW PowerShell terminal**:

```powershell
cd c:\Users\mario\OneDrive\Documents\SEIM\frontend-vue
npm run dev
```

**Expected output:**
```
  VITE v7.2.4  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### Step 3: Test Login Page

1. Open browser to: `http://localhost:5173`
2. You should see the login page with:
   - Purple gradient background
   - Email and password fields
   - "Sign In" button

### Step 4: Test Authentication

Use these credentials to test login:

| Role | Email | Password |
|------|-------|----------|
| **Admin** | `admin@test.com` | `admin123` |
| **Coordinator** | `coordinator@test.com` | `coordinator123` |
| **Student** | `student@test.com` | `student123` |
| **Generic** | `test@example.com` | `testpass123` |

**Test with student account:**

1. Email: `student@test.com`
2. Password: `student123`
3. Click "Sign In"

**Expected behavior:**
- ✅ Loading spinner appears
- ✅ Login request sent to `/api/token/`
- ✅ Redirects to `/dashboard`
- ✅ Dashboard shows welcome message with user name
- ✅ Navigation bar shows user dropdown

### Step 5: Verify Dashboard

Once logged in, you should see:

- **Navbar:** 
  - "SEIM" branding
  - User dropdown with name "Student User"
- **Sidebar:**
  - Dashboard (active)
  - Applications
  - Documents
  - Notifications
  - Settings
- **Main Content:**
  - Welcome message: "Welcome, Student User!"
  - 4 stat cards (currently showing 0)
  - Recent Activity section (placeholder)

### Step 6: Check Browser DevTools

Open DevTools (F12) and check:

**Console Tab:**
- ✅ No errors
- ✅ Log: "Dashboard mounted. User: {user object}"

**Network Tab:**
- ✅ POST `/api/token/` - 200 OK (login)
- ✅ GET `/api/accounts/profile/` - 200 OK (profile)

**Application Tab → Local Storage:**
- ✅ `access_token`: JWT token present
- ✅ `refresh_token`: JWT token present

### Step 7: Test Logout

1. Click on user dropdown in navbar
2. Click "Logout"

**Expected behavior:**
- ✅ Redirects to `/login`
- ✅ Tokens cleared from localStorage
- ✅ Cannot access `/dashboard` (redirects to login)

### Step 8: Test Invalid Credentials

1. Go to login page
2. Email: `invalid@test.com`
3. Password: `wrongpass`
4. Click "Sign In"

**Expected behavior:**
- ✅ Error message appears: "Login failed. Please check your credentials."
- ✅ No redirect
- ✅ Form remains enabled

## 📋 Test Checklist

- [ ] Django backend accessible at localhost:8001
- [ ] Vue dev server starts on localhost:5173
- [ ] Login page renders correctly
- [ ] Student login succeeds
- [ ] Dashboard displays after login
- [ ] User name appears in navbar
- [ ] JWT tokens stored in localStorage
- [ ] Profile API called successfully
- [ ] Logout works correctly
- [ ] Tokens cleared after logout
- [ ] Invalid login shows error
- [ ] No console errors during any operation

## 🐛 Troubleshooting

### Issue: Vue dev server won't start

```powershell
# Check if port 5173 is in use
netstat -ano | findstr "5173"

# If in use, kill the process or restart machine
```

### Issue: Cannot connect to Django

```powershell
# Check Django logs
docker-compose logs -f web

# Verify Django is running
docker-compose ps

# Restart if needed
docker-compose restart web
```

### Issue: Login returns 401 Unauthorized

```powershell
# Verify test users exist
docker-compose exec web python manage.py shell

# In Django shell:
from accounts.models import User
User.objects.filter(email='student@test.com').exists()
# Should return: True

# Exit shell
exit()
```

### Issue: CORS errors in browser console

1. Check Django CORS settings in `seim/settings/development.py`
2. Verify `CORS_ALLOWED_ORIGINS` includes `http://localhost:5173`
3. Restart Django: `docker-compose restart web`
4. Hard refresh browser: `Ctrl + Shift + R`

### Issue: Profile API returns 404

```powershell
# Check if profile exists
docker-compose exec web python manage.py shell

# In Django shell:
from accounts.models import Profile, User
user = User.objects.get(email='student@test.com')
profile, created = Profile.objects.get_or_create(user=user)
print(f"Profile: {profile}, Created: {created}")
exit()
```

## 📊 Expected API Calls

### 1. Login: POST /api/token/

**Request:**
```json
{
  "email": "student@test.com",
  "password": "student123"
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 2. Profile: GET /api/accounts/profile/

**Request Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "student@test.com",
  "first_name": "Student",
  "last_name": "User",
  "full_name": "Student User",
  "role": "student",
  "username": "student",
  "secondary_email": null,
  "gpa": null,
  "language": null
}
```

## ✅ Success Criteria

All of the following must pass:

1. ✅ Login with valid credentials succeeds
2. ✅ JWT tokens stored in localStorage
3. ✅ Profile data fetched and displayed
4. ✅ Dashboard renders with user info
5. ✅ Logout clears tokens and redirects
6. ✅ Invalid login shows error message
7. ✅ No JavaScript errors in console
8. ✅ No CORS errors
9. ✅ Token refresh works (if token expires)
10. ✅ Protected routes redirect to login when not authenticated

## 🎉 Once All Tests Pass

Mark the following tasks complete:
- [x] Day 3 Task 4: Test login flow
- [x] Day 3 Task 5: Auth issues fixed
- [x] Day 3 Task 8: Complete auth flow tested

## 📝 Test Results Template

```
Date: 2026-01-29
Tester: [Your Name]

Backend:
- [✅/❌] Django accessible at localhost:8001
- [✅/❌] Test users created successfully

Frontend:
- [✅/❌] Vue dev server starts
- [✅/❌] Login page renders
- [✅/❌] Valid login succeeds
- [✅/❌] Dashboard displays
- [✅/❌] Profile data loads
- [✅/❌] Logout works
- [✅/❌] Invalid login shows error
- [✅/❌] No console errors

Overall Status: [✅ PASSED / ❌ FAILED]

Notes:
- [Add any observations or issues]
```

---

**🎊 Ready to test!** Open two terminals:
1. **Terminal 1:** Django is already running (docker-compose up -d)
2. **Terminal 2:** Run `npm run dev` in frontend-vue/
3. **Browser:** Go to http://localhost:5173

Good luck! 🚀
