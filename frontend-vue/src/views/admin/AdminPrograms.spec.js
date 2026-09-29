/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import { createRouter, createMemoryHistory } from 'vue-router'
import en from '@/locales/en.json'
import AdminPrograms from './AdminPrograms.vue'

const { mockGet, mockDelete, mockPost, mockPatch } = vi.hoisted(() => ({
  mockGet: vi.fn(),
  mockDelete: vi.fn(),
  mockPost: vi.fn(),
  mockPatch: vi.fn(),
}))
vi.mock('@/services/api', () => ({
  default: { get: mockGet, post: mockPost, patch: mockPatch, delete: mockDelete },
}))
vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: vi.fn(), error: vi.fn() }),
}))
vi.mock('@/composables/useConfirm', () => ({
  useConfirm: () => ({ confirm: vi.fn() }),
}))

let wrapper

function mountPage() {
  const i18n = createI18n({ legacy: false, locale: 'en', messages: { en } })
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', name: 'Dashboard', component: { template: '<div />' } },
        { path: '/help', name: 'HelpCenter', component: { template: '<div />' } },
      { path: '/admin/programs', name: 'AdminPrograms', component: AdminPrograms },
      {
        path: '/admin/programs/:id/destinations',
        name: 'AdminProgramDestinations',
        component: { template: '<div />' },
      },
    ],
  })
  return router.push({ name: 'AdminPrograms' }).then(() =>
    mount(AdminPrograms, {
      global: {
        plugins: [i18n, router],
        stubs: {
          Teleport: true,
        },
      },
    }),
  )
}

describe('AdminPrograms', () => {
  beforeEach(() => {
    mockGet.mockImplementation((url) => {
      if (url === '/api/programs/') {
        return Promise.resolve({
          data: {
            results: [
              {
                id: 3,
                name: 'Erasmus Spring',
                description: 'Semester abroad',
                is_active: true,
                eligibility_ruleset: null,
                application_window_open: true,
                enrollment_capacity: null,
                application_form: 'form-1',
                field_requirements: [],
                field_requirement_catalog: {
                  profile: ['clabe', 'bank_institution'],
                  application: ['host_institution'],
                  form: ['motivation_letter'],
                },
              },
            ],
          },
        })
      }
      if (url === '/api/application-forms/form-types/') {
        return Promise.resolve({
          data: {
            results: [
              {
                id: 'form-1',
                name: 'Exchange form',
                schema: { properties: { motivation_letter: { type: 'string' } } },
              },
            ],
          },
        })
      }
      if (url === '/api/users/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/document-types/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/workflow-versions/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/eligibility-rulesets/') {
        return Promise.resolve({
          data: {
            results: [{ id: 'rs-1', name: 'GPA overlay', is_active: true }],
          },
        })
      }
      if (String(url).includes('/deletion-impact/')) {
        return Promise.resolve({
          data: {
            program: { id: '3', name: 'Erasmus Spring' },
            can_delete: true,
            related: [
              { model: 'exchange.application', label: 'Applications', count: 2 },
              { model: 'documents.document', label: 'Documents', count: 4 },
            ],
            protected: [],
            total_related: 6,
          },
        })
      }
      return Promise.resolve({ data: { results: [] } })
    })
    mockDelete.mockResolvedValue({ status: 204 })
  })

  afterEach(() => {
    wrapper?.unmount()
    wrapper = undefined
  })

  it('shows eligibility rulesets in the program editor', async () => {
    wrapper = await mountPage()
    await flushPromises()
    await wrapper.get('[data-testid="admin-programs-table"]').find('button').trigger('click')
    await flushPromises()
    const select = wrapper.get('[data-testid="admin-program-eligibility-ruleset"]')
    expect(select.exists()).toBe(true)
    expect(select.text()).toContain('GPA overlay')
    expect(wrapper.find('[data-testid="admin-program-field-requirements"]').exists()).toBe(true)
  })

  it('offers dynamic form keys when source is form', async () => {
    wrapper = await mountPage()
    await flushPromises()
    await wrapper.get('[data-testid="admin-programs-table"]').find('button').trigger('click')
    await flushPromises()
    await wrapper.get('[data-testid="admin-program-add-field-req"]').trigger('click')
    const sourceSelect = wrapper.get('[data-testid="admin-program-field-source"]')
    await sourceSelect.setValue('form')
    await flushPromises()
    const keySelect = wrapper.get('[data-testid="admin-program-field-key"]')
    expect(keySelect.text()).toContain('motivation_letter')
    expect(sourceSelect.text()).toContain('Form')
  })

  it('shows related cascade data in the delete modal then deletes', async () => {
    wrapper = await mountPage()
    await flushPromises()
    const deleteBtn = wrapper
      .get('[data-testid="admin-programs-table"]')
      .findAll('button')
      .find((btn) => btn.text().includes('Delete'))
    expect(deleteBtn).toBeTruthy()
    await deleteBtn.trigger('click')
    await flushPromises()

    expect(mockGet).toHaveBeenCalledWith('/api/programs/3/deletion-impact/')
    const impact = wrapper.get('[data-testid="admin-program-delete-impact"]')
    expect(impact.text()).toContain('Applications')
    expect(impact.text()).toContain('2')
    expect(impact.text()).toContain('Documents')
    expect(impact.text()).toContain('4')

    await wrapper.get('[data-testid="form-modal-submit"]').trigger('click')
    await flushPromises()
    expect(mockDelete).toHaveBeenCalledWith('/api/programs/3/')
  })
})
