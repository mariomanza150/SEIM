/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import { createRouter, createMemoryHistory } from 'vue-router'
import en from '@/locales/en.json'
import AdminForms from './AdminForms.vue'

const { mockGet } = vi.hoisted(() => ({ mockGet: vi.fn() }))
vi.mock('@/services/api', () => ({ default: { get: mockGet, post: vi.fn(), patch: vi.fn(), delete: vi.fn() } }))
vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: vi.fn(), error: vi.fn() }),
}))
vi.mock('@/composables/useConfirm', () => ({
  useConfirm: () => ({ confirm: vi.fn() }),
}))

describe('AdminForms', () => {
  beforeEach(() => {
    mockGet.mockResolvedValue({
      data: {
        results: [{ id: 7, name: 'Exchange form', form_type: 'application', field_count: 3, description: '', is_active: true }],
      },
    })
  })

  it('links each form type to the Vue visual builder', async () => {
    const i18n = createI18n({ legacy: false, locale: 'en', messages: { en } })
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', name: 'Dashboard', component: { template: '<div />' } },
        { path: '/admin/forms', name: 'AdminForms', component: AdminForms },
        { path: '/admin/dynforms/:id', name: 'AdminDynformEditor', component: { template: '<div />' } },
      ],
    })
    await router.push({ name: 'AdminForms' })
    const wrapper = mount(AdminForms, { global: { plugins: [i18n, router] } })
    await flushPromises()
    expect(wrapper.get('[data-testid="admin-forms-table"]').text()).toContain('Exchange form')
    expect(wrapper.get('[data-testid="admin-forms-open-builder"]').attributes('href')).toBe('/admin/dynforms/7')
  })
})
