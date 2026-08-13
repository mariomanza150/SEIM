/**
 * VerifyEmail view unit tests
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import VerifyEmail from './VerifyEmail.vue'
import i18n, { setAppLocale } from '@/i18n'

const mockVerifyEmail = vi.fn()
let routeQuery = { token: 'abc123' }

vi.mock('vue-router', () => ({
  useRoute: () => ({ query: routeQuery }),
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => ({
    verifyEmail: mockVerifyEmail,
    error: null,
  }),
}))

describe('VerifyEmail', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    routeQuery = { token: 'abc123' }
    mockVerifyEmail.mockResolvedValue(true)
    setAppLocale('en')
  })

  afterEach(() => {
    setAppLocale('en')
  })

  function mountView() {
    return mount(VerifyEmail, {
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

  it('verifies token from query and shows success', async () => {
    const wrapper = mountView()
    await flushPromises()

    expect(mockVerifyEmail).toHaveBeenCalledWith('abc123')
    expect(wrapper.find('[data-testid="verify-email-success"]').exists()).toBe(true)
  })

  it('shows error when token is missing', async () => {
    routeQuery = {}
    const wrapper = mountView()
    await flushPromises()

    expect(mockVerifyEmail).not.toHaveBeenCalled()
    expect(wrapper.find('[data-testid="verify-email-error"]').text()).toContain(
      'missing a token',
    )
  })
})
