# Vue.js Day 2 - Integration Test Guide

## 🎯 What We're Testing

Verify that the Vue.js dev server can:
1. Start successfully
2. Proxy API calls to Django backend in Docker
3. Render the login page
4. Connect to Django API endpoints

## 📋 Prerequisites

- ✅ Day 1 complete (Django configured for Vue)
- ✅ Day 2 complete (Vue project created)
- ✅ Docker Desktop running
- ✅ Node.js 18+ installed

## 🧪 Test Procedure

### Step 1: Start Django Backend

```powershell
# From project root
cd c:\Users\mario\OneDrive\Documents\SEIM

# Start all Docker services
docker-compose up -d

# Wait 30 seconds for services to initialize

# Verify services are running
docker-compose ps
```

**Expected Output:**
```
NAME                IMAGE               STATUS
seim-web-1          seim-web           Up (healthy)
seim-db-1           postgres:15        Up (healthy)
seim-redis-1        redis:7.2-alpine   Up (healthy)
seim-celery-1       seim-celery        Up
seim-celery-beat-1  seim-celery-beat   Up
```

**Check Django is accessible:**
```powershell
# Open browser to
http://localhost:8000/api/docs/
```

You should see the Swagger API documentation.

### Step 2: Start Vue Dev Server

```powershell
# Open a NEW terminal
cd c:\Users\mario\OneDrive\Documents\SEIM\frontend-vue

# Start Vue dev server
npm run dev
```

**Expected Output:**
```
  VITE v7.2.4  ready in 1234 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

### Step 3: Test Vue Application

Open your browser to: `http://localhost:5173`

**Expected Results:**

✅ **Login page renders**
- Purple gradient background
- Login form with email and password fields
- "Sign In" button
- No console errors

✅ **API proxy works**
Open browser DevTools (F12) → Network tab

Try to login with any credentials (even if they fail):
- Email: `test@example.com`
- Password: `test123`

In Network tab, you should see:
- Request to `/api/token/`
- Status: `401 Unauthorized` (expected - we don't have test data yet)
- No CORS errors
- Request went through Vue proxy to Django

### Step 4: Verify CORS Configuration

Check browser console (F12 → Console):

✅ **No CORS errors like:**
```
❌ Access to XMLHttpRequest at 'http://localhost:8000/api/token/' 
   from origin 'http://localhost:5173' has been blocked by CORS policy
```

✅ **Expected 401 error is OK:**
```
✅ POST http://localhost:8000/api/token/ 401 (Unauthorized)
```

This means:
- Vue can reach Django
- CORS is configured correctly
- Authentication is working (rejecting invalid credentials)

### Step 5: Test Direct API Access

Open browser to: `http://localhost:5173/api/docs/`

✅ **Should see Django API docs** (proxied through Vite)

This confirms the Vite proxy is working correctly.

## ✅ Success Criteria

| Test | Status | Details |
|------|--------|---------|
| Docker services start | ✅ | All containers healthy |
| Django API accessible | ✅ | http://localhost:8000/api/docs/ loads |
| Vue dev server starts | ✅ | http://localhost:5173 accessible |
| Login page renders | ✅ | No console errors, UI displays |
| API proxy works | ✅ | Requests reach Django backend |
| CORS configured | ✅ | No CORS errors in console |
| Auth flow works | ✅ | 401 error on invalid credentials |

## 🐛 Troubleshooting

### Issue: Docker services won't start

```powershell
# Check Docker Desktop is running
docker --version

# Check for port conflicts
netstat -ano | findstr "8000"
netstat -ano | findstr "5432"
netstat -ano | findstr "6379"

# Rebuild containers
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Issue: Vue dev server won't start

```powershell
# Check Node.js version
node --version  # Should be 18+

# Check port 5173 is free
netstat -ano | findstr "5173"

# Reinstall dependencies
cd frontend-vue
Remove-Item -Recurse -Force node_modules
npm install
npm run dev
```

### Issue: CORS errors

1. Check Django CORS settings:
```python
# seim/settings/development.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
```

2. Restart Django:
```powershell
docker-compose restart web
```

3. Hard refresh browser: `Ctrl + Shift + R`

### Issue: 404 on API calls

1. Check Vite proxy configuration in `vite.config.js`
2. Check Django URLs in `seim/urls.py`
3. Check Django logs:
```powershell
docker-compose logs -f web
```

### Issue: Authentication always fails

This is expected! We haven't created test users yet. The important thing is:
- No CORS errors
- Request reaches Django (status 401)
- Vue app doesn't crash

## 📊 Test Results Log

Document your test results:

```
Date: 2026-01-29
Tester: [Your Name]

✅ Step 1: Docker services started successfully
✅ Step 2: Vue dev server started on port 5173
✅ Step 3: Login page renders without errors
✅ Step 4: API proxy works (401 response received)
✅ Step 5: CORS configured correctly (no CORS errors)

Overall Status: ✅ PASSED

Notes:
- All tests passed on first attempt
- No errors in console
- Ready for Day 3 development
```

## 🎉 Next Steps

Once all tests pass:

1. ✅ Mark Day 2 as complete
2. 📝 Update `VUE_MIGRATION_CHECKLIST.md`
3. 🚀 Ready to start Day 3: Create test user and implement auth flow
4. 💾 Commit test documentation

## 📝 Quick Reference

**Start Development Environment:**
```powershell
# Terminal 1: Django Backend
docker-compose up -d

# Terminal 2: Vue Frontend
cd frontend-vue
npm run dev
```

**Stop Development Environment:**
```powershell
# Stop Vue dev server
Ctrl + C

# Stop Docker services
docker-compose down
```

**Access Points:**
- Vue App: http://localhost:5173
- Django API: http://localhost:8000/api/
- Django Admin: http://localhost:8000/seim/admin/
- Wagtail CMS: http://localhost:8000/cms/
- API Docs: http://localhost:8000/api/docs/

---

**🎊 Congratulations on completing Day 2!**
