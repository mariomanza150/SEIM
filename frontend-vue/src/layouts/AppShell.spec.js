/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import AppShell from './AppShell.vue'
import i18n, { setAppLocale } from '@/i18n'

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

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => ({
    userName: 'Sofia Martinez',
    isAdmin: false,
    canUseStaffReviewQueue: false,
    canUsePartnerPortal: false,
    logout: vi.fn().mockResolvedValue(undefined),
  }),
}))

const routeNames = [
  'Dashboard',
  'Applications',
  'ProgramCompare',
  'CoordinatorReviewQueue',
  'CoordinatorWorkload',
  'NotificationRouting',
  'StaffExchangeAgreements',
  'EligibilityRulesets',
  'Nominations',
  'AnalyticsForecasts',
  'PartnerPortal',
  'Documents',
  'DeadlinesCalendar',
  'Notifications',
  'Settings',
  'Profile',
  'Login',
  'AdminPrograms',
  'AdminCatalogs',
  'AdminGrades',
  'AdminForms',
  'AdminDynforms',
  'AdminDataManagement',
  'AdminWorkflows',
  'AdminDocuments',
]

function makeRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      ...routeNames.map((name) => ({
        path: `/${name}`,
        name,
        component: { template: '<div />' },
      })),
      { path: '/', component: { template: '<div />' } },
    ],
  })
}

describe('AppShell navbar', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    setAppLocale('en')
    vi.clearAllMocks()
  })

  afterEach(() => {
    setAppLocale('en')
    localStorage.clear()
  })

  async function mountShell() {
    const router = makeRouter()
    const wrapper = mount(AppShell, {
      attachTo: document.body,
      global: {
        plugins: [createPinia(), i18n, router],
        stubs: {
          RouterView: { template: '<div data-testid="rv" />' },
        },
      },
    })
    await router.isReady()
    await flushPromises()
    return wrapper
  }

  it('always shows notifications and the user name outside the collapse', async () => {
    const wrapper = await mountShell()
    expect(wrapper.find('.navbar-collapse').exists()).toBe(false)
    expect(wrapper.find('[data-testid="notifications-menu"]').exists()).toBe(true)
    expect(wrapper.get('[data-testid="user-menu"]').text()).toContain('Sofia Martinez')
    wrapper.unmount()
  })

  it('opens the user menu on click', async () => {
    const wrapper = await mountShell()
    const toggle = wrapper.get('[data-testid="user-menu"]')
    expect(toggle.attributes('aria-expanded')).toBe('false')

    await toggle.trigger('click')
    expect(toggle.attributes('aria-expanded')).toBe('true')
    expect(wrapper.find('#userDropdown').element.closest('.dropdown').querySelector('.dropdown-menu.show')).toBeTruthy()
    expect(wrapper.text()).toContain('Profile')
    expect(wrapper.get('[data-testid="public-site-link"]').attributes('href')).toBe('/')
    expect(wrapper.get('[data-testid="public-site-link"]').text()).toContain('Public site')
    wrapper.unmount()
  })
})
