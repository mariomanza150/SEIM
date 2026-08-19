/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import { createRouter, createMemoryHistory } from 'vue-router'
import en from '@/locales/en.json'
import AdminUsers from './AdminUsers.vue'

const { mockGet } = vi.hoisted(() => ({ mockGet: vi.fn() }))
vi.mock('@/services/api', () => ({ default: { get: mockGet, post: vi.fn(), patch: vi.fn(), delete: vi.fn() } }))
vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: vi.fn(), error: vi.fn() }),
}))

describe('AdminUsers', () => {
  beforeEach(() => {
    mockGet.mockImplementation((url) => {
      if (url === '/api/users/') {
        return Promise.resolve({
          data: {
            results: [
              {
                id: 'u-1',
                username: 'coord',
                email: 'coord@test.com',
                first_name: 'Cora',
                last_name: 'Dinator',
                roles: ['coordinator'],
                role: 'coordinator',
                is_active: true,
                is_staff: true,
                is_email_verified: true,
              },
            ],
          },
        })
      }
      if (url === '/api/roles/') {
        return Promise.resolve({
          data: { results: [{ id: 1, name: 'coordinator' }, { id: 2, name: 'student' }] },
        })
      }
      return Promise.resolve({ data: { results: [] } })
    })
  })

  it('lists users and shows role checkboxes in the editor', async () => {
    const i18n = createI18n({ legacy: false, locale: 'en', messages: { en } })
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', name: 'Dashboard', component: { template: '<div />' } },
        { path: '/admin/users', name: 'AdminUsers', component: AdminUsers },
      ],
    })
    await router.push({ name: 'AdminUsers' })
    const wrapper = mount(AdminUsers, { global: { plugins: [i18n, router] } })
    await flushPromises()
    expect(wrapper.get('[data-testid="admin-users-table"]').text()).toContain('coord@test.com')
    expect(wrapper.get('[data-testid="admin-users-table"]').text()).toContain('coordinator')
    await wrapper.get('[data-testid="admin-users-table"] button').trigger('click')
    await flushPromises()
    expect(wrapper.get('[data-testid="admin-users-roles"]').text()).toContain('coordinator')
  })
})
