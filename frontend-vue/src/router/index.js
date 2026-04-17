/**
 * Vue Router Configuration
 */
import { nextTick } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { announceRouteNavigation, focusMainContent } from '@/utils/a11y'
import i18n from '@/i18n'
import { resolveDocumentTitle, syncAppSocialMeta, syncCanonicalLink } from '@/utils/documentTitle'
import { resolveAuthenticatedNavigation } from '@/router/authNavigation'
import { routeBusy } from '@/router/routeBusy'

// Route Components (lazy-loaded)
const Login = () => import('@/views/Login.vue')
const AppShell = () => import('@/layouts/AppShell.vue')
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
const AdminPrograms = () => import('@/views/admin/AdminPrograms.vue')
const AdminForms = () => import('@/views/admin/AdminForms.vue')
const AdminWorkflows = () => import('@/views/admin/AdminWorkflows.vue')
const AdminWorkflowEditor = () => import('@/views/admin/AdminWorkflowEditor.vue')
const AdminApplicationEdit = () => import('@/views/admin/AdminApplicationEdit.vue')
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
    component: AppShell,
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: { name: 'Dashboard' } },
      { path: 'dashboard', name: 'Dashboard', component: Dashboard },
      { path: 'applications', name: 'Applications', component: Applications },
      {
        path: 'review-queue',
        name: 'CoordinatorReviewQueue',
        component: CoordinatorReviewQueue,
        meta: { staffReviewQueue: true },
      },
      {
        path: 'coordinator-workload',
        name: 'CoordinatorWorkload',
        component: CoordinatorWorkload,
        meta: { staffReviewQueue: true },
      },
      {
        path: 'notification-routing',
        name: 'NotificationRouting',
        component: NotificationRouting,
        meta: { staffReviewQueue: true },
      },
      {
        path: 'exchange-agreements/:agreementId/documents',
        name: 'StaffAgreementDocuments',
        component: StaffAgreementDocuments,
        meta: { staffReviewQueue: true },
      },
      {
        path: 'exchange-agreements',
        name: 'StaffExchangeAgreements',
        component: StaffExchangeAgreements,
        meta: { staffReviewQueue: true },
      },
      {
        path: 'agreement-documents',
        redirect: { name: 'StaffExchangeAgreements' },
      },
      { path: 'programs/compare', name: 'ProgramCompare', component: ProgramCompare },
      { path: 'applications/new', name: 'ApplicationNew', component: ApplicationForm },
      { path: 'applications/create', redirect: { name: 'ApplicationNew' } },
      { path: 'applications/:id/edit', name: 'ApplicationEdit', component: ApplicationForm },
      { path: 'applications/:id', name: 'ApplicationDetail', component: ApplicationDetail },
      { path: 'documents', name: 'Documents', component: Documents },
      { path: 'documents/:id', name: 'DocumentDetail', component: DocumentDetail },
      { path: 'notifications', name: 'Notifications', component: Notifications },
      { path: 'profile', name: 'Profile', component: Profile },
      { path: 'settings', name: 'Settings', component: Settings },
      { path: 'calendar', name: 'DeadlinesCalendar', component: DeadlinesCalendar },
      { path: 'preferences', redirect: { name: 'Settings' } },

      // SPA admin console (admin-only)
      {
        path: 'admin/programs',
        name: 'AdminPrograms',
        component: AdminPrograms,
        meta: { adminOnly: true },
      },
      {
        path: 'admin/forms',
        name: 'AdminForms',
        component: AdminForms,
        meta: { adminOnly: true },
      },
      {
        path: 'admin/workflows',
        name: 'AdminWorkflows',
        component: AdminWorkflows,
        meta: { adminOnly: true },
      },
      {
        path: 'admin/workflows/:id',
        name: 'AdminWorkflowEditor',
        component: AdminWorkflowEditor,
        meta: { adminOnly: true },
      },
      {
        path: 'admin/applications/:id',
        name: 'AdminApplicationEdit',
        component: AdminApplicationEdit,
        meta: { adminOnly: true },
      },
    ],
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
  routeBusy.value = true
  const authStore = useAuthStore()

  // Normalize trailing slashes - remove trailing slash for consistency
  if (to.path !== '/' && to.path.endsWith('/')) {
    return next({ path: to.path.slice(0, -1), query: to.query, hash: to.hash, replace: true })
  }

  document.title = resolveDocumentTitle(to)
  syncAppSocialMeta((k) => i18n.global.t(k), to)
  if (typeof window !== 'undefined') {
    const canonicalHref = new URL(router.resolve(to).href, window.location.origin).href
    syncCanonicalLink(canonicalHref)
  }

  const requiresAuth = to.matched.some((r) => r.meta && r.meta.requiresAuth)
  if (requiresAuth) {
    const outcome = await resolveAuthenticatedNavigation(to, authStore)
    if (outcome === 'login') {
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }
    if (outcome === 'applications') {
      next({ name: 'Applications', replace: true })
      return
    }
    next()
    return
  }

  // Route doesn't require auth
  if (to.name === 'Login' && authStore.isAuthenticated) {
    next({ name: 'Dashboard' })
  } else {
    next()
  }
})

router.afterEach((to) => {
  announceRouteNavigation(to)
  nextTick(() => {
    routeBusy.value = false
    focusMainContent()
  })
})

router.onError(() => {
  nextTick(() => {
    routeBusy.value = false
  })
})

export default router
