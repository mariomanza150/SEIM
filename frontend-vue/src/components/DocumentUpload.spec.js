/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import DocumentUpload from './DocumentUpload.vue'
import api from '@/services/api'
import i18n, { setAppLocale } from '@/i18n'

vi.mock('@/services/api', () => ({
  default: { get: vi.fn(), post: vi.fn() },
}))

const toastSuccess = vi.fn()
const toastError = vi.fn()

vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: toastSuccess, error: toastError }),
}))

describe('DocumentUpload', () => {
  beforeEach(() => {
    localStorage.clear()
    setAppLocale('en')
    vi.clearAllMocks()
    toastSuccess.mockClear()
    toastError.mockClear()
    api.get.mockResolvedValue({ data: { results: [] } })
    api.post.mockResolvedValue({ data: { id: 'doc-new' } })
  })

  it('renders translated card title and primary action', async () => {
    const wrapper = mount(DocumentUpload, {
      props: { applicationId: '1' },
      global: { plugins: [i18n] },
    })
    await flushPromises()
    expect(wrapper.text()).toContain('Upload document')
    expect(wrapper.find('[data-testid="document-upload-btn"]').text()).toContain('Upload')
  })

  it('loads every document-type page so required types are not dropped', async () => {
    api.get
      .mockResolvedValueOnce({
        data: {
          count: 21,
          next: 'http://localhost:8020/api/document-types/?page=2&page_size=100',
          results: [{ id: 't1', name: 'Kardex Oficial' }],
        },
      })
      .mockResolvedValueOnce({
        data: {
          count: 21,
          next: null,
          results: [{ id: 't2', name: 'transcript', description: 'Academic transcript' }],
        },
      })
    const wrapper = mount(DocumentUpload, {
      props: { applicationId: '1' },
      global: { plugins: [i18n] },
    })
    await flushPromises()
    const labels = wrapper.findAll('[data-testid="document-type-select"] option').map((o) => o.text())
    expect(labels).toContain('Academic transcript')
    expect(labels).not.toContain('transcript')
    expect(api.get).toHaveBeenCalledWith('/api/document-types/?page_size=100')
    expect(api.get).toHaveBeenCalledWith('/api/document-types/?page=2&page_size=100')
  })

  it('prefills the type select from preselectedTypeId using checklist gaps', async () => {
    const checklist = {
      required_count: 2,
      approved_count: 0,
      items: [
        {
          document_type_id: 11,
          name: 'Pasaporte',
          slug: 'pasaporte_vigente',
          status: 'missing',
          accepted_extensions: 'pdf,jpg',
          max_file_size_mb: 5,
        },
        {
          document_type_id: 12,
          name: 'Kardex',
          slug: 'kardex_oficial',
          status: 'approved',
        },
      ],
    }
    const wrapper = mount(DocumentUpload, {
      props: {
        applicationId: '1',
        checklist,
        preselectedTypeId: 11,
      },
      global: { plugins: [i18n] },
    })
    await flushPromises()
    const select = wrapper.find('[data-testid="document-type-select"]')
    expect(select.element.value).toBe('11')
    const labels = select.findAll('option').map((o) => o.text())
    expect(labels).toContain('Pasaporte')
    expect(labels).not.toContain('Kardex')
  })

  it('hides file field until a document type is selected, then updates accept hint', async () => {
    api.get.mockResolvedValue({
      data: {
        results: [
          {
            id: 1,
            name: 'Passport',
            accepted_extensions: 'pdf,jpg',
            max_file_size_mb: 5,
            file_type_families: [],
          },
          {
            id: 2,
            name: 'Motivation letter',
            accepted_extensions: 'pdf,docx',
            max_file_size_mb: null,
            file_type_families: [],
          },
        ],
      },
    })
    const wrapper = mount(DocumentUpload, {
      props: { applicationId: '1' },
      global: { plugins: [i18n] },
    })
    await flushPromises()

    expect(wrapper.find('[data-testid="document-file-field"]').exists()).toBe(false)
    expect(wrapper.find('[data-testid="document-accepted-hint"]').exists()).toBe(false)

    await wrapper.find('[data-testid="document-type-select"]').setValue('1')
    expect(wrapper.find('[data-testid="document-file-field"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="document-file-input"]').attributes('accept')).toBe(
      '.pdf,.jpg',
    )
    expect(wrapper.find('[data-testid="document-accepted-hint"]').text()).toBe(
      'Accepted: PDF, JPG (max 5MB)',
    )

    await wrapper.find('[data-testid="document-type-select"]').setValue('2')
    expect(wrapper.find('[data-testid="document-file-input"]').attributes('accept')).toBe(
      '.pdf,.docx',
    )
    expect(wrapper.find('[data-testid="document-accepted-hint"]').text()).toBe(
      'Accepted: PDF, DOCX (max 10MB)',
    )

    await wrapper.find('[data-testid="document-type-select"]').setValue('')
    expect(wrapper.find('[data-testid="document-file-field"]').exists()).toBe(false)
  })

  it('rejects disallowed file types client-side before upload', async () => {
    api.get.mockResolvedValue({
      data: {
        results: [
          {
            id: 1,
            name: 'Passport',
            accepted_extensions: 'pdf',
            max_file_size_mb: 5,
            file_type_families: [],
          },
        ],
      },
    })
    api.post = vi.fn()
    const wrapper = mount(DocumentUpload, {
      props: { applicationId: '1' },
      global: { plugins: [i18n] },
    })
    await flushPromises()
    await wrapper.find('[data-testid="document-type-select"]').setValue('1')
    const input = wrapper.find('[data-testid="document-file-input"]')
    const badFile = new File(['x'], 'scan.docx', {
      type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    })
    Object.defineProperty(input.element, 'files', { value: [badFile], configurable: true })
    await input.trigger('change')
    expect(wrapper.find('.invalid-feedback').text()).toContain('not allowed')
    expect(api.post).not.toHaveBeenCalled()
  })

  it('uploads a valid file and emits uploaded', async () => {
    api.get.mockResolvedValue({
      data: {
        results: [
          {
            id: 3,
            name: 'Identity document',
            accepted_extensions: 'pdf',
            max_file_size_mb: 5,
            file_type_families: [],
          },
        ],
      },
    })
    const wrapper = mount(DocumentUpload, {
      props: { applicationId: 'app-9' },
      global: { plugins: [i18n] },
    })
    await flushPromises()
    await wrapper.find('[data-testid="document-type-select"]').setValue('3')
    const input = wrapper.find('[data-testid="document-file-input"]')
    const file = new File(['%PDF-1.4'], 'identity.pdf', { type: 'application/pdf' })
    Object.defineProperty(input.element, 'files', { value: [file], configurable: true })
    await input.trigger('change')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()
    expect(api.post).toHaveBeenCalled()
    const [url, formData, config] = api.post.mock.calls[0]
    expect(url).toBe('/api/documents/')
    expect(formData).toBeInstanceOf(FormData)
    expect(formData.get('application')).toBe('app-9')
    expect(formData.get('type')).toBe('3')
    expect(formData.get('file')).toBe(file)
    expect(config.headers['Content-Type']).toBe('multipart/form-data')
    expect(toastSuccess).toHaveBeenCalled()
    expect(wrapper.emitted('uploaded')).toBeTruthy()
  })

  it('surfaces server validation errors when upload fails', async () => {
    api.get.mockResolvedValue({
      data: {
        results: [
          {
            id: 3,
            name: 'Identity document',
            accepted_extensions: 'pdf',
            max_file_size_mb: 5,
            file_type_families: [],
          },
        ],
      },
    })
    api.post.mockRejectedValue({
      response: { data: { file: ['File too large for this document type.'] } },
    })
    const wrapper = mount(DocumentUpload, {
      props: { applicationId: 'app-9' },
      global: { plugins: [i18n] },
    })
    await flushPromises()
    await wrapper.find('[data-testid="document-type-select"]').setValue('3')
    const input = wrapper.find('[data-testid="document-file-input"]')
    const file = new File(['%PDF-1.4'], 'identity.pdf', { type: 'application/pdf' })
    Object.defineProperty(input.element, 'files', { value: [file], configurable: true })
    await input.trigger('change')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()
    expect(wrapper.text()).toContain('File too large for this document type.')
    expect(toastError).toHaveBeenCalled()
  })

  it('requires type and file before submitting', async () => {
    api.get.mockResolvedValue({
      data: {
        results: [
          {
            id: 3,
            name: 'Identity document',
            accepted_extensions: 'pdf',
            max_file_size_mb: 5,
            file_type_families: [],
          },
        ],
      },
    })
    const wrapper = mount(DocumentUpload, {
      props: { applicationId: 'app-9' },
      global: { plugins: [i18n] },
    })
    await flushPromises()
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()
    expect(api.post).not.toHaveBeenCalled()
    expect(wrapper.text()).toContain(i18n.global.t('documentUpload.typeRequired'))

    await wrapper.find('[data-testid="document-type-select"]').setValue('3')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()
    expect(wrapper.text()).toContain(i18n.global.t('documentUpload.fileRequired'))
    expect(api.post).not.toHaveBeenCalled()
  })

  it('shows nothing-to-upload when checklist gaps are empty', async () => {
    const wrapper = mount(DocumentUpload, {
      props: {
        applicationId: 'app-9',
        checklist: {
          required_count: 1,
          items: [
            {
              document_type_id: 11,
              name: 'Identity document',
              slug: 'identity_document',
              status: 'approved',
            },
          ],
        },
      },
      global: { plugins: [i18n] },
    })
    await flushPromises()
    expect(wrapper.find('[data-testid="document-upload-empty"]').exists()).toBe(true)
    expect(api.get).not.toHaveBeenCalled()
  })

  it('focusUploadForm applies preselected type and focuses the type select', async () => {
    api.get.mockResolvedValue({
      data: {
        results: [
          {
            id: 4,
            name: 'Proof of enrollment',
            accepted_extensions: 'pdf',
            max_file_size_mb: 5,
            file_type_families: [],
          },
        ],
      },
    })
    const wrapper = mount(DocumentUpload, {
      props: { applicationId: 'app-9', preselectedTypeId: 4 },
      attachTo: document.body,
      global: { plugins: [i18n] },
    })
    await flushPromises()
    wrapper.vm.focusUploadForm()
    await flushPromises()
    expect(wrapper.find('[data-testid="document-type-select"]').element.value).toBe('4')
    wrapper.unmount()
  })

  it('toasts when document types fail to load', async () => {
    api.get.mockRejectedValue(new Error('network'))
    mount(DocumentUpload, {
      props: { applicationId: 'app-9' },
      global: { plugins: [i18n] },
    })
    await flushPromises()
    expect(toastError).toHaveBeenCalledWith(i18n.global.t('documentUpload.toastTypesError'))
  })
})
