/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import { createRouter, createMemoryHistory } from 'vue-router'
import en from '@/locales/en.json'
import AdminSessions from './AdminSessions.vue'

const { mockGet, mockPost } = vi.hoisted(() => ({
  mockGet: vi.fn(),
  mockPost: vi.fn(),
}))
vi.mock('@/services/api', () => ({
  default: { get: mockGet, post: mockPost, patch: vi.fn(), delete: vi.fn() },
}))
vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: vi.fn(), error: vi.fn() }),
}))
vi.mock('@/composables/useConfirm', () => ({
  useConfirm: () => ({ confirm: vi.fn().mockResolvedValue(false) }),
}))

async function mountPage() {
  const i18n = createI18n({ legacy: false, locale: 'en', messages: { en } })
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', name: 'Dashboard', component: { template: '<div />' } },
      { path: '/admin/sessions', name: 'AdminSessions', component: AdminSessions },
    ],
  })
  await router.push({ name: 'AdminSessions' })
  const wrapper = mount(AdminSessions, { global: { plugins: [i18n, router] } })
  await flushPromises()
  return wrapper
}

describe('AdminSessions', () => {
  beforeEach(() => {
    mockGet.mockImplementation((url) => {
      if (url === '/api/user-sessions/') {
        return Promise.resolve({
          data: {
            results: [
              {
                id: 9,
                user_email: 'coord@test.com',
                user_username: 'coord',
                device: 'Desktop',
                location: 'Monterrey',
                is_active: true,
                last_activity: '2026-08-18T12:00:00Z',
              },
            ],
          },
        })
      }
      if (url === '/api/reminders/') {
        return Promise.resolve({
          data: {
            results: [
              {
                id: 'r-1',
                user_email: 'student@test.com',
                event_title: 'Program start',
                event_type: 'program_start',
                remind_at: '2026-09-01T12:00:00Z',
                sent: false,
              },
            ],
          },
        })
      }
      if (url === '/api/users/') {
        return Promise.resolve({
          data: { results: [{ id: 'u-1', email: 'student@test.com' }] },
        })
      }
      return Promise.resolve({ data: { results: [] } })
    })
  })

  it('lists sessions by default', async () => {
    const wrapper = await mountPage()
    expect(wrapper.get('[data-testid="admin-sessions-table"]').text()).toContain('coord@test.com')
    expect(wrapper.get('[data-testid="admin-sessions-table"]').text()).toContain('Desktop')
  })

  it('lists reminders on the reminders tab', async () => {
    const wrapper = await mountPage()
    await wrapper.get('[data-testid="admin-sessions-tabs"] [data-tab="reminders"]').trigger('click')
    await flushPromises()
    expect(wrapper.get('[data-testid="admin-reminders-table"]').text()).toContain('Program start')
    expect(wrapper.get('[data-testid="admin-reminders-table"]').text()).toContain('student@test.com')
  })
})
