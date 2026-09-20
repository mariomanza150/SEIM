/**
 * Login view unit tests
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import Login from './Login.vue'
import i18n, { setAppLocale } from '@/i18n'

const mockPush = vi.fn()
const mockSuccessToast = vi.fn()
const mockErrorToast = vi.fn()
const mockLogin = vi.fn()
const mockResendVerificationEmail = vi.fn()

const authStoreState = {
  login: mockLogin,
  resendVerificationEmail: mockResendVerificationEmail,
  error: null,
  errorCode: null,
  userName: 'Test User',
}

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: mockPush }),
  useRoute: () => ({ query: {} }),
}))

vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: mockSuccessToast, error: mockErrorToast }),
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => authStoreState,
}))

function mountLogin() {
  return mount(Login, {
    global: {
      plugins: [createPinia(), i18n],
      stubs: {
        RouterLink: {
          template: '<a><slot /></a>',
          props: ['to'],
        },
      },
    },
  })
}

describe('Login', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    vi.useFakeTimers()
    mockLogin.mockResolvedValue(false)
    mockResendVerificationEmail.mockResolvedValue({
      ok: true,
      status: 200,
      message: 'sent',
      retryAfter: null,
    })
    authStoreState.error = null
    authStoreState.errorCode = null
    localStorage.clear()
    sessionStorage.clear()
    setAppLocale('en')
  })

  afterEach(() => {
    setAppLocale('en')
    localStorage.clear()
    sessionStorage.clear()
    vi.useRealTimers()
  })

  it('renders login form with email, password and submit button', () => {
    const wrapper = mountLogin()

    expect(wrapper.find('input#email').exists()).toBe(true)
    expect(wrapper.find('input#password').exists()).toBe(true)
    expect(wrapper.find('button[type="submit"]').exists()).toBe(true)
    expect(wrapper.find('button[type="submit"]').text()).toContain('Sign In')
    expect(wrapper.find('[data-testid="login-create-account"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="login-forgot-password"]').exists()).toBe(true)
  })

  it('calls auth store login on form submit', async () => {
    const wrapper = mountLogin()

    await wrapper.find('input#email').setValue('user@test.com')
    await wrapper.find('input#password').setValue('pass123')
    await wrapper.find('form').trigger('submit.prevent')

    await flushPromises()
    expect(mockLogin).toHaveBeenCalledWith('user@test.com', 'pass123')
  })

  it('has email and password inputs with correct attributes', () => {
    const wrapper = mountLogin()

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

  it('shows resend button when login fails with email_not_verified', async () => {
    authStoreState.error = 'Email not verified. Please check your inbox for the verification link.'
    authStoreState.errorCode = 'email_not_verified'
    mockLogin.mockResolvedValue(false)

    const wrapper = mountLogin()
    await wrapper.find('input#email').setValue('user@test.com')
    await wrapper.find('input#password').setValue('pass123')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    const btn = wrapper.find('[data-testid="login-resend-verification"]')
    expect(btn.exists()).toBe(true)
    expect(btn.text()).toContain('Resend verification email')
  })

  it('calls resendVerificationEmail and starts cooldown after success', async () => {
    authStoreState.error = 'Email not verified. Please check your inbox for the verification link.'
    authStoreState.errorCode = 'email_not_verified'
    mockLogin.mockResolvedValue(false)

    const wrapper = mountLogin()
    await wrapper.find('input#email').setValue('user@test.com')
    await wrapper.find('input#password').setValue('pass123')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    await wrapper.find('[data-testid="login-resend-verification"]').trigger('click')
    await flushPromises()

    expect(mockResendVerificationEmail).toHaveBeenCalledWith('user@test.com')
    expect(mockSuccessToast).toHaveBeenCalled()
    const btn = wrapper.find('[data-testid="login-resend-verification"]')
    expect(btn.attributes('disabled')).toBeDefined()
    expect(btn.text()).toMatch(/Resend available in \d+s/)
  })

  it('disables resend button when cooldown is active in sessionStorage', async () => {
    const until = Date.now() + 120_000
    sessionStorage.setItem('seim_resend_verification_until:user@test.com', String(until))
    authStoreState.error = 'Email not verified. Please check your inbox for the verification link.'
    authStoreState.errorCode = 'email_not_verified'
    mockLogin.mockResolvedValue(false)

    const wrapper = mountLogin()
    await wrapper.find('input#email').setValue('user@test.com')
    await wrapper.find('input#password').setValue('pass123')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    const btn = wrapper.find('[data-testid="login-resend-verification"]')
    expect(btn.attributes('disabled')).toBeDefined()
    expect(btn.text()).toMatch(/Resend available in \d+s/)
  })
})
