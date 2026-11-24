/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { defineComponent, h, nextTick } from 'vue'
import { mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import { useStartWalkthrough } from '@/composables/useStartWalkthrough'
import { useProductTour } from '@/composables/useProductTour'

const authStoreMock = {
  isAuthenticated: true,
  user: { id: 7, email: 'student@example.edu' },
  isAdmin: false,
  canUseStaffReviewQueue: false,
  canUsePartnerPortal: false,
}

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => authStoreMock,
}))

function mountApi(routes = []) {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', name: 'Dashboard', component: { template: '<div />' } },
      { path: '/applications', name: 'Applications', component: { template: '<div />' } },
      { path: '/documents', name: 'Documents', component: { template: '<div />' } },
      ...routes,
    ],
  })
  const pinia = createPinia()
  setActivePinia(pinia)
  const Host = defineComponent({
    setup() {
      return useStartWalkthrough()
    },
    render: () => h('div'),
  })
  const wrapper = mount(Host, {
    global: { plugins: [pinia, router] },
  })
  return { api: wrapper.vm, router, pinia }
}

describe('useStartWalkthrough', () => {
  beforeEach(() => {
    authStoreMock.isAuthenticated = true
    authStoreMock.isAdmin = false
    authStoreMock.canUseStaffReviewQueue = false
    authStoreMock.canUsePartnerPortal = false
    authStoreMock.user = { id: 7, email: 'student@example.edu' }
  })

  it('opens a walkthrough on the current page', async () => {
    const { api, router } = mountApi()
    await router.push({ name: 'Applications' })
    await router.isReady()
    const ok = await api.startWalkthrough('applications', { force: true })
    expect(ok).toBe(true)
    expect(useProductTour().open.value).toBe(true)
    expect(useProductTour().pageId.value).toBe('applications')
  })

  it('requests a pending tour and navigates when off-page', async () => {
    const { api, router } = mountApi()
    await router.push({ name: 'Dashboard' })
    await router.isReady()
    const ok = await api.startWalkthrough('documents', { force: true })
    expect(ok).toBe(true)
    await nextTick()
    expect(router.currentRoute.value.name).toBe('Documents')
    expect(useProductTour().pendingPageId.value).toBe('documents')
  })

  it('resolves walkthrough page from a help article', async () => {
    const { api } = mountApi()
    expect(api.resolvePageTourFromHelp({
      contextual_keys: ['Documents'],
      topic: 'documents',
    })).toBe('documents')
  })
})
