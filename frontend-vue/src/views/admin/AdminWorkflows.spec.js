/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import { createRouter, createMemoryHistory } from 'vue-router'
import en from '@/locales/en.json'
import AdminWorkflows from './AdminWorkflows.vue'

const { mockGet, mockPost } = vi.hoisted(() => ({
  mockGet: vi.fn(),
  mockPost: vi.fn(),
}))
vi.mock('@/services/api', () => ({
  default: { get: mockGet, post: mockPost, patch: vi.fn(), delete: vi.fn() },
}))
vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: vi.fn(), error: vi.fn() }),
}))

async function mountPage() {
  const i18n = createI18n({ legacy: false, locale: 'en', messages: { en } })
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', name: 'Dashboard', component: { template: '<div />' } },
      { path: '/admin/workflows', name: 'AdminWorkflows', component: AdminWorkflows },
      {
        path: '/admin/workflows/:id',
        name: 'AdminWorkflowEditor',
        component: { template: '<div />' },
      },
    ],
  })
  await router.push({ name: 'AdminWorkflows' })
  const wrapper = mount(AdminWorkflows, { global: { plugins: [i18n, router] } })
  await flushPromises()
  return wrapper
}

describe('AdminWorkflows', () => {
  beforeEach(() => {
    mockGet.mockResolvedValue({
      data: {
        results: [
          {
            id: 'wf-1',
            name: 'Exchange flow',
            description: 'Main BPMN',
            is_active: true,
            latest_published_version: { version: 2 },
          },
        ],
      },
    })
    mockPost.mockResolvedValue({ data: { id: 'wf-2', name: 'New flow' } })
  })

  it('lists workflows and links to the BPMN editor', async () => {
    const wrapper = await mountPage()
    expect(wrapper.get('[data-testid="admin-workflows-table"]').text()).toContain('Exchange flow')
    expect(wrapper.get('[data-testid="admin-workflows-table"]').text()).toContain('v2')
    expect(wrapper.get('[data-testid="admin-workflows-open-editor"]').attributes('href')).toBe(
      '/admin/workflows/wf-1',
    )
  })

  it('filters by active flag when the select changes', async () => {
    const wrapper = await mountPage()
    mockGet.mockClear()
    mockGet.mockResolvedValue({ data: { results: [] } })
    const select = wrapper.get('[data-testid="admin-workflows-filters"] select')
    await select.setValue('true')
    await flushPromises()
    expect(mockGet).toHaveBeenCalledWith('/api/workflows/', {
      params: { ordering: 'name', is_active: 'true' },
    })
  })

  it('creates a workflow from the modal', async () => {
    const wrapper = await mountPage()
    const createBtn = wrapper.findAll('button').find((b) => /new workflow/i.test(b.text()))
    expect(createBtn).toBeTruthy()
    await createBtn.trigger('click')
    await wrapper.get('.modal input.form-control').setValue('Nomination flow')
    await wrapper.get('.modal-footer .btn-primary').trigger('click')
    await flushPromises()
    expect(mockPost).toHaveBeenCalledWith('/api/workflows/', {
      name: 'Nomination flow',
      description: '',
      is_active: true,
    })
  })
})
