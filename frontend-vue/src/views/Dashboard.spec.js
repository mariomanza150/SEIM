/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import Dashboard from './Dashboard.vue'
import api from '@/services/api'
import i18n, { setAppLocale } from '@/i18n'
import { fetchDashboardNextSteps } from '@/utils/dashboardNextSteps'

vi.mock('@/services/api', () => ({
  default: { get: vi.fn() },
}))

vi.mock('@/utils/dashboardNextSteps', () => ({
  fetchDashboardNextSteps: vi.fn().mockResolvedValue([]),
}))

const toastError = vi.fn()
vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: vi.fn(), error: toastError }),
}))

const authStoreMock = {
  userName: 'Test Student',
  isAdmin: false,
  canUseStaffReviewQueue: false,
  canUsePartnerPortal: false,
  userRole: 'student',
  logout: vi.fn().mockResolvedValue(undefined),
}

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => authStoreMock,
}))

describe('Dashboard', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    setAppLocale('en')
    authStoreMock.userName = 'Test Student'
    authStoreMock.canUseStaffReviewQueue = false
    authStoreMock.canUsePartnerPortal = false
    authStoreMock.userRole = 'student'
    toastError.mockClear()
    vi.clearAllMocks()
    fetchDashboardNextSteps.mockResolvedValue([])
    api.get.mockResolvedValue({
      data: { applications: 2, documents: 1, notifications: 3, pending: 0 },
    })
  })

  afterEach(() => {
    setAppLocale('en')
    localStorage.clear()
  })

  it('loads stats and shows translated welcome and nav', async () => {
    const wrapper = mount(Dashboard, {
      global: {
        plugins: [createPinia(), i18n],
        stubs: {
          RouterLink: { template: '<a><slot /></a>' },
        },
      },
    })

    await vi.waitFor(() => {
      expect(wrapper.text()).toContain('Welcome, Test Student!')
    })

    await vi.waitFor(() => {
      expect(wrapper.text()).toContain('2')
      expect(wrapper.text()).toContain('Applications')
    })

    expect(wrapper.text()).toContain("Here's what's happening with your exchange program.")
    expect(wrapper.text()).toContain('Documents')
    expect(api.get).toHaveBeenCalledWith('/api/accounts/dashboard/stats/')
  })

  it('links applications stat card to partner portal for partner role (MQ-029)', async () => {
    authStoreMock.userName = 'Test Partner'
    authStoreMock.canUsePartnerPortal = true
    authStoreMock.userRole = 'partner'
    const wrapper = mount(Dashboard, {
      global: {
        plugins: [createPinia(), i18n],
        stubs: {
          RouterLink: {
            props: ['to'],
            template: '<a :data-to="JSON.stringify(to)"><slot /></a>',
          },
        },
      },
    })
    await vi.waitFor(() => {
      expect(wrapper.text()).toContain('2')
    })
    const appsLink = wrapper.findAll('a').find((a) => a.text().includes('Applications'))
    expect(appsLink?.attributes('data-to')).toContain('PartnerPortal')
    const docsLink = wrapper.findAll('a').find((a) => a.text().includes('Documents'))
    expect(docsLink?.attributes('data-to')).toContain('PartnerPortal')
  })

  it('links pending stats to the review queue for staff roles', async () => {
    authStoreMock.userName = 'Test Coordinator'
    authStoreMock.canUseStaffReviewQueue = true
    authStoreMock.userRole = 'coordinator'
    api.get.mockResolvedValue({
      data: { applications: 4, documents: 2, notifications: 1, pending: 5 },
    })
    const wrapper = mount(Dashboard, {
      global: {
        plugins: [createPinia(), i18n],
        stubs: {
          RouterLink: {
            props: ['to'],
            template: '<a :data-to="JSON.stringify(to)"><slot /></a>',
          },
        },
      },
    })
    await vi.waitFor(() => {
      expect(wrapper.text()).toContain('5')
    })
    const pendingLink = wrapper.findAll('a').find((a) => a.text().includes('Pending tasks'))
    expect(pendingLink?.attributes('data-to')).toContain('CoordinatorReviewQueue')
  })

  it('shows stats load error and toast when the stats API fails', async () => {
    api.get.mockRejectedValue(new Error('offline'))
    const wrapper = mount(Dashboard, {
      global: {
        plugins: [createPinia(), i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await vi.waitFor(() => {
      expect(wrapper.text()).toContain(i18n.global.t('dashboard.statsLoadError'))
    })
    expect(toastError).toHaveBeenCalledWith(i18n.global.t('dashboard.statsToastError'))
  })

  it('renders next-step rows returned for the current role', async () => {
    fetchDashboardNextSteps.mockResolvedValue([
      {
        id: 'draft-1',
        title: 'Finish your draft',
        subtitle: 'Program Alpha',
        spaRoute: { name: 'ApplicationEdit', params: { id: '1' } },
      },
    ])
    const wrapper = mount(Dashboard, {
      global: {
        plugins: [createPinia(), i18n],
        stubs: {
          RouterLink: {
            props: ['to'],
            template: '<a :data-to="JSON.stringify(to)"><slot /></a>',
          },
        },
      },
    })
    await vi.waitFor(() => {
      expect(wrapper.text()).toContain('Finish your draft')
    })
    expect(wrapper.text()).toContain('Program Alpha')
    expect(fetchDashboardNextSteps).toHaveBeenCalledWith(
      api,
      expect.objectContaining({ userRole: 'student', canUseStaffReviewQueue: false }),
    )
  })

  it('shows next-steps error copy when the helper rejects', async () => {
    fetchDashboardNextSteps.mockRejectedValue(new Error('offline'))
    const wrapper = mount(Dashboard, {
      global: {
        plugins: [createPinia(), i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await vi.waitFor(() => {
      expect(wrapper.text()).toContain(i18n.global.t('dashboard.nextStepsLoadError'))
    })
  })

  it('soft-refreshes stats and next steps on application sync events', async () => {
    const wrapper = mount(Dashboard, {
      global: {
        plugins: [createPinia(), i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await vi.waitFor(() => {
      expect(wrapper.text()).toContain('2')
    })
    api.get.mockClear()
    fetchDashboardNextSteps.mockClear()
    api.get.mockResolvedValue({
      data: { applications: 9, documents: 1, notifications: 0, pending: 0 },
    })
    window.dispatchEvent(new Event('seim-application-sync'))
    await vi.waitFor(() => {
      expect(wrapper.text()).toContain('9')
    })
    expect(fetchDashboardNextSteps).toHaveBeenCalled()
    wrapper.unmount()
  })
})
