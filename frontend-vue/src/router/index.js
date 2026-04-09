/**
 * Vue Router Configuration
 */
import { nextTick } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { announceRouteNavigation, focusMainContent } from '@/utils/a11y'
import i18n from '@/i18n'
import { resolveDocumentTitle, syncAppSocialMeta } from '@/utils/documentTitle'

// Route Components (lazy-loaded)
const Login = () => import('@/views/Login.vue')
const Dashboard = () => import('@/views/Dashboard.vue')
const Applications = () => import('@/views/Applications.vue')
const CoordinatorReviewQueue = () => import('@/views/CoordinatorReviewQueue.vue')
const CoordinatorWorkload = () => import('@/views/CoordinatorWorkload.vue')
const NotificationRouting = () => import('@/views/NotificationRouting.vue')
const StaffExchangeAgreements = () => import('@/views/StaffExchangeAgreements.vue')
const StaffAgreementDocuments = () => import('@/views/StaffAgreementDocuments.vue')
const ProgramCompare = () => import('@/views/ProgramCompare.vue')
const ApplicationForm = () => import('@/views/ApplicationForm.vue')
const ApplicationDetail = () => import('@/views/ApplicationDetail.vue')
const Documents = () => import('@/views/Documents.vue')
const DocumentDetail = () => import('@/views/DocumentDetail.vue')
const Notifications = () => import('@/views/Notifications.vue')
const Profile = () => import('@/views/Profile.vue')
const Settings = () => import('@/views/Settings.vue')
const DeadlinesCalendar = () => import('@/views/DeadlinesCalendar.vue')
const NotFound = () => import('@/views/NotFound.vue')

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: {
      requiresAuth: false,
    },
  },
  {
    path: '/',
    name: 'Home',
    redirect: { name: 'Dashboard' },
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: {
      requiresAuth: true,
    },
  },
  {
    path: '/applications',
    name: 'Applications',
    component: Applications,
    meta: {
      requiresAuth: true,
    },
  },
  {
    path: '/review-queue',
    name: 'CoordinatorReviewQueue',
    component: CoordinatorReviewQueue,
    meta: {
      requiresAuth: true,
      staffReviewQueue: true,
    },
  },
  {
    path: '/coordinator-workload',
    name: 'CoordinatorWorkload',
    component: CoordinatorWorkload,
    meta: {
      requiresAuth: true,
      staffReviewQueue: true,
    },
  },
  {
    path: '/notification-routing',
    name: 'NotificationRouting',
    component: NotificationRouting,
    meta: {
      requiresAuth: true,
      staffReviewQueue: true,
    },
  },
  {
    path: '/exchange-agreements',
    name: 'StaffExchangeAgreements',
    component: StaffExchangeAgreements,
    meta: {
      requiresAuth: true,
      staffReviewQueue: true,
    },
  },
  {
    path: '/agreement-documents',
    name: 'StaffAgreementDocuments',
    component: StaffAgreementDocuments,
    meta: {
      requiresAuth: true,
      staffReviewQueue: true,
    },
  },
  {
    path: '/programs/compare',
    name: 'ProgramCompare',
    component: ProgramCompare,
    meta: {
      requiresAuth: true,
    },
  },
  {
    path: '/applications/new',
    name: 'ApplicationNew',
    component: ApplicationForm,
    meta: {
      requiresAuth: true,
    },
  },
  {
    path: '/applications/create',
    redirect: {
      name: 'ApplicationNew',
    },
  },
  {
    path: '/applications/:id/edit',
    name: 'ApplicationEdit',
    component: ApplicationForm,
    meta: {
      requiresAuth: true,
    },
  },
  {
    path: '/applications/:id',
    name: 'ApplicationDetail',
    component: ApplicationDetail,
    meta: {
      requiresAuth: true,
    },
  },
  {
    path: '/documents',
    name: 'Documents',
    component: Documents,
    meta: {
      requiresAuth: true,
    },
  },
  {
    path: '/documents/:id',
    name: 'DocumentDetail',
    component: DocumentDetail,
    meta: {
      requiresAuth: true,
    },
  },
  {
    path: '/notifications',
    name: 'Notifications',
    component: Notifications,
    meta: {
      requiresAuth: true,
    },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: {
      requiresAuth: true,
    },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings,
    meta: {
      requiresAuth: true,
    },
  },
  {
    path: '/calendar',
    name: 'DeadlinesCalendar',
    component: DeadlinesCalendar,
    meta: {
      requiresAuth: true,
    },
  },
  {
    path: '/preferences',
    redirect: {
      name: 'Settings',
    },
  },
  // Catch-all 404
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
  },
]

const router = createRouter({
  history: createWebHistory('/seim/'),
  routes,
  strict: false,
})

// Navigation Guards
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // Normalize trailing slashes - remove trailing slash for consistency
  if (to.path !== '/' && to.path.endsWith('/')) {
    return next({ path: to.path.slice(0, -1), query: to.query, hash: to.hash, replace: true })
  }

  document.title = resolveDocumentTitle(to)
  syncAppSocialMeta((k) => i18n.global.t(k), to)

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
      if (to.meta.staffReviewQueue && !authStore.canUseStaffReviewQueue) {
        next({ name: 'Applications', replace: true })
        return
      }
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

router.afterEach((to) => {
  announceRouteNavigation(to)
  nextTick(() => {
    focusMainContent()
  })
})

export default router
