/**
 * @vitest-environment jsdom
 */
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import i18n, { setAppLocale } from '@/i18n'
import api from '@/services/api'
import TesterReports from './TesterReports.vue'
import TesterReportDetail from './TesterReportDetail.vue'

vi.mock('@/services/api', () => ({ default: { get: vi.fn(), post: vi.fn(), patch: vi.fn() } }))
vi.mock('vue-router', () => ({ useRoute: () => ({ params: { id: 'i1' }, query: {} }) }))

const stubs = { RouterLink: { template: '<a><slot /></a>' } }
const issue = {
  id: 'i1', reference: 'QA-1', title: 'Broken', severity: 'major', status: 'new', reporter: { email: 't@x' },
  created_at: '2026-10-17T07:00:00Z', attachments: [], comments: [{ id: 'c1', body: 'hi', author: { email: 't@x' }, is_internal: false, is_system: false, created_at: '2026-10-17T07:00:00Z' }],
  diagnostics: {}, attachment_count: 0,
}

function contextFor(extra = {}) {
  return { data: { enabled: true, is_tester: true, is_triager: false, ...extra } }
}

describe('Tester reports views', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    setAppLocale('en')
    vi.clearAllMocks()
  })

  it('shows not-available when the toolkit is off', async () => {
    api.get.mockRejectedValue({ response: { status: 404 } })
    const w = mount(TesterReports, { global: { plugins: [i18n], stubs } })
    await flushPromises()
    expect(w.find('[data-testid="qa-not-available"]').exists()).toBe(true)
  })

  it('lists own reports (mine=1 for non-triagers)', async () => {
    api.get.mockImplementation((url) =>
      url === '/api/qa/context/' ? Promise.resolve(contextFor()) : Promise.resolve({ data: { results: [issue] } }),
    )
    const w = mount(TesterReports, { global: { plugins: [i18n], stubs } })
    await flushPromises()
    expect(w.text()).toContain('QA-1')
    const listCall = api.get.mock.calls.find((c) => c[0] === '/api/qa/issues/')
    expect(listCall[1].params.mine).toBe(1)
  })

  it('shows the empty state', async () => {
    api.get.mockImplementation((url) =>
      url === '/api/qa/context/' ? Promise.resolve(contextFor({ is_triager: true })) : Promise.resolve({ data: [] }),
    )
    const w = mount(TesterReports, { global: { plugins: [i18n], stubs } })
    await flushPromises()
    expect(w.find('[data-testid="qa-reports-empty"]').exists()).toBe(true)
  })

  it('renders detail and posts a comment', async () => {
    api.get.mockImplementation((url) =>
      url === '/api/qa/context/' ? Promise.resolve(contextFor()) : Promise.resolve({ data: issue }),
    )
    api.post.mockResolvedValue({ data: {} })
    const w = mount(TesterReportDetail, { props: { id: 'i1' }, global: { plugins: [i18n], stubs } })
    await flushPromises()
    expect(w.text()).toContain('QA-1')
    expect(w.text()).toContain('hi')
    await w.find('#qa-comment').setValue('more info')
    await w.find('form').trigger('submit')
    await flushPromises()
    expect(api.post).toHaveBeenCalledWith('/api/qa/issues/i1/comments/', { body: 'more info', is_internal: false })
  })
})
