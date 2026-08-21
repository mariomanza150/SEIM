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
                status_name: 'nominated',
                partner_nomination_acknowledged_at: null,
                document_checklist: {
                  complete: false,
                  required_count: 1,
                  approved_count: 0,
                  items: [
                    { name: 'Official Transcript', status: 'missing', required: true, due_now: true },
                  ],
                },
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
    expect(wrapper.find('[data-testid="partner-application-status"]').text()).toBe('Nominated')
    await wrapper.find('[data-testid="partner-view-documents"]').trigger('click')
    await flushPromises()
    expect(wrapper.find('[data-testid="partner-document-category"]').text()).toBe('Signed copy')
  })

  it('shows a read-only applicant document checklist', async () => {
    const wrapper = mount(PartnerPortal, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' }, PageHeader: { template: '<div><slot /></div>' } },
      },
    })
    await flushPromises()
    await wrapper.find('[data-testid="partner-view-checklist"]').trigger('click')
    expect(wrapper.find('[data-testid="partner-checklist"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="partner-checklist-name"]').text()).toBe('Official Transcript')
    expect(wrapper.find('[data-testid="partner-checklist-status"]').text()).toBe('Missing')
    expect(wrapper.find('[data-testid="partner-checklist-summary"]').text()).toContain('Incomplete')
  })

  it('acknowledges a nominated applicant', async () => {
    api.post.mockResolvedValue({
      data: {
        id: 'app-1',
        status_name: 'nominated',
        partner_nomination_acknowledged_at: '2026-08-20T12:00:00Z',
      },
    })
    const wrapper = mount(PartnerPortal, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' }, PageHeader: { template: '<div><slot /></div>' } },
      },
    })
    await flushPromises()
    expect(wrapper.find('[data-testid="partner-ack-nomination"]').exists()).toBe(true)
    await wrapper.find('[data-testid="partner-ack-nomination"]').trigger('click')
    await flushPromises()
    expect(api.post).toHaveBeenCalledWith('/api/partner/applications/app-1/acknowledge-nomination/')
    expect(wrapper.find('[data-testid="partner-nomination-acked"]').exists()).toBe(true)
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

  it('uploads an agreement document from the docs panel', async () => {
    let docsPayload = [
      { id: 'd1', title: 'Demo signed Erasmus framework', category: 'signed_copy', file: '/media/old.pdf' },
    ]
    api.get.mockImplementation((url) => {
      if (String(url).includes('/api/partner/agreements/') && String(url).includes('/documents/')) {
        return Promise.resolve({ data: docsPayload })
      }
      if (String(url).includes('/api/partner/agreements/') && String(url).includes('/comments/')) {
        return Promise.resolve({ data: [] })
      }
      if (String(url).includes('/api/partner/agreements/')) {
        return Promise.resolve({
          data: { results: [{ id: 'ag-1', title: 'Bilateral MoU', partner_institution_name: 'TU Berlin', status: 'active' }] },
        })
      }
      if (String(url).includes('/api/partner/applications/')) {
        return Promise.resolve({ data: { results: [] } })
      }
      return Promise.reject(new Error(url))
    })
    api.post.mockImplementation(() => {
      const created = {
        id: 'd2',
        title: 'Partner signed',
        category: 'signed_copy',
        file: '/media/agreement_repository/signed.pdf',
      }
      docsPayload = [created, ...docsPayload]
      return Promise.resolve({ data: created })
    })
    const wrapper = mount(PartnerPortal, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' }, PageHeader: { template: '<div><slot /></div>' } },
      },
    })
    await flushPromises()
    await wrapper.find('[data-testid="partner-view-documents"]').trigger('click')
    await flushPromises()
    expect(wrapper.find('[data-testid="partner-doc-upload"]').exists()).toBe(true)
    await wrapper.find('[data-testid="partner-doc-title"]').setValue('Partner signed')
    const file = new File(['%PDF-1.4'], 'signed.pdf', { type: 'application/pdf' })
    const input = wrapper.find('[data-testid="partner-doc-file"]')
    Object.defineProperty(input.element, 'files', { value: [file] })
    await input.trigger('change')
    await wrapper.find('[data-testid="partner-doc-upload"]').find('form').trigger('submit')
    await flushPromises()
    expect(api.post).toHaveBeenCalled()
    const [url, body, config] = api.post.mock.calls.find((c) =>
      String(c[0]).includes('/documents/'),
    )
    expect(url).toBe('/api/partner/agreements/ag-1/documents/')
    expect(body).toBeInstanceOf(FormData)
    expect(body.get('supersedes')).toBeNull()
    expect(config.headers['Content-Type']).toBe('multipart/form-data')
    expect(wrapper.text()).toContain('Partner signed')
    expect(wrapper.find('[data-testid="partner-document-download"]').exists()).toBe(true)
  })

  it('lets a partner supersede the current signed copy', async () => {
    let docsPayload = [
      { id: 'd1', title: 'Demo signed Erasmus framework', category: 'signed_copy', file: '/media/old.pdf' },
      {
        id: 'd2',
        title: 'Updated signed',
        category: 'signed_copy',
        supersedes: 'd1',
        file: '/media/new.pdf',
      },
    ]
    api.get.mockImplementation((url, config) => {
      if (String(url).includes('/api/partner/agreements/') && String(url).includes('/documents/')) {
        const currentOnly = config?.params?.current_only === 'true'
        return Promise.resolve({
          data: currentOnly ? docsPayload.filter((r) => r.id === 'd2' || r.id === 'd3') : docsPayload,
        })
      }
      if (String(url).includes('/api/partner/agreements/') && String(url).includes('/comments/')) {
        return Promise.resolve({ data: [] })
      }
      if (String(url).includes('/api/partner/agreements/')) {
        return Promise.resolve({
          data: { results: [{ id: 'ag-1', title: 'Bilateral MoU', partner_institution_name: 'TU Berlin', status: 'active' }] },
        })
      }
      if (String(url).includes('/api/partner/applications/')) {
        return Promise.resolve({ data: { results: [] } })
      }
      return Promise.reject(new Error(url))
    })
    api.post.mockImplementation(() => {
      const created = {
        id: 'd3',
        title: 'Partner replacement',
        category: 'signed_copy',
        supersedes: 'd2',
        file: '/media/agreement_repository/v3.pdf',
      }
      docsPayload = [created, ...docsPayload]
      return Promise.resolve({ data: created })
    })
    const wrapper = mount(PartnerPortal, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' }, PageHeader: { template: '<div><slot /></div>' } },
      },
    })
    await flushPromises()
    await wrapper.find('[data-testid="partner-view-documents"]').trigger('click')
    await flushPromises()
    expect(wrapper.find('[data-testid="partner-document-superseded"]').exists()).toBe(true)
    expect(wrapper.findAll('[data-testid="partner-document-current"]').length).toBe(1)
    await wrapper.find('[data-testid="partner-document-supersede"]').trigger('click')
    expect(wrapper.find('[data-testid="partner-doc-supersedes"]').element.value).toBe('d2')
    const file = new File(['%PDF-1.4'], 'v3.pdf', { type: 'application/pdf' })
    const input = wrapper.find('[data-testid="partner-doc-file"]')
    Object.defineProperty(input.element, 'files', { value: [file] })
    await input.trigger('change')
    await wrapper.find('[data-testid="partner-doc-upload"]').find('form').trigger('submit')
    await flushPromises()
    const call = api.post.mock.calls.find((c) => String(c[0]).includes('/documents/'))
    expect(call[1].get('supersedes')).toBe('d2')
    expect(call[1].get('category')).toBe('signed_copy')
  })
})
