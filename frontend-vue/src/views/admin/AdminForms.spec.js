/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import { createRouter, createMemoryHistory } from 'vue-router'
import en from '@/locales/en.json'
import AdminForms from './AdminForms.vue'

const { mockGet, mockPost, mockConfirm } = vi.hoisted(() => ({
  mockGet: vi.fn(),
  mockPost: vi.fn(),
  mockConfirm: vi.fn(),
}))
vi.mock('@/services/api', () => ({
  default: { get: mockGet, post: mockPost, patch: vi.fn(), delete: vi.fn() },
}))
vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: vi.fn(), error: vi.fn() }),
}))
vi.mock('@/composables/useConfirm', () => ({
  useConfirm: () => ({ confirm: mockConfirm }),
}))

async function mountPage() {
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
  return wrapper
}

describe('AdminForms', () => {
  beforeEach(() => {
    mockGet.mockResolvedValue({
      data: {
        results: [
          {
            id: 7,
            name: 'Exchange form',
            form_type: 'application',
            field_count: 3,
            description: '',
            is_active: true,
          },
        ],
      },
    })
    mockPost.mockResolvedValue({ data: { id: 8 } })
    mockConfirm.mockResolvedValue(false)
  })

  it('links each form type to the Vue visual builder', async () => {
    const wrapper = await mountPage()
    expect(wrapper.get('[data-testid="admin-forms-table"]').text()).toContain('Exchange form')
    expect(wrapper.get('[data-testid="admin-forms-open-builder"]').attributes('href')).toBe(
      '/admin/dynforms/7',
    )
  })

  it('refetches when form type filter changes', async () => {
    const wrapper = await mountPage()
    mockGet.mockClear()
    mockGet.mockResolvedValue({ data: { results: [] } })
    const typeSelect = wrapper
      .get('[data-testid="admin-forms-filters"]')
      .findAll('select')
      .at(0)
    await typeSelect.setValue('application')
    await flushPromises()
    expect(mockGet).toHaveBeenCalledWith('/api/application-forms/form-types/', {
      params: { ordering: 'name', form_type: 'application' },
    })
  })

  it('creates a form type from the editor modal', async () => {
    const wrapper = await mountPage()
    const createBtn = wrapper.findAll('button').find((b) => /new form/i.test(b.text()))
    expect(createBtn).toBeTruthy()
    await createBtn.trigger('click')
    expect(wrapper.find('.modal').exists()).toBe(true)
    await wrapper.get('.modal input.form-control').setValue('Mobility form')
    await wrapper.get('.modal-footer .btn-primary').trigger('click')
    await flushPromises()
    expect(mockPost).toHaveBeenCalled()
    const [, payload] = mockPost.mock.calls[0]
    expect(payload.name).toBe('Mobility form')
    expect(payload.form_type).toBe('application')
    expect(payload.schema).toEqual({ type: 'object', properties: {}, required: [] })
  })
})
