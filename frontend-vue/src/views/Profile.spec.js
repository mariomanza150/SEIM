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
  middle_name: 'Byron',
  last_name: 'Lovelace',
  mothers_last_name: 'Milbanke',
  email: 'ada@example.com',
  matricula: '1234567',
  secondary_email: 'ada@example.net',
  gender: 'female',
  date_of_birth: '2000-01-01',
  birthplace: 'Monterrey',
  postal_code: '64000',
  passport_number: 'P123456',
  mobile_phone: '8112345678',
  rfc: 'LOVA000101ABC',
  academic_level: 'level-1',
  school: 'school-1',
  unidad: 'unidad-1',
  home_academic_program: 'program-1',
  ingress_date: '2023-08-01',
  current_semester: 5,
  credits_approved_percent: 60,
  bank_institution: 'bank-1',
  clabe: '012345678901234567',
  is_ready_to_apply: true,
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
    api.get.mockImplementation((url, config) => {
      if (url === '/api/accounts/profile/') return Promise.resolve({ data: profilePayload })
      if (url === '/api/accounts/catalogs/academic-levels/') {
        return Promise.resolve({ data: [{ id: 'level-1', name: 'Undergraduate' }] })
      }
      if (url === '/api/accounts/catalogs/schools/') {
        return Promise.resolve({
          data: [
            { id: 'school-1', name: 'Engineering' },
            { id: 'school-2', name: 'Architecture Faculty' },
          ],
        })
      }
      if (url === '/api/accounts/catalogs/unidades/') {
        return Promise.resolve({ data: [{ id: 'unidad-1', name: 'Ciudad Universitaria' }] })
      }
      if (url === '/api/accounts/catalogs/banks/') {
        return Promise.resolve({ data: [{ id: 'bank-1', name: 'BBVA' }] })
      }
      if (url === '/api/accounts/catalogs/programs/') {
        const school = config?.params?.school
        if (school === 'school-2') {
          return Promise.resolve({ data: [{ id: 'program-2', name: 'Architecture' }] })
        }
        expect(school).toBe('school-1')
        return Promise.resolve({ data: [{ id: 'program-1', name: 'Computer Science' }] })
      }
      if (url === '/grades/api/scales/active/') return Promise.resolve({ data: [] })
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })
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
    expect(wrapper.find('nav').attributes('aria-label')).toBe(i18n.global.t('profilePage.breadcrumbAria'))
    expect(wrapper.find('[data-testid="profile-page-heading"]').text()).toContain('Profile')
    expect(wrapper.text()).toContain('Complete your personal and academic profile before starting an application.')
    expect(wrapper.text()).toContain('Personal')
    expect(wrapper.text()).toContain('Academic')
    expect(wrapper.text()).toContain('Banking')
    expect(wrapper.text()).toContain('ready for applications')
    expect(wrapper.text()).toContain('Additional languages')
    expect(wrapper.text()).toContain('Cancel')
    expect(wrapper.find('[data-testid="profile-gpa"]').attributes('placeholder')).toBe(
      i18n.global.t('profilePage.gpaPlaceholder'),
    )
    expect(api.get).toHaveBeenCalledWith('/api/accounts/catalogs/academic-levels/')
    expect(api.get).toHaveBeenCalledWith('/api/accounts/catalogs/schools/')
    expect(api.get).toHaveBeenCalledWith('/api/accounts/catalogs/unidades/')
    expect(api.get).toHaveBeenCalledWith('/api/accounts/catalogs/banks/')
  })

  it('uses profilePage.loadingSpinner on the loading state spinner', async () => {
    let resolveGet
    api.get.mockImplementation((url) => {
      if (url === '/api/accounts/profile/') {
        return new Promise((resolve) => {
          resolveGet = resolve
        })
      }
      return Promise.resolve({ data: [] })
    })
    const wrapper = mount(Profile, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    const spinner = wrapper.find('.spinner-border')
    expect(spinner.exists()).toBe(true)
    expect(spinner.attributes('aria-label')).toBe(i18n.global.t('profilePage.loadingSpinner'))
    resolveGet({ data: profilePayload })
    await flushPromises()
    expect(wrapper.find('.spinner-border').exists()).toBe(false)
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
    expect(wrapper.text()).toContain('Completa tus datos personales y académicos')
    expect(wrapper.text()).toContain('Idiomas adicionales')
    expect(wrapper.text()).toContain('Cancelar')
    expect(wrapper.find('[data-testid="profile-gpa"]').attributes('placeholder')).toBe(
      i18n.global.t('profilePage.gpaPlaceholder'),
    )
  })

  it('sets autocomplete and label[for] on account, GPA, and primary language fields', async () => {
    const wrapper = mount(Profile, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.find('label[for="profile-first-name"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="profile-first-name"]').attributes('autocomplete')).toBe('given-name')
    expect(wrapper.find('[data-testid="profile-first-name"]').attributes('name')).toBe('given-name')
    expect(wrapper.find('[data-testid="profile-last-name"]').attributes('autocomplete')).toBe('family-name')
    expect(wrapper.find('[data-testid="profile-email"]').attributes('autocomplete')).toBe('email')
    expect(wrapper.find('[data-testid="profile-gpa"]').attributes('autocomplete')).toBe('off')
    expect(wrapper.find('[data-testid="profile-language"]').attributes('autocomplete')).toBe('language')
    expect(wrapper.find('[data-testid="profile-language-level"]').attributes('autocomplete')).toBe('off')
  })

  it('reloads programs when school changes and clears the prior selection', async () => {
    const wrapper = mount(Profile, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    const programSelect = wrapper.find('[data-testid="profile-program"]')
    expect(programSelect.element.value).toBe('program-1')
    expect(programSelect.text()).toContain('Computer Science')

    await wrapper.find('[data-testid="profile-school"]').setValue('school-2')
    await flushPromises()

    expect(api.get).toHaveBeenCalledWith('/api/accounts/catalogs/programs/', {
      params: { school: 'school-2' },
    })
    expect(programSelect.element.value).toBe('')
    expect(programSelect.text()).toContain('Architecture')
    expect(programSelect.text()).not.toContain('Computer Science')
  })

  it('PATCHes semester, credits, bank, and CLABE on save', async () => {
    const wrapper = mount(Profile, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    await wrapper.find('[data-testid="profile-current-semester"]').setValue(6)
    await wrapper.find('[data-testid="profile-credits-percent"]').setValue(75)
    await wrapper.find('[data-testid="profile-bank"]').setValue('bank-1')
    await wrapper.find('[data-testid="profile-clabe"]').setValue('012345678901234567')
    await wrapper.find('form').trigger('submit')
    await flushPromises()
    expect(api.patch).toHaveBeenCalledWith(
      '/api/accounts/profile/',
      expect.objectContaining({
        current_semester: 6,
        credits_approved_percent: 75,
        bank_institution: 'bank-1',
        clabe: '012345678901234567',
      }),
    )
  })

  it('renders bank options and the CLABE input in the banking section', async () => {
    const wrapper = mount(Profile, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.find('[data-testid="profile-banking-section"]').exists()).toBe(true)
    const bankSelect = wrapper.find('[data-testid="profile-bank"]')
    expect(bankSelect.exists()).toBe(true)
    expect(bankSelect.text()).toContain('BBVA')
    const clabe = wrapper.find('[data-testid="profile-clabe"]')
    expect(clabe.exists()).toBe(true)
    expect(clabe.attributes('maxlength')).toBe('18')
    expect(clabe.element.value).toBe('012345678901234567')
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
