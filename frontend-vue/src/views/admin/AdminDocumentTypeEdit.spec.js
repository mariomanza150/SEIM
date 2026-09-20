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

function mockDocumentTypePayload(overrides = {}) {
  return {
    id: 9,
    name: 'Transcript',
    slug: 'transcript',
    has_template: false,
    template_filename: '',
    program_requirements: [
      {
        id: 1,
        program: 'p1',
        program_name: 'Erasmus',
        is_required: true,
        required_from_status: null,
      },
    ],
    ...overrides,
  }
}

async function mountEditor() {
  const i18n = createI18n({ legacy: false, locale: 'en', messages: { en } })
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', name: 'Dashboard', component: { template: '<div />' } },
      { path: '/admin/documents', name: 'AdminDocuments', component: { template: '<div />' } },
      { path: '/admin/documents/:id', name: 'AdminDocumentTypeEdit', component: AdminDocumentTypeEdit },
    ],
  })
  await router.push({ name: 'AdminDocumentTypeEdit', params: { id: '9' } })
  const wrapper = mount(AdminDocumentTypeEdit, {
    global: {
      plugins: [i18n, router],
      stubs: { RouterLink: { template: '<a><slot /></a>' } },
    },
  })
  await flushPromises()
  return { wrapper, i18n }
}

describe('AdminDocumentTypeEdit', () => {
  beforeEach(() => {
    mockGet.mockImplementation((url) => {
      if (url === '/api/document-types/9/') {
        return Promise.resolve({ data: mockDocumentTypePayload() })
      }
      if (url.startsWith('/api/programs/')) {
        return Promise.resolve({ data: { results: [{ id: 'p1', name: 'Erasmus' }] } })
      }
      if (url === '/api/document-types/merge-fields/') {
        return Promise.resolve({
          data: {
            fields: [
              { name: 'StudentName', group: 'student', description: 'Full name' },
              { name: 'ProgramName', group: 'program', description: 'Program title' },
              { name: 'ApplicationId', group: 'application', description: 'Application id' },
            ],
          },
        })
      }
      if (url === '/api/document-types/file-type-families/') {
        return Promise.resolve({
          data: {
            results: [
              { id: 1, slug: 'pdf', name: 'PDF', extensions: 'pdf', aliases: '' },
              { id: 2, slug: 'image', name: 'Image', extensions: 'jpg,png', aliases: 'photo' },
            ],
          },
        })
      }
      return Promise.resolve({ data: {} })
    })
  })

  it('shows a required-from select instead of a required checkbox', async () => {
    const { wrapper, i18n } = await mountEditor()
    const select = wrapper.get('[data-testid="admin-document-required-from"]')
    expect(select.element.value).toBe('submitted')
    expect(select.text()).toContain(i18n.global.t('adminDocuments.req.optionalThroughout'))
    expect(wrapper.find('[data-testid="admin-document-requirements"] input.form-check-input').exists()).toBe(false)
  })

  it('opens identity, template, and workflow by default; keeps instructions and constraints collapsed', async () => {
    const { wrapper } = await mountEditor()

    expect(
      wrapper
        .get('[data-testid="admin-document-section-identity"] [data-testid="collapsible-card-toggle"]')
        .attributes('aria-expanded'),
    ).toBe('true')
    expect(
      wrapper
        .get('[data-testid="admin-document-section-template"] [data-testid="collapsible-card-toggle"]')
        .attributes('aria-expanded'),
    ).toBe('true')
    expect(
      wrapper
        .get('[data-testid="admin-document-requirements"] [data-testid="collapsible-card-toggle"]')
        .attributes('aria-expanded'),
    ).toBe('true')
    expect(
      wrapper
        .get('[data-testid="admin-document-section-instructions"] [data-testid="collapsible-card-toggle"]')
        .attributes('aria-expanded'),
    ).toBe('false')
    expect(
      wrapper
        .get('[data-testid="admin-document-section-constraints"] [data-testid="collapsible-card-toggle"]')
        .attributes('aria-expanded'),
    ).toBe('false')
    expect(wrapper.find('[data-testid="admin-document-section-instructions"] [data-testid="collapsible-card-panel"]').exists()).toBe(
      false,
    )
  })

  it('opens merge fields when a template is attached; keeps nested groups collapsed until toggled', async () => {
    mockGet.mockImplementation((url) => {
      if (url === '/api/document-types/9/') {
        return Promise.resolve({
          data: mockDocumentTypePayload({
            has_template: true,
            template_filename: 'letter.docx',
            program_requirements: [],
          }),
        })
      }
      if (url.startsWith('/api/programs/')) {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/document-types/merge-fields/') {
        return Promise.resolve({
          data: {
            fields: [
              { name: 'StudentName', group: 'student', description: 'Full name' },
              { name: 'ProgramName', group: 'program', description: 'Program title' },
            ],
          },
        })
      }
      if (url === '/api/document-types/file-type-families/') {
        return Promise.resolve({ data: { results: [] } })
      }
      return Promise.resolve({ data: {} })
    })

    const { wrapper } = await mountEditor()

    const mergeToggle = wrapper.get(
      '[data-testid="admin-document-section-merge-fields"] [data-testid="collapsible-card-toggle"]',
    )
    expect(mergeToggle.attributes('aria-expanded')).toBe('true')
    expect(wrapper.get('[data-testid="admin-document-section-merge-fields"]').text()).toContain('2')

    const studentGroup = wrapper.get('[data-testid="admin-document-merge-group-student"]')
    expect(studentGroup.find('[data-testid="collapsible-card-toggle"]').attributes('aria-expanded')).toBe(
      'false',
    )
    expect(studentGroup.find('[data-testid="collapsible-card-panel"]').exists()).toBe(false)

    await studentGroup.find('[data-testid="collapsible-card-toggle"]').trigger('click')
    expect(studentGroup.find('[data-testid="collapsible-card-panel"]').exists()).toBe(true)
    expect(studentGroup.text()).toContain('StudentName')
  })

  it('keeps merge fields collapsed when no template is attached', async () => {
    const { wrapper } = await mountEditor()
    expect(
      wrapper
        .get('[data-testid="admin-document-section-merge-fields"] [data-testid="collapsible-card-toggle"]')
        .attributes('aria-expanded'),
    ).toBe('false')
  })
})
