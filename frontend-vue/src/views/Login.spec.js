/**
 * Login view unit tests
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import Login from './Login.vue'
import i18n, { setAppLocale } from '@/i18n'

const mockPush = vi.fn()
const mockSuccessToast = vi.fn()
const mockErrorToast = vi.fn()
const mockLogin = vi.fn()

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: mockPush }),
  useRoute: () => ({ query: {} }),
}))

vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: mockSuccessToast, error: mockErrorToast }),
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => ({
    login: mockLogin,
    error: null,
    userName: 'Test User',
  }),
}))

describe('Login', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    mockLogin.mockResolvedValue(false)
    localStorage.clear()
    setAppLocale('en')
  })

  afterEach(() => {
    setAppLocale('en')
    localStorage.clear()
  })

  it('renders login form with email, password and submit button', () => {
    const wrapper = mount(Login, {
      global: {
        plugins: [createPinia(), i18n],
      },
    })

    expect(wrapper.find('input#email').exists()).toBe(true)
    expect(wrapper.find('input#password').exists()).toBe(true)
    expect(wrapper.find('button[type="submit"]').exists()).toBe(true)
    expect(wrapper.find('button[type="submit"]').text()).toContain('Sign In')
    expect(wrapper.text()).toContain('SEIM')
    expect(wrapper.text()).toContain('Sign in to continue')
  })

  it('calls auth store login on form submit', async () => {
    const wrapper = mount(Login, {
      global: {
        plugins: [createPinia(), i18n],
      },
    })

    await wrapper.find('input#email').setValue('user@test.com')
    await wrapper.find('input#password').setValue('pass123')
    await wrapper.find('form').trigger('submit.prevent')

    await wrapper.vm.$nextTick()
    expect(mockLogin).toHaveBeenCalledWith('user@test.com', 'pass123')
  })

  it('has email and password inputs with correct attributes', () => {
    const wrapper = mount(Login, {
      global: {
        plugins: [createPinia(), i18n],
      },
    })

    const emailInput = wrapper.find('input#email')
    const passwordInput = wrapper.find('input#password')

    expect(emailInput.attributes('type')).toBe('email')
    expect(emailInput.attributes('name')).toBe('username')
    expect(emailInput.attributes('autocomplete')).toBe('username')
    expect(emailInput.attributes('placeholder')).toContain('email')
    expect(passwordInput.attributes('type')).toBe('password')
    expect(passwordInput.attributes('name')).toBe('password')
    expect(passwordInput.attributes('autocomplete')).toBe('current-password')
    expect(passwordInput.attributes('placeholder')).toContain('password')
  })
})
