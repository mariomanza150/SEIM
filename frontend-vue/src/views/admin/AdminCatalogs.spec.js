/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import { createRouter, createMemoryHistory } from 'vue-router'
import en from '@/locales/en.json'
import AdminCatalogs from './AdminCatalogs.vue'

const { mockGet, mockPost, mockPatch, mockDelete } = vi.hoisted(() => ({
  mockGet: vi.fn(),
  mockPost: vi.fn(),
  mockPatch: vi.fn(),
  mockDelete: vi.fn(),
}))
vi.mock('@/services/api', () => ({
  default: { get: mockGet, post: mockPost, patch: mockPatch, delete: mockDelete },
}))
vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: vi.fn(), error: vi.fn() }),
}))
vi.mock('@/composables/useConfirm', () => ({
  useConfirm: () => ({ confirm: vi.fn().mockResolvedValue(false) }),
}))

async function mountPage() {
  const i18n = createI18n({ legacy: false, locale: 'en', messages: { en } })
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', name: 'Dashboard', component: { template: '<div />' } },
      { path: '/admin/catalogs', name: 'AdminCatalogs', component: AdminCatalogs },
      { path: '/admin/programs', name: 'AdminPrograms', component: { template: '<div />' } },
      {
        path: '/admin/programs/:id/destinations',
        name: 'AdminProgramDestinations',
        component: { template: '<div />' },
      },
    ],
  })
  await router.push({ name: 'AdminCatalogs' })
  const wrapper = mount(AdminCatalogs, { global: { plugins: [i18n, router] } })
  await flushPromises()
  return wrapper
}

describe('AdminCatalogs', () => {
  beforeEach(() => {
    mockGet.mockImplementation((url) => {
      if (url === '/api/accounts/catalogs/academic-levels/') {
        return Promise.resolve({
          data: { results: [{ id: 'lvl-1', name: 'Bachelor', code: 'B', ordering: 0, is_active: true }] },
        })
      }
      if (url === '/api/accounts/catalogs/schools/') {
        return Promise.resolve({
          data: {
            results: [{ id: 'sch-1', name: 'Engineering Faculty', code: 'ENG', ordering: 1, is_active: true }],
          },
        })
      }
      if (url === '/api/programs/') {
        return Promise.resolve({
          data: { results: [{ id: 42, name: 'Erasmus 2026' }] },
        })
      }
      if (url === '/api/accounts/catalogs/allowed-email-domains/') {
        return Promise.resolve({
          data: {
            results: [{ id: 'dom-1', name: 'uanl.edu.mx', code: 'uanl', ordering: 0, is_active: true }],
          },
        })
      }
      return Promise.resolve({ data: { results: [] } })
    })
  })

  it('lists a school name on the schools tab', async () => {
    const wrapper = await mountPage()
    await wrapper.get('[data-testid="admin-catalogs-tabs"] [data-tab="schools"]').trigger('click')
    await flushPromises()
    expect(wrapper.get('[data-testid="admin-catalogs-table"]').text()).toContain('Engineering Faculty')
  })

  it('links destinations to the program destinations page', async () => {
    const wrapper = await mountPage()
    await wrapper.get('[data-testid="admin-catalogs-tabs"] [data-tab="destinations"]').trigger('click')
    await flushPromises()
    expect(wrapper.get('[data-testid="admin-catalogs-destinations"] a').attributes('href')).toBe(
      '/admin/programs/42/destinations',
    )
  })

  it('wires create-form labels and disables empty-row save', async () => {
    const wrapper = await mountPage()
    expect(wrapper.get('label[for="catalog-create-name"]').exists()).toBe(true)
    expect(wrapper.get('#catalog-create-name').element.tagName).toBe('INPUT')
    const save = wrapper.get('[data-testid="admin-catalogs-save-row"]')
    expect(save.attributes('disabled')).toBeUndefined()
    await wrapper.get('[data-testid="admin-catalogs-table"] input').setValue('')
    expect(wrapper.get('[data-testid="admin-catalogs-save-row"]').attributes('disabled')).toBeDefined()
  })

  it('renders allowed email domains without i18n linked-message errors', async () => {
    const wrapper = await mountPage()
    await wrapper.get('[data-testid="admin-catalogs-tabs"] [data-tab="domains"]').trigger('click')
    await flushPromises()
    expect(wrapper.get('[data-testid="admin-catalogs-table"]').text()).toContain('uanl.edu.mx')
    expect(wrapper.text()).toContain('@')
  })
})
