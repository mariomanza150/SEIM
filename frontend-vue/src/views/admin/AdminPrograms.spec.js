/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import { createRouter, createMemoryHistory } from 'vue-router'
import en from '@/locales/en.json'
import AdminPrograms from './AdminPrograms.vue'

const { mockGet } = vi.hoisted(() => ({ mockGet: vi.fn() }))
vi.mock('@/services/api', () => ({ default: { get: mockGet, post: vi.fn(), patch: vi.fn(), delete: vi.fn() } }))
vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: vi.fn(), error: vi.fn() }),
}))
vi.mock('@/composables/useConfirm', () => ({
  useConfirm: () => ({ confirm: vi.fn() }),
}))

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
              },
            ],
          },
        })
      }
      if (url === '/api/application-forms/form-types/') {
        return Promise.resolve({ data: { results: [] } })
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
      return Promise.resolve({ data: { results: [] } })
    })
  })

  it('shows eligibility rulesets in the program editor', async () => {
    const i18n = createI18n({ legacy: false, locale: 'en', messages: { en } })
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', name: 'Dashboard', component: { template: '<div />' } },
        { path: '/admin/programs', name: 'AdminPrograms', component: AdminPrograms },
        {
          path: '/admin/programs/:id/destinations',
          name: 'AdminProgramDestinations',
          component: { template: '<div />' },
        },
      ],
    })
    await router.push({ name: 'AdminPrograms' })
    const wrapper = mount(AdminPrograms, { global: { plugins: [i18n, router] } })
    await flushPromises()
    await wrapper.get('[data-testid="admin-programs-table"]').find('button').trigger('click')
    await flushPromises()
    const select = wrapper.get('[data-testid="admin-program-eligibility-ruleset"]')
    expect(select.exists()).toBe(true)
    expect(select.text()).toContain('GPA overlay')
  })
})
