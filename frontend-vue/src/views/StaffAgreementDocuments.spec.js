/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import StaffAgreementDocuments from './StaffAgreementDocuments.vue'
import api from '@/services/api'
import i18n, { setAppLocale } from '@/i18n'

vi.mock('@/services/api', () => ({
  default: { get: vi.fn(), post: vi.fn(), delete: vi.fn() },
}))

vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: vi.fn(), error: vi.fn() }),
}))

describe('StaffAgreementDocuments', () => {
  beforeEach(() => {
    localStorage.clear()
    setAppLocale('en')
    vi.clearAllMocks()
    api.get.mockImplementation((url) => {
      if (url === '/api/saved-searches/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/exchange-agreements/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/agreement-documents/') {
        return Promise.resolve({ data: { results: [], count: 0 } })
      }
      return Promise.reject(new Error(`Unexpected GET ${url}`))
    })
  })

  afterEach(() => {
    setAppLocale('en')
    localStorage.clear()
  })

  it('shows shared pagination.previous and pagination.next when list spans pages', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/saved-searches/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/exchange-agreements/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/agreement-documents/') {
        return Promise.resolve({
          data: {
            results: [{ id: 1, title: 'Doc', category: 'other' }],
            count: 25,
            next: 'http://test/api/agreement-documents/?page=2',
            previous: null,
          },
        })
      }
      return Promise.reject(new Error(`Unexpected GET ${url}`))
    })
    const wrapper = mount(StaffAgreementDocuments, {
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

  it('shows translated heading and empty state', async () => {
    const wrapper = mount(StaffAgreementDocuments, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.text()).toContain('Agreement documents')
    expect(wrapper.find('[data-testid="agreement-docs-empty"]').text()).toContain(
      'No repository documents match these filters',
    )
    expect(wrapper.find('[data-testid="agreement-docs-preset-name"]').attributes('placeholder')).toBe(
      i18n.global.t('staffAgreementDocumentsPage.presetNamePlaceholder'),
    )
  })

  it('file download link uses noopener noreferrer', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/saved-searches/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/exchange-agreements/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/agreement-documents/') {
        return Promise.resolve({
          data: {
            results: [
              {
                id: 'ad-1',
                title: 'Signed',
                category: 'signed_copy',
                file: '/media/agreements/signed.pdf',
                created_at: '2026-01-01T00:00:00Z',
                agreement: null,
              },
            ],
            count: 1,
            next: null,
            previous: null,
          },
        })
      }
      return Promise.reject(new Error(`Unexpected GET ${url}`))
    })
    const wrapper = mount(StaffAgreementDocuments, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    const a = wrapper.find('a[target="_blank"]')
    expect(a.exists()).toBe(true)
    expect(a.attributes('rel')).toBe('noopener noreferrer')
  })
})
