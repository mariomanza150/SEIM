/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import { createRouter, createMemoryHistory } from 'vue-router'
import en from '@/locales/en.json'
import AdminGrades from './AdminGrades.vue'

const { mockGet } = vi.hoisted(() => ({ mockGet: vi.fn() }))
vi.mock('@/services/api', () => ({ default: { get: mockGet, post: vi.fn(), patch: vi.fn(), delete: vi.fn() } }))
vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: vi.fn(), error: vi.fn() }),
}))
vi.mock('@/composables/useConfirm', () => ({
  useConfirm: () => ({ confirm: vi.fn() }),
}))

describe('AdminGrades', () => {
  beforeEach(() => {
    mockGet.mockImplementation((url) => {
      if (String(url) === '/api/grades/scales/') {
        return Promise.resolve({
          data: {
            results: [
              {
                id: 'scale-1',
                name: 'US GPA 4.0 Scale',
                code: 'US_GPA_4',
                country: 'United States',
                is_active: true,
                min_value: 0,
                max_value: 4,
                grade_count: 1,
              },
            ],
          },
        })
      }
      if (String(url).includes('/api/grades/values')) {
        return Promise.resolve({ data: [] })
      }
      return Promise.resolve({ data: { results: [] } })
    })
  })

  it('lists grade scales', async () => {
    const i18n = createI18n({ legacy: false, locale: 'en', messages: { en } })
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', name: 'Dashboard', component: { template: '<div />' } },
        { path: '/admin/grades', name: 'AdminGrades', component: AdminGrades },
      ],
    })
    await router.push({ name: 'AdminGrades' })
    const wrapper = mount(AdminGrades, { global: { plugins: [i18n, router] } })
    await flushPromises()
    expect(wrapper.get('[data-testid="admin-grades-scales"]').text()).toContain('US GPA 4.0 Scale')
  })
})
