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
})
