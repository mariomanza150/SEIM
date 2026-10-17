/**
 * @vitest-environment jsdom
 */
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import i18n, { setAppLocale } from '@/i18n'
import api from '@/services/api'
import { useQaStore } from '@/stores/qa'
import TesterAccounts from './TesterAccounts.vue'
import TesterOutbox from './TesterOutbox.vue'
import TesterHub from './TesterHub.vue'
import TesterGuide from './TesterGuide.vue'
import ActingAsBanner from '@/components/qa/ActingAsBanner.vue'

const push = vi.fn()
vi.mock('@/services/api', () => ({ default: { get: vi.fn(), post: vi.fn(), patch: vi.fn() } }))
vi.mock('vue-router', () => ({ useRouter: () => ({ push }), useRoute: () => ({ params: {}, query: {} }) }))
const switchToDemo = vi.fn()
const returnToMyAccount = vi.fn()
vi.mock('@/qa/roleSwitch', () => ({
  switchToDemo: (...a) => switchToDemo(...a),
  startImpersonation: vi.fn(),
  returnToMyAccount: (...a) => returnToMyAccount(...a),
}))
const confirmMock = vi.fn()
vi.mock('@/composables/useConfirm', () => ({ useConfirm: () => ({ confirm: confirmMock }) }))

const stubs = { RouterLink: { template: '<a><slot /></a>' } }

function routeGet(map, ctx = {}) {
  api.get.mockImplementation((url) => {
    if (url === '/api/qa/context/') return Promise.resolve({ data: { enabled: true, is_tester: true, ...ctx } })
    if (url in map) return Promise.resolve({ data: map[url] })
    return Promise.reject(new Error(`unexpected ${url}`))
  })
}

describe('tester tools views', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    setAppLocale('en')
    vi.clearAllMocks()
  })

  it('accounts: lists demo accounts and switches', async () => {
    routeGet({ '/api/qa/demo-accounts/': { results: [{ id: 'd1', email: 'student@test.com', role: 'student', name: 'Ana' }] } })
    switchToDemo.mockResolvedValue({})
    const w = mount(TesterAccounts, { global: { plugins: [i18n], stubs } })
    await flushPromises()
    expect(w.text()).toContain('student@test.com')
    expect(w.text()).toContain('Student')
    expect(w.find('[data-testid="qa-impersonate"]').exists()).toBe(false)
    await w.find('[data-testid="qa-switch-student@test.com"]').trigger('click')
    await flushPromises()
    expect(switchToDemo).toHaveBeenCalledWith('d1')
    expect(push).toHaveBeenCalledWith({ name: 'Dashboard' })
  })

  it('accounts: triagers see impersonation and errors surface', async () => {
    routeGet({ '/api/qa/demo-accounts/': { results: [{ id: 'd1', email: 'a@test.com', role: 'admin' }] } }, { is_triager: true })
    switchToDemo.mockRejectedValue(new Error('x'))
    const w = mount(TesterAccounts, { global: { plugins: [i18n], stubs } })
    await flushPromises()
    expect(w.find('[data-testid="qa-impersonate"]').exists()).toBe(true)
    await w.find('[data-testid="qa-switch-a@test.com"]').trigger('click')
    await flushPromises()
    expect(w.text()).toContain('Could not switch accounts')
  })

  it('accounts: not available for non-testers', async () => {
    api.get.mockRejectedValue({ response: { status: 404 } })
    const w = mount(TesterAccounts, { global: { plugins: [i18n], stubs } })
    await flushPromises()
    expect(w.find('[data-testid="qa-not-available"]').exists()).toBe(true)
  })

  it('outbox: lists and renders html in a sandboxed iframe', async () => {
    routeGet({
      '/api/qa/outbox/': { capturing: true, results: [{ id: 'm1', subject: 'Verify', to: ['s@test.com'], created_at: '2026-10-17T00:00:00Z' }] },
      '/api/qa/outbox/m1/': { id: 'm1', subject: 'Verify', to: ['s@test.com'], cc: [], body_html: '<p>Hi</p>', body_text: 'Hi' },
    })
    const w = mount(TesterOutbox, { global: { plugins: [i18n], stubs } })
    await flushPromises()
    await w.find('[data-testid="qa-outbox-list"] button').trigger('click')
    await flushPromises()
    const frame = w.find('[data-testid="qa-outbox-iframe"]')
    expect(frame.exists()).toBe(true)
    expect(frame.attributes('sandbox')).toBe('')
    expect(w.find('[data-testid="qa-outbox-not-capturing"]').exists()).toBe(false)
  })

  it('outbox: warns when capture is off and shows empty state', async () => {
    routeGet({ '/api/qa/outbox/': { capturing: false, results: [] } })
    const w = mount(TesterOutbox, { global: { plugins: [i18n], stubs } })
    await flushPromises()
    expect(w.find('[data-testid="qa-outbox-not-capturing"]').exists()).toBe(true)
    expect(w.find('[data-testid="qa-outbox-empty"]').exists()).toBe(true)
  })

  it('hub: shows flags, and triagers can queue a reset', async () => {
    routeGet(
      { '/api/qa/flags/': { feature_flags: { NEW_UI: true }, institution: { scholarships_enabled: false }, environment: { email_capture: true, demo_password_configured: true } } },
      { is_triager: true, deploy_tier: 'test' },
    )
    confirmMock.mockResolvedValue(true)
    api.post.mockResolvedValue({ status: 202, data: { queued: true } })
    const w = mount(TesterHub, { global: { plugins: [i18n], stubs } })
    await flushPromises()
    expect(w.text()).toContain('NEW_UI')
    expect(w.text()).toContain('scholarships_enabled')
    await w.find('[data-testid="qa-hub-reset"] button').trigger('click')
    await flushPromises()
    expect(api.post).toHaveBeenCalledWith('/api/qa/reset-demo/', { confirm: 'RESET' })
    expect(w.text()).toContain('Reset started')
  })

  it('hub: reset hidden for non-triagers; conflict message', async () => {
    routeGet({ '/api/qa/flags/': { feature_flags: {}, institution: {}, environment: {} } })
    const w = mount(TesterHub, { global: { plugins: [i18n], stubs } })
    await flushPromises()
    expect(w.find('[data-testid="qa-hub-reset"]').exists()).toBe(false)
  })

  it('hub: reset already running', async () => {
    routeGet({ '/api/qa/flags/': { feature_flags: {}, institution: {}, environment: {} } }, { is_triager: true })
    confirmMock.mockResolvedValue(true)
    api.post.mockRejectedValue({ response: { status: 409 } })
    const w = mount(TesterHub, { global: { plugins: [i18n], stubs } })
    await flushPromises()
    await w.find('[data-testid="qa-hub-reset"] button').trigger('click')
    await flushPromises()
    expect(w.text()).toContain('already running')
  })

  it('guide renders all sections in Spanish', async () => {
    setAppLocale('es')
    routeGet({})
    const w = mount(TesterGuide, { global: { plugins: [i18n], stubs } })
    await flushPromises()
    expect(w.text()).toContain('Guía para testers')
    expect(w.findAll('section').length).toBe(5)
    expect(w.text()).toContain('contraseña demo')
  })

  it('acting-as banner returns to the tester account', async () => {
    const qa = useQaStore()
    qa.context = { enabled: true, is_tester: true, acting_as: { id: 'd1', email: 's@test.com', role: 'student', mode: 'switch' } }
    returnToMyAccount.mockResolvedValue(true)
    const w = mount(ActingAsBanner, { global: { plugins: [i18n], stubs } })
    expect(w.text()).toContain('Testing as s@test.com (Student)')
    await w.find('[data-testid="qa-return-button"]').trigger('click')
    await flushPromises()
    expect(push).toHaveBeenCalledWith({ name: 'TesterAccounts' })
  })

  it('acting-as banner shows impersonation copy and falls back to login', async () => {
    const qa = useQaStore()
    qa.context = { enabled: true, is_tester: true, acting_as: { id: 'u', email: 'u@x.com', role: 'coordinator', mode: 'impersonate' } }
    returnToMyAccount.mockResolvedValue(false)
    const w = mount(ActingAsBanner, { global: { plugins: [i18n], stubs } })
    expect(w.text()).toContain('audit log')
    await w.find('[data-testid="qa-return-button"]').trigger('click')
    await flushPromises()
    expect(push).toHaveBeenCalledWith({ name: 'Login' })
  })
})
