/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import App from './App.vue'
import i18n, { setAppLocale } from '@/i18n'

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn().mockResolvedValue({ data: {} }),
  },
}))

vi.mock('@/services/websocket', () => ({
  useNotificationWebSocket: () => ({
    connectIfAuthenticated: vi.fn(),
    disconnect: vi.fn(),
  }),
}))

vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ info: vi.fn() }),
}))

vi.mock('@/services/uiPreferences', () => ({
  applyUiPreferences: vi.fn(),
  clearUiPreferences: vi.fn(),
  readStoredUiPreferences: vi.fn(() => null),
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => ({
    isAuthenticated: false,
    accessToken: null,
    checkAuth: vi.fn().mockResolvedValue(undefined),
  }),
}))

describe('App shell accessibility', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    localStorage.clear()
    setAppLocale('en')
  })

  afterEach(() => {
    setAppLocale('en')
    localStorage.clear()
  })

  it('renders skip link targeting main landmark', () => {
    const wrapper = mount(App, {
      global: {
        plugins: [createPinia(), i18n],
        stubs: {
          RouterView: { template: '<div data-testid="rv">page</div>' },
          ToastContainer: { template: '<div />' },
        },
      },
    })

    const skip = wrapper.find('a.seim-skip-link')
    expect(skip.exists()).toBe(true)
    expect(skip.attributes('href')).toBe('#main-content')
    expect(skip.text()).toContain('Skip to main content')

    const main = wrapper.find('#main-content')
    expect(main.exists()).toBe(true)
    expect(main.attributes('tabindex')).toBe('-1')
    expect(main.find('[data-testid="rv"]').exists()).toBe(true)
  })

  it('updates skip link text when locale changes', async () => {
    const wrapper = mount(App, {
      global: {
        plugins: [createPinia(), i18n],
        stubs: {
          RouterView: { template: '<div data-testid="rv">page</div>' },
          ToastContainer: { template: '<div />' },
        },
      },
    })

    setAppLocale('es')
    await wrapper.vm.$nextTick()
    expect(wrapper.find('a.seim-skip-link').text()).toContain('Saltar al contenido principal')
  })
})
