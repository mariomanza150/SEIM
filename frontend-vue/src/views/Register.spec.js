/**
 * Register view unit tests
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import Register from './Register.vue'
import i18n, { setAppLocale } from '@/i18n'
import axios from 'axios'

const mockSuccessToast = vi.fn()
const mockErrorToast = vi.fn()
const mockRegister = vi.fn()

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() }),
  useRoute: () => ({ query: {} }),
}))

vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: mockSuccessToast, error: mockErrorToast }),
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => ({
    register: mockRegister,
    error: null,
  }),
}))

vi.mock('axios', () => ({
  default: { get: vi.fn() },
}))

describe('Register', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    mockRegister.mockResolvedValue(false)
    axios.get.mockResolvedValue({
      data: [{ id: 'domain-1', name: 'uanl.edu.mx' }],
    })
    localStorage.clear()
    setAppLocale('en')
  })

  afterEach(() => {
    setAppLocale('en')
    localStorage.clear()
  })

  function mountRegister() {
    return mount(Register, {
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

  it('renders required name fields and loads allowed domains', async () => {
    const wrapper = mountRegister()

    await vi.waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith(
        expect.stringContaining('/api/accounts/catalogs/allowed-email-domains/'),
      )
    })
    await flushPromises()
    expect(wrapper.find('[data-testid="register-email"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="register-username"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="register-first-name"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="register-middle-name"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="register-last-name"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="register-mothers-last-name"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="register-password"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="register-password2"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="register-submit"]').text()).toContain('Create account')
    expect(wrapper.text()).toContain('uanl.edu.mx')
  })

  it('calls auth store register on valid submit', async () => {
    mockRegister.mockResolvedValue(true)
    const wrapper = mountRegister()

    await vi.waitFor(() => expect(axios.get).toHaveBeenCalled())
    await wrapper.find('#email').setValue('new@uanl.edu.mx')
    await wrapper.find('#username').setValue('newuser')
    await wrapper.find('#first_name').setValue('New')
    await wrapper.find('#middle_name').setValue('Middle')
    await wrapper.find('#last_name').setValue('User')
    await wrapper.find('#mothers_last_name').setValue('Family')
    await wrapper.find('#password').setValue('Passw0rd!')
    await wrapper.find('#password2').setValue('Passw0rd!')
    await wrapper.find('form').trigger('submit.prevent')
    await wrapper.vm.$nextTick()

    expect(mockRegister).toHaveBeenCalledWith({
      email: 'new@uanl.edu.mx',
      username: 'newuser',
      password: 'Passw0rd!',
      password2: 'Passw0rd!',
      first_name: 'New',
      middle_name: 'Middle',
      last_name: 'User',
      mothers_last_name: 'Family',
    })
    expect(wrapper.find('[data-testid="register-success"]').exists()).toBe(true)
  })

  it('shows password mismatch without calling register', async () => {
    const wrapper = mountRegister()

    await wrapper.find('#email').setValue('new@test.com')
    await wrapper.find('#username').setValue('newuser')
    await wrapper.find('#password').setValue('Passw0rd!')
    await wrapper.find('#password2').setValue('Different1!')
    await wrapper.find('form').trigger('submit.prevent')
    await wrapper.vm.$nextTick()

    expect(mockRegister).not.toHaveBeenCalled()
    expect(wrapper.text()).toContain('Passwords do not match')
  })
})
