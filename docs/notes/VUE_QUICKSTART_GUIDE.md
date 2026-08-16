# SEIM Vue.js Migration - Quick Start Guide

**Purpose:** Get the Vue.js project up and running in 30 minutes  
**Last Updated:** 2026-01-29

---

## 🚀 Step-by-Step Setup

### Step 1: Create Vue Project (5 minutes)

```bash
# Navigate to project root
cd c:\Users\mario\OneDrive\Documents\SEIM

# Create Vue project
npm create vue@latest frontend-vue

# When prompted, choose:
# ✔ TypeScript? … Yes
# ✔ JSX Support? … No
# ✔ Vue Router? … Yes
# ✔ Pinia? … Yes
# ✔ Vitest? … Yes
# ✔ E2E Testing? … Yes (Playwright)
# ✔ ESLint? … Yes
# ✔ Prettier? … Yes

# Navigate to new project
cd frontend-vue

# Install dependencies
npm install

# Install additional packages
npm install axios bootstrap bootstrap-icons
npm install -D @types/bootstrap
```

---

### Step 2: Configure Vite (5 minutes)

Create/update `frontend-vue/vite.config.ts`:

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
    }
  }
})
```

---

### Step 3: Create Basic Structure (10 minutes)

Create the following folder structure:

```bash
cd src
mkdir services composables types stores/modules views/auth views/dashboard components/common
```

**Create API Client** - `src/services/api.ts`:

```typescript
import axios, { type AxiosInstance } from 'axios'
import type { AxiosError, InternalAxiosRequestConfig } from 'axios'

const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
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

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Token expired, try to refresh
      const refreshToken = localStorage.getItem('seim_refresh_token')
      if (refreshToken) {
        try {
          const response = await axios.post('http://localhost:8000/api/token/refresh/', {
            refresh: refreshToken
          })
          const newToken = response.data.access
          localStorage.setItem('seim_access_token', newToken)
          
          // Retry original request
          if (error.config) {
            error.config.headers.Authorization = `Bearer ${newToken}`
            return api.request(error.config)
          }
        } catch (refreshError) {
          // Refresh failed, logout
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

**Create Auth Store** - `src/stores/auth.ts`:

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  role: string
}

interface LoginCredentials {
  username: string
  password: string
}

interface LoginResponse {
  access: string
  refresh: string
  user: User
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('seim_access_token'))
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isCoordinator = computed(() => 
    ['admin', 'coordinator'].includes(user.value?.role || '')
  )
  const isStudent = computed(() => user.value?.role === 'student')
  const fullName = computed(() => 
    user.value ? `${user.value.first_name} ${user.value.last_name}` : ''
  )

  // Actions
  async function login(credentials: LoginCredentials): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const response = await api.post<LoginResponse>('/api/accounts/login/', credentials)
      token.value = response.data.access
      user.value = response.data.user
      
      localStorage.setItem('seim_access_token', response.data.access)
      localStorage.setItem('seim_refresh_token', response.data.refresh)
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Login failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function logout(): Promise<void> {
    try {
      await api.post('/api/accounts/logout/')
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      user.value = null
      token.value = null
      localStorage.removeItem('seim_access_token')
      localStorage.removeItem('seim_refresh_token')
    }
  }

  async function fetchUser(): Promise<void> {
    if (!token.value) return
    
    try {
      const response = await api.get<User>('/api/accounts/profile/')
      user.value = response.data
    } catch (err) {
      console.error('Fetch user error:', err)
      await logout()
    }
  }

  async function initialize(): Promise<void> {
    if (token.value) {
      await fetchUser()
    }
  }

  return {
    // State
    user,
    token,
    loading,
    error,
    // Getters
    isAuthenticated,
    isAdmin,
    isCoordinator,
    isStudent,
    fullName,
    // Actions
    login,
    logout,
    fetchUser,
    initialize,
  }
})
```

---

### Step 4: Create Router (5 minutes)

Update `src/router/index.ts`:

```typescript
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/Home.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/auth/Login.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/auth/Register.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('@/views/dashboard/Dashboard.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/applications',
      name: 'applications',
      component: () => import('@/views/applications/ApplicationsList.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/programs',
      name: 'programs',
      component: () => import('@/views/programs/ProgramsList.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/views/Profile.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/views/NotFound.vue')
    }
  ]
})

// Navigation guard
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // Initialize auth store if needed
  if (authStore.token && !authStore.user) {
    await authStore.initialize()
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else if (to.name === 'login' && authStore.isAuthenticated) {
    next({ name: 'dashboard' })
  } else {
    next()
  }
})

export default router
```

---

### Step 5: Create Basic Components (5 minutes)

**Login Page** - `src/views/auth/Login.vue`:

```vue
<template>
  <div class="login-container">
    <div class="login-card">
      <h1>SEIM Login</h1>
      
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username">Username</label>
          <input
            id="username"
            v-model="credentials.username"
            type="text"
            class="form-control"
            required
            autofocus
          />
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input
            id="password"
            v-model="credentials.password"
            type="password"
            class="form-control"
            required
          />
        </div>

        <div v-if="authStore.error" class="alert alert-danger">
          {{ authStore.error }}
        </div>

        <button 
          type="submit" 
          class="btn btn-primary w-100"
          :disabled="authStore.loading"
        >
          <span v-if="authStore.loading">Logging in...</span>
          <span v-else>Login</span>
        </button>
      </form>

      <div class="mt-3 text-center">
        <router-link to="/register">Don't have an account? Register</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const credentials = ref({
  username: '',
  password: ''
})

async function handleLogin() {
  try {
    await authStore.login(credentials.value)
    router.push('/dashboard')
  } catch (error) {
    console.error('Login failed:', error)
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  background: white;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 10px 40px rgba(0,0,0,0.1);
  width: 100%;
  max-width: 400px;
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-control {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 0.5rem;
  font-size: 1rem;
}

.form-control:focus {
  outline: none;
  border-color: #667eea;
}

.btn {
  padding: 0.75rem;
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover {
  background: #5568d3;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.alert {
  padding: 0.75rem;
  margin-bottom: 1rem;
  border-radius: 0.5rem;
}

.alert-danger {
  background: #fee;
  color: #c33;
  border: 1px solid #fcc;
}
</style>
```

**Dashboard Page** - `src/views/dashboard/Dashboard.vue`:

```vue
<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <h1>Welcome, {{ authStore.fullName || authStore.user?.username }}!</h1>
      <div class="user-info">
        <span class="badge badge-primary">{{ authStore.user?.role }}</span>
        <button @click="handleLogout" class="btn btn-sm btn-outline">Logout</button>
      </div>
    </header>

    <div class="dashboard-content">
      <div class="stats-grid">
        <div class="stat-card">
          <h3>Applications</h3>
          <p class="stat-value">{{ stats.applications }}</p>
        </div>
        <div class="stat-card">
          <h3>Programs</h3>
          <p class="stat-value">{{ stats.programs }}</p>
        </div>
        <div class="stat-card">
          <h3>Documents</h3>
          <p class="stat-value">{{ stats.documents }}</p>
        </div>
      </div>

      <div class="quick-actions">
        <h2>Quick Actions</h2>
        <div class="actions-grid">
          <router-link to="/applications" class="action-card">
            <i class="bi bi-file-earmark-text"></i>
            <span>View Applications</span>
          </router-link>
          <router-link to="/programs" class="action-card">
            <i class="bi bi-calendar-event"></i>
            <span>Browse Programs</span>
          </router-link>
          <router-link to="/profile" class="action-card">
            <i class="bi bi-person"></i>
            <span>My Profile</span>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const router = useRouter()
const authStore = useAuthStore()

const stats = ref({
  applications: 0,
  programs: 0,
  documents: 0
})

async function loadStats() {
  try {
    const response = await api.get('/api/metrics/dashboard/')
    stats.value = response.data
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.dashboard {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.badge {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  background: #667eea;
  color: white;
  text-transform: capitalize;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: #667eea;
  margin: 0;
}

.quick-actions h2 {
  margin-bottom: 1rem;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.action-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 2rem;
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  text-decoration: none;
  color: inherit;
  transition: all 0.3s;
}

.action-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.action-card i {
  font-size: 2rem;
  color: #667eea;
}
</style>
```

---

### Step 6: Update Main App (2 minutes)

Update `src/App.vue`:

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

onMounted(() => {
  authStore.initialize()
})
</script>

<style>
@import 'bootstrap/dist/css/bootstrap.min.css';
@import 'bootstrap-icons/font/bootstrap-icons.css';

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #f5f7fa;
}

#app {
  min-height: 100vh;
}
</style>
```

---

### Step 7: Create Environment File (2 minutes)

Create `frontend-vue/.env.development`:

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

Create `frontend-vue/.env.production`:

```env
VITE_API_URL=https://your-domain.com
VITE_WS_URL=wss://your-domain.com
```

---

### Step 8: Start Development (1 minute)

```bash
# Terminal 1: Start Django backend
cd c:\Users\mario\OneDrive\Documents\SEIM
python manage.py runserver

# Terminal 2: Start Vue frontend
cd frontend-vue
npm run dev
```

Open browser to `http://localhost:5173`

---

## ✅ Verification Checklist

- [ ] Vue dev server running on port 5173
- [ ] Django backend running on port 8000
- [ ] Can access login page
- [ ] Can login successfully
- [ ] Dashboard loads after login
- [ ] Can logout
- [ ] Protected routes redirect to login
- [ ] API calls work through proxy

---

## 🐛 Common Issues

### Issue: "Cannot find module '@/...'"
**Solution:** Check `tsconfig.json` has correct path alias:
```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

### Issue: CORS errors
**Solution:** Check Django CORS settings allow `http://localhost:5173`

### Issue: 401 Unauthorized
**Solution:** Check token is being sent in Authorization header

---

## 📚 Next Steps

After basic setup works:

1. **Add more views** (Applications, Programs, Documents)
2. **Add more stores** (Applications, Programs, Notifications)
3. **Add proper UI components** (Tables, Forms, Modals)
4. **Add tests** (Vitest for unit, Playwright for E2E)
5. **Add error boundaries** and loading states
6. **Implement WebSocket** for real-time notifications

---

**Time to Complete:** ~30 minutes  
**Difficulty:** Intermediate  
**Prerequisites:** Node.js 18+, Django backend running

**Need help?** Refer to the full migration plan: `VUE_MIGRATION_PLAN.md`
