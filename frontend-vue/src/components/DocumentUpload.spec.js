/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import DocumentUpload from './DocumentUpload.vue'
import api from '@/services/api'
import i18n, { setAppLocale } from '@/i18n'

vi.mock('@/services/api', () => ({
  default: { get: vi.fn() },
}))

vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: vi.fn(), error: vi.fn() }),
}))

describe('DocumentUpload', () => {
  beforeEach(() => {
    localStorage.clear()
    setAppLocale('en')
    vi.clearAllMocks()
    api.get.mockResolvedValue({ data: { results: [] } })
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
})
