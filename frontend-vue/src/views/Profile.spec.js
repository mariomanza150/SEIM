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

const { mockErrorToast, mockSuccessToast } = vi.hoisted(() => ({
  mockErrorToast: vi.fn(),
  mockSuccessToast: vi.fn(),
}))

vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ error: mockErrorToast, success: mockSuccessToast }),
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
  grade_scale: 'scale-1',
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
        expect(config?.params?.unidad).toBe('unidad-1')
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
      if (url === '/api/grades/scales/active/' || url === '/grades/api/scales/active/') {
        return Promise.resolve({ data: [{ id: 'scale-1', name: '4.0 scale' }] })
      }
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
    expect(wrapper.text()).toContain('Complete your personal, academic, and eligibility profile before starting an application.')
    expect(wrapper.text()).toContain('Personal')
    expect(wrapper.text()).toContain('Academic')
    expect(wrapper.text()).toContain('Banking')
    expect(wrapper.text()).toContain('You can start an application.')
    expect(wrapper.text()).toContain('Additional languages')
    expect(wrapper.text()).toContain('Cancel')
    expect(wrapper.find('[data-testid="profile-gpa"]').attributes('placeholder')).toBe(
      i18n.global.t('profilePage.gpaPlaceholder'),
    )
    expect(api.get).toHaveBeenCalledWith('/api/accounts/catalogs/academic-levels/')
    expect(api.get).toHaveBeenCalledWith('/api/accounts/catalogs/schools/', { params: { unidad: 'unidad-1' } })
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
    await flushPromises()
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
    expect(wrapper.text()).toContain('Completa tus datos personales, académicos y de elegibilidad')
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
    expect(wrapper.find('[data-testid="profile-language"]').attributes('autocomplete')).toBe('off')
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

  it('loads personal, academic, and banking fields from the profile API', async () => {
    const wrapper = mount(Profile, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.find('[data-testid="profile-secondary-email"]').element.value).toBe('ada@example.net')
    expect(wrapper.find('[data-testid="profile-mobile"]').element.value).toBe('8112345678')
    expect(wrapper.find('[data-testid="profile-academic-level"]').element.value).toBe('level-1')
    expect(wrapper.find('[data-testid="profile-school"]').element.value).toBe('school-1')
    expect(wrapper.find('[data-testid="profile-program"]').element.value).toBe('program-1')
    expect(wrapper.find('[data-testid="profile-unidad"]').element.value).toBe('unidad-1')
    expect(wrapper.find('[data-testid="profile-gender"]').element.value).toBe('female')
    expect(wrapper.find('[data-testid="profile-dob"]').element.value).toBe('2000-01-01')
    expect(wrapper.find('[data-testid="profile-birthplace"]').element.value).toBe('Monterrey')
    expect(wrapper.find('[data-testid="profile-postal-code"]').element.value).toBe('64000')
    expect(wrapper.find('[data-testid="profile-passport"]').element.value).toBe('P123456')
    expect(wrapper.find('[data-testid="profile-rfc"]').element.value).toBe('LOVA000101ABC')
    expect(wrapper.find('[data-testid="profile-bank"]').element.value).toBe('bank-1')
    expect(wrapper.find('[data-testid="profile-clabe"]').element.value).toBe('012345678901234567')
    expect(wrapper.find('[data-testid="profile-gpa"]').element.value).toBe('3.5')
    expect(wrapper.find('[data-testid="profile-grade-scale"]').element.value).toBe('scale-1')
    expect(wrapper.find('[data-testid="profile-credits-percent"]').element.value).toBe('60')
    expect(wrapper.find('[data-testid="profile-ingress-date"]').element.value).toBe('2023-08-01')
    expect(wrapper.find('[data-testid="profile-language"]').element.value).toBe('English')
    expect(wrapper.find('[data-testid="profile-language-level"]').element.value).toBe('B2')
  })

  it('hydrates eligibility fields from decimal strings and nested grade-scale payloads', async () => {
    const scaleId = '702ec46e-6ce8-4300-be45-8bd008734674'
    api.get.mockImplementation((url) => {
      if (url === '/api/accounts/profile/') {
        return Promise.resolve({
          data: {
            ...profilePayload,
            gpa: 4.0,
            grade_scale: scaleId,
            grade_scale_name: 'US GPA 4.0 Scale',
            credits_approved_percent: '50.00',
            ingress_date: '2024-06-24',
            current_semester: null,
            language: 'English',
            language_level: 'C2',
          },
        })
      }
      if (String(url).includes('/api/accounts/catalogs/academic-levels')) {
        return Promise.resolve({ data: [{ id: 'level-1', name: 'Undergraduate' }] })
      }
      if (String(url).includes('/api/accounts/catalogs/schools')) {
        return Promise.resolve({ data: [{ id: 'school-1', name: 'Engineering' }] })
      }
      if (String(url).includes('/api/accounts/catalogs/unidades')) {
        return Promise.resolve({ data: [{ id: 'unidad-1', name: 'Ciudad Universitaria' }] })
      }
      if (String(url).includes('/api/accounts/catalogs/banks')) {
        return Promise.resolve({ data: [{ id: 'bank-1', name: 'BBVA' }] })
      }
      if (String(url).includes('/api/accounts/catalogs/programs')) {
        return Promise.resolve({ data: [{ id: 'program-1', name: 'Computer Science' }] })
      }
      if (url === '/api/grades/scales/active/') {
        return Promise.reject(new Error('not mounted'))
      }
      if (url === '/grades/api/scales/active/') {
        return Promise.resolve({
          data: [{
            id: scaleId,
            name: 'US GPA 4.0 Scale',
            grade_values: [{ id: 'gv-1', label: 'A', numeric_value: 4.0 }],
          }],
        })
      }
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })
    const wrapper = mount(Profile, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.find('[data-testid="profile-gpa"]').element.value).toBe('4')
    expect(wrapper.find('[data-testid="profile-grade-scale"]').element.value).toBe(scaleId)
    expect(wrapper.find('[data-testid="profile-credits-percent"]').element.value).toBe('50')
    expect(wrapper.find('[data-testid="profile-ingress-date"]').element.value).toBe('2024-06-24')
    expect(wrapper.find('[data-testid="profile-language"]').element.value).toBe('English')
    expect(wrapper.find('[data-testid="profile-language-level"]').element.value).toBe('C2')
  })

  it('PATCHes personal, eligibility, bank, and CLABE fields on save', async () => {
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
        secondary_email: 'ada@example.net',
        mobile_phone: '8112345678',
        academic_level: 'level-1',
        school: 'school-1',
        unidad: 'unidad-1',
        home_academic_program: 'program-1',
        gender: 'female',
        date_of_birth: '2000-01-01',
        birthplace: 'Monterrey',
        postal_code: '64000',
        passport_number: 'P123456',
        rfc: 'LOVA000101ABC',
      }),
    )
    expect(api.patch.mock.calls[0][1].email).toBeUndefined()
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

  it('does not mark middle name, maternal last name, passport, or RFC as required', async () => {
    const wrapper = mount(Profile, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.find('[data-testid="profile-middle-name"]').attributes('required')).toBeUndefined()
    expect(wrapper.find('[data-testid="profile-mothers-last-name"]').attributes('required')).toBeUndefined()
    expect(wrapper.find('[data-testid="profile-passport"]').attributes('required')).toBeUndefined()
    expect(wrapper.find('[data-testid="profile-rfc"]').attributes('required')).toBeUndefined()
    expect(wrapper.find('[data-testid="profile-first-name"]').attributes('required')).toBeDefined()
  })

  it('toasts a single catalog error when several catalog requests fail', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/accounts/profile/') return Promise.resolve({ data: profilePayload })
      if (String(url).includes('/api/accounts/catalogs/')) {
        return Promise.reject(new Error('catalog down'))
      }
      if (url === '/api/grades/scales/active/') return Promise.resolve({ data: [] })
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })
    mount(Profile, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    const catalogToasts = mockErrorToast.mock.calls.filter(
      ([message]) => message === i18n.global.t('profilePage.toastCatalogError'),
    )
    expect(catalogToasts).toHaveLength(1)
  })

  it('does not toast catalog error when only the new grades path is missing', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/accounts/profile/') return Promise.resolve({ data: profilePayload })
      if (String(url).includes('/api/accounts/catalogs/')) {
        if (url.includes('programs')) {
          return Promise.resolve({ data: [{ id: 'program-1', name: 'Computer Science' }] })
        }
        return Promise.resolve({ data: [] })
      }
      if (url === '/api/grades/scales/active/') return Promise.reject(new Error('not found'))
      if (url === '/grades/api/scales/active/') return Promise.resolve({ data: [] })
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })
    mount(Profile, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    const catalogToasts = mockErrorToast.mock.calls.filter(
      ([message]) => message === i18n.global.t('profilePage.toastCatalogError'),
    )
    expect(catalogToasts).toHaveLength(0)
  })

  it('keeps UUID catalog values selected after load', async () => {
    const levelId = '509b0dc2-2245-4e90-8e04-6052714da1ac'
    const schoolId = '7ea99e43-8efb-4afa-aba2-fc76006c5f5d'
    const programId = '4c925b4b-0077-485c-940b-bd60ca7f9ff0'
    const unidadId = '41a53d01-9a88-4a2c-930d-942b675a317c'
    api.get.mockImplementation((url, config) => {
      if (url === '/api/accounts/profile/') {
        return Promise.resolve({
          data: {
            ...profilePayload,
            academic_level: levelId,
            academic_level_name: 'Licenciatura',
            school: schoolId,
            school_name: 'Derecho',
            unidad: unidadId,
            unidad_name: 'Sureste',
            home_academic_program: programId,
            home_academic_program_name: 'Licenciatura en Derecho',
          },
        })
      }
      if (url === '/api/accounts/catalogs/academic-levels/') {
        return Promise.resolve({ data: [{ id: levelId, name: 'Licenciatura' }] })
      }
      if (url === '/api/accounts/catalogs/schools/') {
        expect(config?.params?.unidad).toBe(unidadId)
        return Promise.resolve({ data: [{ id: schoolId, name: 'Derecho' }] })
      }
      if (url === '/api/accounts/catalogs/unidades/') {
        return Promise.resolve({ data: [{ id: unidadId, name: 'Sureste' }] })
      }
      if (url === '/api/accounts/catalogs/banks/') {
        return Promise.resolve({ data: [{ id: 'bank-1', name: 'BBVA' }] })
      }
      if (url === '/api/accounts/catalogs/programs/') {
        expect(config?.params?.school).toBe(schoolId)
        return Promise.resolve({ data: [{ id: programId, name: 'Licenciatura en Derecho' }] })
      }
      if (url === '/api/grades/scales/active/' || url === '/grades/api/scales/active/') {
        return Promise.resolve({ data: [] })
      }
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })
    const wrapper = mount(Profile, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.find('[data-testid="profile-academic-level"]').element.value).toBe(levelId)
    expect(wrapper.find('[data-testid="profile-school"]').element.value).toBe(schoolId)
    expect(wrapper.find('[data-testid="profile-program"]').element.value).toBe(programId)
    expect(wrapper.find('[data-testid="profile-unidad"]').element.value).toBe(unidadId)
    expect(wrapper.find('[data-testid="profile-first-name"]').element.value).toBe('Ada')
    const programCalls = api.get.mock.calls.filter(([url]) => url === '/api/accounts/catalogs/programs/')
    expect(programCalls).toHaveLength(1)
  })

  it('lists eligibility fields still required to apply', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/accounts/profile/') {
        return Promise.resolve({
          data: {
            ...profilePayload,
            gpa: null,
            grade_scale: '',
            credits_approved_percent: null,
            ingress_date: '',
            current_semester: null,
            is_ready_to_apply: false,
          },
        })
      }
      if (String(url).includes('/api/accounts/catalogs/')) {
        return Promise.resolve({ data: [] })
      }
      if (url === '/api/grades/scales/active/' || url === '/grades/api/scales/active/') {
        return Promise.resolve({ data: [{ id: 'scale-1', name: '4.0 scale' }] })
      }
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })
    const wrapper = mount(Profile, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    const missing = wrapper.find('[data-testid="profile-missing-fields"]')
    expect(missing.exists()).toBe(true)
    expect(missing.text()).toContain('GPA')
    expect(missing.text()).toContain('Grading scale')
    expect(missing.text()).toContain('Credits approved')
    expect(wrapper.find('[data-testid="profile-gpa"]').attributes('required')).toBeDefined()
    expect(wrapper.find('[data-testid="profile-grade-scale"]').attributes('required')).toBeDefined()
  })
})
