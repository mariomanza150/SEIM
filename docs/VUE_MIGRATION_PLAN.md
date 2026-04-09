# SEIM Frontend - Vue.js Migration Plan

**Date:** January 29, 2026  
**Decision:** Migrate from Django Templates + jQuery to Vue.js SPA  
**Strategy:** Keep Django backend, admin, and useful components

> Historical planning document. Keep this file for migration rationale only. It supersedes the narrower working-note files that previously lived alongside it: `docs/VUE_MIGRATION_EXECUTION_PLAN.md`, `docs/VUE_DAY2_TEST_GUIDE.md`, `docs/VUE_DAY3_TESTING.md`, and `docs/VUE_WEEK1_TASKS.md`. For the current implementation state, use `frontend-vue/README.md` and `docs/VUE_TEST_RESULTS.md`.

---

## 🎯 Migration Strategy Overview

### What We're Keeping ✅
- **Django Backend:** All REST APIs, business logic, ORM
- **Django Admin:** Complete admin interface
- **Django Auth:** Session management for admin
- **REST API:** All existing endpoints
- **WebSocket:** Real-time notifications
- **Database:** PostgreSQL with all models
- **Celery:** Background tasks
- **Redis:** Caching and WebSocket

### What We're Replacing 🔄
- **Django Templates** → Vue.js Components
- **jQuery** → Vue.js Reactivity
- **Inline JavaScript** → Vue.js Composition API
- **Bootstrap JS** → Vue.js Components (or keep Bootstrap CSS)
- **Template-based routing** → Vue Router

### What We're Adding ➕
- **Vue 3** with Composition API
- **Vue Router** for client-side routing
- **Pinia** for state management
- **Vite** for blazing fast builds
- **TypeScript** (optional but recommended)
- **Vue DevTools** for debugging

---

## 🏗️ New Architecture

```
┌──────────────────────────────────────────────────┐
│                 Vue.js SPA                        │
│  • Vue 3 + Composition API                        │
│  • Vue Router (client-side routing)               │
│  • Pinia (state management)                       │
│  • Vite (build tool)                              │
└───────────────────┬──────────────────────────────┘
                    │
                    │ HTTP/REST + WebSocket
                    │
┌───────────────────┴──────────────────────────────┐
│              Django Backend                       │
│  • REST API (DRF)                                 │
│  • JWT Authentication                             │
│  • WebSocket (Django Channels)                    │
│  • Business Logic                                 │
│  • Database (PostgreSQL)                          │
└───────────────────┬──────────────────────────────┘
                    │
┌───────────────────┴──────────────────────────────┐
│         Django Admin (Separate)                   │
│  • /admin/ (traditional Django)                   │
│  • Session-based auth                             │
│  • Staff/admin management                         │
└──────────────────────────────────────────────────┘
```

---

## 📂 New Project Structure

```
SEIM/
├── backend/                        # Django Backend
│   ├── seim/                       # Django project
│   ├── accounts/                   # User management
│   ├── exchange/                   # Exchange programs
│   ├── documents/                  # Document handling
│   ├── notifications/              # Notifications
│   ├── analytics/                  # Analytics
│   ├── api/                        # API endpoints
│   └── manage.py
│
├── frontend-vue/                   # NEW Vue.js SPA
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── main.ts                 # App entry point
│   │   ├── App.vue                 # Root component
│   │   ├── router/
│   │   │   └── index.ts            # Vue Router config
│   │   ├── stores/                 # Pinia stores
│   │   │   ├── auth.ts             # Auth state
│   │   │   ├── user.ts             # User state
│   │   │   └── notifications.ts   # Notifications
│   │   ├── views/                  # Page components
│   │   │   ├── Home.vue
│   │   │   ├── Dashboard.vue
│   │   │   ├── Login.vue
│   │   │   ├── Applications/
│   │   │   ├── Programs/
│   │   │   └── Documents/
│   │   ├── components/             # Reusable components
│   │   │   ├── common/
│   │   │   │   ├── AppHeader.vue
│   │   │   │   ├── AppFooter.vue
│   │   │   │   └── AppSidebar.vue
│   │   │   ├── forms/
│   │   │   ├── tables/
│   │   │   └── notifications/
│   │   ├── composables/            # Vue composables
│   │   │   ├── useAuth.ts
│   │   │   ├── useApi.ts
│   │   │   ├── useWebSocket.ts
│   │   │   └── useNotifications.ts
│   │   ├── services/               # API services
│   │   │   ├── api.ts              # API client
│   │   │   ├── auth.ts             # Auth service
│   │   │   ├── applications.ts
│   │   │   ├── programs.ts
│   │   │   └── documents.ts
│   │   ├── utils/                  # Utilities
│   │   │   ├── formatters.ts
│   │   │   ├── validators.ts
│   │   │   └── constants.ts
│   │   ├── assets/                 # Static assets
│   │   │   ├── styles/
│   │   │   └── images/
│   │   └── types/                  # TypeScript types
│   │       ├── models.ts
│   │       └── api.ts
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── index.html
│
└── docs/
    └── VUE_MIGRATION_PLAN.md       # This file
```

---

## 🚀 Migration Approach: Gradual vs Big Bang

### Option A: Big Bang Migration (Recommended)
**Timeline:** 6-8 weeks  
**Risk:** Medium  
**Approach:** Build complete Vue app, switch over at once

**Pros:**
- Clean break, no legacy code
- Simpler to reason about
- Faster once complete
- No hybrid complexity

**Cons:**
- Longer before users see benefits
- Higher initial risk
- Need feature parity before launch

### Option B: Gradual Migration
**Timeline:** 12-16 weeks  
**Risk:** Low  
**Approach:** Page by page migration

**Pros:**
- Lower risk
- Can deploy incrementally
- Easier rollback

**Cons:**
- Two systems to maintain
- Complex routing setup
- Longer total time
- More technical debt

**Recommendation:** **Option A (Big Bang)** - Your current frontend needs significant work anyway, so a clean rewrite makes sense.

---

## 📅 Implementation Timeline

### Phase 0: Preparation (Week 1)
**Goal:** Set up Vue project and ensure backend API is ready

**Tasks:**
- [ ] Audit existing Django REST API endpoints
- [ ] Document API contracts
- [ ] Fix any API issues
- [ ] Set up Vue 3 project with Vite
- [ ] Install dependencies (Vue Router, Pinia, Axios)
- [ ] Configure TypeScript
- [ ] Set up ESLint, Prettier
- [ ] Create base folder structure

**Deliverables:**
- Working Vue dev environment
- API documentation
- Project boilerplate

---

### Phase 1: Core Infrastructure (Week 2-3)
**Goal:** Build foundation - auth, routing, state management

**Tasks:**
- [ ] Set up Vue Router with routes
- [ ] Create Pinia stores (auth, user, notifications)
- [ ] Build API client with Axios interceptors
- [ ] Implement JWT authentication
- [ ] Create auth composables (useAuth, useUser)
- [ ] Build layout components (header, footer, sidebar)
- [ ] Set up WebSocket client
- [ ] Implement dark mode with Vue
- [ ] Create error handling system
- [ ] Set up loading states

**Key Files to Create:**
```typescript
// src/services/api.ts
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 10000
})

// Request interceptor
api.interceptors.request.use((config) => {
  const authStore = useAuthStore()
  if (authStore.token) {
    config.headers.Authorization = `Bearer ${authStore.token}`
  }
  return config
})

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const authStore = useAuthStore()
      await authStore.refreshToken()
    }
    return Promise.reject(error)
  }
)

export default api
```

```typescript
// src/stores/auth.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<User | null>(null)
  
  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isCoordinator = computed(() => 
    ['admin', 'coordinator'].includes(user.value?.role || '')
  )
  
  async function login(username: string, password: string) {
    const response = await api.post('/api/accounts/login/', {
      username,
      password
    })
    token.value = response.data.access
    localStorage.setItem('token', response.data.access)
    localStorage.setItem('refresh', response.data.refresh)
    await fetchUser()
  }
  
  async function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('refresh')
  }
  
  async function fetchUser() {
    const response = await api.get('/api/accounts/profile/')
    user.value = response.data
  }
  
  return { token, user, isAuthenticated, isAdmin, isCoordinator, login, logout }
})
```

**Deliverables:**
- Working authentication flow
- Protected routes
- API integration
- Layout components

---

### Phase 2: Core Pages (Week 4-5)
**Goal:** Build main user-facing pages

**Tasks:**
- [ ] Home/Landing page
- [ ] Login page
- [ ] Register page
- [ ] Dashboard (student view)
- [ ] Dashboard (coordinator view)
- [ ] Dashboard (admin view)
- [ ] Profile page
- [ ] Settings page
- [ ] 404/Error pages

**Example Dashboard Component:**
```vue
<!-- src/views/Dashboard.vue -->
<template>
  <div class="dashboard">
    <DashboardHeader :user="user" @refresh="loadData" />
    
    <div class="dashboard-content">
      <!-- Quick Actions -->
      <QuickActions :role="user.role" />
      
      <!-- Statistics -->
      <StatisticsCards 
        v-if="stats"
        :stats="stats"
        :role="user.role"
      />
      
      <!-- Recent Activity -->
      <RecentActivity 
        :applications="recentApplications"
        :loading="loading"
      />
      
      <!-- Role-specific content -->
      <component 
        :is="roleComponent"
        :user="user"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useApplicationsStore } from '@/stores/applications'
import DashboardHeader from '@/components/dashboard/DashboardHeader.vue'
import QuickActions from '@/components/dashboard/QuickActions.vue'
import StatisticsCards from '@/components/dashboard/StatisticsCards.vue'
import RecentActivity from '@/components/dashboard/RecentActivity.vue'
import StudentDashboard from '@/components/dashboard/StudentDashboard.vue'
import CoordinatorDashboard from '@/components/dashboard/CoordinatorDashboard.vue'
import AdminDashboard from '@/components/dashboard/AdminDashboard.vue'

const authStore = useAuthStore()
const applicationsStore = useApplicationsStore()

const user = computed(() => authStore.user)
const stats = ref(null)
const recentApplications = ref([])
const loading = ref(false)

const roleComponent = computed(() => {
  switch (user.value?.role) {
    case 'admin': return AdminDashboard
    case 'coordinator': return CoordinatorDashboard
    default: return StudentDashboard
  }
})

async function loadData() {
  loading.value = true
  try {
    const [statsData, appsData] = await Promise.all([
      applicationsStore.fetchStats(),
      applicationsStore.fetchRecent()
    ])
    stats.value = statsData
    recentApplications.value = appsData
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.dashboard {
  padding: 2rem;
}

.dashboard-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}
</style>
```

**Deliverables:**
- All core pages functional
- Role-based views working
- Navigation working

---

### Phase 3: Feature Modules (Week 6-7)
**Goal:** Build feature-specific pages and components

**Applications Module:**
- [ ] Applications list
- [ ] Application detail
- [ ] Application form (create/edit)
- [ ] Application status workflow

**Programs Module:**
- [ ] Programs list
- [ ] Program detail
- [ ] Program form (admin only)
- [ ] Program search/filter

**Documents Module:**
- [ ] Documents list
- [ ] Document upload
- [ ] Document viewer
- [ ] Document validation (coordinator)

**Notifications Module:**
- [ ] Notification center
- [ ] Notification preferences
- [ ] Real-time updates

**Deliverables:**
- All major features working
- Full CRUD operations
- File uploads working
- Real-time notifications

---

### Phase 4: Polish & Testing (Week 8)
**Goal:** Refinement, testing, optimization

**Tasks:**
- [ ] Add comprehensive unit tests (Vitest)
- [ ] Add E2E tests (Playwright)
- [ ] Performance optimization
- [ ] Accessibility audit (WCAG 2.1 AA)
- [ ] Mobile responsiveness
- [ ] Dark mode polish
- [ ] Error handling refinement
- [ ] Loading states polish
- [ ] SEO meta tags
- [ ] Analytics integration

**Deliverables:**
- >80% test coverage
- All major browsers tested
- Performance optimized
- Accessibility compliant

---

### Phase 5: Deployment & Migration (Week 9)
**Goal:** Deploy to production

**Tasks:**
- [ ] Build production bundle
- [ ] Configure Django to serve Vue app
- [ ] Set up CI/CD pipeline
- [ ] Database migration (if needed)
- [ ] User communication
- [ ] Staged rollout (beta users first)
- [ ] Monitor errors
- [ ] Quick fixes for issues
- [ ] Full production rollout

**Deliverables:**
- Vue app in production
- Zero downtime migration
- Monitoring in place

---

## 🔧 Technical Implementation Details

### Django Backend Changes

**1. Serve Vue SPA:**

```python
# seim/urls.py
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView

urlpatterns = [
    # Django Admin (keep separate)
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', include('api.urls')),
    path('api/accounts/', include('accounts.urls')),
    path('api/programs/', include('exchange.urls')),
    path('api/documents/', include('documents.urls')),
    path('api/notifications/', include('notifications.urls')),
    
    # WebSocket
    path('ws/', include('notifications.routing')),
    
    # Serve Vue SPA (catch-all)
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html')),
]
```

**2. Static files configuration:**

```python
# settings/production.py
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Vue build output
STATICFILES_DIRS = [
    BASE_DIR / 'frontend-vue' / 'dist' / 'assets',
]

# Template for Vue SPA
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'frontend-vue' / 'dist'],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
            ],
        },
    },
]
```

**3. CORS configuration:**

```python
# settings/base.py
INSTALLED_APPS += ['corsheaders']

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    # ... other middleware
]

# Development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",
]

# Production
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
]
```

---

### Vue Configuration

**vite.config.ts:**

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
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
    },
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    rollupOptions: {
      output: {
        manualChunks: {
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          'ui-vendor': ['bootstrap'],
        },
      },
    },
  },
})
```

**package.json:**

```json
{
  "name": "seim-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview",
    "test": "vitest",
    "test:e2e": "playwright test",
    "lint": "eslint . --ext .vue,.js,.jsx,.cjs,.mjs,.ts,.tsx,.cts,.mts --fix",
    "format": "prettier --write src/"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.0",
    "pinia": "^2.1.0",
    "axios": "^1.6.0",
    "bootstrap": "^5.3.0",
    "bootstrap-icons": "^1.11.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "@vue/test-utils": "^2.4.0",
    "typescript": "^5.3.0",
    "vue-tsc": "^1.8.0",
    "vite": "^5.0.0",
    "vitest": "^1.0.0",
    "@playwright/test": "^1.40.0",
    "eslint": "^8.55.0",
    "prettier": "^3.1.0"
  }
}
```

---

## 🎨 UI Component Library Decision

### Option 1: Keep Bootstrap CSS + Vue Components
**Pros:** Familiar, less migration work  
**Cons:** Not Vue-native

### Option 2: Use Vue UI Library

**Recommended:** **PrimeVue** or **Vuetify**

**PrimeVue:**
- Comprehensive component set
- Good documentation
- Theme support (light/dark)
- Accessibility built-in
- TypeScript support

**Vuetify:**
- Material Design
- More opinionated
- Larger bundle
- Great components

**My Recommendation:** **PrimeVue** - Good balance of features and bundle size

---

## 📊 Migration Checklist

### Pre-Migration
- [ ] Full backup of current codebase
- [ ] Document all current features
- [ ] API endpoint audit
- [ ] User acceptance testing plan
- [ ] Rollback plan prepared

### During Migration
- [ ] Vue project set up
- [ ] Core infrastructure complete
- [ ] All pages migrated
- [ ] All features working
- [ ] Tests passing (>80% coverage)
- [ ] Performance benchmarks met

### Post-Migration
- [ ] Production deployment successful
- [ ] User training/documentation
- [ ] Monitor error rates
- [ ] Performance monitoring
- [ ] User feedback collection
- [ ] Remove old frontend code

---

## 🎯 Success Criteria

### Performance
- [ ] Lighthouse score >90
- [ ] Initial load <2s
- [ ] Time to interactive <3s
- [ ] Bundle size <500KB

### Quality
- [ ] Test coverage >80%
- [ ] Zero critical bugs
- [ ] Accessibility score >95
- [ ] Zero console errors

### Features
- [ ] All existing features working
- [ ] Real-time notifications working
- [ ] File uploads working
- [ ] Dark mode working
- [ ] Multi-language working

---

## 💰 Resource Requirements

### Team
- **1 Senior Vue Developer** (full-time, 9 weeks)
- **1 Backend Developer** (part-time, 2 weeks) - API fixes
- **1 QA Engineer** (part-time, 4 weeks) - Testing
- **1 DevOps Engineer** (1 week) - Deployment

### Budget Estimate
- Development: 9 weeks × 40 hours = 360 hours
- QA: 4 weeks × 20 hours = 80 hours
- DevOps: 40 hours
- **Total: ~480 hours**

### Tools/Services
- Hosting (no change)
- CI/CD pipeline updates (~$100)
- Monitoring tools (optional, ~$50/month)
- **Total: ~$100-200**

---

## 🚨 Risks & Mitigation

### Risk 1: Feature Parity
**Risk:** Missing features in Vue version  
**Mitigation:** Comprehensive feature checklist, side-by-side testing

### Risk 2: API Issues
**Risk:** Backend APIs not suitable for SPA  
**Mitigation:** API audit in Phase 0, fix issues early

### Risk 3: Authentication Complexity
**Risk:** JWT auth issues  
**Mitigation:** Test auth thoroughly, implement refresh token logic

### Risk 4: Timeline Overrun
**Risk:** 9 weeks becomes 12 weeks  
**Mitigation:** Weekly reviews, MVP approach, cut nice-to-haves

### Risk 5: User Resistance
**Risk:** Users don't like new UI  
**Mitigation:** Beta testing, gather feedback, iterate

---

## 📝 Next Steps

### Immediate Actions (This Week)

1. **Get approval** for Vue migration
2. **Set up Vue project** - Run initial setup
3. **Audit backend API** - Ensure it's SPA-ready
4. **Create project board** - Track progress
5. **Schedule kickoff** - Team alignment

### Commands to Start

```bash
# Create Vue project
npm create vue@latest frontend-vue
# Choose: TypeScript, Vue Router, Pinia, Vitest, E2E Testing

cd frontend-vue
npm install

# Additional dependencies
npm install axios bootstrap bootstrap-icons
npm install -D @types/bootstrap

# Start development
npm run dev
```

---

## 🎓 Learning Resources

### For Team
- Vue 3 Official Docs: https://vuejs.org/
- Vue Router: https://router.vuejs.org/
- Pinia: https://pinia.vuejs.org/
- Vite: https://vitejs.dev/
- TypeScript: https://www.typescriptlang.org/

### Video Courses (Optional)
- Vue Mastery (recommended)
- Udemy Vue 3 courses
- Frontend Masters

---

**Ready to proceed?** This is a significant but worthwhile undertaking. The new Vue.js frontend will be:
- ✅ Modern and maintainable
- ✅ Fast and performant
- ✅ Easy to test
- ✅ Great developer experience
- ✅ Future-proof

**Document Version:** 1.0  
**Last Updated:** 2026-01-29  
**Status:** Awaiting Approval
