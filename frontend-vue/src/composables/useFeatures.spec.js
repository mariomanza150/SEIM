/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import { ref } from 'vue'
import AppShell from '@/layouts/AppShell.vue'
import i18n, { setAppLocale } from '@/i18n'
import api from '@/services/api'
import { resolveAuthenticatedNavigation } from '@/router/authNavigation'
import { buildCommandPaletteItems } from '@/utils/commandPaletteItems'
import { useFeatures } from '@/composables/useFeatures'

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn().mockResolvedValue({ data: { results: [], count: 0 } }),
    patch: vi.fn().mockResolvedValue({ data: {} }),
  },
}))

vi.mock('bootstrap', () => ({
  Offcanvas: {
    getInstance: vi.fn(() => null),
  },
}))

const authStoreMock = {
  userName: 'Sofia Martinez',
  isAdmin: false,
  canUseStaffReviewQueue: true,
  canUsePartnerPortal: false,
  logout: vi.fn().mockResolvedValue(undefined),
}

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => authStoreMock,
}))

const scholarshipsEnabledRef = ref(true)
const loadFeaturesMock = vi.fn().mockResolvedValue({ scholarships_enabled: true })

vi.mock('@/composables/useFeatures', () => ({
  useFeatures: () => ({
    features: ref({ scholarships_enabled: true }),
    loading: ref(false),
    error: ref(''),
    scholarshipsEnabled: scholarshipsEnabledRef,
    loadFeatures: loadFeaturesMock,
    updateFeatures: vi.fn(),
    _resetFeaturesState: vi.fn(),
  }),
  scholarshipsEnabledFromState: (state) => state?.scholarships_enabled !== false,
}))

const staffRouteNames = [
  'Dashboard',
  'Applications',
  'ProgramCompare',
  'CoordinatorReviewQueue',
  'CoordinatorWorkload',
  'NotificationRouting',
  'StaffExchangeAgreements',
  'EligibilityRulesets',
  'ScholarshipScoringRulesets',
  'Nominations',
  'AnalyticsForecasts',
  'PartnerPortal',
  'Documents',
  'ToeflPractice',
  'DeadlinesCalendar',
  'Notifications',
  'HelpCenter',
  'Profile',
  'Settings',
  'Login',
]

function makeRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      ...staffRouteNames.map((name) => ({
        path: `/${name}`,
        name,
        component: { template: '<div />' },
      })),
      { path: '/', name: 'DashboardHome', component: { template: '<div />' } },
    ],
  })
}

describe('scholarships feature flag — SPA surfaces', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    setAppLocale('en')
    scholarshipsEnabledRef.value = true
    authStoreMock.canUseStaffReviewQueue = true
    authStoreMock.isAdmin = false
    vi.clearAllMocks()
    api.get.mockResolvedValue({ data: { results: [], count: 0 } })
  })

  afterEach(() => {
    setAppLocale('en')
  })

  it('hides scholarship nav item when scholarships are disabled', async () => {
    scholarshipsEnabledRef.value = false
    const router = makeRouter()
    await router.push({ name: 'Dashboard' })
    const wrapper = mount(AppShell, {
      attachTo: document.body,
      global: {
        plugins: [createPinia(), i18n, router],
        stubs: { RouterView: { template: '<div />' } },
      },
    })
    await router.isReady()
    await flushPromises()

    expect(wrapper.text()).toContain('Eligibility rulesets')
    expect(wrapper.text()).not.toContain('Scholarship scoring rubric')
    wrapper.unmount()
  })

  it('shows scholarship nav item when scholarships are enabled', async () => {
    scholarshipsEnabledRef.value = true
    const router = makeRouter()
    await router.push({ name: 'Dashboard' })
    const wrapper = mount(AppShell, {
      attachTo: document.body,
      global: {
        plugins: [createPinia(), i18n, router],
        stubs: { RouterView: { template: '<div />' } },
      },
    })
    await router.isReady()
    await flushPromises()

    expect(wrapper.text()).toContain('Scholarship scoring rubric')
    wrapper.unmount()
  })

  it('redirects scholarship route when feature is off', async () => {
    const authStore = {
      accessToken: 'jwt',
      isAuthenticated: true,
      isAdmin: false,
      canUseStaffReviewQueue: true,
      canUsePartnerPortal: false,
      checkAuth: vi.fn(),
    }
    const to = {
      meta: { requiresAuth: true, staffReviewQueue: true, scholarshipsFeature: true },
      fullPath: '/scholarship-scoring-rulesets',
    }
    expect(
      await resolveAuthenticatedNavigation(to, authStore, { scholarshipsEnabled: false }),
    ).toBe('dashboard')
    expect(
      await resolveAuthenticatedNavigation(to, authStore, { scholarshipsEnabled: true }),
    ).toBe('next')
  })

  it('omits scholarship command palette item when disabled', () => {
    const off = buildCommandPaletteItems({
      t: i18n.global.t,
      canUsePartnerPortal: false,
      canUseStaffReviewQueue: true,
      isAdmin: false,
      scholarshipsEnabled: false,
    })
    expect(off.some((item) => item.id === 'scholarshipScoringRulesets')).toBe(false)

    const on = buildCommandPaletteItems({
      t: i18n.global.t,
      canUsePartnerPortal: false,
      canUseStaffReviewQueue: true,
      isAdmin: false,
      scholarshipsEnabled: true,
    })
    expect(on.some((item) => item.id === 'scholarshipScoringRulesets')).toBe(true)
  })
})
