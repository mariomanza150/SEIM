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
})
