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

async function mountList(results) {
  mockGet.mockResolvedValue({ data: { results } })
  const i18n = createI18n({ legacy: false, locale: 'en', messages: { en } })
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', name: 'Dashboard', component: { template: '<div />' } },
      { path: '/help', name: 'HelpCenter', component: { template: '<div />' } },
      { path: '/admin/documents', name: 'AdminDocuments', component: AdminDocuments },
      { path: '/admin/documents/:id', name: 'AdminDocumentTypeEdit', component: { template: '<div />' } },
    ],
  })
  await router.push({ name: 'AdminDocuments' })
  const wrapper = mount(AdminDocuments, { global: { plugins: [i18n, router] } })
  await flushPromises()
  return { wrapper, i18n }
}

describe('AdminDocuments', () => {
  beforeEach(() => {
    mockGet.mockReset()
  })

  it('lists document types and links to the editor', async () => {
    const { wrapper } = await mountList([
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
    ])
    expect(wrapper.get('[data-testid="admin-documents-table"]').text()).toContain('Learning Agreement')
    expect(wrapper.get('[data-testid="admin-documents-open-editor"]').attributes('href')).toBe('/admin/documents/9')
  })

  it('flags download_only and template_download types missing a template file', async () => {
    const { wrapper, i18n } = await mountList([
      {
        id: 1,
        name: 'Missing Download Only',
        slug: 'missing_dl',
        submission_mode: 'download_only',
        has_template: false,
        requirement_count: 0,
      },
      {
        id: 2,
        name: 'Missing Template Download',
        slug: 'missing_td',
        submission_mode: 'template_download',
        has_template: false,
        requirement_count: 0,
      },
      {
        id: 3,
        name: 'Upload Type',
        slug: 'upload_type',
        submission_mode: 'upload',
        has_template: false,
        requirement_count: 0,
      },
      {
        id: 4,
        name: 'Has Template',
        slug: 'has_tpl',
        submission_mode: 'download_only',
        has_template: true,
        requirement_count: 0,
      },
    ])
    const badges = wrapper.findAll(
      '[data-testid="admin-documents-table"] [data-testid="admin-documents-missing-template"]',
    )
    expect(badges).toHaveLength(2)
    expect(badges[0].text()).toBe(i18n.global.t('adminDocuments.missingTemplateBadge'))
    expect(wrapper.text()).toContain('Missing Download Only')
    expect(wrapper.text()).toContain('Missing Template Download')
    expect(
      wrapper
        .findAll('[data-testid="admin-documents-table"] tr')
        .filter((row) => row.text().includes('Upload Type'))[0]
        .find('[data-testid="admin-documents-missing-template"]')
        .exists(),
    ).toBe(false)
  })
})
