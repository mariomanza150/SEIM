/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import AnalyticsForecasts from './AnalyticsForecasts.vue'
import api from '@/services/api'
import i18n, { setAppLocale } from '@/i18n'

vi.mock('@/services/api', () => ({
  default: { get: vi.fn() },
}))

describe('AnalyticsForecasts', () => {
  beforeEach(() => {
    setAppLocale('en')
    vi.clearAllMocks()
    api.get.mockResolvedValue({
      data: {
        demand: {
          trend_per_week: 1.5,
          history: [{ week_start: '2026-06-01', applications: 2 }],
          forecast: [{ week_start: '2026-08-17', predicted_applications: 4 }],
        },
        bottlenecks: {
          pending_review: 3,
          aging_over_7_days: 1,
          waitlisted: 0,
          by_program: [{ program_id: 'p1', program_name: 'Erasmus', pending_count: 3 }],
        },
        deadline_risk: [],
      },
    })
  })

  it('renders demand forecast and bottlenecks', async () => {
    const wrapper = mount(AnalyticsForecasts, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' }, PageHeader: { template: '<div><slot /></div>' } },
      },
    })
    await flushPromises()
    expect(wrapper.find('[data-testid="analytics-forecasts-page"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('Erasmus')
    expect(wrapper.text()).toContain('4')
    expect(api.get).toHaveBeenCalledWith('/api/admin/dashboard/forecasts/')
  })
})
