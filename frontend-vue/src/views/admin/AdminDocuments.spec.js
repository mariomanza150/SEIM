/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import { createRouter, createMemoryHistory } from 'vue-router'
import en from '@/locales/en.json'
import AdminDocuments from './AdminDocuments.vue'

const { mockGet, mockPost } = vi.hoisted(() => ({
  mockGet: vi.fn(),
  mockPost: vi.fn(),
}))
vi.mock('@/services/api', () => ({ default: { get: mockGet, post: mockPost, patch: vi.fn(), delete: vi.fn() } }))
vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: vi.fn(), error: vi.fn() }),
}))

describe('AdminDocuments', () => {
  beforeEach(() => {
    mockGet.mockResolvedValue({
      data: {
        results: [
          {
            id: 9,
            name: 'Learning Agreement',
            slug: 'learning_agreement',
            submission_mode: 'template_download',
            has_template: true,
            accepted_extensions: 'pdf,docx',
            max_file_size_mb: 5,
            requirement_count: 2,
          },
        ],
      },
    })
  })

  it('lists document types and links to the editor', async () => {
    const i18n = createI18n({ legacy: false, locale: 'en', messages: { en } })
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', name: 'Dashboard', component: { template: '<div />' } },
        { path: '/admin/documents', name: 'AdminDocuments', component: AdminDocuments },
        { path: '/admin/documents/:id', name: 'AdminDocumentTypeEdit', component: { template: '<div />' } },
      ],
    })
    await router.push({ name: 'AdminDocuments' })
    const wrapper = mount(AdminDocuments, { global: { plugins: [i18n, router] } })
    await flushPromises()
    expect(wrapper.get('[data-testid="admin-documents-table"]').text()).toContain('Learning Agreement')
    expect(wrapper.get('[data-testid="admin-documents-open-editor"]').attributes('href')).toBe('/admin/documents/9')
  })
})
