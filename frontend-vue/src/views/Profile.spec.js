/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import Profile from './Profile.vue'
import api from '@/services/api'
import i18n, { setAppLocale } from '@/i18n'

vi.mock('@/services/api', () => ({
  default: { get: vi.fn(), patch: vi.fn() },
}))

vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ error: vi.fn(), success: vi.fn() }),
}))

const profilePayload = {
  first_name: 'Ada',
  last_name: 'Lovelace',
  email: 'ada@example.com',
  gpa: 3.5,
  language: 'English',
  language_level: 'B2',
  additional_languages: [{ name: 'French', level: 'A2' }],
}

describe('Profile', () => {
  beforeEach(() => {
    localStorage.clear()
    setAppLocale('en')
    vi.clearAllMocks()
    api.get.mockResolvedValue({ data: profilePayload })
    api.patch.mockResolvedValue({ data: profilePayload })
  })

  afterEach(() => {
    setAppLocale('en')
    localStorage.clear()
  })

  it('renders translated headings and eligibility copy in English', async () => {
    const wrapper = mount(Profile, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.find('[data-testid="profile-page-heading"]').text()).toContain('Profile')
    expect(wrapper.text()).toContain('Update your account and eligibility information for exchange programs.')
    expect(wrapper.text()).toContain('Eligibility (for exchange programs)')
    expect(wrapper.text()).toContain('Additional languages')
    expect(wrapper.text()).toContain('Tip')
  })

  it('renders Spanish copy when locale is es', async () => {
    setAppLocale('es')
    const wrapper = mount(Profile, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.find('[data-testid="profile-page-heading"]').text()).toContain('Perfil')
    expect(wrapper.text()).toContain('Actualiza los datos de tu cuenta y tu elegibilidad')
    expect(wrapper.text()).toContain('Idiomas adicionales')
    expect(wrapper.text()).toContain('Consejo')
  })

  it('shows primary CEFR labels from locale', async () => {
    const wrapper = mount(Profile, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    const html = wrapper.html()
    expect(html).toContain('A1 – Beginner')
    expect(html).toContain('C2 – Proficient')
  })
})
