/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import Documents from './Documents.vue'
import api from '@/services/api'
import i18n, { setAppLocale } from '@/i18n'

vi.mock('@/services/api', () => ({
  default: { get: vi.fn() },
}))

vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ error: vi.fn(), success: vi.fn() }),
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => ({
    canUseStaffReviewQueue: false,
  }),
}))

function mockEmptyApis() {
  api.get.mockImplementation((url) => {
    if (url === '/api/applications/') {
      return Promise.resolve({ data: { results: [], count: 0 } })
    }
    if (url === '/api/document-types/') {
      return Promise.resolve({ data: { results: [] } })
    }
    if (url === '/api/documents/') {
      return Promise.resolve({ data: { results: [], count: 0, next: null, previous: null } })
    }
    return Promise.reject(new Error(`Unexpected GET ${url}`))
  })
}

describe('Documents', () => {
  beforeEach(() => {
    localStorage.clear()
    setAppLocale('en')
    vi.clearAllMocks()
    mockEmptyApis()
  })

  afterEach(() => {
    setAppLocale('en')
    localStorage.clear()
  })

  it('shows translated empty state for student', async () => {
    const wrapper = mount(Documents, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.find('nav').attributes('aria-label')).toBe(i18n.global.t('documentsPage.breadcrumbAria'))
    expect(wrapper.find('[data-testid="documents-heading"]').text()).toContain('Documents')
    expect(wrapper.text()).toContain('No documents yet')
    expect(wrapper.text()).toContain('Manage your uploaded documents for applications')
  })

  it('uses Spanish breadcrumb aria when locale is es', async () => {
    setAppLocale('es')
    const wrapper = mount(Documents, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.find('nav').attributes('aria-label')).toBe('Migas de pan')
  })

  it('renders document row with view link', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/') {
        return Promise.resolve({
          data: { results: [{ id: 'app-1', program: { name: 'Spring Abroad' } }], count: 1 },
        })
      }
      if (url === '/api/document-types/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/documents/') {
        return Promise.resolve({
          data: {
            results: [
              {
                id: 'doc-1',
                application: 'app-1',
                file: '/media/student/file.pdf',
                is_valid: true,
                created_at: '2026-01-01T00:00:00Z',
                type: { name: 'CV' },
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

    const wrapper = mount(Documents, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.text()).toContain('Spring Abroad')
    expect(wrapper.text()).toContain(i18n.global.t('documentDetailPage.statusValidatedShort'))
    expect(wrapper.find('[data-testid="document-detail-link"]').exists()).toBe(true)
  })

  it('uses documentDetailPage fallbacks for missing file, application, and upload date', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/') {
        return Promise.resolve({ data: { results: [], count: 0 } })
      }
      if (url === '/api/document-types/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/documents/') {
        return Promise.resolve({
          data: {
            results: [
              {
                id: 'doc-sparse',
                application: null,
                file: null,
                is_valid: false,
                created_at: null,
                type: { name: 'Other' },
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

    const wrapper = mount(Documents, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.text()).toContain(i18n.global.t('documentDetailPage.fileUnknown'))
    expect(wrapper.text()).toContain(i18n.global.t('documentDetailPage.unknownApplication'))
    expect(wrapper.text()).toContain(i18n.global.t('documentDetailPage.notAvailable'))
    expect(wrapper.text()).toContain(i18n.global.t('documentDetailPage.statusPendingShort'))
  })

  it('shows shared pagination.previous and pagination.next when list spans pages', async () => {
    const results = Array.from({ length: 10 }, (_, i) => ({
      id: `doc-${i}`,
      application: 'app-1',
      file: `/media/f${i}.pdf`,
      is_valid: true,
      created_at: '2026-01-01T00:00:00Z',
      type: { name: 'CV' },
    }))
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/') {
        return Promise.resolve({
          data: { results: [{ id: 'app-1', program: { name: 'Spring Abroad' } }], count: 1 },
        })
      }
      if (url === '/api/document-types/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/documents/') {
        return Promise.resolve({
          data: {
            results,
            count: 11,
            next: 'http://test/api/documents/?page=2',
            previous: null,
          },
        })
      }
      return Promise.reject(new Error(`Unexpected GET ${url}`))
    })

    const wrapper = mount(Documents, {
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
