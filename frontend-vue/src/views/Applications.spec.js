/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import Applications from './Applications.vue'
import api from '@/services/api'
import i18n, { setAppLocale } from '@/i18n'

vi.mock('@/services/api', () => ({
  default: { get: vi.fn(), delete: vi.fn() },
}))

vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: vi.fn(), error: vi.fn() }),
}))

const routeQuery = { status: '' }
vi.mock('vue-router', () => ({
  useRoute: () => ({ query: routeQuery }),
}))

function mountApplications() {
  return mount(Applications, {
    global: {
      plugins: [createPinia(), i18n],
      stubs: { RouterLink: { template: '<a><slot /></a>' } },
    },
  })
}

describe('Applications', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    setAppLocale('en')
    routeQuery.status = ''
    delete routeQuery.direction
    vi.clearAllMocks()
    global.confirm = vi.fn(() => false)
  })

  afterEach(() => {
    setAppLocale('en')
    localStorage.clear()
  })

  it('shows translated empty state when list is empty', async () => {
    api.get.mockResolvedValue({ data: { results: [], count: 0, next: null, previous: null } })
    const wrapper = mountApplications()
    await flushPromises()
    expect(wrapper.find('nav').attributes('aria-label')).toBe(i18n.global.t('applicationsPage.breadcrumbAria'))
    expect(wrapper.text()).toContain('No applications yet')
    expect(wrapper.text()).toContain('My applications')
  })

  it('renders draft card with translated labels', async () => {
    api.get.mockResolvedValue({
      data: {
        results: [
          {
            id: '1',
            status: 'draft',
            created_at: '2026-01-10T12:00:00Z',
            submitted_at: '2026-01-11T12:00:00Z',
            program: { name: 'Test Program', institution: 'Uni' },
          },
        ],
        count: 1,
        next: null,
        previous: null,
      },
    })
    const wrapper = mountApplications()
    await flushPromises()
    expect(wrapper.text()).toContain('Test Program')
    expect(wrapper.text()).toContain('Draft')
    expect(wrapper.text()).toContain(`${i18n.global.t('applicationDetailPage.submitted')}:`)
    expect(wrapper.text()).toContain('View details')
    expect(wrapper.find('[data-testid="application-detail-link"]').exists()).toBe(true)
  })

  it('renders program_name when API returns program id without nested object', async () => {
    api.get.mockResolvedValue({
      data: {
        results: [
          {
            id: '1',
            status: 'draft',
            created_at: '2026-01-10T12:00:00Z',
            submitted_at: null,
            program: '00000000-0000-0000-0000-000000000001',
            program_name: 'DAAD Exchange',
          },
        ],
        count: 1,
        next: null,
        previous: null,
      },
    })
    const wrapper = mountApplications()
    await flushPromises()
    expect(wrapper.text()).toContain('DAAD Exchange')
    expect(wrapper.text()).not.toContain(i18n.global.t('applicationDetailPage.unknownProgram'))
  })

  it('uses applicationDetailPage fallbacks for sparse program and missing dates', async () => {
    api.get.mockResolvedValue({
      data: {
        results: [
          {
            id: 'sparse',
            status: 'submitted',
            created_at: null,
            submitted_at: null,
            program: { name: '', institution: null },
          },
        ],
        count: 1,
        next: null,
        previous: null,
      },
    })
    const wrapper = mountApplications()
    await flushPromises()
    expect(wrapper.text()).toContain(i18n.global.t('applicationDetailPage.unknownProgram'))
    const na = i18n.global.t('applicationDetailPage.notAvailable')
    expect(wrapper.text()).toContain(`${i18n.global.t('applicationDetailPage.created')}: ${na}`)
    expect(wrapper.find('[data-testid="application-host"]').exists()).toBe(false)
    expect(wrapper.text()).toContain(i18n.global.t('applicationDetailPage.status.submitted'))
    expect(wrapper.text()).toContain(`${i18n.global.t('applicationDetailPage.created')}:`)
  })

  it('shows shared pagination.previous and pagination.next when list spans pages', async () => {
    const results = Array.from({ length: 10 }, (_, i) => ({
      id: String(i),
      status: 'draft',
      created_at: '2026-01-10T12:00:00Z',
      program: { name: `Program ${i}`, institution: 'Uni' },
    }))
    api.get.mockResolvedValue({
      data: {
        results,
        count: 11,
        next: 'http://test/api/applications/?page=2',
        previous: null,
      },
    })
    const wrapper = mountApplications()
    await flushPromises()
    expect(wrapper.text()).toContain(i18n.global.t('pagination.previous'))
    expect(wrapper.text()).toContain(i18n.global.t('pagination.next'))
    const ariaLabels = wrapper.find('ul.pagination').findAll('button').map((b) => b.attributes('aria-label'))
    expect(ariaLabels).toContain(i18n.global.t('pagination.previous'))
    expect(ariaLabels).toContain(i18n.global.t('pagination.next'))
    expect(ariaLabels).toContain(i18n.global.t('pagination.pageNumberAria', { n: 1 }))
    expect(ariaLabels).toContain(i18n.global.t('pagination.pageNumberAria', { n: 2 }))
  })

  it('sends page=1 when status filter changes instead of a DOM event', async () => {
    api.get.mockResolvedValue({ data: { results: [], count: 0, next: null, previous: null } })
    const wrapper = mountApplications()
    await flushPromises()
    api.get.mockClear()
    await wrapper.find('[data-testid="applications-filter-status"]').setValue('draft')
    await wrapper.find('[data-testid="applications-filter-status"]').trigger('change')
    await flushPromises()
    expect(api.get).toHaveBeenCalledWith('/api/applications/', {
      params: { page: 1, ordering: '-created_at', status: 'draft', direction: 'outgoing' },
    })
  })

  it('includes nominated, waitlist, cancelled, and withdrawn status filters', async () => {
    api.get.mockResolvedValue({ data: { results: [], count: 0, next: null, previous: null } })
    const wrapper = mountApplications()
    await flushPromises()
    const opts = wrapper.find('[data-testid="applications-filter-status"]').findAll('option')
    const values = opts.map((o) => o.element.value)
    expect(values).toEqual([
      '',
      'draft',
      'submitted',
      'under_review',
      'nominated',
      'waitlist',
      'approved',
      'rejected',
      'completed',
      'cancelled',
      'withdrawn',
    ])
    expect(opts.find((o) => o.element.value === 'nominated')?.text()).toBe(
      i18n.global.t('applicationDetailPage.status.nominated'),
    )
  })

  it('shows host_institution_name when program is a FK id', async () => {
    api.get.mockResolvedValue({
      data: {
        results: [
          {
            id: '1',
            status: 'nominated',
            created_at: '2026-01-10T12:00:00Z',
            program: '00000000-0000-0000-0000-000000000001',
            program_name: 'DAAD Exchange',
            host_institution_name: 'Technical University of Munich',
          },
        ],
        count: 1,
        next: null,
        previous: null,
      },
    })
    const wrapper = mountApplications()
    await flushPromises()
    expect(wrapper.find('[data-testid="application-host"]').text()).toContain(
      'Technical University of Munich',
    )
    expect(wrapper.text()).not.toContain(i18n.global.t('applicationDetailPage.notAvailable'))
  })

  it('applies ?status= from route query on mount (MQ-026)', async () => {
    routeQuery.status = 'nominated'
    api.get.mockResolvedValue({ data: { results: [], count: 0, next: null, previous: null } })
    const wrapper = mountApplications()
    await flushPromises()
    expect(wrapper.find('[data-testid="applications-filter-status"]').element.value).toBe('nominated')
    expect(api.get).toHaveBeenCalledWith('/api/applications/', {
      params: { page: 1, ordering: '-created_at', status: 'nominated', direction: 'outgoing' },
    })
  })

  it('uses a compact filter bar with clear next to primary filters', async () => {
    api.get.mockResolvedValue({ data: { results: [], count: 0, next: null, previous: null } })
    const wrapper = mountApplications()
    await flushPromises()
    expect(wrapper.find('[data-testid="applications-filters"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="compact-filter-clear"]').exists()).toBe(true)
    // Exchange date range lives in the advanced disclosure.
    expect(wrapper.find('[data-testid="compact-filter-advanced-toggle"]').exists()).toBe(true)
    expect(wrapper.find('.seim-page-breadcrumb').exists()).toBe(true)
  })

  describe('incoming / outgoing tabs and exchange filters', () => {
    const empty = { data: { results: [], count: 0, next: null, previous: null } }
    const programsPayload = {
      data: {
        results: [
          { id: 'p-1', name: 'DAAD Exchange' },
          { id: 'p-2', name: 'Erasmus Madrid' },
        ],
        count: 2,
        next: null,
        previous: null,
      },
    }

    function mockByUrl() {
      api.get.mockImplementation((url) =>
        Promise.resolve(url === '/api/programs/' ? programsPayload : empty),
      )
    }

    function applicationCalls() {
      return api.get.mock.calls.filter(([url]) => url === '/api/applications/').map(([, cfg]) => cfg.params)
    }

    it('defaults to the Outgoing tab and loads outgoing programs for the filter', async () => {
      mockByUrl()
      const wrapper = mountApplications()
      await flushPromises()
      expect(wrapper.find('[data-testid="applications-tab-outgoing"]').classes()).toContain('active')
      expect(wrapper.find('[data-testid="applications-tab-incoming"]').text()).toContain(
        i18n.global.t('applicationsPage.tabIncoming'),
      )
      expect(api.get).toHaveBeenCalledWith('/api/programs/', {
        params: { direction: 'outgoing', page_size: 100, ordering: 'name' },
      })
      expect(applicationCalls().at(-1)).toMatchObject({ page: 1, direction: 'outgoing' })
      expect(wrapper.find('[data-testid="applications-filter-program-wrap"]').exists()).toBe(true)
    })

    it('switching to Incoming refetches page 1, hides and clears the program filter', async () => {
      mockByUrl()
      const wrapper = mountApplications()
      await flushPromises()
      wrapper.vm.filters.program = 'p-2'
      await flushPromises()
      expect(applicationCalls().at(-1)).toMatchObject({ page: 1, direction: 'outgoing', program: 'p-2' })

      await wrapper.find('[data-testid="applications-tab-incoming"]').trigger('click')
      await flushPromises()
      const last = applicationCalls().at(-1)
      expect(last).toMatchObject({ page: 1, direction: 'incoming' })
      expect(last.program).toBeUndefined()
      expect(wrapper.vm.filters.program).toBe('')
      expect(wrapper.find('[data-testid="applications-filter-program-wrap"]').exists()).toBe(false)
    })

    it('period and date range changes refetch page 1 with the API params', async () => {
      mockByUrl()
      const wrapper = mountApplications()
      await flushPromises()
      const periodSelect = wrapper.find('[data-testid="applications-filter-period"]')
      const year = new Date().getFullYear()
      expect(periodSelect.findAll('option').map((o) => o.element.value)).toContain(`${year}-2`)
      await periodSelect.setValue(`${year}-2`)
      await flushPromises()
      expect(applicationCalls().at(-1)).toMatchObject({ page: 1, period: `${year}-2` })

      wrapper.vm.filters.start_date = '2026-08-01'
      wrapper.vm.filters.end_date = '2026-12-15'
      await flushPromises()
      expect(applicationCalls().at(-1)).toMatchObject({
        page: 1,
        start_date: '2026-08-01',
        end_date: '2026-12-15',
      })
    })

    it('honours ?direction=incoming from the route', async () => {
      routeQuery.direction = 'incoming'
      mockByUrl()
      const wrapper = mountApplications()
      await flushPromises()
      expect(wrapper.find('[data-testid="applications-tab-incoming"]').classes()).toContain('active')
      expect(applicationCalls()[0]).toMatchObject({ direction: 'incoming' })
    })

    it('clear filters keeps the active tab and refetches once', async () => {
      mockByUrl()
      const wrapper = mountApplications()
      await flushPromises()
      await wrapper.find('[data-testid="applications-tab-incoming"]').trigger('click')
      wrapper.vm.filters.period = '2026'
      await flushPromises()
      api.get.mockClear()
      await wrapper.find('[data-testid="compact-filter-clear"]').trigger('click')
      await flushPromises()
      const calls = applicationCalls()
      expect(calls).toHaveLength(1)
      expect(calls[0]).toEqual({ page: 1, ordering: '-created_at', direction: 'incoming' })
    })
  })
})
