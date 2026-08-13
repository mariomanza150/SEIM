/**
 * PasswordReset view unit tests
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import PasswordReset from './PasswordReset.vue'
import i18n, { setAppLocale } from '@/i18n'

const mockSuccessToast = vi.fn()
const mockErrorToast = vi.fn()
const mockRequestPasswordReset = vi.fn()

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() }),
  useRoute: () => ({ query: {} }),
}))

vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: mockSuccessToast, error: mockErrorToast }),
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => ({
    requestPasswordReset: mockRequestPasswordReset,
    error: null,
  }),
}))

describe('PasswordReset', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    mockRequestPasswordReset.mockResolvedValue(false)
    setAppLocale('en')
  })

  afterEach(() => {
    setAppLocale('en')
  })

  function mountView() {
    return mount(PasswordReset, {
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

  it('renders the email form', () => {
    const wrapper = mountView()
    expect(wrapper.find('[data-testid="password-reset-form"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="password-reset-email"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('Reset your password')
  })

  it('requests a reset email on submit', async () => {
    mockRequestPasswordReset.mockResolvedValue(true)
    const wrapper = mountView()
    await wrapper.find('[data-testid="password-reset-email"]').setValue('ada@example.com')
    await wrapper.find('form').trigger('submit.prevent')
    await wrapper.vm.$nextTick()
    expect(mockRequestPasswordReset).toHaveBeenCalledWith('ada@example.com')
    expect(wrapper.find('[data-testid="password-reset-success"]').exists()).toBe(true)
  })
})
