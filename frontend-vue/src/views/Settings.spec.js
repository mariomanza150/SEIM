import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import Settings from './Settings.vue'
import api from '@/services/api'
import i18n, { LOCALE_STORAGE_KEY, setAppLocale } from '@/i18n'
import { useAuthStore } from '@/stores/auth'

const mockSuccessToast = vi.fn()
const mockErrorToast = vi.fn()

vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: mockSuccessToast, error: mockErrorToast }),
}))

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
    patch: vi.fn(),
  },
}))

function mountView() {
  const pinia = createPinia()
  setActivePinia(pinia)
  return mount(Settings, {
    global: {
      plugins: [pinia, i18n],
      stubs: {
        RouterLink: { template: '<a><slot /></a>' },
      },
    },
  })
}

const defaultSettingsPayload = {
  theme: 'auto',
  font_size: 'normal',
  high_contrast: false,
  reduce_motion: false,
  email_applications: true,
  email_documents: true,
  email_comments: true,
  email_programs: false,
  email_system: true,
  inapp_applications: true,
  inapp_documents: true,
  inapp_comments: true,
  inapp_programs: true,
  inapp_system: true,
  notification_digest_frequency: 'off',
  email_notification_digest: false,
  profile_public: false,
  share_analytics: true,
}

describe('Settings', () => {
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

  it('loads user settings into the form', async () => {
    api.get.mockResolvedValue({
      data: {
        theme: 'dark',
        font_size: 'large',
        high_contrast: true,
        reduce_motion: true,
        email_applications: false,
        email_documents: true,
        email_comments: true,
        email_programs: true,
        email_system: true,
        inapp_applications: true,
        inapp_documents: false,
        inapp_comments: true,
        inapp_programs: true,
        inapp_system: true,
        notification_digest_frequency: 'weekly',
        email_notification_digest: true,
        profile_public: true,
        share_analytics: false,
      },
    })

    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="settings-theme"]').exists()).toBe(true)
    })

    expect(wrapper.find('[data-testid="settings-theme"]').element.value).toBe('dark')
    expect(wrapper.find('[data-testid="settings-font-size"]').element.value).toBe('large')
    expect(wrapper.find('#high_contrast').element.checked).toBe(true)
    expect(wrapper.find('#reduce_motion').element.checked).toBe(true)
    expect(wrapper.find('#profile_public').element.checked).toBe(true)
    expect(wrapper.find('#share_analytics').element.checked).toBe(false)
    expect(wrapper.find('[data-testid="settings-digest-frequency"]').element.value).toBe('weekly')
    expect(wrapper.find('[data-testid="settings-email-digest"]').element.checked).toBe(true)
    expect(wrapper.text()).toContain(i18n.global.t('settings.cancel'))
  })

  it('saves updated settings', async () => {
    api.get.mockResolvedValue({
      data: {
        theme: 'auto',
        font_size: 'normal',
        high_contrast: false,
        reduce_motion: false,
        email_applications: true,
        email_documents: true,
        email_comments: true,
        email_programs: false,
        email_system: true,
        inapp_applications: true,
        inapp_documents: true,
        inapp_comments: true,
        inapp_programs: true,
        inapp_system: true,
        notification_digest_frequency: 'off',
        email_notification_digest: false,
        profile_public: false,
        share_analytics: true,
      },
    })
    api.patch.mockResolvedValue({ data: {} })

    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="settings-theme"]').exists()).toBe(true)
    })

    await wrapper.find('[data-testid="settings-theme"]').setValue('dark')
    await wrapper.find('#high_contrast').setValue(true)
    await wrapper.find('#email_programs').setValue(true)
    await wrapper.find('#share_analytics').setValue(false)
    await wrapper.find('form').trigger('submit.prevent')

    expect(api.patch).toHaveBeenCalledWith('/api/accounts/user-settings/', expect.objectContaining({
      theme: 'dark',
      high_contrast: true,
      email_programs: true,
      share_analytics: false,
    }))
    expect(mockSuccessToast).toHaveBeenCalledWith(i18n.global.t('settings.toastSaved'))
  })

  it('persists interface language selection locally', async () => {
    api.get.mockResolvedValue({
      data: {
        theme: 'auto',
        font_size: 'normal',
        high_contrast: false,
        reduce_motion: false,
        email_applications: true,
        email_documents: true,
        email_comments: true,
        email_programs: false,
        email_system: true,
        inapp_applications: true,
        inapp_documents: true,
        inapp_comments: true,
        inapp_programs: true,
        inapp_system: true,
        notification_digest_frequency: 'off',
        email_notification_digest: false,
        profile_public: false,
        share_analytics: true,
      },
    })

    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="settings-ui-language"]').exists()).toBe(true)
    })

    await wrapper.find('[data-testid="settings-ui-language"]').setValue('es')
    expect(localStorage.getItem(LOCALE_STORAGE_KEY)).toBe('es')
  })

  it('shows notification routing link for staff', async () => {
    api.get.mockResolvedValue({ data: { ...defaultSettingsPayload } })
    const pinia = createPinia()
    setActivePinia(pinia)
    const auth = useAuthStore()
    auth.accessToken = 't'
    auth.user = { role: 'coordinator', full_name: 'Coord' }
    const wrapper = mount(Settings, {
      global: {
        plugins: [pinia, i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="settings-theme"]').exists()).toBe(true)
    })
    const link = wrapper.find('[data-testid="settings-notification-routing-link"]')
    expect(link.exists()).toBe(true)
    expect(link.text()).toContain('How these toggles map')
  })

  it('hides notification routing link for students', async () => {
    api.get.mockResolvedValue({ data: { ...defaultSettingsPayload } })
    const pinia = createPinia()
    setActivePinia(pinia)
    const auth = useAuthStore()
    auth.accessToken = 't'
    auth.user = { role: 'student', full_name: 'Stu' }
    const wrapper = mount(Settings, {
      global: {
        plugins: [pinia, i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="settings-theme"]').exists()).toBe(true)
    })
    expect(wrapper.find('[data-testid="settings-notification-routing-link"]').exists()).toBe(false)
  })
})
