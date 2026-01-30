# SEIM Vue.js Migration - Execution Plan

**Project:** SEIM Student Exchange Information Manager  
**Start Date:** TBD  
**Target Completion:** 9 weeks from start  
**Last Updated:** 2026-01-29

---

## 🎯 Migration Strategy

### What We're Keeping (No Changes)
- ✅ **Django Backend** - All business logic, models, ORM
- ✅ **Django Admin** at `/seim/admin/` - Staff management
- ✅ **Wagtail CMS** at `/cms/` - Content management
- ✅ **All REST APIs** at `/api/` - Endpoints stay the same
- ✅ **JWT Authentication** - Already configured
- ✅ **WebSocket** (Channels) - Real-time notifications
- ✅ **PostgreSQL + Redis** - Database and caching
- ✅ **Celery** - Background tasks

### What We're Replacing
- 🔄 **Django Templates** → Vue.js components
- 🔄 **Frontend app** (`/seim/` routes) → Vue Router
- 🔄 **jQuery** → Vue.js reactivity
- 🔄 **Inline JavaScript** → Vue SPA

### New URL Structure
```
/                       → Vue.js SPA (student/staff interface)
/login                  → Vue.js login page
/dashboard              → Vue.js dashboard
/applications           → Vue.js applications
/programs               → Vue.js programs
...etc                  → All user-facing pages in Vue

/seim/admin/            → Django Admin (unchanged)
/cms/                   → Wagtail CMS Admin (unchanged)
/api/                   → REST API endpoints (unchanged)
/api/token/             → JWT token endpoints (unchanged)
/api/docs/              → Swagger API docs (unchanged)
```

---

## 📋 Pre-Migration Checklist

### Before You Start
- [ ] **Backup everything** - Full database and code backup
- [ ] **Git clean state** - Commit all pending changes
- [ ] **Create feature branch** - `git checkout -b feature/vue-migration`
- [ ] **Document current features** - List everything that must work
- [ ] **Team alignment** - Everyone knows the plan
- [ ] **Stakeholder approval** - Business sign-off obtained
- [ ] **Resource allocation** - 1 senior dev for 9 weeks confirmed

---

## 🚀 Phase 0: Backend Preparation (Week 1)

### Day 1: Environment & API Audit

#### Morning: Backend Setup
```bash
# 1. Create new branch
git checkout -b feature/vue-migration

# 2. Verify current backend is working
python manage.py runserver
# Test: http://localhost:8000/api/docs/

# 3. Check all dependencies
pip list | grep -E "(django|rest|cors|jwt)"
```

**Expected Output:**
```
Django                        5.1.4
djangorestframework          3.16.1
django-cors-headers          4.9.0
djangorestframework-simplejwt 5.5.1
```

#### Afternoon: API Audit
- [ ] Document all API endpoints (use `/api/docs/`)
- [ ] Test each endpoint with Postman/Insomnia
- [ ] Verify JWT authentication works
- [ ] Check CORS settings
- [ ] Test WebSocket connection

**Create:** `docs/API_ENDPOINTS.md` - List all endpoints for Vue to use

---

### Day 2: Django Configuration for Vue SPA

#### Update CORS Settings

**File:** `seim/settings/base.py`

```python
# Add to CORS configuration (around line 200-220)

# Development CORS - Allow Vue dev server
if DEBUG:
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:5173",
        "http://localhost:3000",  # Alternative port
    ]
    CORS_ALLOW_CREDENTIALS = True
else:
    # Production - Your domain
    CORS_ALLOWED_ORIGINS = [
        "https://your-domain.com",
        "https://www.your-domain.com",
    ]
    CORS_ALLOW_CREDENTIALS = True

# Allow all methods for development
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Allow common headers
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
```

#### Update URL Configuration

**File:** `seim/urls.py` (Replace entire file)

```python
"""
URL configuration for SEIM project - Vue.js SPA Version
"""
from django.contrib import admin
from django.urls import include, path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django_js_reverse.views import urls_js
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Wagtail imports
from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from core.views import health_check

urlpatterns = [
    # Health check
    path("health/", health_check, name="health_check"),
    
    # Django Admin (staff only)
    path("seim/admin/", admin.site.urls),
    
    # Wagtail CMS Admin (staff only)
    path("cms/", include(wagtailadmin_urls)),
    path("cms-documents/", include(wagtaildocs_urls)),
    
    # REST API Endpoints (used by Vue.js frontend)
    path("api/", include(("api.urls", "api"), namespace="api")),
    path("api/accounts/", include("accounts.urls")),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    
    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    
    # Application forms API
    path('api/application-forms/', include(('application_forms.urls', 'application_forms'), namespace='application_forms')),
    
    # Internationalization
    path('i18n/', include('django.conf.urls.i18n')),
    
    # JavaScript reverse URLs (if needed)
    path("jsreverse/", urls_js, name="js_reverse"),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Vue.js SPA - Catch all routes (EXCEPT admin and API)
# This serves the Vue app for all user-facing URLs
urlpatterns += [
    # Serve Vue.js index.html for all non-API, non-admin routes
    re_path(r'^(?!seim/admin|cms|api|media|static).*$', 
            TemplateView.as_view(template_name='index.html'), 
            name='vue-app'),
]
```

**Key Changes:**
- Removed `/seim/` frontend URLs (handled by Vue now)
- Added catch-all route for Vue SPA
- Kept admin and API routes separate
- Vue handles ALL user-facing URLs

#### Update Template Configuration

**File:** `seim/settings/base.py` (around line 100-120)

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',  # Keep for admin/Wagtail
            BASE_DIR / 'frontend-vue' / 'dist',  # Vue.js build output
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'wagtail.contrib.settings.context_processors.settings',
            ],
        },
    },
]
```

#### Update Static Files Configuration

**File:** `seim/settings/base.py` (around line 350-370)

```python
# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [
    BASE_DIR / 'static',  # Django static files
    BASE_DIR / 'frontend-vue' / 'dist' / 'assets',  # Vue.js build assets
]

# WhiteNoise configuration for production static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

**Action Items:**
- [ ] Update `seim/settings/base.py` - CORS settings
- [ ] Update `seim/urls.py` - URL routing
- [ ] Update `seim/settings/base.py` - Templates config
- [ ] Update `seim/settings/base.py` - Static files config
- [ ] Test: `python manage.py check` - Should pass

---

### Day 3: Vue.js Project Setup

#### Create Vue Project

```bash
# In project root (c:\Users\mario\OneDrive\Documents\SEIM)
npm create vue@latest frontend-vue

# When prompted:
# ✔ TypeScript? … Yes
# ✔ JSX Support? … No
# ✔ Vue Router? … Yes
# ✔ Pinia? … Yes
# ✔ Vitest? … Yes
# ✔ E2E Testing? … Yes (Playwright)
# ✔ ESLint? … Yes
# ✔ Prettier? … Yes

cd frontend-vue
npm install

# Install additional dependencies
npm install axios bootstrap@5.3.0 bootstrap-icons
npm install -D @types/bootstrap
```

#### Configure Vite

**File:** `frontend-vue/vite.config.ts`

```typescript
import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
      '/media': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    emptyOutDir: true,
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          'bootstrap': ['bootstrap'],
        },
      },
    },
  },
})
```

#### Create Environment Files

**File:** `frontend-vue/.env.development`

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

**File:** `frontend-vue/.env.production`

```env
VITE_API_URL=https://your-domain.com
VITE_WS_URL=wss://your-domain.com
```

#### Update .gitignore

**File:** `.gitignore` (add these lines)

```gitignore
# Vue.js frontend
frontend-vue/node_modules/
frontend-vue/dist/
frontend-vue/.vite/
frontend-vue/.env.local
frontend-vue/.env.*.local
frontend-vue/coverage/
frontend-vue/playwright-report/
frontend-vue/test-results/
```

**Action Items:**
- [ ] Create Vue project
- [ ] Install dependencies
- [ ] Configure Vite
- [ ] Create env files
- [ ] Update .gitignore
- [ ] Test: `npm run dev` in frontend-vue folder

---

### Day 4: Core Vue Infrastructure

Follow `VUE_QUICKSTART_GUIDE.md` to create:

- [ ] API client (`src/services/api.ts`)
- [ ] Auth store (`src/stores/auth.ts`)
- [ ] Router setup (`src/router/index.ts`)
- [ ] Basic folder structure

**Test:** Can call Django API from Vue dev server

---

### Day 5: Integration Testing

#### Test Django + Vue Integration

**Terminal 1:** Start Django
```bash
cd c:\Users\mario\OneDrive\Documents\SEIM
python manage.py runserver
```

**Terminal 2:** Start Vue
```bash
cd c:\Users\mario\OneDrive\Documents\SEIM\frontend-vue
npm run dev
```

**Browser:** Open http://localhost:5173

**Tests:**
- [ ] Vue dev server runs
- [ ] Can call `/api/token/` - Get JWT token
- [ ] Can call `/api/accounts/profile/` - Get user data
- [ ] CORS works (no errors in console)
- [ ] WebSocket connects (check console)

**Troubleshooting:**
- CORS errors? Check Django CORS settings
- 404 on API? Check proxy in vite.config.ts
- Token issues? Check JWT settings in Django

---

## 🏗️ Phase 1: Authentication & Foundation (Week 2-3)

Follow `VUE_FIRST_SPRINT.md` for detailed day-by-day tasks.

### Week 2 Deliverables
- ✅ Login page working
- ✅ JWT authentication working
- ✅ Protected routes working
- ✅ Basic dashboard
- ✅ User state management

### Week 3 Deliverables
- ✅ Role-based dashboards
- ✅ Navigation components
- ✅ Common UI components library
- ✅ API integration tested

---

## 🎨 Phase 2: Core Pages Migration (Week 4-5)

### Pages to Migrate (Priority Order)

#### Week 4: Student Interface

**Day 1-2: Applications**
- [ ] Applications list page
- [ ] Application detail view
- [ ] Application status tracking

**Day 3-4: Programs**
- [ ] Programs list with filters
- [ ] Program detail view
- [ ] Program search

**Day 5: Documents**
- [ ] Documents list
- [ ] Document upload
- [ ] Document viewer

#### Week 5: Staff/Admin Interface

**Day 1-2: Coordinator Dashboard**
- [ ] Application review interface
- [ ] Document validation
- [ ] Status updates

**Day 3-4: Admin Features**
- [ ] User management interface
- [ ] System analytics
- [ ] Settings management

**Day 5: Polish & Integration**
- [ ] Fix bugs
- [ ] Add loading states
- [ ] Add error handling

---

## 🚀 Phase 3: Feature Completion (Week 6-7)

### Week 6: Advanced Features

**Applications Module:**
- [ ] Create new application
- [ ] Edit application
- [ ] Submit application
- [ ] Withdraw application
- [ ] Application timeline
- [ ] Comments/notes

**Programs Module:**
- [ ] Program creation (admin)
- [ ] Program editing (admin)
- [ ] Program activation/deactivation
- [ ] Program analytics

**Documents Module:**
- [ ] Multiple file upload
- [ ] Document types
- [ ] Document validation workflow
- [ ] Document resubmission

### Week 7: Notifications & Real-time

**Notification Center:**
- [ ] Notification list
- [ ] Mark as read
- [ ] Notification preferences
- [ ] Real-time updates via WebSocket

**WebSocket Integration:**
- [ ] Connect to Django Channels
- [ ] Handle reconnection
- [ ] Display toast notifications
- [ ] Update UI in real-time

---

## ✨ Phase 4: Polish & Testing (Week 8)

### Day 1-2: Unit Testing

```bash
cd frontend-vue
npm run test
```

**Target Coverage:** 80%+

- [ ] Auth store tests
- [ ] API client tests
- [ ] Component tests (critical components)
- [ ] Router tests
- [ ] Utility function tests

### Day 3-4: E2E Testing

```bash
cd frontend-vue
npx playwright test
```

**Critical Flows:**
- [ ] Login flow
- [ ] Create application flow
- [ ] Upload document flow
- [ ] Application review flow (coordinator)
- [ ] Logout flow

### Day 5: Performance & Accessibility

**Performance:**
- [ ] Run Lighthouse audit
- [ ] Optimize bundle size
- [ ] Add lazy loading
- [ ] Add loading skeletons

**Accessibility:**
- [ ] WCAG 2.1 AA compliance
- [ ] Keyboard navigation
- [ ] Screen reader testing
- [ ] Color contrast check

---

## 🚀 Phase 5: Production Deployment (Week 9)

### Day 1: Build & Test

```bash
cd frontend-vue
npm run build
```

**Verify:**
- [ ] Build succeeds
- [ ] No console errors
- [ ] Bundle size acceptable (<1MB)
- [ ] All routes work in production build

### Day 2: Django Production Setup

#### Update requirements.txt

No changes needed - Django already has everything!

#### Collect Static Files

```bash
python manage.py collectstatic --noinput
```

This will copy Vue's `dist/` files to Django's `staticfiles/`

### Day 3: Docker Update

**File:** `Dockerfile` (Add Node.js for building Vue)

```dockerfile
# syntax=docker/dockerfile:1
FROM node:18 AS frontend-builder

# Build Vue.js frontend
WORKDIR /app/frontend-vue
COPY frontend-vue/package*.json ./
RUN npm ci
COPY frontend-vue/ ./
RUN npm run build

# Python stage
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    libmagic1 \
    libjpeg-dev \
    libpng-dev \
    libwebp-dev \
    zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements*.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements-dev.txt

# Copy project files
COPY . .

# Copy Vue build from frontend-builder
COPY --from=frontend-builder /app/frontend-vue/dist /app/frontend-vue/dist

# Create media directory
RUN mkdir -p /app/media

# Collect static files
RUN python manage.py collectstatic --noinput

# Make scripts executable
RUN chmod +x /app/scripts/wait-for-db.sh

EXPOSE 8000

CMD ["/app/scripts/wait-for-db.sh"]
```

### Day 4: Deployment

#### Development Server

```bash
# Terminal 1: Django
python manage.py runserver 0.0.0.0:8000

# Terminal 2: Vue (only for development)
cd frontend-vue && npm run dev
```

#### Production Server

```bash
# Build Vue
cd frontend-vue
npm run build

# Collect static files
python manage.py collectstatic --noinput

# Run with Gunicorn + Daphne
daphne -b 0.0.0.0 -p 8000 seim.asgi:application
```

#### Docker Compose

```bash
docker-compose up --build
```

### Day 5: Monitoring & Rollback Plan

**Monitoring:**
- [ ] Set up error tracking (Sentry already configured)
- [ ] Monitor API response times
- [ ] Track user sessions
- [ ] Monitor WebSocket connections

**Rollback Plan:**

1. **Keep old frontend code** in separate branch
2. **If issues arise:**
   ```bash
   # Quick rollback
   git checkout main
   git revert feature/vue-migration
   docker-compose down
   docker-compose up --build
   ```

3. **Or revert Django URLs:**
   - Restore old `seim/urls.py`
   - Re-enable `frontend` app
   - Restart server

---

## 📊 Progress Tracking

### Week-by-Week Checklist

**Week 1: Preparation** ⏳
- [ ] Backend audit complete
- [ ] Django configured for Vue
- [ ] Vue project created
- [ ] Integration tested

**Week 2-3: Foundation** ⏳
- [ ] Authentication working
- [ ] Dashboard created
- [ ] Navigation working
- [ ] Component library started

**Week 4-5: Core Pages** ⏳
- [ ] All student pages migrated
- [ ] All staff pages migrated
- [ ] All features working

**Week 6-7: Advanced Features** ⏳
- [ ] CRUD operations complete
- [ ] File uploads working
- [ ] WebSocket notifications live

**Week 8: Testing & Polish** ⏳
- [ ] 80%+ test coverage
- [ ] E2E tests passing
- [ ] Performance optimized
- [ ] Accessibility compliant

**Week 9: Deployment** ⏳
- [ ] Production build successful
- [ ] Docker updated
- [ ] Deployed to production
- [ ] Monitoring active

---

## 🐛 Common Issues & Solutions

### Issue: CORS Errors
**Symptom:** Console shows CORS policy errors

**Solution:**
```python
# seim/settings/base.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
]
CORS_ALLOW_CREDENTIALS = True
```

### Issue: 404 on API Calls
**Symptom:** `/api/...` returns 404

**Solution:**
- Check Vite proxy configuration
- Verify Django URLs are correct
- Check Django is running on port 8000

### Issue: Authentication Loop
**Symptom:** Keeps redirecting to login

**Solution:**
- Check JWT token is being saved to localStorage
- Verify token is sent in Authorization header
- Check token hasn't expired

### Issue: Static Files Not Loading
**Symptom:** Vue app shows blank page in production

**Solution:**
```bash
python manage.py collectstatic --noinput
# Check STATIC_ROOT and STATICFILES_DIRS in settings
```

### Issue: WebSocket Won't Connect
**Symptom:** Real-time notifications not working

**Solution:**
- Verify Daphne is running (not just Gunicorn)
- Check WebSocket URL (ws:// not http://)
- Verify channels is in INSTALLED_APPS

---

## 📞 Daily Standup Questions

Use these for daily check-ins:

1. **What did I accomplish yesterday?**
2. **What am I working on today?**
3. **Any blockers or issues?**
4. **Am I on track with the timeline?**
5. **Do I need help from anyone?**

---

## 🎯 Success Criteria

### Technical
- ✅ All features from Django templates working in Vue
- ✅ JWT authentication working correctly
- ✅ Real-time notifications working
- ✅ >80% test coverage
- ✅ Lighthouse score >90
- ✅ Zero critical bugs

### Business
- ✅ Users can perform all previous tasks
- ✅ Performance improved (faster navigation)
- ✅ Mobile experience improved
- ✅ Staff training completed
- ✅ Documentation updated

### Team
- ✅ Team confident with Vue.js
- ✅ Code is maintainable
- ✅ Development velocity increased
- ✅ Fewer bugs reported

---

## 📚 Resources

### Documentation
- **Vue 3:** https://vuejs.org/
- **Vue Router:** https://router.vuejs.org/
- **Pinia:** https://pinia.vuejs.org/
- **Vite:** https://vitejs.dev/
- **DRF:** https://www.django-rest-framework.org/

### Project Docs
- `VUE_MIGRATION_PLAN.md` - Master plan
- `VUE_QUICKSTART_GUIDE.md` - 30-min setup
- `VUE_FIRST_SPRINT.md` - Week 1-2 details
- `VUE_DECISION_SUMMARY.md` - Business justification

---

## 🚀 Getting Started NOW

### Option 1: Quick Test (30 minutes)
```bash
# Follow VUE_QUICKSTART_GUIDE.md
# See Vue.js working with your Django backend
```

### Option 2: Start Migration (This Week)
```bash
# Day 1-5 of this plan
# Set up everything properly
# Begin building
```

**Which do you want to start with?**

---

**Document Owner:** Senior Frontend Developer  
**Status:** Ready to Execute  
**Next Review:** End of Week 1  
**Questions?** Refer to detailed guides or ask team lead
