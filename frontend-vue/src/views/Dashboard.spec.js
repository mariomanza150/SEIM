/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import Dashboard from './Dashboard.vue'
import api from '@/services/api'
import i18n, { setAppLocale } from '@/i18n'

vi.mock('@/services/api', () => ({
  default: { get: vi.fn() },
}))

vi.mock('@/utils/dashboardNextSteps', () => ({
  fetchDashboardNextSteps: vi.fn().mockResolvedValue([]),
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => ({
    userName: 'Alex Student',
    isAdmin: false,
    canUseStaffReviewQueue: false,
    userRole: 'student',
    logout: vi.fn().mockResolvedValue(undefined),
  }),
}))

describe('Dashboard', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    setAppLocale('en')
    vi.clearAllMocks()
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
      expect(wrapper.text()).toContain('Welcome, Alex Student!')
    })

    await vi.waitFor(() => {
      expect(wrapper.text()).toContain('2')
      expect(wrapper.text()).toContain('Applications')
    })

    expect(wrapper.text()).toContain("Here's what's happening with your exchange program.")
    expect(wrapper.text()).toContain('Documents')
    expect(api.get).toHaveBeenCalledWith('/api/accounts/dashboard/stats/')
  })
})
