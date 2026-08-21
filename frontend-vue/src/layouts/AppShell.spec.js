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
  'HelpCenter',
  'HelpArticle',
  'Settings',
  'Profile',
  'Login',
  'AdminPrograms',
  'AdminCatalogs',
  'AdminGrades',
  'AdminUsers',
  'AdminSessions',
  'AdminWorkflowCatalogs',
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

  it('uses navbar-expand so utility dropdowns overlay instead of stretching the bar', async () => {
    const wrapper = await mountShell()
    const nav = wrapper.get('[data-testid="app-shell"] .navbar')
    expect(nav.classes()).toContain('navbar-expand')
    expect(nav.classes()).toContain('seim-app-shell__navbar')

    const userMenu = wrapper.get('#userDropdown').element.closest('.dropdown')
    const userDropdownMenu = userMenu?.querySelector('.dropdown-menu')
    expect(userDropdownMenu).toBeTruthy()
    expect(userDropdownMenu.classList.contains('dropdown-menu-end')).toBe(true)

    const notifMenu = wrapper.get('[data-testid="notifications-menu"]').element.closest('.dropdown')
    const notifDropdownMenu = notifMenu?.querySelector('.dropdown-menu')
    expect(notifDropdownMenu).toBeTruthy()
    expect(notifDropdownMenu.classList.contains('dropdown-menu-end')).toBe(true)
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

  it('shows Help in the primary sidebar nav', async () => {
    const wrapper = await mountShell()
    const helpLinks = wrapper.findAll('a').filter((a) => a.text().includes('Help'))
    expect(helpLinks.length).toBeGreaterThan(0)
    expect(helpLinks[0].attributes('href')).toContain('/HelpCenter')
    wrapper.unmount()
  })
})
