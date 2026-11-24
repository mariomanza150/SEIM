/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import { createRouter, createMemoryHistory } from 'vue-router'
import en from '@/locales/en.json'
import AdminDocumentTypeEdit from './AdminDocumentTypeEdit.vue'

const {
  mockGet,
  mockPost,
  mockPut,
  mockPatch,
  mockDelete,
  mockSuccessToast,
  mockErrorToast,
  mockConfirm,
} = vi.hoisted(() => ({
  mockGet: vi.fn(),
  mockPost: vi.fn(),
  mockPut: vi.fn(),
  mockPatch: vi.fn(),
  mockDelete: vi.fn(),
  mockSuccessToast: vi.fn(),
  mockErrorToast: vi.fn(),
  mockConfirm: vi.fn(),
}))
vi.mock('@/services/api', () => ({
  default: { get: mockGet, patch: mockPatch, put: mockPut, post: mockPost, delete: mockDelete },
}))
vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: mockSuccessToast, error: mockErrorToast }),
}))
vi.mock('@/composables/useConfirm', () => ({
  useConfirm: () => ({ confirm: mockConfirm }),
}))

function mockDocumentTypePayload(overrides = {}) {
  return {
    id: 9,
    name: 'Transcript',
    slug: 'transcript',
    has_template: false,
    template_filename: '',
    program_requirements: [
      {
        id: 1,
        program: 'p1',
        program_name: 'Erasmus',
        is_required: true,
        required_from_status: null,
      },
    ],
    ...overrides,
  }
}

async function mountEditor() {
  const i18n = createI18n({ legacy: false, locale: 'en', messages: { en } })
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', name: 'Dashboard', component: { template: '<div />' } },
      { path: '/admin/documents', name: 'AdminDocuments', component: { template: '<div />' } },
      { path: '/admin/documents/:id', name: 'AdminDocumentTypeEdit', component: AdminDocumentTypeEdit },
    ],
  })
  await router.push({ name: 'AdminDocumentTypeEdit', params: { id: '9' } })
  // Mount via <router-view> so onBeforeRouteLeave registers correctly.
  const wrapper = mount(
    { template: '<router-view />' },
    {
      global: {
        plugins: [i18n, router],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    },
  )
  await flushPromises()
  return { wrapper, i18n, router }
}

describe('AdminDocumentTypeEdit', () => {
  beforeEach(() => {
    mockErrorToast.mockClear()
    mockSuccessToast.mockClear()
    mockConfirm.mockReset()
    mockConfirm.mockResolvedValue(true)
    mockPatch.mockReset()
    mockPatch.mockResolvedValue({
      data: mockDocumentTypePayload({ program_requirements: [] }),
    })
    mockPut.mockReset()
    mockPut.mockResolvedValue({
      data: { active: true, filter: {}, labels: {}, added: 0, matched: 0, already_listed: 0 },
    })
    mockGet.mockImplementation((url) => {
      if (url === '/api/document-types/9/') {
        return Promise.resolve({ data: mockDocumentTypePayload() })
      }
      if (url.startsWith('/api/programs/')) {
        return Promise.resolve({ data: { results: [{ id: 'p1', name: 'Erasmus' }] } })
      }
      if (url === '/api/document-types/merge-fields/') {
        return Promise.resolve({
          data: {
            fields: [
              { name: 'StudentName', group: 'student', description: 'Full name' },
              { name: 'ProgramName', group: 'program', description: 'Program title' },
              { name: 'ApplicationId', group: 'application', description: 'Application id' },
            ],
          },
        })
      }
      if (url === '/api/document-types/file-type-families/') {
        return Promise.resolve({
          data: {
            results: [
              { id: 1, slug: 'pdf', name: 'PDF', extensions: 'pdf', aliases: '' },
              { id: 2, slug: 'image', name: 'Image', extensions: 'jpg,png', aliases: 'photo' },
            ],
          },
        })
      }
      if (url === '/api/document-types/9/prefill-students/filter-options/') {
        return Promise.resolve({
          data: {
            domains: ['example.edu'],
            unidades: [{ id: 'u1', name: 'Campus North' }],
            schools: [{ id: 's1', name: 'Engineering', unidad_id: 'u1' }],
          },
        })
      }
      if (url === '/api/document-types/9/prefill-students/active-filters/') {
        return Promise.resolve({
          data: { active: false, filter: null, labels: {} },
        })
      }
      if (url === '/api/document-types/9/prefill-students/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url.startsWith('/api/document-types/9/prefill-students/candidates/')) {
        return Promise.resolve({ data: { results: [] } })
      }
      return Promise.resolve({ data: {} })
    })
    mockPost.mockResolvedValue({ data: { added: 0, already_listed: 0, not_found: [] } })
    mockDelete.mockResolvedValue({})
  })

  it('shows a required-from select instead of a required checkbox', async () => {
    const { wrapper, i18n } = await mountEditor()
    const select = wrapper.get('[data-testid="admin-document-required-from"]')
    expect(select.element.value).toBe('submitted')
    expect(select.text()).toContain(i18n.global.t('adminDocuments.req.optionalThroughout'))
    expect(wrapper.find('[data-testid="admin-document-requirements"] input.form-check-input').exists()).toBe(false)
  })

  it('opens identity, template, and workflow by default; keeps instructions and constraints collapsed', async () => {
    const { wrapper } = await mountEditor()

    expect(
      wrapper
        .get('[data-testid="admin-document-section-identity"] [data-testid="collapsible-card-toggle"]')
        .attributes('aria-expanded'),
    ).toBe('true')
    expect(
      wrapper
        .get('[data-testid="admin-document-section-template"] [data-testid="collapsible-card-toggle"]')
        .attributes('aria-expanded'),
    ).toBe('true')
    expect(
      wrapper
        .get('[data-testid="admin-document-requirements"] [data-testid="collapsible-card-toggle"]')
        .attributes('aria-expanded'),
    ).toBe('true')
    expect(
      wrapper
        .get('[data-testid="admin-document-section-instructions"] [data-testid="collapsible-card-toggle"]')
        .attributes('aria-expanded'),
    ).toBe('false')
    expect(
      wrapper
        .get('[data-testid="admin-document-section-constraints"] [data-testid="collapsible-card-toggle"]')
        .attributes('aria-expanded'),
    ).toBe('false')
    expect(wrapper.find('[data-testid="admin-document-section-instructions"] [data-testid="collapsible-card-panel"]').exists()).toBe(
      false,
    )
  })

  it('opens merge fields when a template is attached; keeps nested groups collapsed until toggled', async () => {
    mockGet.mockImplementation((url) => {
      if (url === '/api/document-types/9/') {
        return Promise.resolve({
          data: mockDocumentTypePayload({
            has_template: true,
            template_filename: 'letter.docx',
            program_requirements: [],
          }),
        })
      }
      if (url.startsWith('/api/programs/')) {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/document-types/merge-fields/') {
        return Promise.resolve({
          data: {
            fields: [
              { name: 'StudentName', group: 'student', description: 'Full name' },
              { name: 'ProgramName', group: 'program', description: 'Program title' },
            ],
          },
        })
      }
      if (url === '/api/document-types/file-type-families/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/document-types/9/prefill-students/') {
        return Promise.resolve({ data: { results: [] } })
      }
      return Promise.resolve({ data: {} })
    })

    const { wrapper } = await mountEditor()

    const mergeToggle = wrapper.get(
      '[data-testid="admin-document-section-merge-fields"] [data-testid="collapsible-card-toggle"]',
    )
    expect(mergeToggle.attributes('aria-expanded')).toBe('true')
    expect(wrapper.get('[data-testid="admin-document-section-merge-fields"]').text()).toContain('2')

    const studentGroup = wrapper.get('[data-testid="admin-document-merge-group-student"]')
    expect(studentGroup.find('[data-testid="collapsible-card-toggle"]').attributes('aria-expanded')).toBe(
      'false',
    )
    expect(studentGroup.find('[data-testid="collapsible-card-panel"]').exists()).toBe(false)

    await studentGroup.find('[data-testid="collapsible-card-toggle"]').trigger('click')
    expect(studentGroup.find('[data-testid="collapsible-card-panel"]').exists()).toBe(true)
    expect(studentGroup.text()).toContain('StudentName')
  })

  it('keeps merge fields collapsed when no template is attached', async () => {
    const { wrapper } = await mountEditor()
    expect(
      wrapper
        .get('[data-testid="admin-document-section-merge-fields"] [data-testid="collapsible-card-toggle"]')
        .attributes('aria-expanded'),
    ).toBe('false')
  })

  it('shows prefill students section with empty state and bulk add result', async () => {
    mockGet.mockImplementation((url) => {
      if (url === '/api/document-types/9/') {
        return Promise.resolve({ data: mockDocumentTypePayload({ program_requirements: [] }) })
      }
      if (url.startsWith('/api/programs/')) {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/document-types/merge-fields/') {
        return Promise.resolve({ data: { fields: [] } })
      }
      if (url === '/api/document-types/file-type-families/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/document-types/9/prefill-students/') {
        return Promise.resolve({
          data: {
            results: [
              {
                id: 7,
                full_name: 'Ana Lopez',
                email: 'ana.lopez@example.com',
                matricula: 'A01234567',
              },
            ],
          },
        })
      }
      if (url.startsWith('/api/document-types/9/prefill-students/candidates/')) {
        return Promise.resolve({
          data: {
            results: [
              {
                id: 8,
                full_name: 'Bruno Diaz',
                email: 'bruno.diaz@example.com',
                matricula: 'A07654321',
                already_listed: false,
              },
            ],
          },
        })
      }
      return Promise.resolve({ data: {} })
    })
    mockPost.mockResolvedValue({
      data: { added: 1, already_listed: 0, not_found: ['missing@example.com'] },
    })

    const { wrapper, i18n } = await mountEditor()
    const section = wrapper.get('[data-testid="admin-document-section-prefill-students"]')
    expect(section.text()).toContain(i18n.global.t('adminDocuments.sections.prefillStudents'))
    expect(wrapper.find('[data-testid="admin-prefill-student-list"]').text()).toContain('Ana Lopez')

    await wrapper.get('[data-testid="admin-prefill-bulk-text"]').setValue('bruno.diaz@example.com\nmissing@example.com')
    await wrapper.get('[data-testid="admin-prefill-bulk-submit"]').trigger('click')
    await flushPromises()
    expect(mockPost).toHaveBeenCalledWith(
      '/api/document-types/9/prefill-students/bulk/',
      expect.objectContaining({ text: 'bruno.diaz@example.com\nmissing@example.com' }),
    )
    const result = wrapper.get('[data-testid="admin-prefill-bulk-result"]')
    expect(result.text()).toContain('missing@example.com')
  })

  it('renders a preview button per listed student and downloads with ?student=', async () => {
    mockGet.mockImplementation((url, config) => {
      if (url === '/api/document-types/9/') {
        return Promise.resolve({
          data: mockDocumentTypePayload({
            program_requirements: [],
            slug: 'transcript',
            name: 'Transcript',
          }),
        })
      }
      if (url.startsWith('/api/programs/')) {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/document-types/merge-fields/') {
        return Promise.resolve({ data: { fields: [] } })
      }
      if (url === '/api/document-types/file-type-families/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/document-types/9/prefill-students/') {
        return Promise.resolve({
          data: {
            results: [
              {
                id: 'stu-7',
                username: 'ana.lopez',
                full_name: 'Ana Lopez',
                email: 'ana.lopez@example.com',
                matricula: 'A01234567',
              },
            ],
          },
        })
      }
      if (url === '/api/document-types/9/download-template/') {
        expect(config).toEqual(
          expect.objectContaining({
            params: { student: 'stu-7' },
            responseType: 'blob',
          }),
        )
        return Promise.resolve({
          data: new Blob(['docx'], {
            type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
          }),
          headers: {
            'content-type':
              'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'content-disposition': 'attachment; filename="transcript_ana.lopez.docx"',
          },
        })
      }
      return Promise.resolve({ data: {} })
    })

    const clickSpy = vi.fn()
    const origCreate = document.createElement.bind(document)
    vi.spyOn(document, 'createElement').mockImplementation((tag) => {
      const el = origCreate(tag)
      if (tag === 'a') el.click = clickSpy
      return el
    })
    global.URL.createObjectURL = vi.fn(() => 'blob:preview')
    global.URL.revokeObjectURL = vi.fn()

    const { wrapper, i18n } = await mountEditor()
    const previewBtn = wrapper.get('[data-testid="admin-prefill-student-preview"]')
    expect(previewBtn.text()).toContain(i18n.global.t('adminDocuments.prefillStudents.preview'))
    expect(previewBtn.attributes('aria-label')).toBe(
      i18n.global.t('adminDocuments.prefillStudents.previewAria', { name: 'Ana Lopez' }),
    )

    await previewBtn.trigger('click')
    await flushPromises()
    expect(mockGet).toHaveBeenCalledWith(
      '/api/document-types/9/download-template/',
      expect.objectContaining({
        params: { student: 'stu-7' },
        responseType: 'blob',
      }),
    )
    expect(clickSpy).toHaveBeenCalled()
    document.createElement.mockRestore()
  })

  it('shows pending-template hint and uploads on Guardar when a file is selected', async () => {
    mockPost.mockResolvedValue({
      data: {
        has_template: true,
        template_filename: 'mobility.docx',
      },
    })
    const { wrapper, i18n } = await mountEditor()
    const input = wrapper.get('[data-testid="admin-document-type-template"]')
    const file = new File(['docx'], 'mobility.docx', {
      type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    })
    Object.defineProperty(input.element, 'files', { value: [file], configurable: true })
    await input.trigger('change')
    expect(wrapper.get('[data-testid="admin-document-template-pending"]').text()).toContain(
      'mobility.docx',
    )

    await wrapper.get('[data-testid="admin-document-type-save"]').trigger('click')
    await flushPromises()
    expect(mockPatch).toHaveBeenCalledWith(
      '/api/document-types/9/',
      expect.objectContaining({ name: 'Transcript' }),
    )
    expect(mockPost).toHaveBeenCalledWith(
      '/api/document-types/9/upload-template/',
      expect.any(FormData),
    )
    expect(mockSuccessToast).toHaveBeenCalledWith(
      i18n.global.t('adminDocuments.toastSavedWithTemplate'),
    )
    expect(wrapper.find('[data-testid="admin-document-template-pending"]').exists()).toBe(false)
  })

  it('warns that the template was NOT saved when upload fails after Guardar', async () => {
    mockPost.mockRejectedValue(new Error('upload failed'))
    const { wrapper, i18n } = await mountEditor()
    const input = wrapper.get('[data-testid="admin-document-type-template"]')
    const file = new File(['docx'], 'broken.docx', {
      type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    })
    Object.defineProperty(input.element, 'files', { value: [file], configurable: true })
    await input.trigger('change')
    await wrapper.get('[data-testid="admin-document-type-save"]').trigger('click')
    await flushPromises()
    expect(mockPatch).toHaveBeenCalled()
    expect(mockErrorToast).toHaveBeenCalledWith(
      i18n.global.t('adminDocuments.templateNotSavedAfterSave'),
    )
    expect(wrapper.find('[data-testid="admin-document-template-pending"]').exists()).toBe(true)
  })

  it('confirms before leaving when a template file is pending upload', async () => {
    mockConfirm.mockResolvedValue(false)
    const { wrapper, i18n, router } = await mountEditor()
    const input = wrapper.get('[data-testid="admin-document-type-template"]')
    const file = new File(['docx'], 'pending.docx', {
      type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    })
    Object.defineProperty(input.element, 'files', { value: [file], configurable: true })
    await input.trigger('change')

    await router.push({ name: 'AdminDocuments' })
    await flushPromises()
    expect(mockConfirm).toHaveBeenCalledWith(
      expect.objectContaining({
        title: i18n.global.t('adminDocuments.templatePendingLeaveTitle'),
        message: i18n.global.t('adminDocuments.templatePendingLeaveMessage'),
      }),
    )
    expect(router.currentRoute.value.name).toBe('AdminDocumentTypeEdit')
  })

  it('shows an error toast when prefill preview download fails', async () => {
    mockGet.mockImplementation((url) => {
      if (url === '/api/document-types/9/') {
        return Promise.resolve({ data: mockDocumentTypePayload({ program_requirements: [] }) })
      }
      if (url.startsWith('/api/programs/')) {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/document-types/merge-fields/') {
        return Promise.resolve({ data: { fields: [] } })
      }
      if (url === '/api/document-types/file-type-families/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/document-types/9/prefill-students/filter-options/') {
        return Promise.resolve({ data: { domains: [], unidades: [], schools: [] } })
      }
      if (url === '/api/document-types/9/prefill-students/') {
        return Promise.resolve({
          data: {
            results: [
              {
                id: 'stu-7',
                full_name: 'Ana Lopez',
                email: 'ana.lopez@example.com',
                matricula: 'A01234567',
              },
            ],
          },
        })
      }
      if (url === '/api/document-types/9/download-template/') {
        return Promise.reject(new Error('preview failed'))
      }
      return Promise.resolve({ data: {} })
    })

    const { wrapper, i18n } = await mountEditor()
    await wrapper.get('[data-testid="admin-prefill-student-preview"]').trigger('click')
    await flushPromises()
    expect(mockErrorToast).toHaveBeenCalledWith(
      i18n.global.t('adminDocuments.prefillStudents.previewError'),
    )
  })

  async function openPrefillSection(wrapper) {
    const section = wrapper.get('[data-testid="admin-document-section-prefill-students"]')
    const toggle = section.get('[data-testid="collapsible-card-toggle"]')
    if (toggle.attributes('aria-expanded') !== 'true') {
      await toggle.trigger('click')
      await flushPromises()
    }
  }

  it('previews filter matches then confirms add without sending id lists', async () => {
    mockPost.mockImplementation((url, body) => {
      if (url === '/api/document-types/9/prefill-students/filter-preview/') {
        expect(body).toEqual({ domain: 'example.edu', unidad_id: 'u1' })
        expect(body).not.toHaveProperty('user_ids')
        expect(body).not.toHaveProperty('ids')
        return Promise.resolve({
          data: {
            filter: body,
            matched: 3,
            new_count: 2,
            already_listed: 1,
            samples: [
              {
                id: 'stu-8',
                full_name: 'Bruno Diaz',
                email: 'bruno.diaz@example.edu',
                matricula: 'A07654321',
              },
            ],
          },
        })
      }
      if (url === '/api/document-types/9/prefill-students/filter-confirm/') {
        expect(body).toEqual({ domain: 'example.edu', unidad_id: 'u1' })
        expect(body).not.toHaveProperty('user_ids')
        return Promise.resolve({
          data: {
            filter: body,
            matched: 3,
            added: 2,
            already_listed: 1,
            active_filters: {
              active: true,
              filter: { domain: 'example.edu', unidad_id: 'u1', school_id: null },
              labels: { domain: 'example.edu', unidad: 'Campus North', school: '' },
            },
          },
        })
      }
      return Promise.resolve({ data: {} })
    })

    const { wrapper, i18n } = await mountEditor()
    await openPrefillSection(wrapper)
    expect(wrapper.find('[data-testid="admin-prefill-filter-panel"]').exists()).toBe(true)

    await wrapper.get('[data-testid="admin-prefill-filter-domain"]').setValue('example.edu')
    await wrapper.get('[data-testid="admin-prefill-filter-unidad"]').setValue('u1')
    await wrapper.get('[data-testid="admin-prefill-filter-preview"]').trigger('click')
    await flushPromises()

    const preview = wrapper.get('[data-testid="admin-prefill-filter-preview-result"]')
    expect(preview.text()).toContain('Bruno Diaz')
    expect(preview.text()).toContain(
      i18n.global.t('adminDocuments.prefillStudents.filterPreviewSummary', {
        matched: 3,
        newCount: 2,
        already: 1,
      }),
    )

    await wrapper.get('[data-testid="admin-prefill-filter-confirm"]').trigger('click')
    await flushPromises()
    expect(mockConfirm).toHaveBeenCalled()
    expect(mockPost).toHaveBeenCalledWith(
      '/api/document-types/9/prefill-students/filter-confirm/',
      { domain: 'example.edu', unidad_id: 'u1' },
    )
    expect(mockSuccessToast).toHaveBeenCalledWith(
      i18n.global.t('adminDocuments.prefillStudents.filterToastAdded', { added: 2 }),
    )
    expect(wrapper.find('[data-testid="admin-prefill-active-filters"]').exists()).toBe(true)
    expect(wrapper.get('[data-testid="admin-prefill-active-filters-summary"]').text()).toContain(
      'example.edu',
    )
  })

  it('disables filter confirm until preview reports new students', async () => {
    mockPost.mockResolvedValue({
      data: { matched: 1, new_count: 0, already_listed: 1, samples: [] },
    })
    const { wrapper } = await mountEditor()
    await openPrefillSection(wrapper)
    const confirmBtn = wrapper.get('[data-testid="admin-prefill-filter-confirm"]')
    expect(confirmBtn.attributes('disabled')).toBeDefined()

    await wrapper.get('[data-testid="admin-prefill-filter-preview"]').trigger('click')
    await flushPromises()
    expect(confirmBtn.attributes('disabled')).toBeDefined()
    expect(mockPost).toHaveBeenCalledWith(
      '/api/document-types/9/prefill-students/filter-preview/',
      {},
    )
  })

  it('shows active filters indicator and supports edit and clear', async () => {
    mockGet.mockImplementation((url) => {
      if (url === '/api/document-types/9/') {
        return Promise.resolve({ data: mockDocumentTypePayload({ program_requirements: [] }) })
      }
      if (url.startsWith('/api/programs/')) {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/document-types/merge-fields/') {
        return Promise.resolve({ data: { fields: [] } })
      }
      if (url === '/api/document-types/file-type-families/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/document-types/9/prefill-students/filter-options/') {
        return Promise.resolve({
          data: {
            domains: ['example.edu'],
            unidades: [{ id: 'u1', name: 'Campus North' }],
            schools: [{ id: 's1', name: 'Engineering', unidad_id: 'u1' }],
          },
        })
      }
      if (url === '/api/document-types/9/prefill-students/active-filters/') {
        return Promise.resolve({
          data: {
            active: true,
            filter: { domain: 'example.edu', unidad_id: 'u1', school_id: 's1' },
            labels: { domain: 'example.edu', unidad: 'Campus North', school: 'Engineering' },
          },
        })
      }
      if (url === '/api/document-types/9/prefill-students/') {
        return Promise.resolve({ data: { results: [] } })
      }
      return Promise.resolve({ data: {} })
    })
    mockDelete.mockResolvedValue({
      data: { active: false, filter: null, labels: {} },
    })

    const { wrapper, i18n } = await mountEditor()
    await openPrefillSection(wrapper)

    const banner = wrapper.get('[data-testid="admin-prefill-active-filters"]')
    expect(banner.text()).toContain(i18n.global.t('adminDocuments.prefillStudents.activeFiltersTitle'))
    expect(wrapper.get('[data-testid="admin-prefill-active-filters-summary"]').text()).toContain(
      'Campus North',
    )
    expect(wrapper.get('[data-testid="admin-prefill-active-filters-summary"]').text()).toContain(
      'Engineering',
    )

    await wrapper.get('[data-testid="admin-prefill-active-filters-edit"]').trigger('click')
    await flushPromises()
    expect(wrapper.get('[data-testid="admin-prefill-filter-domain"]').element.value).toBe(
      'example.edu',
    )
    expect(wrapper.get('[data-testid="admin-prefill-filter-unidad"]').element.value).toBe('u1')
    expect(wrapper.get('[data-testid="admin-prefill-filter-school"]').element.value).toBe('s1')

    await wrapper.get('[data-testid="admin-prefill-active-filters-clear"]').trigger('click')
    await flushPromises()
    expect(mockConfirm).toHaveBeenCalled()
    expect(mockDelete).toHaveBeenCalledWith(
      '/api/document-types/9/prefill-students/active-filters/',
    )
    expect(wrapper.find('[data-testid="admin-prefill-active-filters"]').exists()).toBe(false)
    expect(mockSuccessToast).toHaveBeenCalledWith(
      i18n.global.t('adminDocuments.prefillStudents.activeFiltersCleared'),
    )
  })

  it('saves active filters from the filter panel without requiring preview matches', async () => {
    mockPut.mockResolvedValue({
      data: {
        active: true,
        filter: { domain: 'example.edu', unidad_id: null, school_id: null },
        labels: { domain: 'example.edu', unidad: '', school: '' },
        matched: 2,
        added: 1,
        already_listed: 1,
      },
    })
    const { wrapper, i18n } = await mountEditor()
    await openPrefillSection(wrapper)
    await wrapper.get('[data-testid="admin-prefill-filter-domain"]').setValue('example.edu')
    await wrapper.get('[data-testid="admin-prefill-filter-save-active"]').trigger('click')
    await flushPromises()
    expect(mockConfirm).toHaveBeenCalled()
    expect(mockPut).toHaveBeenCalledWith(
      '/api/document-types/9/prefill-students/active-filters/',
      { domain: 'example.edu' },
    )
    expect(wrapper.find('[data-testid="admin-prefill-active-filters"]').exists()).toBe(true)
    expect(mockSuccessToast).toHaveBeenCalledWith(
      i18n.global.t('adminDocuments.prefillStudents.filterSaveActiveToast', { added: 1 }),
    )
  })
})
