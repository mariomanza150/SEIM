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
    const advancedToggle = wrapper.find('button.btn-link')
    await advancedToggle.trigger('click')
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

  it('shows shared pagination.previous and pagination.next when queue spans pages', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/saved-searches/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/applications/') {
        return Promise.resolve({
          data: {
            results: [
              {
                id: 1,
                status: 'submitted',
                program_name: 'P',
                student_display_name: 'S',
                student_email: 's@test.com',
                submitted_at: null,
              },
            ],
            count: 25,
            next: 'http://test/api/applications/?page=2',
            previous: null,
          },
        })
      }
      return Promise.reject(new Error(`Unexpected GET ${url}`))
    })
    const wrapper = mount(CoordinatorReviewQueue, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.text()).toContain(i18n.global.t('pagination.previous'))
    expect(wrapper.text()).toContain(i18n.global.t('pagination.next'))
    const ariaLabels = wrapper.find('ul.pagination').findAll('button').map((b) => b.attributes('aria-label'))
    expect(ariaLabels).toContain(i18n.global.t('pagination.pageNumberAria', { n: 1 }))
    expect(ariaLabels).toContain(i18n.global.t('pagination.pageNumberAria', { n: 2 }))
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
