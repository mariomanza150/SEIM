/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import Applications from './Applications.vue'
import api from '@/services/api'
import i18n, { setAppLocale } from '@/i18n'

vi.mock('@/services/api', () => ({
  default: { get: vi.fn(), delete: vi.fn() },
}))

vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: vi.fn(), error: vi.fn() }),
}))

describe('Applications', () => {
  beforeEach(() => {
    localStorage.clear()
    setAppLocale('en')
    vi.clearAllMocks()
    global.confirm = vi.fn(() => false)
  })

  afterEach(() => {
    setAppLocale('en')
    localStorage.clear()
  })

  it('shows translated empty state when list is empty', async () => {
    api.get.mockResolvedValue({ data: { results: [], count: 0, next: null, previous: null } })
    const wrapper = mount(Applications, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.find('nav').attributes('aria-label')).toBe(i18n.global.t('applicationsPage.breadcrumbAria'))
    expect(wrapper.text()).toContain('No applications yet')
    expect(wrapper.text()).toContain('My applications')
  })

  it('renders draft card with translated labels', async () => {
    api.get.mockResolvedValue({
      data: {
        results: [
          {
            id: '1',
            status: 'draft',
            created_at: '2026-01-10T12:00:00Z',
            submitted_at: '2026-01-11T12:00:00Z',
            program: { name: 'Test Program', institution: 'Uni' },
          },
        ],
        count: 1,
        next: null,
        previous: null,
      },
    })
    const wrapper = mount(Applications, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.text()).toContain('Test Program')
    expect(wrapper.text()).toContain('Draft')
    expect(wrapper.text()).toContain(`${i18n.global.t('applicationDetailPage.submitted')}:`)
    expect(wrapper.text()).toContain('View details')
    expect(wrapper.find('[data-testid="application-detail-link"]').exists()).toBe(true)
  })

  it('uses applicationDetailPage fallbacks for sparse program and missing dates', async () => {
    api.get.mockResolvedValue({
      data: {
        results: [
          {
            id: 'sparse',
            status: 'submitted',
            created_at: null,
            submitted_at: null,
            program: { name: '', institution: null },
          },
        ],
        count: 1,
        next: null,
        previous: null,
      },
    })
    const wrapper = mount(Applications, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.text()).toContain(i18n.global.t('applicationDetailPage.unknownProgram'))
    const na = i18n.global.t('applicationDetailPage.notAvailable')
    expect(wrapper.text().split(na).length - 1).toBeGreaterThanOrEqual(2)
    expect(wrapper.text()).toContain(i18n.global.t('applicationDetailPage.status.submitted'))
    expect(wrapper.text()).toContain(`${i18n.global.t('applicationDetailPage.created')}:`)
  })

  it('shows shared pagination.previous and pagination.next when list spans pages', async () => {
    const results = Array.from({ length: 10 }, (_, i) => ({
      id: String(i),
      status: 'draft',
      created_at: '2026-01-10T12:00:00Z',
      program: { name: `Program ${i}`, institution: 'Uni' },
    }))
    api.get.mockResolvedValue({
      data: {
        results,
        count: 11,
        next: 'http://test/api/applications/?page=2',
        previous: null,
      },
    })
    const wrapper = mount(Applications, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.text()).toContain(i18n.global.t('pagination.previous'))
    expect(wrapper.text()).toContain(i18n.global.t('pagination.next'))
  })
})
