/**
 * Vue Router Configuration
 */
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Route Components (lazy-loaded)
const Login = () => import('@/views/Login.vue')
const Dashboard = () => import('@/views/Dashboard.vue')
const Applications = () => import('@/views/Applications.vue')
const ApplicationForm = () => import('@/views/ApplicationForm.vue')
const ApplicationDetail = () => import('@/views/ApplicationDetail.vue')
const NotFound = () => import('@/views/NotFound.vue')

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: {
      requiresAuth: false,
      title: 'Login - SEIM',
    },
  },
  {
    path: '/',
    name: 'Home',
    redirect: '/dashboard',
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: {
      requiresAuth: true,
      title: 'Dashboard - SEIM',
    },
  },
  {
    path: '/applications',
    name: 'Applications',
    component: Applications,
    meta: {
      requiresAuth: true,
      title: 'Applications - SEIM',
    },
  },
  {
    path: '/applications/new',
    name: 'ApplicationNew',
    component: ApplicationForm,
    meta: {
      requiresAuth: true,
      title: 'New Application - SEIM',
    },
  },
  {
    path: '/applications/:id/edit',
    name: 'ApplicationEdit',
    component: ApplicationForm,
    meta: {
      requiresAuth: true,
      title: 'Edit Application - SEIM',
    },
  },
  {
    path: '/applications/:id',
    name: 'ApplicationDetail',
    component: ApplicationDetail,
    meta: {
      requiresAuth: true,
      title: 'Application Details - SEIM',
    },
  },
  // Catch-all 404
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
    meta: {
      title: '404 - Page Not Found',
    },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// Navigation Guards
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // Update page title
  document.title = to.meta.title || 'SEIM'

  // Check if route requires authentication
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      // Check if we have a stored token
      if (authStore.accessToken) {
        try {
          await authStore.checkAuth()
          if (authStore.isAuthenticated) {
            next()
          } else {
            next({ name: 'Login', query: { redirect: to.fullPath } })
          }
        } catch (err) {
          next({ name: 'Login', query: { redirect: to.fullPath } })
        }
      } else {
        next({ name: 'Login', query: { redirect: to.fullPath } })
      }
    } else {
      next()
    }
  } else {
    // Route doesn't require auth
    if (to.name === 'Login' && authStore.isAuthenticated) {
      // Already logged in, redirect to dashboard
      next({ name: 'Dashboard' })
    } else {
      next()
    }
  }
})

export default router
