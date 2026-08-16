/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import { createRouter, createMemoryHistory } from 'vue-router'
import en from '@/locales/en.json'
import AdminDataManagement from './AdminDataManagement.vue'

const { mockGet } = vi.hoisted(() => ({ mockGet: vi.fn() }))
vi.mock('@/services/api', () => ({ default: { get: mockGet } }))

function mountPage() {
  const i18n = createI18n({ legacy: false, locale: 'en', messages: { en } })
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', name: 'Dashboard', component: { template: '<div />' } },
      { path: '/admin/data-management', name: 'AdminDataManagement', component: AdminDataManagement },
    ],
  })
  return mount(AdminDataManagement, {
    global: { plugins: [i18n, router] },
  })
}

describe('AdminDataManagement', () => {
  beforeEach(() => {
    mockGet.mockImplementation((url) => {
      if (url === '/api/data-management/catalog/') {
        return Promise.resolve({
          data: {
            sections: [
              { key: 'data_export', title: 'Data export', description: 'Export', url: '/data-management/data-export/' },
            ],
          },
        })
      }
      return Promise.resolve({ data: { results: [] } })
    })
  })

  it('renders catalog tools from the API', async () => {
    const wrapper = mountPage()
    await flushPromises()
    expect(mockGet).toHaveBeenCalledWith('/api/data-management/catalog/')
    expect(wrapper.get('[data-testid="data-management-tool"]').attributes('href')).toBe(
      '/data-management/data-export/',
    )
  })
})
