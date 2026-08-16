/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import { createRouter, createMemoryHistory } from 'vue-router'
import en from '@/locales/en.json'
import AdminDataManagement from './AdminDataManagement.vue'

const { mockGet, mockPost } = vi.hoisted(() => ({
  mockGet: vi.fn(),
  mockPost: vi.fn(),
}))
vi.mock('@/services/api', () => ({ default: { get: mockGet, post: mockPost } }))

async function mountPage(query = {}) {
  const i18n = createI18n({ legacy: false, locale: 'en', messages: { en } })
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', name: 'Dashboard', component: { template: '<div />' } },
      { path: '/admin/data-management', name: 'AdminDataManagement', component: AdminDataManagement },
    ],
  })
  await router.push({ name: 'AdminDataManagement', query })
  return mount(AdminDataManagement, {
    global: { plugins: [i18n, router] },
  })
}

describe('AdminDataManagement', () => {
  beforeEach(() => {
    mockPost.mockResolvedValue({ data: { message: 'Export queued.' } })
    mockGet.mockImplementation((url) => {
      if (url === '/api/data-management/catalog/') {
        return Promise.resolve({
          data: {
            sections: [
              { key: 'data_export', title: 'Data export', description: 'Export', url: '/seim/admin/data-management?section=data_export' },
              { key: 'database', title: 'Database reset', description: 'Reset', url: '/seim/admin/data-management?section=database' },
            ],
          },
        })
      }
      if (url === '/api/data-management/resources/') {
        return Promise.resolve({
          data: { results: [{ id: 'exp-1', name: 'Export users', format: 'CSV' }] },
        })
      }
      return Promise.resolve({ data: { results: [] } })
    })
  })

  it('renders catalog tools and executes a section item in the SPA', async () => {
    const wrapper = await mountPage({ section: 'data_export' })
    await flushPromises()
    expect(mockGet).toHaveBeenCalledWith('/api/data-management/catalog/')
    expect(wrapper.get('[data-testid="data-management-tool"]').text()).toContain('Data export')
    expect(wrapper.get('[data-testid="data-management-items"]').text()).toContain('Export users')
    await wrapper.get('[data-testid="data-execute"]').trigger('click')
    await flushPromises()
    expect(mockPost).toHaveBeenCalledWith('/api/data-management/execute/', {
      section: 'data_export',
      item_id: 'exp-1',
    })
  })

  it('queues a confirmed database reset from the SPA', async () => {
    const wrapper = await mountPage({ section: 'database' })
    await flushPromises()
    await wrapper.get('[data-testid="data-reset-confirm"]').setValue('RESET')
    await wrapper.get('[data-testid="data-reset-run"]').trigger('click')
    await flushPromises()
    expect(mockPost).toHaveBeenCalledWith('/api/data-management/execute/', {
      section: 'database',
      confirm: 'RESET',
    })
  })
})
