/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import { createRouter, createMemoryHistory } from 'vue-router'
import en from '@/locales/en.json'
import AdminDynformEditor from './AdminDynformEditor.vue'

const { mockGet, mockPatch } = vi.hoisted(() => ({
  mockGet: vi.fn(),
  mockPatch: vi.fn(),
}))
vi.mock('@/services/api', () => ({ default: { get: mockGet, patch: mockPatch } }))

describe('AdminDynformEditor', () => {
  beforeEach(() => {
    mockGet.mockResolvedValue({
      data: {
        id: 7,
        name: 'Exchange form',
        description: '',
        form_type: 'application',
        is_active: true,
        schema: { type: 'object', properties: {}, required: [] },
        ui_schema: {},
        step_definitions: [],
      },
    })
    mockPatch.mockResolvedValue({ data: {} })
  })

  it('adds a field, previews it, and saves the schema', async () => {
    const i18n = createI18n({ legacy: false, locale: 'en', messages: { en } })
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/admin/dynforms', name: 'AdminDynforms', component: { template: '<div />' } },
        { path: '/admin/dynforms/:id', name: 'AdminDynformEditor', component: AdminDynformEditor },
      ],
    })
    await router.push({ name: 'AdminDynformEditor', params: { id: '7' } })
    const wrapper = mount(AdminDynformEditor, { global: { plugins: [i18n, router] } })
    await flushPromises()

    await wrapper.get('[data-testid="dynforms-add-email"]').trigger('click')
    expect(wrapper.get('[data-testid="dynforms-canvas"]').text()).toContain('Email')
    expect(wrapper.get('[data-testid="dynforms-preview"]').text()).toContain('Email')

    await wrapper.get('[data-testid="dynforms-save"]').trigger('click')
    await flushPromises()
    expect(mockPatch).toHaveBeenCalled()
    const payload = mockPatch.mock.calls[0][1]
    const fieldId = Object.keys(payload.schema.properties)[0]
    expect(payload.schema.properties[fieldId].format).toBe('email')
  })
})
