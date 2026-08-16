/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import { createRouter, createMemoryHistory } from 'vue-router'
import en from '@/locales/en.json'
import AdminDynforms from './AdminDynforms.vue'

const { mockGet } = vi.hoisted(() => ({ mockGet: vi.fn() }))
vi.mock('@/services/api', () => ({ default: { get: mockGet, post: vi.fn(), delete: vi.fn() } }))

describe('AdminDynforms', () => {
  beforeEach(() => {
    mockGet.mockResolvedValue({
      data: {
        results: [{ id: 7, name: 'Exchange form', form_type: 'application', field_count: 3, description: '' }],
      },
    })
  })

  it('lists form types and opens the Vue visual builder', async () => {
    const i18n = createI18n({ legacy: false, locale: 'en', messages: { en } })
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', name: 'Dashboard', component: { template: '<div />' } },
        { path: '/admin/dynforms', name: 'AdminDynforms', component: AdminDynforms },
        { path: '/admin/dynforms/:id', name: 'AdminDynformEditor', component: { template: '<div />' } },
      ],
    })
    await router.push({ name: 'AdminDynforms' })
    const wrapper = mount(AdminDynforms, { global: { plugins: [i18n, router] } })
    await flushPromises()
    expect(wrapper.get('[data-testid="dynforms-table"]').text()).toContain('Exchange form')
    expect(wrapper.get('[data-testid="dynforms-open-builder"]').attributes('href')).toBe('/admin/dynforms/7')
    expect(wrapper.find('[data-testid="dynforms-legacy-builder"]').exists()).toBe(false)
  })
})
