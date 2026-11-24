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

const mockToastError = vi.fn()
vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ error: mockToastError, success: vi.fn() }),
}))

const authStoreMock = {
  canUseStaffReviewQueue: false,
}

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => authStoreMock,
}))

vi.mock('@/composables/useStaffSavedPresets', async () => {
  const { ref } = await import('vue')
  return {
    useStaffSavedPresets: () => ({
      savedPresets: ref([]),
      newPresetName: ref(''),
      saveAsDefault: ref(false),
      presetsLoading: ref(false),
      loadPresets: vi.fn().mockResolvedValue(undefined),
      savePreset: vi.fn(),
      deletePreset: vi.fn(),
      setDefaultPreset: vi.fn(),
    }),
  }
})

function mockEmptyApis() {
  api.get.mockImplementation((url) => {
    if (url === '/api/applications/') {
      return Promise.resolve({ data: { results: [], count: 0 } })
    }
    if (url === '/api/document-types/') {
      return Promise.resolve({ data: { results: [] } })
    }
    if (url === '/api/document-types/my-prefill-templates/') {
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
    authStoreMock.canUseStaffReviewQueue = false
    vi.clearAllMocks()
    mockToastError.mockClear()
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
    expect(wrapper.find('.seim-page-breadcrumb').exists()).toBe(true)
    expect(wrapper.find('[data-testid="compact-filter-clear"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="compact-filter-advanced-toggle"]').exists()).toBe(false)
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
      if (url === '/api/document-types/my-prefill-templates/') {
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
    expect(wrapper.text()).toContain(i18n.global.t('applicationDetailPage.checklist.approved'))
    expect(wrapper.find('[data-testid="document-detail-link"]').exists()).toBe(true)
    const downloadBtn = wrapper.find('[data-testid="document-download"]')
    expect(downloadBtn.exists()).toBe(true)
    expect(downloadBtn.attributes('aria-label')).toBe(i18n.global.t('documentsPage.downloadTitle'))
    // Mobile cards must include actions (ResponsiveList previously had empty mobile markup).
    expect(wrapper.find('[data-testid="documents-mobile-0"]').exists()).toBe(true)
    expect(
      wrapper.find('[data-testid="documents-mobile-0"] [data-testid="document-detail-link"]').exists(),
    ).toBe(true)
  })

  it('toasts when document-type filter options fail to load', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/') {
        return Promise.resolve({ data: { results: [], count: 0 } })
      }
      if (url === '/api/document-types/') {
        return Promise.reject(new Error('network'))
      }
      if (url === '/api/document-types/my-prefill-templates/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/documents/') {
        return Promise.resolve({ data: { results: [], count: 0, next: null, previous: null } })
      }
      return Promise.reject(new Error(`Unexpected GET ${url}`))
    })

    mount(Documents, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(mockToastError).toHaveBeenCalledWith(i18n.global.t('documentsPage.filtersLoadError'))
  })

  it('shows Plantillas para ti only when prefill templates exist', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/') {
        return Promise.resolve({ data: { results: [], count: 0 } })
      }
      if (url === '/api/document-types/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/document-types/my-prefill-templates/') {
        return Promise.resolve({
          data: {
            results: [
              {
                id: 42,
                name: 'Learning Agreement',
                slug: 'learning_agreement',
                has_template: true,
                template_filename: 'agreement.docx',
              },
            ],
          },
        })
      }
      if (url === '/api/documents/') {
        return Promise.resolve({ data: { results: [], count: 0, next: null, previous: null } })
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
    const block = wrapper.find('[data-testid="prefill-templates-block"]')
    expect(block.exists()).toBe(true)
    expect(block.text()).toContain(i18n.global.t('documentsPage.prefillTemplatesTitle'))
    expect(block.text()).toContain('Learning Agreement')
    expect(wrapper.find('[data-testid="prefill-template-download"]').text()).toContain(
      i18n.global.t('documentsPage.prefillDownload'),
    )
  })

  it('hides Plantillas para ti when the list is empty', async () => {
    const wrapper = mount(Documents, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.find('[data-testid="prefill-templates-block"]').exists()).toBe(false)
  })

  it('downloads via authenticated preview endpoint', async () => {
    const clickSpy = vi.fn()
    const origCreate = document.createElement.bind(document)
    vi.spyOn(document, 'createElement').mockImplementation((tag) => {
      const el = origCreate(tag)
      if (tag === 'a') {
        el.click = clickSpy
      }
      return el
    })
    global.URL.createObjectURL = vi.fn(() => 'blob:doc')
    global.URL.revokeObjectURL = vi.fn()

    api.get.mockImplementation((url) => {
      if (url === '/api/applications/') {
        return Promise.resolve({ data: { results: [], count: 0 } })
      }
      if (url === '/api/document-types/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/document-types/my-prefill-templates/') {
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
      if (url === '/api/documents/doc-1/preview/') {
        return Promise.resolve({
          data: new Blob(['%PDF'], { type: 'application/pdf' }),
          headers: { 'content-type': 'application/pdf', 'content-disposition': 'inline; filename="file.pdf"' },
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
    await wrapper.find('[data-testid="document-download"]').trigger('click')
    await flushPromises()
    expect(api.get).toHaveBeenCalledWith('/api/documents/doc-1/preview/', { responseType: 'blob' })
    expect(clickSpy).toHaveBeenCalled()
    document.createElement.mockRestore()
  })

  it('uses documentDetailPage fallbacks for missing file, application, and upload date', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/') {
        return Promise.resolve({ data: { results: [], count: 0 } })
      }
      if (url === '/api/document-types/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/document-types/my-prefill-templates/') {
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
    expect(wrapper.text()).toContain(i18n.global.t('applicationDetailPage.checklist.pending_review'))
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
      if (url === '/api/document-types/my-prefill-templates/') {
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
    const ariaLabels = wrapper.find('ul.pagination').findAll('button').map((b) => b.attributes('aria-label'))
    expect(ariaLabels).toContain(i18n.global.t('pagination.previous'))
    expect(ariaLabels).toContain(i18n.global.t('pagination.next'))
    expect(ariaLabels).toContain(i18n.global.t('pagination.pageNumberAria', { n: 1 }))
    expect(ariaLabels).toContain(i18n.global.t('pagination.pageNumberAria', { n: 2 }))
  })

  it('application filter options use i18n status labels (MQ-025)', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/') {
        return Promise.resolve({
          data: {
            results: [
              {
                id: 'diego-1',
                program_name: 'DAAD Exchange - Munich',
                status: 'nominated',
              },
              {
                id: 'tokyo-1',
                program_name: 'Tokyo',
                status: 'under_review',
              },
            ],
            count: 2,
          },
        })
      }
      if (url === '/api/document-types/') {
        return Promise.resolve({
          data: {
            results: [
              {
                id: 1,
                name: 'carta_beca',
                slug: 'carta_beca',
                description: 'Scholarship letter',
              },
            ],
          },
        })
      }
      if (url === '/api/document-types/my-prefill-templates/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/documents/') {
        return Promise.resolve({ data: { results: [], count: 0, next: null, previous: null } })
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

    const appSelect = wrapper.findAll('select')[0]
    expect(appSelect.text()).toContain('DAAD Exchange - Munich (Nominated)')
    expect(appSelect.text()).toContain('Tokyo (Under review)')

    const typeSelect = wrapper.findAll('select')[1]
    expect(typeSelect.text()).toContain('Scholarship letter')
    expect(typeSelect.text()).not.toContain('carta_beca')
  })

  async function openStaffAdvancedFilters(wrapper) {
    await wrapper.get('[data-testid="compact-filter-advanced-toggle"]').trigger('click')
    await flushPromises()
  }

  it('staff pending-review filter forces pending status and refetch', async () => {
    authStoreMock.canUseStaffReviewQueue = true
    const wrapper = mount(Documents, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    await openStaffAdvancedFilters(wrapper)
    api.get.mockClear()
    mockEmptyApis()
    await wrapper.get('[data-testid="filter-pending-review"]').trigger('click')
    await flushPromises()
    const docsCalls = api.get.mock.calls.filter(([url]) => url === '/api/documents/')
    expect(docsCalls.length).toBeGreaterThan(0)
    expect(docsCalls.at(-1)[1].params).toMatchObject({
      pending_review: true,
      is_valid: 'false',
      page: 1,
    })
  })

  it('staff overdue filter toggles the overdue query param', async () => {
    authStoreMock.canUseStaffReviewQueue = true
    const wrapper = mount(Documents, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    await openStaffAdvancedFilters(wrapper)
    api.get.mockClear()
    mockEmptyApis()
    await wrapper.get('[data-testid="filter-overdue"]').trigger('click')
    await flushPromises()
    const docsCalls = api.get.mock.calls.filter(([url]) => url === '/api/documents/')
    expect(docsCalls.at(-1)[1].params).toMatchObject({ overdue: true, page: 1 })
  })

  it('clear filters resets staff toggles and reloads the first page', async () => {
    authStoreMock.canUseStaffReviewQueue = true
    const wrapper = mount(Documents, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    await openStaffAdvancedFilters(wrapper)
    await wrapper.get('[data-testid="filter-overdue"]').trigger('click')
    await flushPromises()
    api.get.mockClear()
    mockEmptyApis()
    await wrapper.get('[data-testid="compact-filter-clear"]').trigger('click')
    await flushPromises()
    const docsCalls = api.get.mock.calls.filter(([url]) => url === '/api/documents/')
    expect(docsCalls.at(-1)[1].params).toEqual({
      page: 1,
      ordering: '-created_at',
    })
  })

  it('toasts when document download fails', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/') {
        return Promise.resolve({ data: { results: [], count: 0 } })
      }
      if (url === '/api/document-types/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/document-types/my-prefill-templates/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/documents/') {
        return Promise.resolve({
          data: {
            results: [
              {
                id: 'doc-1',
                application: 'app-1',
                file: '/media/uploads/sample.pdf',
                is_valid: true,
                created_at: '2026-01-01T00:00:00Z',
                type: { name: 'Identity document' },
              },
            ],
            count: 1,
            next: null,
            previous: null,
          },
        })
      }
      if (url === '/api/documents/doc-1/preview/') {
        return Promise.reject(new Error('offline'))
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
    await wrapper.find('[data-testid="document-download"]').trigger('click')
    await flushPromises()
    expect(mockToastError).toHaveBeenCalledWith(i18n.global.t('documentsPage.downloadError'))
  })

  it('downloads a prefill template through the authenticated endpoint', async () => {
    const clickSpy = vi.fn()
    const origCreate = document.createElement.bind(document)
    vi.spyOn(document, 'createElement').mockImplementation((tag) => {
      const el = origCreate(tag)
      if (tag === 'a') el.click = clickSpy
      return el
    })
    global.URL.createObjectURL = vi.fn(() => 'blob:template')
    global.URL.revokeObjectURL = vi.fn()

    api.get.mockImplementation((url) => {
      if (url === '/api/applications/') {
        return Promise.resolve({ data: { results: [], count: 0 } })
      }
      if (url === '/api/document-types/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/document-types/my-prefill-templates/') {
        return Promise.resolve({
          data: {
            results: [
              {
                id: 7,
                name: 'Learning plan template',
                slug: 'learning_plan',
                has_template: true,
                template_filename: 'learning-plan.docx',
              },
            ],
          },
        })
      }
      if (url === '/api/documents/') {
        return Promise.resolve({ data: { results: [], count: 0, next: null, previous: null } })
      }
      if (url === '/api/document-types/7/download-template/') {
        return Promise.resolve({
          data: new Blob(['docx'], { type: 'application/octet-stream' }),
          headers: {
            'content-type': 'application/octet-stream',
            'content-disposition': 'attachment; filename="learning-plan.docx"',
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
    await wrapper.get('[data-testid="prefill-template-download"]').trigger('click')
    await flushPromises()
    expect(api.get).toHaveBeenCalledWith('/api/document-types/7/download-template/', {
      responseType: 'blob',
    })
    expect(clickSpy).toHaveBeenCalled()
    document.createElement.mockRestore()
  })

  it('shows a load error when the documents list request fails', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/') {
        return Promise.resolve({ data: { results: [], count: 0 } })
      }
      if (url === '/api/document-types/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/document-types/my-prefill-templates/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/documents/') {
        return Promise.reject(new Error('network'))
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
    expect(wrapper.text()).toContain(i18n.global.t('documentsPage.loadError'))
    expect(mockToastError).toHaveBeenCalledWith(i18n.global.t('documentsPage.loadToastError'))
  })
})
