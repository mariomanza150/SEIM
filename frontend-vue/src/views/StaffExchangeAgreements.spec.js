/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import StaffExchangeAgreements from './StaffExchangeAgreements.vue'
import api from '@/services/api'
import i18n, { setAppLocale } from '@/i18n'

vi.mock('@/services/api', () => ({
  default: { get: vi.fn(), post: vi.fn(), delete: vi.fn() },
}))

vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: vi.fn(), error: vi.fn() }),
}))

describe('StaffExchangeAgreements', () => {
  beforeEach(() => {
    localStorage.clear()
    setAppLocale('en')
    vi.clearAllMocks()
    api.get.mockImplementation((url) => {
      if (url === '/api/programs/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/saved-searches/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/exchange-agreements/') {
        return Promise.resolve({ data: { results: [], count: 0 } })
      }
      return Promise.reject(new Error(`Unexpected GET ${url}`))
    })
  })

  afterEach(() => {
    setAppLocale('en')
    localStorage.clear()
  })

  it('shows translated heading and empty state', async () => {
    const wrapper = mount(StaffExchangeAgreements, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.text()).toContain('Exchange agreements')
    expect(wrapper.find('[data-testid="agreements-empty"]').text()).toContain(
      'No agreements match these filters',
    )
    expect(wrapper.find('[data-testid="agreements-preset-name"]').attributes('placeholder')).toBe(
      i18n.global.t('exchangeAgreementsPage.presetNamePlaceholder'),
    )
  })
})
