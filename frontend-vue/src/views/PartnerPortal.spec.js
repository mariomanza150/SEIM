/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import PartnerPortal from './PartnerPortal.vue'
import api from '@/services/api'
import i18n, { setAppLocale } from '@/i18n'

vi.mock('@/services/api', () => ({
  default: { get: vi.fn(), post: vi.fn() },
}))

describe('PartnerPortal', () => {
  beforeEach(() => {
    setAppLocale('en')
    vi.clearAllMocks()
    api.get.mockImplementation((url) => {
      if (String(url).includes('/api/partner/agreements/') && String(url).includes('/documents/')) {
        return Promise.resolve({
          data: [{ id: 'd1', title: 'Demo signed Erasmus framework', category: 'signed_copy' }],
        })
      }
      if (String(url).includes('/api/partner/agreements/') && String(url).includes('/comments/')) {
        return Promise.resolve({
          data: [{ id: 'ac1', text: 'Renewal timing?', author_display_name: 'Coordinator' }],
        })
      }
      if (String(url).includes('/api/partner/agreements/')) {
        return Promise.resolve({
          data: { results: [{ id: 'ag-1', title: 'Bilateral MoU', partner_institution_name: 'TU Berlin', status: 'active' }] },
        })
      }
      if (String(url).includes('/api/partner/applications/') && String(url).includes('/comments/')) {
        return Promise.resolve({
          data: [{ id: 'c1', text: 'Hello partner', author_display_name: 'Coordinator' }],
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
    expect(wrapper.find('[data-testid="partner-agreement-status"]').text()).toBe('Active')
    expect(wrapper.find('[data-testid="partner-application-status"]').text()).toBe('Submitted')
    await wrapper.find('[data-testid="partner-view-documents"]').trigger('click')
    await flushPromises()
    expect(wrapper.find('[data-testid="partner-document-category"]').text()).toBe('Signed copy')
  })

  it('opens a public message thread for an applicant', async () => {
    api.post.mockResolvedValue({
      data: { id: 'c2', text: 'Nomination received', author_display_name: 'Partner' },
    })
    const wrapper = mount(PartnerPortal, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' }, PageHeader: { template: '<div><slot /></div>' } },
      },
    })
    await flushPromises()
    await wrapper.find('[data-testid="partner-open-thread"]').trigger('click')
    await flushPromises()
    expect(wrapper.find('[data-testid="partner-thread"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('Hello partner')
    await wrapper.find('[data-testid="partner-thread-text"]').setValue('Nomination received')
    await wrapper.find('[data-testid="partner-thread"]').find('form').trigger('submit')
    await flushPromises()
    expect(api.post).toHaveBeenCalledWith(
      '/api/partner/applications/app-1/comments/',
      { text: 'Nomination received' },
    )
    expect(wrapper.text()).toContain('Nomination received')
  })

  it('opens a public message thread for an agreement', async () => {
    api.post.mockResolvedValue({
      data: { id: 'ac2', text: 'We can sign in June', author_display_name: 'Partner' },
    })
    const wrapper = mount(PartnerPortal, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' }, PageHeader: { template: '<div><slot /></div>' } },
      },
    })
    await flushPromises()
    await wrapper.find('[data-testid="partner-open-agreement-thread"]').trigger('click')
    await flushPromises()
    expect(wrapper.find('[data-testid="partner-agreement-thread"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('Renewal timing?')
    await wrapper.find('[data-testid="partner-agreement-thread-text"]').setValue('We can sign in June')
    await wrapper.find('[data-testid="partner-agreement-thread"]').find('form').trigger('submit')
    await flushPromises()
    expect(api.post).toHaveBeenCalledWith(
      '/api/partner/agreements/ag-1/comments/',
      { text: 'We can sign in June' },
    )
    expect(wrapper.text()).toContain('We can sign in June')
  })
})
