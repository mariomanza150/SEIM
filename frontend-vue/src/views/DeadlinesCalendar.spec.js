/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import DeadlinesCalendar from './DeadlinesCalendar.vue'
import api from '@/services/api'
import i18n, { setAppLocale } from '@/i18n'

vi.mock('@/services/api', () => ({
  default: { get: vi.fn() },
}))

vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: vi.fn(), error: vi.fn() }),
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => ({
    canUseStaffReviewQueue: false,
  }),
}))

const mockPush = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({ push: mockPush }),
}))

describe('DeadlinesCalendar', () => {
  beforeEach(() => {
    localStorage.clear()
    setAppLocale('en')
    vi.clearAllMocks()
    api.get.mockImplementation((url) => {
      if (url === '/api/calendar/events/subscribe-token/') {
        return Promise.resolve({ data: { ics_url: 'https://example/ics', webcal_url: 'webcal://example' } })
      }
      if (url === '/api/saved-searches/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/calendar/events/') {
        return Promise.resolve({ data: [] })
      }
      return Promise.reject(new Error(`Unexpected GET ${url}`))
    })
  })

  afterEach(() => {
    setAppLocale('en')
    localStorage.clear()
  })

  it('shows translated title and empty state', async () => {
    const wrapper = mount(DeadlinesCalendar, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.text()).toContain('Deadlines and calendar')
    expect(wrapper.find('[data-testid="calendar-empty"]').text()).toContain(
      'No events in this range with the current filters',
    )
    expect(wrapper.find('[data-testid="calendar-preset-name"]').attributes('placeholder')).toBe(
      i18n.global.t('calendarPage.presetNamePlaceholder'),
    )
  })
})
