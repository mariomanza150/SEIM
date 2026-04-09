/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import DocumentDetail from './DocumentDetail.vue'
import api from '@/services/api'
import i18n, { setAppLocale } from '@/i18n'

vi.mock('vue-router', () => ({
  useRoute: () => ({ params: { id: 'doc-1' } }),
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => ({
    userRole: 'student',
    checkAuth: vi.fn().mockResolvedValue(undefined),
  }),
}))

vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: vi.fn(), error: vi.fn() }),
}))

vi.mock('@/services/api', () => ({
  default: { get: vi.fn(), post: vi.fn(), patch: vi.fn() },
}))

function mockSuccessFlow() {
  api.get.mockImplementation((url, config) => {
    if (url === '/api/applications/') {
      return Promise.resolve({
        data: { results: [{ id: 'app-1', program: { name: 'Spring Program' } }], count: 1 },
      })
    }
    if (url === '/api/documents/doc-1/') {
      return Promise.resolve({
        data: {
          id: 'doc-1',
          application: 'app-1',
          file: '/media/student/transcript.pdf',
          is_valid: true,
          created_at: '2026-01-01T12:00:00Z',
          updated_at: '2026-01-02T12:00:00Z',
          type: { name: 'Transcript' },
          uploaded_by: 'student@test.edu',
          validations: [],
          resubmission_requests: [],
          comments: [],
        },
      })
    }
    if (String(url).includes('/api/documents/doc-1/preview/')) {
      return Promise.resolve({ data: new Blob(['%PDF'], { type: 'application/pdf' }) })
    }
    return Promise.reject(new Error(`Unexpected GET ${url}`))
  })
}

describe('DocumentDetail', () => {
  beforeEach(() => {
    localStorage.clear()
    setAppLocale('en')
    vi.clearAllMocks()
    mockSuccessFlow()
  })

  afterEach(() => {
    setAppLocale('en')
    localStorage.clear()
  })

  it('renders loaded document with translated labels (student)', async () => {
    const wrapper = mount(DocumentDetail, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.find('[data-testid="document-detail-page"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('Transcript')
    expect(wrapper.text()).toContain('Spring Program')
    expect(wrapper.text()).toContain('Validated')
    expect(wrapper.text()).toContain('Preview')
    expect(wrapper.text()).toContain('Replace file')
    for (const a of wrapper.findAll('a[target="_blank"]')) {
      expect(a.attributes('rel')).toBe('noopener noreferrer')
    }
  })

  it('shows translated error when document fetch fails', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/documents/doc-1/') {
        return Promise.reject({ response: { status: 404 } })
      }
      return Promise.reject(new Error(`Unexpected GET ${url}`))
    })

    const wrapper = mount(DocumentDetail, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.text()).toContain('Failed to load document')
    expect(wrapper.text()).toContain('Back to Documents')
  })

  it('uses documentDetailPage fallbacks for missing file, uploader, dates, and application', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/') {
        return Promise.resolve({ data: { results: [], count: 0 } })
      }
      if (url === '/api/documents/doc-1/') {
        return Promise.resolve({
          data: {
            id: 'doc-1',
            application: null,
            file: null,
            is_valid: false,
            created_at: null,
            updated_at: null,
            validated_at: null,
            type: { name: 'Transcript' },
            uploaded_by: null,
            validations: [],
            resubmission_requests: [],
            comments: [],
          },
        })
      }
      return Promise.reject(new Error(`Unexpected GET ${url}`))
    })

    const wrapper = mount(DocumentDetail, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.text()).toContain(i18n.global.t('documentDetailPage.fileUnknown'))
    expect(wrapper.text()).toContain(i18n.global.t('documentDetailPage.unknownApplication'))
    const na = i18n.global.t('documentDetailPage.notAvailable')
    expect(wrapper.text().split(na).length - 1).toBeGreaterThanOrEqual(2)
  })
})
