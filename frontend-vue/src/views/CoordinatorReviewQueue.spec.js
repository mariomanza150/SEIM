/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import CoordinatorReviewQueue from './CoordinatorReviewQueue.vue'
import api from '@/services/api'
import i18n, { setAppLocale } from '@/i18n'

vi.mock('@/services/api', () => ({
  default: { get: vi.fn(), post: vi.fn(), delete: vi.fn() },
}))

vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: vi.fn(), error: vi.fn() }),
}))

describe('CoordinatorReviewQueue', () => {
  beforeEach(() => {
    localStorage.clear()
    setAppLocale('en')
    vi.clearAllMocks()
    api.get.mockImplementation((url) => {
      if (url === '/api/saved-searches/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/applications/') {
        return Promise.resolve({ data: { results: [], count: 0, next: null, previous: null } })
      }
      return Promise.reject(new Error(`Unexpected GET ${url}`))
    })
  })

  afterEach(() => {
    setAppLocale('en')
    localStorage.clear()
  })

  it('shows translated empty state', async () => {
    const wrapper = mount(CoordinatorReviewQueue, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.find('[data-testid="review-queue-empty"]').text()).toContain(
      'No applications match these filters'
    )
    expect(wrapper.text()).toContain('Application review queue')
    expect(wrapper.find('[data-testid="review-queue-preset-name"]').attributes('placeholder')).toBe(
      i18n.global.t('reviewQueuePage.presetNamePlaceholder'),
    )
  })

  it('uses reviewQueuePage keys for status options, sort labels, and clear', async () => {
    const wrapper = mount(CoordinatorReviewQueue, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    const selects = wrapper.findAll('select.form-select')
    expect(selects.length).toBeGreaterThanOrEqual(2)
    const statusOpts = selects[0].findAll('option')
    const draft = statusOpts.find((o) => o.element.value === 'draft')
    expect(draft?.text()).toBe(i18n.global.t('reviewQueuePage.status.draft'))
    expect(wrapper.text()).toContain(i18n.global.t('reviewQueuePage.sortRecentlySubmitted'))
    expect(wrapper.text()).toContain(i18n.global.t('reviewQueuePage.clearFilters'))
  })

  it('uses Spanish reviewQueuePage status and clear strings', async () => {
    setAppLocale('es')
    const wrapper = mount(CoordinatorReviewQueue, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    const selects = wrapper.findAll('select.form-select')
    const draft = selects[0].findAll('option').find((o) => o.element.value === 'draft')
    expect(draft?.text()).toBe(i18n.global.t('reviewQueuePage.status.draft'))
    expect(wrapper.text()).toContain(i18n.global.t('reviewQueuePage.clearFilters'))
  })
})
