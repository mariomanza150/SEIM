# SEIM Vue.js Migration - Week 1 Tasks

**Goal:** Have Django backend ready for Vue.js and Vue project set up  
**Duration:** 5 days  
**Output:** Working Vue app talking to Django backend

---

## ✅ Pre-Flight Checklist

Before starting Day 1:

- [ ] **Full backup** of database and code
- [ ] **Commit** all current work to Git
- [ ] **Create branch:** `git checkout -b feature/vue-migration`
- [ ] **Node.js 18+** installed (`node --version`)
- [ ] **npm** available (`npm --version`)
- [ ] **Django running** (`python manage.py runserver`)
- [ ] **Team notified** about migration start

---

## 📅 Day 1: Backend Configuration

**Time:** 6-8 hours  
**Goal:** Configure Django to work with Vue SPA

### Morning: Update Django Settings (3 hours)

#### Task 1.1: Update CORS Settings

**File:** `seim\settings\base.py`

**Find this section** (around line 200):

```python
# CORS settings
```

**Replace with:**

```python
# CORS Configuration for Vue.js SPA
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
    "http://127.0.0.1:5173",
    "http://localhost:3000",  # Alternative
] if DEBUG else [
    "https://your-domain.com",  # Production domain
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

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

**Test:**
```bash
python manage.py check
# Should see: System check identified no issues (0 silenced).
```

---

#### Task 1.2: Update Template Directories

**File:** `seim\settings\base.py`

**Find TEMPLATES section** (around line 100):

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
```

**Change to:**

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',  # Keep for Django admin/Wagtail
            BASE_DIR / 'frontend-vue' / 'dist',  # Vue build output
        ],
```

---

#### Task 1.3: Update Static Files

**File:** `seim\settings\base.py`

**Find STATICFILES_DIRS** (around line 350):

```python
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
```

**Change to:**

```python
STATICFILES_DIRS = [
    BASE_DIR / 'static',
    # Vue assets will be added here after first build:
    # BASE_DIR / 'frontend-vue' / 'dist' / 'assets',
]

# Note: Uncomment the Vue assets line after first Vue build
```

**Save all files**

---

### Afternoon: Update URL Configuration (3 hours)

#### Task 1.4: Backup Current URLs

```bash
# Create backup
cp seim\urls.py seim\urls_OLD_BACKUP.py
```

#### Task 1.5: Update URLs for Vue SPA

**File:** `seim\urls.py`

**Replace the entire file with:**

```python
"""
URL configuration for SEIM project - Vue.js SPA Version
Separates admin/API routes from user-facing routes (handled by Vue)
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
    # ============================================
    # ADMIN INTERFACES (Server-side Django/Wagtail)
    # ============================================
    path("seim/admin/", admin.site.urls),  # Django Admin
    path("cms/", include(wagtailadmin_urls)),  # Wagtail CMS Admin
    path("cms-documents/", include(wagtaildocs_urls)),
    
    # ============================================
    # REST API ENDPOINTS (Used by Vue.js)
    # ============================================
    path("api/", include(("api.urls", "api"), namespace="api")),
    path("api/accounts/", include("accounts.urls")),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/application-forms/", include(('application_forms.urls', 'application_forms'), namespace='application_forms')),
    
    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    
    # ============================================
    # UTILITIES
    # ============================================
    path("health/", health_check, name="health_check"),
    path('i18n/', include('django.conf.urls.i18n')),
    path("jsreverse/", urls_js, name="js_reverse"),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# ============================================
# VUE.JS SPA - CATCH ALL USER-FACING ROUTES
# ============================================
# This must be LAST - catches all routes not matched above
# Vue Router will handle the actual routing
urlpatterns += [
    re_path(r'^(?!seim/admin|cms|api|media|static).*$', 
            TemplateView.as_view(template_name='index.html'), 
            name='vue-app'),
]
```

**Save and test:**

```bash
python manage.py check
# Should pass with no errors

python manage.py runserver
# Visit http://localhost:8000/api/docs/
# Should see Swagger API documentation
```

---

#### Task 1.6: Update .gitignore

**File:** `.gitignore`

**Add these lines at the end:**

```gitignore
# Vue.js Frontend
frontend-vue/node_modules/
frontend-vue/dist/
frontend-vue/.vite/
frontend-vue/.env.local
frontend-vue/.env.*.local
frontend-vue/coverage/
frontend-vue/playwright-report/
frontend-vue/test-results/
frontend-vue/.eslintcache
```

---

### End of Day 1: Commit Changes

```bash
git add .
git commit -m "Configure Django for Vue.js SPA integration

- Update CORS settings for Vue dev server
- Add Vue dist folder to template directories
- Update URL configuration to serve Vue SPA
- Keep admin and API routes separate
- Add Vue files to .gitignore"

git push origin feature/vue-migration
```

**✅ Day 1 Complete!** Django is ready for Vue.js

---

## 📅 Day 2: Vue Project Setup

**Time:** 6-8 hours  
**Goal:** Create and configure Vue.js project

### Morning: Create Vue Project (3 hours)

#### Task 2.1: Create Vue Project

```bash
# In project root: C:\Users\mario\OneDrive\Documents\SEIM
npm create vue@latest frontend-vue
```

**Interactive Prompts - Choose:**
```
✔ Project name: frontend-vue
✔ Add TypeScript? Yes
✔ Add JSX Support? No
✔ Add Vue Router for Single Page Application development? Yes
✔ Add Pinia for state management? Yes
✔ Add Vitest for Unit Testing? Yes
✔ Add an End-to-End Testing Solution? Yes › Playwright
✔ Add ESLint for code quality? Yes
✔ Add Prettier for code formatting? Yes
```

**Install dependencies:**

```bash
cd frontend-vue
npm install

# Install additional packages
npm install axios bootstrap@5.3.0 bootstrap-icons
npm install -D @types/bootstrap

# Verify installation
npm list
```

**Expected output:** Should see all packages installed without errors

---

#### Task 2.2: Configure Vite

**File:** `frontend-vue\vite.config.ts`

**Replace entire contents with:**

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
      // Proxy API calls to Django backend
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      // Proxy WebSocket connections
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
        changeOrigin: true,
      },
      // Proxy media files
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

---

#### Task 2.3: Create Environment Files

**File:** `frontend-vue\.env.development`

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
VITE_APP_TITLE=SEIM - Student Exchange
```

**File:** `frontend-vue\.env.production`

```env
VITE_API_URL=https://your-production-domain.com
VITE_WS_URL=wss://your-production-domain.com
VITE_APP_TITLE=SEIM - Student Exchange
```

---

### Afternoon: Test Integration (3 hours)

#### Task 2.4: Start Development Servers

**Terminal 1 - Django:**
```bash
cd C:\Users\mario\OneDrive\Documents\SEIM
python manage.py runserver
```

**Terminal 2 - Vue:**
```bash
cd C:\Users\mario\OneDrive\Documents\SEIM\frontend-vue
npm run dev
```

**Expected output:**
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

---

#### Task 2.5: Test Connection

**Open browser:** http://localhost:5173

**Should see:** Default Vue welcome page

**Open browser console (F12):**

```javascript
// Test API connection
fetch('http://localhost:5173/api/schema/')
  .then(r => r.json())
  .then(d => console.log('API Connected:', d))
  .catch(e => console.error('API Error:', e))
```

**Expected:** Should see API schema data, no CORS errors

---

### End of Day 2: Commit Vue Project

```bash
git add .
git commit -m "Initialize Vue.js project with Vite

- Create Vue 3 project with TypeScript
- Configure Vite with Django proxy
- Set up development and production environments
- Install Bootstrap and required dependencies
- Test integration with Django backend"

git push origin feature/vue-migration
```

**✅ Day 2 Complete!** Vue project set up and talking to Django

---

## 📅 Day 3: Core Infrastructure

**Time:** 8 hours  
**Goal:** Build API client, auth store, and router

### Task 3.1: Create Folder Structure (30 minutes)

```bash
cd frontend-vue\src
mkdir services composables types stores components\common components\forms components\layout views\auth views\dashboard utils
```

**Your structure should look like:**
```
src/
├── assets/
├── components/
│   ├── common/
│   ├── forms/
│   └── layout/
├── composables/
├── router/
├── services/
├── stores/
├── types/
├── utils/
├── views/
│   ├── auth/
│   └── dashboard/
├── App.vue
└── main.ts
```

---

### Task 3.2: Create API Client (1 hour)

**File:** `frontend-vue\src\services\api.ts`

**Copy code from** `VUE_QUICKSTART_GUIDE.md` section "Create API Client"

Or create from scratch:

```typescript
import axios, { type AxiosInstance, type AxiosError, type InternalAxiosRequestConfig } from 'axios'

const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - add JWT token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('seim_access_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

// Response interceptor - handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      const refreshToken = localStorage.getItem('seim_refresh_token')
      if (refreshToken) {
        try {
          const response = await axios.post('http://localhost:8000/api/token/refresh/', {
            refresh: refreshToken
          })
          const newToken = response.data.access
          localStorage.setItem('seim_access_token', newToken)
          
          if (error.config) {
            error.config.headers.Authorization = `Bearer ${newToken}`
            return api.request(error.config)
          }
        } catch (refreshError) {
          localStorage.removeItem('seim_access_token')
          localStorage.removeItem('seim_refresh_token')
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(error)
  }
)

export default api
```

**Test:**
```bash
npm run dev
# Check for TypeScript errors
```

---

### Task 3.3: Create Auth Store (2 hours)

**File:** `frontend-vue\src\stores\auth.ts`

**Copy complete code from** `VUE_QUICKSTART_GUIDE.md` section "Create Auth Store"

**Test:**
```bash
npm run dev
# No TypeScript errors
```

---

### Task 3.4: Configure Router (2 hours)

**File:** `frontend-vue\src\router\index.ts`

**Copy complete code from** `VUE_QUICKSTART_GUIDE.md` section "Create Router"

---

### Task 3.5: Create Type Definitions (1 hour)

**File:** `frontend-vue\src\types\models.ts`

```typescript
export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  role: 'student' | 'coordinator' | 'admin'
  is_active: boolean
  date_joined: string
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface LoginResponse {
  access: string
  refresh: string
  user: User
}

export interface Application {
  id: string
  program: string
  status: string
  created_at: string
  updated_at: string
  student: number
}

export interface Program {
  id: number
  name: string
  description: string
  is_active: boolean
  start_date: string
  end_date: string
}
```

---

### End of Day 3: Commit Infrastructure

```bash
git add .
git commit -m "Add Vue.js core infrastructure

- Create API client with JWT token management
- Add auth store with Pinia
- Configure Vue Router with auth guards
- Define TypeScript types for models
- Set up folder structure"

git push origin feature/vue-migration
```

**✅ Day 3 Complete!** Core infrastructure ready

---

## 📅 Day 4: Login Page

**Time:** 6-8 hours  
**Goal:** Working login page with authentication

### Task 4.1: Create Login Component (3 hours)

**File:** `frontend-vue\src\views\auth\Login.vue`

**Copy complete code from** `VUE_QUICKSTART_GUIDE.md` section "Login Page"

---

### Task 4.2: Update Main App (1 hour)

**File:** `frontend-vue\src\App.vue`

```vue
<template>
  <div id="app">
    <RouterView />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

onMounted(async () => {
  // Initialize auth on app load
  await authStore.initialize()
})
</script>

<style>
@import 'bootstrap/dist/css/bootstrap.min.css';
@import 'bootstrap-icons/font/bootstrap-icons.css';

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #f5f7fa;
}

#app {
  min-height: 100vh;
}
</style>
```

---

### Task 4.3: Create Home/Landing Page (2 hours)

**File:** `frontend-vue\src\views\Home.vue`

```vue
<template>
  <div class="home">
    <div class="hero">
      <h1>SEIM</h1>
      <p>Student Exchange Information Manager</p>
      <div class="actions">
        <router-link to="/login" class="btn btn-primary btn-lg">
          Login
        </router-link>
        <router-link to="/register" class="btn btn-outline-light btn-lg">
          Register
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

onMounted(() => {
  // Redirect to dashboard if already logged in
  if (authStore.isAuthenticated) {
    router.push('/dashboard')
  }
})
</script>

<style scoped>
.home {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.hero {
  text-align: center;
  color: white;
  padding: 2rem;
}

.hero h1 {
  font-size: 4rem;
  font-weight: bold;
  margin-bottom: 1rem;
}

.hero p {
  font-size: 1.5rem;
  margin-bottom: 2rem;
  opacity: 0.9;
}

.actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.btn {
  padding: 1rem 2rem;
  font-size: 1.1rem;
  text-decoration: none;
  border-radius: 0.5rem;
  transition: all 0.3s;
}

.btn-primary {
  background: white;
  color: #667eea;
  border: 2px solid white;
}

.btn-primary:hover {
  background: transparent;
  color: white;
}

.btn-outline-light {
  background: transparent;
  color: white;
  border: 2px solid white;
}

.btn-outline-light:hover {
  background: white;
  color: #667eea;
}
</style>
```

---

### Task 4.4: Test Login Flow (1 hour)

**Start servers:**

Terminal 1:
```bash
python manage.py runserver
```

Terminal 2:
```bash
cd frontend-vue
npm run dev
```

**Test sequence:**
1. Open http://localhost:5173
2. Should see home page
3. Click "Login"
4. Enter credentials (use Django admin user)
5. Submit form
6. Should redirect to dashboard (even if empty)
7. Check browser localStorage - should have tokens

**Debug:**
- Check browser console for errors
- Check Network tab for API calls
- Verify `/api/token/` is called
- Verify `/api/accounts/profile/` is called

---

### End of Day 4: Commit Login Feature

```bash
git add .
git commit -m "Add login page and authentication flow

- Create login page with form
- Add home/landing page
- Integrate with auth store
- Test complete login flow
- Add navigation guards"

git push origin feature/vue-migration
```

**✅ Day 4 Complete!** Can login to Vue app!

---

## 📅 Day 5: Dashboard & Review

**Time:** 6-8 hours  
**Goal:** Basic dashboard and week review

### Task 5.1: Create Dashboard (4 hours)

**File:** `frontend-vue\src\views\dashboard\Dashboard.vue`

**Copy complete code from** `VUE_QUICKSTART_GUIDE.md` section "Dashboard Page"

---

### Task 5.2: Create 404 Page (1 hour)

**File:** `frontend-vue\src\views\NotFound.vue`

```vue
<template>
  <div class="not-found">
    <h1>404</h1>
    <p>Page not found</p>
    <router-link to="/dashboard" class="btn btn-primary">
      Go to Dashboard
    </router-link>
  </div>
</template>

<style scoped>
.not-found {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.not-found h1 {
  font-size: 6rem;
  color: #667eea;
  margin-bottom: 1rem;
}

.not-found p {
  font-size: 1.5rem;
  color: #666;
  margin-bottom: 2rem;
}

.btn {
  padding: 0.75rem 2rem;
  text-decoration: none;
  background: #667eea;
  color: white;
  border-radius: 0.5rem;
}
</style>
```

---

### Task 5.3: Week 1 Review (2 hours)

**Checklist - What Works:**
- [ ] Django runs without errors
- [ ] Vue dev server runs
- [ ] Can call API from Vue
- [ ] Login page works
- [ ] Authentication stores tokens
- [ ] Dashboard loads after login
- [ ] Can logout
- [ ] Protected routes redirect to login
- [ ] No CORS errors
- [ ] No console errors

**If any items above don't work - FIX THEM before Week 2!**

---

### Task 5.4: Documentation

Create: `WEEK1_SUMMARY.md`

```markdown
# Week 1 Summary

## Completed
- ✅ Django configured for Vue SPA
- ✅ Vue project created and configured
- ✅ API client with JWT token management
- ✅ Auth store with Pinia
- ✅ Vue Router with navigation guards
- ✅ Login page working
- ✅ Dashboard (basic version)
- ✅ Integration tested

## Issues Encountered
[List any problems and how you solved them]

## Next Week
- Build out dashboard components
- Add role-based views
- Create component library
- Add more pages (applications, programs)

## Team Feedback
[Notes from the team]
```

---

### End of Day 5: Final Week 1 Commit

```bash
git add .
git commit -m "Complete Week 1 - Vue.js foundation ready

- Add dashboard with user info
- Add 404 page
- Week 1 review complete
- All critical infrastructure working
- Ready for Week 2 feature development"

git push origin feature/vue-migration

# Create pull request for review (optional)
# Or merge to main if approved
```

**✅ Week 1 Complete!** 🎉

---

## 🎯 Week 1 Success Criteria

You've succeeded if:
- ✅ Can start Django backend
- ✅ Can start Vue frontend
- ✅ Can login through Vue
- ✅ Tokens are saved and used
- ✅ Dashboard loads user data
- ✅ Can logout
- ✅ No critical errors
- ✅ Team understands the setup

---

## 📚 Resources Used This Week

- `VUE_MIGRATION_EXECUTION_PLAN.md` - Master plan
- `VUE_QUICKSTART_GUIDE.md` - Code examples
- Vue.js docs - https://vuejs.org
- Django REST docs - https://www.django-rest-framework.org

---

## 🚀 Ready for Week 2?

**Week 2 Focus:**
- Build dashboard components
- Add role-based content
- Create reusable UI components
- Add navigation
- Start building feature pages

**Follow:** `VUE_FIRST_SPRINT.md` for Week 2 tasks

---

**Celebrate!** You've laid the foundation for a modern Vue.js frontend! 🎊

**Document Version:** 1.0  
**Status:** Ready to Execute  
**Questions?** Review detailed guides or ask team
