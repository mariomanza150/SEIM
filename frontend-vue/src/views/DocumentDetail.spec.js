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
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
}))

const mockAuthStore = {
  userRole: 'student',
  checkAuth: vi.fn().mockResolvedValue(undefined),
}

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockAuthStore,
}))

const mockToastError = vi.fn()
const mockToastSuccess = vi.fn()
vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: mockToastSuccess, error: mockToastError }),
}))

const mockConfirm = vi.fn().mockResolvedValue(true)
vi.mock('@/composables/useConfirm', () => ({
  useConfirm: () => ({ confirm: mockConfirm }),
}))

vi.mock('@/services/api', () => ({
  default: { get: vi.fn(), post: vi.fn(), patch: vi.fn() },
}))

function mockSuccessFlow(overrides = {}) {
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
          is_valid: false,
          validated_at: null,
          created_at: '2026-01-01T12:00:00Z',
          updated_at: '2026-01-02T12:00:00Z',
          type: {
            name: 'Transcript',
            has_template: true,
            id: 9,
            resolved_accepted_extensions: 'pdf',
            accepted_extensions: '',
            max_file_size_mb: 5,
          },
          uploaded_by: 'student@test.edu',
          validations: [],
          resubmission_requests: [],
          comments: [],
          can_replace: true,
          ...overrides,
        },
      })
    }
    if (String(url).includes('/api/documents/doc-1/preview/')) {
      return Promise.resolve({
        data: new Blob(['%PDF'], { type: '' }),
        headers: { 'content-type': 'application/pdf' },
      })
    }
    return Promise.reject(new Error(`Unexpected GET ${url}`))
  })
}

describe('DocumentDetail', () => {
  beforeEach(() => {
    localStorage.clear()
    setAppLocale('en')
    mockAuthStore.userRole = 'student'
    mockConfirm.mockResolvedValue(true)
    vi.clearAllMocks()
    mockSuccessFlow()
    vi.stubGlobal('URL', {
      ...URL,
      createObjectURL: vi.fn(() => 'blob:mock-preview'),
      revokeObjectURL: vi.fn(),
    })
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
    expect(wrapper.text()).toContain(i18n.global.t('documentDetailPage.pendingValidation'))
    expect(wrapper.text()).toContain('Preview')
    expect(wrapper.find('[data-testid="replace-file-section"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="replace-accepted-hint"]').text()).toBe(
      'Accepted: PDF (max 5MB)',
    )
    expect(wrapper.find('[data-testid="replace-file-input"]').attributes('accept')).toBe('.pdf')
    expect(wrapper.find('[data-testid="download-type-template"]').exists()).toBe(true)
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
  })

  it('when preview returns non-PDF body for a PDF, shows recovery download and open-in-new-tab actions', async () => {
    api.get.mockImplementation((url) => {
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
        return Promise.resolve({
          data: new Blob(['<html></html>'], { type: 'text/html' }),
          headers: { 'content-type': 'text/html; charset=utf-8' },
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
    const recovery = wrapper.find('[data-testid="preview-error-recovery"]')
    expect(recovery.exists()).toBe(true)
    expect(recovery.text()).toContain(i18n.global.t('documentDetailPage.previewError'))
    const links = recovery.findAll('a')
    expect(links.length).toBe(2)
    expect(links[0].attributes('download')).toBeDefined()
    expect(links[1].attributes('target')).toBe('_blank')
    expect(links[1].attributes('rel')).toBe('noopener noreferrer')
  })

  it('renders a PDF embed when preview returns a PDF blob', async () => {
    const wrapper = mount(DocumentDetail, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    const embed = wrapper.find('[data-testid="document-preview-pdf"]')
    expect(embed.exists()).toBe(true)
    expect(embed.attributes('type')).toBe('application/pdf')
    expect(embed.attributes('src')).toBe('blob:mock-preview')
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

  it('shows display names and i18n validation results instead of slugs', async () => {
    api.get.mockImplementation((url) => {
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
            uploaded_by: 'student',
            uploaded_by_name: 'Sofia Martinez',
            validations: [
              {
                id: 'val-1',
                result: 'valid',
                validator_name: 'Camila Coordinator',
                validated_at: '2026-01-02T12:00:00Z',
              },
            ],
            resubmission_requests: [],
            comments: [
              {
                id: 'c-1',
                author: 'coordinator',
                author_name: 'Camila Coordinator',
                text: 'Stamp is readable.',
                created_at: '2026-01-02T13:00:00Z',
              },
            ],
          },
        })
      }
      if (String(url).includes('/api/documents/doc-1/preview/')) {
        return Promise.resolve({
          data: new Blob(['%PDF'], { type: '' }),
          headers: { 'content-type': 'application/pdf' },
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
    expect(wrapper.text()).toContain('Sofia Martinez')
    expect(wrapper.text()).toContain('Camila Coordinator')
    expect(wrapper.find('[data-testid="validation-result"]').text()).toBe(
      i18n.global.t('documentDetailPage.validationResult.valid'),
    )
    expect(wrapper.text()).toContain('Stamp is readable.')
  })

  it('shows Invalid instead of Pending after staff rejection', async () => {
    api.get.mockImplementation((url) => {
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
            is_valid: false,
            validated_at: '2026-01-02T12:00:00Z',
            created_at: '2026-01-01T12:00:00Z',
            updated_at: '2026-01-02T12:00:00Z',
            type: { name: 'Transcript' },
            uploaded_by: 'student',
            validations: [{ id: 'val-1', result: 'invalid', validated_at: '2026-01-02T12:00:00Z' }],
            resubmission_requests: [],
            comments: [],
          },
        })
      }
      if (String(url).includes('/api/documents/doc-1/preview/')) {
        return Promise.resolve({
          data: new Blob(['%PDF'], { type: '' }),
          headers: { 'content-type': 'application/pdf' },
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
    const invalid = i18n.global.t('documentDetailPage.validationResult.invalid')
    expect(wrapper.text()).toContain(invalid)
    expect(wrapper.text()).toContain(i18n.global.t('applicationDetailPage.checklist.invalid'))
    expect(wrapper.text()).not.toContain(i18n.global.t('applicationDetailPage.checklist.pending_review'))
    expect(wrapper.find('[data-testid="validation-result"]').text()).toBe(invalid)
  })

  it('hides replace and template download when the document is approved', async () => {
    mockSuccessFlow({
      is_valid: true,
      validated_at: '2026-01-02T12:00:00Z',
      can_replace: false,
      type: { name: 'Transcript', has_template: true, id: 9 },
    })
    const wrapper = mount(DocumentDetail, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.find('[data-testid="replace-file-section"]').exists()).toBe(false)
    expect(wrapper.find('[data-testid="download-type-template"]').exists()).toBe(false)
  })

  it('shows template download again when staff requested resubmission', async () => {
    mockSuccessFlow({
      is_valid: true,
      validated_at: '2026-01-02T12:00:00Z',
      can_replace: true,
      resubmission_requests: [{ id: 'rr-1', resolved: false, reason: 'Clearer scan' }],
      type: { name: 'Transcript', has_template: true, id: 9 },
    })
    const wrapper = mount(DocumentDetail, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.find('[data-testid="replace-file-section"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="download-type-template"]').exists()).toBe(true)
  })

  it('requires a rejection note before marking invalid', async () => {
    mockAuthStore.userRole = 'coordinator'
    api.post.mockResolvedValue({ data: {} })
    const wrapper = mount(DocumentDetail, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    const buttons = wrapper.findAll('button')
    const invalidBtn = buttons.find((b) => b.text().includes(i18n.global.t('documentDetailPage.markInvalid')))
    expect(invalidBtn).toBeTruthy()
    await invalidBtn.trigger('click')
    await flushPromises()
    expect(mockToastError).toHaveBeenCalledWith(i18n.global.t('documentDetailPage.invalidNoteRequired'))
    expect(api.post).not.toHaveBeenCalled()
    expect(mockConfirm).not.toHaveBeenCalled()
  })

  it('confirms and posts invalid with note details', async () => {
    mockAuthStore.userRole = 'coordinator'
    api.post.mockResolvedValue({ data: {} })
    const wrapper = mount(DocumentDetail, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    const noteField = wrapper.findAll('textarea').find((ta) =>
      ta.attributes('placeholder') === i18n.global.t('documentDetailPage.validationNotePlaceholder'),
    )
    expect(noteField).toBeTruthy()
    await noteField.setValue('Blurry scan — please reupload')
    const buttons = wrapper.findAll('button')
    const invalidBtn = buttons.find((b) => b.text().includes(i18n.global.t('documentDetailPage.markInvalid')))
    await invalidBtn.trigger('click')
    await flushPromises()
    expect(mockConfirm).toHaveBeenCalled()
    expect(api.post).toHaveBeenCalledWith('/api/documents/doc-1/validate_document/', {
      result: 'invalid',
      details: 'Blurry scan — please reupload',
    })
  })

  it('soft-confirms before marking valid', async () => {
    mockAuthStore.userRole = 'coordinator'
    api.post.mockResolvedValue({ data: {} })
    const wrapper = mount(DocumentDetail, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    const buttons = wrapper.findAll('button')
    const validBtn = buttons.find((b) => b.text().includes(i18n.global.t('documentDetailPage.markValid')))
    await validBtn.trigger('click')
    await flushPromises()
    expect(mockConfirm).toHaveBeenCalled()
    expect(api.post).toHaveBeenCalledWith('/api/documents/doc-1/validate_document/', {
      result: 'valid',
      details: '',
    })
  })
})
