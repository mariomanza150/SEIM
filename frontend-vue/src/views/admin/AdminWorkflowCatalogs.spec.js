/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import { createRouter, createMemoryHistory } from 'vue-router'
import en from '@/locales/en.json'
import AdminWorkflowCatalogs from './AdminWorkflowCatalogs.vue'

const { mockGet, mockPost, mockPatch, mockDelete } = vi.hoisted(() => ({
  mockGet: vi.fn(),
  mockPost: vi.fn(),
  mockPatch: vi.fn(),
  mockDelete: vi.fn(),
}))
vi.mock('@/services/api', () => ({
  default: { get: mockGet, post: mockPost, patch: mockPatch, delete: mockDelete },
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
      {
        path: '/admin/workflow-catalogs',
        name: 'AdminWorkflowCatalogs',
        component: AdminWorkflowCatalogs,
      },
    ],
  })
  await router.push({ name: 'AdminWorkflowCatalogs' })
  const wrapper = mount(AdminWorkflowCatalogs, { global: { plugins: [i18n, router] } })
  await flushPromises()
  return wrapper
}

describe('AdminWorkflowCatalogs', () => {
  beforeEach(() => {
    mockGet.mockImplementation((url) => {
      if (url === '/api/application-statuses/') {
        return Promise.resolve({
          data: [{ id: 1, name: 'draft', order: 1 }],
        })
      }
      if (url === '/api/notification-types/') {
        return Promise.resolve({
          data: [{ id: 2, name: 'status_change' }],
        })
      }
      return Promise.resolve({ data: [] })
    })
  })

  it('lists application statuses by default', async () => {
    const wrapper = await mountPage()
    expect(wrapper.get('[data-testid="admin-workflow-catalogs-table"]').text()).toContain('draft')
  })

  it('lists notification types on the types tab', async () => {
    const wrapper = await mountPage()
    await wrapper.get('[data-testid="admin-workflow-catalogs-tabs"] [data-tab="types"]').trigger('click')
    await flushPromises()
    expect(wrapper.get('[data-testid="admin-workflow-catalogs-table"]').text()).toContain('status_change')
  })
})
