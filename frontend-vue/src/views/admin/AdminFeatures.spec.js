/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import AdminFeatures from './AdminFeatures.vue'
import i18n, { setAppLocale } from '@/i18n'
import api from '@/services/api'

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
    patch: vi.fn(),
  },
}))

vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: vi.fn(), error: vi.fn() }),
}))

vi.mock('@/composables/useFeatures', async () => {
  const { ref } = await import('vue')
  const features = ref({
    scholarships_enabled: true,
    document_version_history_enabled: true,
    document_version_history_student: false,
    document_version_history_coordinator: true,
    document_version_history_admin: true,
    updated_at: '2026-01-01T00:00:00Z',
  })
  return {
    useFeatures: () => ({
      features,
      scholarshipsEnabled: ref(true),
      documentVersionHistoryEnabled: ref(true),
      loadFeatures: vi.fn(async () => {
        const { data } = await api.get('/api/features/')
        features.value = data
        return data
      }),
      updateFeatures: vi.fn(async (payload) => {
        const { data } = await api.patch('/api/features/', payload)
        features.value = data
        return data
      }),
    }),
  }
})

function makeRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', name: 'Dashboard', component: { template: '<div />' } },
      { path: '/admin/features', name: 'AdminFeatures', component: AdminFeatures },
    ],
  })
}

describe('AdminFeatures', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    setAppLocale('en')
    vi.clearAllMocks()
    api.get.mockResolvedValue({
      data: {
        scholarships_enabled: true,
        document_version_history_enabled: true,
        document_version_history_student: false,
        document_version_history_coordinator: true,
        document_version_history_admin: true,
        updated_at: '2026-01-01T00:00:00Z',
      },
    })
    api.patch.mockResolvedValue({
      data: {
        scholarships_enabled: false,
        document_version_history_enabled: true,
        document_version_history_student: false,
        document_version_history_coordinator: true,
        document_version_history_admin: true,
        updated_at: '2026-01-02T00:00:00Z',
      },
    })
  })

  it('loads and toggles scholarships_enabled', async () => {
    const router = makeRouter()
    await router.push({ name: 'AdminFeatures' })
    const wrapper = mount(AdminFeatures, {
      global: {
        plugins: [createPinia(), i18n, router],
        stubs: {
          PageHeader: { template: '<div><slot /><slot name="breadcrumb" /><slot name="actions" /></div>' },
          PageBreadcrumb: true,
          PageStateShell: { template: '<div><slot /></div>' },
        },
      },
    })
    await flushPromises()

    expect(wrapper.find('[data-testid="admin-features-page"]').exists()).toBe(true)
    const toggle = wrapper.get('[data-testid="scholarships-enabled-switch"]')
    expect(toggle.element.checked).toBe(true)

    await toggle.setValue(false)
    await flushPromises()

    expect(api.patch).toHaveBeenCalledWith(
      '/api/features/',
      expect.objectContaining({ scholarships_enabled: false }),
    )
    wrapper.unmount()
  })

  it('renders document version history role toggles', async () => {
    const router = makeRouter()
    await router.push({ name: 'AdminFeatures' })
    const wrapper = mount(AdminFeatures, {
      global: {
        plugins: [createPinia(), i18n, router],
        stubs: {
          PageHeader: { template: '<div><slot /><slot name="breadcrumb" /><slot name="actions" /></div>' },
          PageBreadcrumb: true,
          PageStateShell: { template: '<div><slot /></div>' },
        },
      },
    })
    await flushPromises()
    expect(wrapper.find('[data-testid="admin-features-doc-history-card"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="doc-history-student-switch"]').exists()).toBe(true)
    wrapper.unmount()
  })
})
