/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import { createPinia, setActivePinia } from 'pinia'
import i18n, { setAppLocale } from '@/i18n'
import { useCommandPalette } from '@/composables/useCommandPalette'
import CommandPalette from '@/components/CommandPalette.vue'

const push = vi.fn(() => Promise.resolve())

vi.mock('vue-router', () => ({
  useRouter: () => ({ push }),
  useRoute: () => ({ name: 'Dashboard', params: {}, query: {} }),
}))

const authStoreMock = {
  isAuthenticated: true,
  isAdmin: false,
  canUseStaffReviewQueue: false,
  canUsePartnerPortal: false,
  logout: vi.fn().mockResolvedValue(undefined),
}

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => authStoreMock,
}))

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
    patch: vi.fn(),
  },
}))

describe('CommandPalette', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    setAppLocale('en')
    useCommandPalette().closePalette()
    push.mockClear()
    authStoreMock.isAuthenticated = true
    authStoreMock.isAdmin = false
    authStoreMock.canUseStaffReviewQueue = false
    authStoreMock.canUsePartnerPortal = false
  })

  afterEach(() => {
    useCommandPalette().closePalette()
  })

  it('filters results and navigates on item click', async () => {
    const wrapper = mount(CommandPalette, {
      global: { plugins: [i18n] },
      attachTo: document.body,
    })

    useCommandPalette().openPalette()
    await nextTick()
    await nextTick()

    expect(document.querySelector('[data-testid="command-palette"]')).toBeTruthy()

    const input = document.querySelector('[data-testid="command-palette-input"]')
    expect(input).toBeTruthy()
    input.value = 'documents'
    input.dispatchEvent(new Event('input', { bubbles: true }))
    await nextTick()

    const item = document.querySelector('[data-testid="command-palette-item-documents"]')
    expect(item).toBeTruthy()
    item.click()
    await nextTick()

    expect(push).toHaveBeenCalledWith({ name: 'Documents' })
    expect(useCommandPalette().paletteState.open).toBe(false)

    wrapper.unmount()
  })
})
