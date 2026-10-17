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
    get: vi.fn().mockImplementation((url) => {
      if (url === '/api/features/') {
        return Promise.resolve({ data: { scholarships_enabled: true } })
      }
      if (url === '/api/branding/') {
        return Promise.resolve({
          data: {
            logo_url: '',
            nav_brand: 'SEIM',
            short_name: 'SEIM',
            name: 'SEIM',
            theme_css: 'uadec/theme.css',
            theme: {},
          },
        })
      }
      return Promise.resolve({ data: { results: [], count: 0 } })
    }),
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
  canUseStaffReviewQueue: false,
  canUsePartnerPortal: false,
  logout: vi.fn().mockResolvedValue(undefined),
}

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => authStoreMock,
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
  'ToeflPractice',
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
  'AdminFeatures',
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

  async function mountShell(startName = 'Dashboard') {
    const router = makeRouter()
    await router.push({ name: startName })
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
    return { wrapper, router }
  }

  it('always shows notifications and the user name outside the collapse', async () => {
    const { wrapper } = await mountShell()
    expect(wrapper.find('.navbar-collapse').exists()).toBe(false)
    expect(wrapper.find('[data-testid="notifications-menu"]').exists()).toBe(true)
    expect(wrapper.get('[data-testid="user-menu"]').text()).toContain('Sofia Martinez')
    wrapper.unmount()
  })

  it('uses navbar-expand so utility dropdowns overlay instead of stretching the bar', async () => {
    const { wrapper } = await mountShell()
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
    const { wrapper } = await mountShell()
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

  it('logs out and navigates to the Login route', async () => {
    authStoreMock.logout.mockClear()
    const { wrapper, router } = await mountShell('Dashboard')
    await wrapper.get('[data-testid="user-menu"]').trigger('click')
    await wrapper.get('[data-testid="logout-link"]').trigger('click')
    await flushPromises()

    expect(authStoreMock.logout).toHaveBeenCalled()
    expect(router.currentRoute.value.name).toBe('Login')
    wrapper.unmount()
  })

  it('shows Help in the primary sidebar nav', async () => {
    const { wrapper } = await mountShell()
    const helpLinks = wrapper.findAll('a').filter((a) => a.text().includes('Help'))
    expect(helpLinks.length).toBeGreaterThan(0)
    expect(helpLinks[0].attributes('href')).toContain('/HelpCenter')
    wrapper.unmount()
  })

  describe('sidebar collapse and route scroll', () => {
    it('collapses the desktop sidebar to an icon rail and persists it', async () => {
      const { wrapper } = await mountShell()
      const aside = () => wrapper.find('[data-testid="app-shell-aside"]')
      const main = () => wrapper.find('[data-testid="app-shell-main"]')
      expect(aside().classes()).toContain('col-lg-2')
      expect(main().classes()).toContain('col-lg-10')

      await wrapper.find('[data-testid="sidebar-rail-toggle"]').trigger('click')
      expect(aside().classes()).toContain('seim-app-shell__aside--rail')
      expect(main().classes()).toContain('col')
      expect(main().classes()).not.toContain('col-lg-10')
      expect(localStorage.getItem('seim.sidebarCollapsed')).toBe('1')
      expect(wrapper.find('[data-testid="sidebar-rail-toggle"]').attributes('aria-label')).toBe(
        i18n.global.t('nav.expandSidebar'),
      )
      // Rail keeps navigation reachable via icon links with accessible names.
      const railLinks = aside().findAll('a')
      expect(railLinks.length).toBeGreaterThan(0)
      expect(railLinks[0].attributes('aria-label')).toBeTruthy()

      await wrapper.find('[data-testid="sidebar-collapse-toggle"]').trigger('click')
      expect(aside().classes()).toContain('col-lg-2')
      expect(localStorage.getItem('seim.sidebarCollapsed')).toBe('0')
      wrapper.unmount()
    })

    it('restores the collapsed sidebar from localStorage', async () => {
      localStorage.setItem('seim.sidebarCollapsed', '1')
      const { wrapper } = await mountShell()
      expect(wrapper.find('[data-testid="app-shell-aside"]').classes()).toContain('seim-app-shell__aside--rail')
      wrapper.unmount()
    })

    it('renders collapsible nav sections', async () => {
      const { wrapper } = await mountShell()
      const toggle = wrapper.find('#seim-aside-nav-section-main-header')
      expect(toggle.exists()).toBe(true)
      expect(toggle.attributes('aria-expanded')).toBe('true')
      wrapper.unmount()
    })

    it('scrolls main content into view on route change', async () => {
      window.scrollTo = vi.fn()
      Object.defineProperty(window, 'scrollY', { value: 900, writable: true, configurable: true })
      const { wrapper, router } = await mountShell()
      await router.push({ name: 'Applications' })
      await flushPromises()
      expect(window.scrollTo).toHaveBeenCalled()
      window.scrollTo.mockClear()
      await router.push({ name: 'Applications', query: { status: 'draft' } })
      await flushPromises()
      expect(window.scrollTo).not.toHaveBeenCalled()
      window.scrollY = 0
      wrapper.unmount()
    })
  })
})
