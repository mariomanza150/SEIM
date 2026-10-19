/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import { createRouter, createMemoryHistory } from 'vue-router'
import en from '@/locales/en.json'
import AdminUsers from './AdminUsers.vue'

const { mockGet, mockPatch } = vi.hoisted(() => ({ mockGet: vi.fn(), mockPatch: vi.fn() }))
vi.mock('@/services/api', () => ({ default: { get: mockGet, post: vi.fn(), patch: mockPatch, delete: vi.fn() } }))
vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: vi.fn(), error: vi.fn() }),
}))

const users = [
  { id: 'u-1', username: 'tess', email: 'tess@test.com', roles: ['student'], role: 'student', is_active: true, is_staff: false, is_email_verified: true, is_tester: true },
  { id: 'u-2', username: 'nora', email: 'nora@test.com', roles: ['student'], role: 'student', is_active: true, is_staff: false, is_email_verified: true, is_tester: false },
]

async function mountPage() {
  const i18n = createI18n({ legacy: false, locale: 'en', messages: { en } })
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', name: 'Dashboard', component: { template: '<div />' } },
      { path: '/help', name: 'HelpCenter', component: { template: '<div />' } },
      { path: '/admin/users', name: 'AdminUsers', component: AdminUsers },
    ],
  })
  await router.push({ name: 'AdminUsers' })
  const wrapper = mount(AdminUsers, {
    global: { plugins: [i18n, router], stubs: { Teleport: { template: '<div><slot /></div>' } } },
    attachTo: document.body,
  })
  await flushPromises()
  return wrapper
}

describe('AdminUsers tester flag', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockGet.mockImplementation((url) => {
      if (url === '/api/users/') return Promise.resolve({ data: { results: users } })
      if (url === '/api/roles/') return Promise.resolve({ data: { results: [{ id: 2, name: 'student' }] } })
      return Promise.resolve({ data: { results: [] } })
    })
    mockPatch.mockResolvedValue({ data: {} })
  })

  it('shows a Tester badge only for testers', async () => {
    const wrapper = await mountPage()
    const badges = wrapper.findAll('[data-testid="admin-users-tester-badge"]')
    expect(badges).toHaveLength(1)
    expect(badges[0].element.closest('tr').textContent).toContain('tess@test.com')
    wrapper.unmount()
  })

  it('sends is_tester filter in users query params', async () => {
    const wrapper = await mountPage()
    await wrapper.get('[data-testid="admin-users-filter-tester"]').setValue('true')
    await flushPromises()
    const last = mockGet.mock.calls.filter(([u]) => u === '/api/users/').at(-1)
    expect(last[1].params.is_tester).toBe('true')
    wrapper.unmount()
  })

  it('toggles is_tester in the editor and PATCHes it', async () => {
    const wrapper = await mountPage()
    const rows = wrapper.findAll('[data-testid="admin-users-table"] tbody tr')
    await rows[1].get('button').trigger('click')
    await flushPromises()
    const box = wrapper.get('[data-testid="admin-users-tester-checkbox"]')
    expect(box.element.checked).toBe(false)
    await box.setValue(true)
    await wrapper.get('[data-testid="form-modal-submit"]').trigger('click')
    await flushPromises()
    expect(mockPatch).toHaveBeenCalledWith('/api/users/u-2/', expect.objectContaining({ is_tester: true }))
    wrapper.unmount()
  })
})
