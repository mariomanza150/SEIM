/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import AnalyticsForecasts from './AnalyticsForecasts.vue'
import api from '@/services/api'
import i18n, { setAppLocale } from '@/i18n'

vi.mock('@/services/api', () => ({
  default: { get: vi.fn(), post: vi.fn(), delete: vi.fn() },
}))

vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: vi.fn(), error: vi.fn() }),
}))

vi.mock('@/composables/useConfirm', () => ({
  useConfirm: () => ({ confirm: vi.fn().mockResolvedValue(false) }),
}))

const forecastPayload = {
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
  filters: { program: '' },
}

function mockApis({ presets = [] } = {}) {
  api.get.mockImplementation((url) => {
    if (url === '/api/programs/') {
      return Promise.resolve({
        data: { results: [{ id: 'p1', name: 'Erasmus' }, { id: 'p2', name: 'Bilateral' }] },
      })
    }
    if (url === '/api/saved-searches/') {
      return Promise.resolve({ data: { results: presets } })
    }
    if (url === '/api/admin/dashboard/forecasts/') {
      return Promise.resolve({ data: forecastPayload })
    }
    return Promise.reject(new Error(`Unexpected GET ${url}`))
  })
}

describe('AnalyticsForecasts', () => {
  beforeEach(() => {
    setAppLocale('en')
    vi.clearAllMocks()
    mockApis()
  })

  afterEach(() => {
    setAppLocale('en')
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
    expect(api.get).toHaveBeenCalledWith('/api/admin/dashboard/forecasts/', { params: {} })
    expect(wrapper.find('[data-testid="forecasts-preset-name"]').attributes('placeholder')).toBe(
      i18n.global.t('analyticsForecastsPage.presetNamePlaceholder'),
    )
  })

  it('passes program query param when a program is selected', async () => {
    const wrapper = mount(AnalyticsForecasts, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' }, PageHeader: { template: '<div><slot /></div>' } },
      },
    })
    await flushPromises()
    await wrapper.find('[data-testid="forecasts-program"]').setValue('p1')
    await wrapper.find('[data-testid="forecasts-program"]').trigger('change')
    await flushPromises()
    expect(api.get).toHaveBeenCalledWith('/api/admin/dashboard/forecasts/', {
      params: { program: 'p1' },
    })
  })

  it('applies default saved preset program filter on load', async () => {
    mockApis({
      presets: [{ id: 's1', name: 'Erasmus only', is_default: true, filters: { program: 'p1' } }],
    })
    const wrapper = mount(AnalyticsForecasts, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' }, PageHeader: { template: '<div><slot /></div>' } },
      },
    })
    await flushPromises()
    expect(wrapper.find('[data-testid="forecasts-program"]').element.value).toBe('p1')
    expect(api.get).toHaveBeenCalledWith('/api/admin/dashboard/forecasts/', {
      params: { program: 'p1' },
    })
    expect(wrapper.find('[data-testid="forecasts-preset-apply"]').text()).toBe('Erasmus only')
  })
})
