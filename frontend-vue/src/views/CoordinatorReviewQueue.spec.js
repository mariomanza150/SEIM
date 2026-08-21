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

vi.mock('@/composables/useConfirm', () => ({
  useConfirm: () => ({ confirm: vi.fn() }),
}))

const routeQuery = { status: '' }
const routerPush = vi.fn()
vi.mock('vue-router', () => ({
  useRoute: () => ({ query: routeQuery }),
  useRouter: () => ({ push: routerPush }),
}))

function mockQueueApps(results) {
  api.get.mockImplementation((url) => {
    if (url === '/api/saved-searches/') {
      return Promise.resolve({ data: { results: [] } })
    }
    if (url === '/api/applications/') {
      return Promise.resolve({
        data: {
          results,
          count: results.length,
          next: null,
          previous: null,
        },
      })
    }
    return Promise.reject(new Error(`Unexpected GET ${url}`))
  })
}

const sampleApps = [
  {
    id: 11,
    status: 'submitted',
    program_name: 'P1',
    student_display_name: 'Ada',
    student_email: 'ada@test.com',
    submitted_at: null,
  },
  {
    id: 22,
    status: 'under_review',
    program_name: 'P2',
    student_display_name: 'Bob',
    student_email: 'bob@test.com',
    submitted_at: null,
  },
]

describe('CoordinatorReviewQueue', () => {
  beforeEach(() => {
    localStorage.clear()
    setAppLocale('en')
    routeQuery.status = ''
    routerPush.mockReset()
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
    const advancedToggle = wrapper.find('[data-testid="compact-filter-advanced-toggle"]')
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
    const statusSelect = wrapper.find('[data-testid="review-queue-filter-status"]')
    const statusOpts = statusSelect.findAll('option')
    const draft = statusOpts.find((o) => o.element.value === 'draft')
    expect(draft?.text()).toBe(i18n.global.t('reviewQueuePage.status.draft'))
    expect(wrapper.text()).toContain(i18n.global.t('reviewQueuePage.clearFilters'))
    await wrapper.get('[data-testid="compact-filter-advanced-toggle"]').trigger('click')
    expect(wrapper.text()).toContain(i18n.global.t('reviewQueuePage.sortRecentlySubmitted'))
    const statusValues = statusOpts.map((o) => o.element.value)
    expect(statusValues).toContain('nominated')
    expect(statusValues).toContain('waitlist')
    expect(statusValues).toContain('cancelled')
    expect(statusValues).toContain('withdrawn')
    expect(statusOpts.find((o) => o.element.value === 'nominated')?.text()).toBe(
      i18n.global.t('reviewQueuePage.status.nominated'),
    )
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
    const draft = wrapper.find('[data-testid="review-queue-filter-status"]').findAll('option').find((o) => o.element.value === 'draft')
    expect(draft?.text()).toBe(i18n.global.t('reviewQueuePage.status.draft'))
    expect(wrapper.text()).toContain(i18n.global.t('reviewQueuePage.clearFilters'))
  })

  it('sends page=1 when status filter changes instead of a DOM event', async () => {
    const wrapper = mount(CoordinatorReviewQueue, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    api.get.mockClear()
    const statusSelect = wrapper.find('[data-testid="review-queue-filter-status"]')
    await statusSelect.setValue('submitted')
    await statusSelect.trigger('change')
    await flushPromises()
    expect(api.get).toHaveBeenCalledWith('/api/applications/', {
      params: { page: 1, ordering: '-submitted_at', status: 'submitted' },
    })
  })

  it('applies ?status= from route query on mount (MQ-026)', async () => {
    routeQuery.status = 'nominated'
    const wrapper = mount(CoordinatorReviewQueue, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.find('[data-testid="review-queue-filter-status"]').element.value).toBe('nominated')
    expect(api.get).toHaveBeenCalledWith('/api/applications/', {
      params: { page: 1, ordering: '-submitted_at', status: 'nominated' },
    })
  })

  it('supports multi-select with sticky selection bar and open selected', async () => {
    mockQueueApps(sampleApps)
    const wrapper = mount(CoordinatorReviewQueue, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
      attachTo: document.body,
    })
    await flushPromises()
    expect(wrapper.find('[data-testid="review-queue-selection-bar"]').exists()).toBe(false)
    const checks = wrapper.findAll('[data-testid="review-queue-row-select"]')
    await checks[0].setValue(true)
    await checks[1].setValue(true)
    expect(wrapper.find('[data-testid="review-queue-selection-bar"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="review-queue-selection-count"]').text()).toContain('2')
    await wrapper.find('[data-testid="review-queue-open-selected"]').trigger('click')
    expect(routerPush).toHaveBeenCalledWith({ name: 'ApplicationDetail', params: { id: 11 } })
    await wrapper.find('[data-testid="review-queue-clear-selection"]').trigger('click')
    expect(wrapper.find('[data-testid="review-queue-selection-bar"]').exists()).toBe(false)
    wrapper.unmount()
  })

  it('moves focus with j/k and opens focused row with Enter', async () => {
    mockQueueApps(sampleApps)
    const wrapper = mount(CoordinatorReviewQueue, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
      attachTo: document.body,
    })
    await flushPromises()
    const rows = wrapper.findAll('[data-testid="review-queue-row"]')
    expect(rows[0].classes()).toContain('table-active')
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'j', bubbles: true }))
    await flushPromises()
    expect(rows[1].classes()).toContain('table-active')
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'x', bubbles: true }))
    await flushPromises()
    expect(wrapper.find('[data-testid="review-queue-selection-count"]').text()).toContain('1')
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }))
    expect(routerPush).toHaveBeenCalledWith({ name: 'ApplicationDetail', params: { id: 22 } })
    wrapper.unmount()
  })

  it('shows Spanish selection and keyboard copy', async () => {
    setAppLocale('es')
    mockQueueApps(sampleApps)
    const wrapper = mount(CoordinatorReviewQueue, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.find('[data-testid="review-queue-keyboard-hint"]').text()).toBe(
      i18n.global.t('reviewQueuePage.keyboardHint'),
    )
    await wrapper.findAll('[data-testid="review-queue-row-select"]')[0].setValue(true)
    expect(wrapper.find('[data-testid="review-queue-open-selected"]').text()).toBe(
      i18n.global.t('reviewQueuePage.openSelected'),
    )
  })
})
