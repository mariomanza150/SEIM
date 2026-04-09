/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import App from './App.vue'

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
  })

  it('renders skip link targeting main landmark', () => {
    const wrapper = mount(App, {
      global: {
        plugins: [createPinia()],
        stubs: {
          RouterView: { template: '<div data-testid="rv">page</div>' },
          ToastContainer: { template: '<div />' },
        },
      },
    })

    const skip = wrapper.find('a.seim-skip-link')
    expect(skip.exists()).toBe(true)
    expect(skip.attributes('href')).toBe('#main-content')

    const main = wrapper.find('#main-content')
    expect(main.exists()).toBe(true)
    expect(main.attributes('tabindex')).toBe('-1')
    expect(main.find('[data-testid="rv"]').exists()).toBe(true)
  })
})
