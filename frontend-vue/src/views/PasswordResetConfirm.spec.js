/**
 * PasswordResetConfirm view unit tests
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import PasswordResetConfirm from './PasswordResetConfirm.vue'
import i18n, { setAppLocale } from '@/i18n'

const mockSuccessToast = vi.fn()
const mockErrorToast = vi.fn()
const mockConfirmPasswordReset = vi.fn()
let routeQuery = { email: 'ada@example.com', token: 'tok123' }

vi.mock('vue-router', () => ({
  useRoute: () => ({ query: routeQuery }),
}))

vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: mockSuccessToast, error: mockErrorToast }),
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => ({
    confirmPasswordReset: mockConfirmPasswordReset,
    error: null,
  }),
}))

describe('PasswordResetConfirm', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    routeQuery = { email: 'ada@example.com', token: 'tok123' }
    mockConfirmPasswordReset.mockResolvedValue(true)
    setAppLocale('en')
  })

  afterEach(() => {
    setAppLocale('en')
  })

  function mountView() {
    return mount(PasswordResetConfirm, {
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

  it('prefills email and token from the query string', () => {
    const wrapper = mountView()
    expect(wrapper.find('[data-testid="password-reset-confirm-email"]').element.value).toBe(
      'ada@example.com',
    )
    expect(wrapper.find('[data-testid="password-reset-confirm-token"]').element.value).toBe(
      'tok123',
    )
  })

  it('rejects mismatched passwords without calling the store', async () => {
    const wrapper = mountView()
    await wrapper.find('[data-testid="password-reset-confirm-password"]').setValue('Newpass1!')
    await wrapper.find('[data-testid="password-reset-confirm-password2"]').setValue('Other1!')
    await wrapper.find('form').trigger('submit.prevent')
    expect(mockConfirmPasswordReset).not.toHaveBeenCalled()
    expect(wrapper.text()).toContain('do not match')
  })

  it('confirms the reset and shows success', async () => {
    const wrapper = mountView()
    await wrapper.find('[data-testid="password-reset-confirm-password"]').setValue('Newpass1!')
    await wrapper.find('[data-testid="password-reset-confirm-password2"]').setValue('Newpass1!')
    await wrapper.find('form').trigger('submit.prevent')
    await wrapper.vm.$nextTick()
    expect(mockConfirmPasswordReset).toHaveBeenCalledWith({
      email: 'ada@example.com',
      token: 'tok123',
      new_password: 'Newpass1!',
    })
    expect(wrapper.find('[data-testid="password-reset-confirm-success"]').exists()).toBe(true)
  })
})
