/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import PartnerPortal from './PartnerPortal.vue'
import api from '@/services/api'
import i18n, { setAppLocale } from '@/i18n'

vi.mock('@/services/api', () => ({
  default: { get: vi.fn() },
}))

describe('PartnerPortal', () => {
  beforeEach(() => {
    setAppLocale('en')
    vi.clearAllMocks()
    api.get.mockImplementation((url) => {
      if (String(url).includes('/api/partner/agreements/')) {
        return Promise.resolve({
          data: { results: [{ id: 'ag-1', title: 'Bilateral MoU', partner_institution_name: 'TU Berlin', status: 'active' }] },
        })
      }
      if (String(url).includes('/api/partner/applications/')) {
        return Promise.resolve({
          data: {
            results: [
              {
                id: 'app-1',
                student_display_name: 'Ada L.',
                program_name: 'Erasmus',
                status_name: 'submitted',
                document_checklist: { complete: false, items: [] },
              },
            ],
          },
        })
      }
      return Promise.reject(new Error(url))
    })
  })

  it('renders agreements and applicants', async () => {
    const wrapper = mount(PartnerPortal, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' }, PageHeader: { template: '<div><slot /></div>' } },
      },
    })
    await flushPromises()
    expect(wrapper.find('[data-testid="partner-portal-page"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('Bilateral MoU')
    expect(wrapper.text()).toContain('Ada L.')
    expect(wrapper.text()).toContain('Erasmus')
  })
})
