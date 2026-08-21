/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import { createRouter, createMemoryHistory } from 'vue-router'
import en from '@/locales/en.json'
import AdminDocumentTypeEdit from './AdminDocumentTypeEdit.vue'

const { mockGet } = vi.hoisted(() => ({ mockGet: vi.fn() }))
vi.mock('@/services/api', () => ({
  default: { get: mockGet, patch: vi.fn(), post: vi.fn(), delete: vi.fn() },
}))
vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: vi.fn(), error: vi.fn() }),
}))
vi.mock('@/composables/useConfirm', () => ({
  useConfirm: () => ({ confirm: vi.fn() }),
}))

describe('AdminDocumentTypeEdit', () => {
  beforeEach(() => {
    mockGet.mockImplementation((url) => {
      if (url === '/api/document-types/9/') {
        return Promise.resolve({
          data: {
            id: 9,
            name: 'Transcript',
            slug: 'transcript',
            program_requirements: [
              {
                id: 1,
                program: 'p1',
                program_name: 'Erasmus',
                is_required: true,
                required_from_status: null,
              },
            ],
          },
        })
      }
      if (url.startsWith('/api/programs/')) {
        return Promise.resolve({ data: { results: [{ id: 'p1', name: 'Erasmus' }] } })
      }
      if (url === '/api/document-types/merge-fields/') {
        return Promise.resolve({ data: { fields: [] } })
      }
      return Promise.resolve({ data: {} })
    })
  })

  it('shows a required-from select instead of a required checkbox', async () => {
    const i18n = createI18n({ legacy: false, locale: 'en', messages: { en } })
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', name: 'Dashboard', component: { template: '<div />' } },
        { path: '/admin/documents/:id', name: 'AdminDocumentTypeEdit', component: AdminDocumentTypeEdit },
      ],
    })
    await router.push({ name: 'AdminDocumentTypeEdit', params: { id: '9' } })
    const wrapper = mount(AdminDocumentTypeEdit, { global: { plugins: [i18n, router] } })
    await flushPromises()
    const select = wrapper.get('[data-testid="admin-document-required-from"]')
    expect(select.element.value).toBe('submitted')
    expect(select.text()).toContain(i18n.global.t('adminDocuments.req.optionalThroughout'))
    expect(wrapper.find('[data-testid="admin-document-requirements"] input.form-check-input').exists()).toBe(false)
  })
})
