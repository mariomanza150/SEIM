/**
 * @vitest-environment jsdom
 */
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import i18n, { setAppLocale } from '@/i18n'
import api from '@/services/api'
import QaTriage from './QaTriage.vue'
import TesterChecklist from './TesterChecklist.vue'
import IssueTriagePanel from '@/components/qa/IssueTriagePanel.vue'
import IssueVerifyPanel from '@/components/qa/IssueVerifyPanel.vue'
import { testerMenuLinks } from '@/qa/menuLinks'

vi.mock('@/services/api', () => ({ default: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() } }))
vi.mock('vue-router', () => ({ useRouter: () => ({ push: vi.fn() }), useRoute: () => ({ params: {}, query: {} }) }))
const toast = { success: vi.fn(), error: vi.fn() }
vi.mock('@/composables/useToast', () => ({ useToast: () => toast }))

const stubs = { RouterLink: { template: '<a><slot /></a>' } }

function routeGet(map, ctx = {}) {
  api.get.mockImplementation((url) => {
    if (url === '/api/qa/context/') return Promise.resolve({ data: { enabled: true, is_tester: true, ...ctx } })
    if (url in map) return Promise.resolve({ data: map[url] })
    return Promise.reject(new Error(`unexpected ${url}`))
  })
}

const scenario = (extra = {}) => ({
  id: 's1', code: 'AUTH-01', area: 'Accounts', role: 'student', title: 'Sign in', steps: 'Do it', expected: 'Works', result: null, ...extra,
})

describe('phase 3 tester views', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    setAppLocale('en')
    vi.clearAllMocks()
  })

  it('menu adds triage only for triagers', () => {
    expect(testerMenuLinks({ isTriager: false }).map((l) => l.name)).not.toContain('QaTriage')
    expect(testerMenuLinks({ isTriager: true }).map((l) => l.name)).toContain('QaTriage')
    expect(testerMenuLinks().map((l) => l.name)).toContain('TesterChecklist')
  })

  it('triage page is triager-only', async () => {
    routeGet({})
    const w = mount(QaTriage, { global: { plugins: [i18n], stubs } })
    await flushPromises()
    expect(w.find('[data-testid="qa-not-available"]').exists()).toBe(true)
  })

  it('triage page lists open reports and changes status inline', async () => {
    routeGet(
      { '/api/qa/issues/': { results: [{ id: 'i1', number: 7, reference: 'QA-7', title: 'Bug', severity: 'major', status: 'new', reporter: { email: 't@x' } }] } },
      { is_triager: true },
    )
    api.patch.mockResolvedValue({ data: {} })
    const w = mount(QaTriage, { global: { plugins: [i18n], stubs } })
    await flushPromises()
    const call = api.get.mock.calls.find((c) => c[0] === '/api/qa/issues/')
    expect(call[1].params.open).toBe(1)
    await w.find('[data-testid="qa-triage-status-7"]').setValue('fixed')
    await flushPromises()
    expect(api.patch).toHaveBeenCalledWith('/api/qa/issues/i1/', { status: 'fixed' })
    expect(toast.success).toHaveBeenCalled()
  })

  it('triage page reverts status on failure and filters', async () => {
    routeGet(
      { '/api/qa/issues/': { results: [{ id: 'i1', number: 7, reference: 'QA-7', title: 'Bug', severity: 'major', status: 'new' }] } },
      { is_triager: true },
    )
    api.patch.mockRejectedValue(new Error('x'))
    const w = mount(QaTriage, { global: { plugins: [i18n], stubs } })
    await flushPromises()
    await w.find('[data-testid="qa-triage-status-7"]').setValue('closed')
    await flushPromises()
    expect(toast.error).toHaveBeenCalled()
    await w.find('#qa-tg-status').setValue('all')
    await w.find('#qa-tg-assigned').setValue('me')
    await flushPromises()
    const last = api.get.mock.calls.filter((c) => c[0] === '/api/qa/issues/').pop()
    expect(last[1].params.open).toBeUndefined()
    expect(last[1].params.assigned).toBe('me')
  })

  it('triage panel saves fields', async () => {
    api.get.mockResolvedValue({ data: { results: [{ id: 'u1', email: 'boss@x' }] } })
    api.patch.mockResolvedValue({ data: {} })
    const w = mount(IssueTriagePanel, {
      props: { issue: { id: 'i1', status: 'new', severity: 'minor', assignee: null, duplicate_of_reference: 'QA-3' } },
      global: { plugins: [i18n] },
    })
    await flushPromises()
    await w.find('#qa-tr-status').setValue('in_progress')
    await w.find('#qa-tr-assignee').setValue('u1')
    await w.find('form').trigger('submit')
    await flushPromises()
    expect(api.patch).toHaveBeenCalledWith('/api/qa/issues/i1/', expect.objectContaining({ status: 'in_progress', assignee_id: 'u1', duplicate_of_number: 3 }))
    expect(w.emitted('updated')).toBeTruthy()
  })

  it('triage panel shows server errors', async () => {
    api.get.mockRejectedValue(new Error('x'))
    api.patch.mockRejectedValue({ response: { data: { duplicate_of_number: ['Unknown report.'] } } })
    const w = mount(IssueTriagePanel, { props: { issue: { id: 'i1', status: 'new', severity: 'minor' } }, global: { plugins: [i18n] } })
    await flushPromises()
    await w.find('form').trigger('submit')
    await flushPromises()
    expect(w.text()).toContain('Unknown report.')
  })

  it('verify panel confirms and reopens', async () => {
    api.post.mockResolvedValue({ data: {} })
    const w = mount(IssueVerifyPanel, { props: { issue: { id: 'i1', status: 'fixed', resolved_in_commit: 'abcdef123' } }, global: { plugins: [i18n] } })
    expect(w.text()).toContain('abcdef1')
    await w.find('[data-testid="qa-verify-ok"]').trigger('click')
    await flushPromises()
    expect(api.post).toHaveBeenCalledWith('/api/qa/issues/i1/verify/', { result: 'verified', comment: '' })
    await w.find('[data-testid="qa-verify-reopen"]').trigger('click')
    await w.find('textarea').setValue('nope')
    await w.find('[data-testid="qa-verify-reopen"]').trigger('click')
    await flushPromises()
    expect(api.post).toHaveBeenLastCalledWith('/api/qa/issues/i1/verify/', { result: 'reopen', comment: 'nope' })
  })

  it('checklist records outcomes and offers to report failures', async () => {
    routeGet({ '/api/qa/scenarios/': { build: 'abc1234def', summary: { todo: 1 }, results: [scenario()] } })
    api.post.mockResolvedValue({ data: { outcome: 'fail', note: '', issue_number: null } })
    const events = []
    window.addEventListener('seim:qa-report', (e) => events.push(e.detail))
    const w = mount(TesterChecklist, { global: { plugins: [i18n], stubs } })
    await flushPromises()
    expect(w.text()).toContain('abc1234')
    await w.find('[data-testid="qa-scenario-AUTH-01-fail"]').trigger('click')
    await flushPromises()
    expect(api.post).toHaveBeenCalledWith('/api/qa/scenarios/s1/result/', { outcome: 'fail', note: '' })
    expect(w.find('[data-testid="qa-checklist-summary"]').text()).toContain('Fail: 1')
    await w.findAll('button').find((b) => b.text().includes('Report this failure')).trigger('click')
    expect(events[0].title).toBe('AUTH-01: Sign in')
    api.delete.mockResolvedValue({ status: 204 })
    await w.findAll('button').find((b) => b.text() === 'Clear').trigger('click')
    await flushPromises()
    expect(api.delete).toHaveBeenCalledWith('/api/qa/scenarios/s1/result/')
  })

  it('checklist matrix for triagers', async () => {
    routeGet(
      {
        '/api/qa/scenarios/': { build: 'abc', summary: {}, results: [scenario()] },
        '/api/qa/scenarios/matrix/': {
          current: 'abc1234', builds: ['abc1234', 'old0001'],
          results: [{ ...scenario(), builds: { abc1234: { outcome: 'fail', counts: { fail: 1 }, issues: [4] }, old0001: null } }],
        },
      },
      { is_triager: true },
    )
    const w = mount(TesterChecklist, { global: { plugins: [i18n], stubs } })
    await flushPromises()
    await w.find('[data-testid="qa-checklist-matrix-tab"]').trigger('click')
    await flushPromises()
    const table = w.find('[data-testid="qa-checklist-matrix"]')
    expect(table.text()).toContain('QA-4')
    expect(table.text()).toContain('Fail')
  })
})
