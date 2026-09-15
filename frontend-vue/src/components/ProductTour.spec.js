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
  tourIdForRole,
} from '@/utils/tourDefinitions'
import ProductTour from '@/components/ProductTour.vue'

const authStoreMock = {
  isAuthenticated: true,
  user: { id: 42, email: 'student@test.com', role: 'student' },
  isAdmin: false,
  canUseStaffReviewQueue: false,
  canUsePartnerPortal: false,
}

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => authStoreMock,
}))

vi.mock('vue-router', () => ({
  useRoute: () => ({ name: 'Dashboard' }),
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
    useProductTour().closeTour()
    authStoreMock.user = { id: 42, email: 'student@test.com', role: 'student' }
    authStoreMock.isAuthenticated = true
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
    useProductTour().openTour({ role: 'student', tourId })
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
})
