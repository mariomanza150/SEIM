/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import { createPinia, setActivePinia } from 'pinia'
import i18n, { setAppLocale } from '@/i18n'
import { useProductTour } from '@/composables/useProductTour'
import {
  clearTourCompletion,
  isTourCompleted,
  markTourCompleted,
  tourIdForPage,
  tourIdForRole,
} from '@/utils/tourDefinitions'
import ProductTour from '@/components/ProductTour.vue'

const authStoreMock = {
  isAuthenticated: true,
  user: { id: 42, email: 'student@example.edu', role: 'student' },
  isAdmin: false,
  canUseStaffReviewQueue: false,
  canUsePartnerPortal: false,
}

const routeMock = { name: 'Dashboard' }

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => authStoreMock,
}))

vi.mock('vue-router', () => ({
  useRoute: () => routeMock,
  useRouter: () => ({ push: vi.fn() }),
}))

vi.mock('@/services/uiPreferences', () => ({
  readStoredUiPreferences: () => ({ reduce_motion: false }),
}))

describe('ProductTour', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    setAppLocale('en')
    localStorage.clear()
    document.body.innerHTML = ''
    useProductTour().closeTour()
    authStoreMock.user = { id: 42, email: 'student@example.edu', role: 'student' }
    authStoreMock.isAuthenticated = true
    authStoreMock.isAdmin = false
    authStoreMock.canUseStaffReviewQueue = false
    authStoreMock.canUsePartnerPortal = false
    routeMock.name = 'Dashboard'
  })

  afterEach(() => {
    useProductTour().closeTour()
  })

  it('skips and marks tour complete', async () => {
    const wrapper = mount(ProductTour, {
      global: { plugins: [i18n, createPinia()] },
      attachTo: document.body,
    })
    setActivePinia(wrapper.vm.$.appContext.config.globalProperties.$pinia)
    const tourId = tourIdForRole('student')
    useProductTour().openTour({ role: 'student', tourId, pageId: 'dashboard' })
    await nextTick()
    await nextTick()
    expect(document.querySelector('[data-testid="product-tour"]')).toBeTruthy()
    document.querySelector('[data-testid="product-tour-skip"]').click()
    await nextTick()
    expect(isTourCompleted(42, tourId)).toBe(true)
    expect(useProductTour().open.value).toBe(false)
    wrapper.unmount()
  })

  it('replay event clears completion and reopens', async () => {
    const pinia = createPinia()
    setActivePinia(pinia)
    const wrapper = mount(ProductTour, {
      global: { plugins: [i18n, pinia] },
      attachTo: document.body,
    })
    const tourId = tourIdForRole('student')
    markTourCompleted(42, tourId)
    expect(isTourCompleted(42, tourId)).toBe(true)
    window.dispatchEvent(new CustomEvent('seim-replay-product-tour'))
    await nextTick()
    await nextTick()
    expect(isTourCompleted(42, tourId)).toBe(false)
    expect(useProductTour().open.value).toBe(true)
    clearTourCompletion(42, tourId)
    wrapper.unmount()
  })

  it('starts a page tour and skips missing targets when advancing', async () => {
    const fixtures = document.createElement('div')
    fixtures.innerHTML = `
      <div data-tour="applications-header"></div>
      <div data-tour="applications-filters"></div>
      <div data-tour="applications-list"></div>
    `
    document.body.appendChild(fixtures)
    for (const el of fixtures.querySelectorAll('[data-tour]')) {
      Object.defineProperty(el, 'getBoundingClientRect', {
        value: () => ({ width: 40, height: 20, top: 10, left: 10, bottom: 30, right: 50 }),
      })
    }

    const pinia = createPinia()
    setActivePinia(pinia)
    const wrapper = mount(ProductTour, {
      global: { plugins: [i18n, pinia] },
      attachTo: document.body,
    })
    routeMock.name = 'Applications'
    const tourId = tourIdForPage('applications', 'student')
    window.dispatchEvent(
      new CustomEvent('seim-start-page-tour', { detail: { pageId: 'applications', force: true } }),
    )
    await nextTick()
    await nextTick()
    expect(useProductTour().open.value).toBe(true)
    expect(useProductTour().pageId.value).toBe('applications')
    expect(document.querySelector('[data-testid="product-tour-title"]')?.textContent).toMatch(/Applications/i)
    // actions/tabs selectors are missing — progress total counts only mounted steps
    const progress = document.querySelector('[data-testid="product-tour-progress"]')?.textContent || ''
    expect(progress).toMatch(/Step 1 of 3/)
    document.querySelector('[data-testid="product-tour-next"]').click()
    await nextTick()
    // Skips missing actions/tabs and lands on filters
    expect(document.querySelector('[data-testid="product-tour-title"]')?.textContent).toMatch(/Filters/i)
    clearTourCompletion(42, tourId)
    wrapper.unmount()
    fixtures.remove()
  })
})
