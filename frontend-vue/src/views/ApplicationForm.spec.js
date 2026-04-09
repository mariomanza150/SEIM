import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ApplicationForm from './ApplicationForm.vue'
import api from '@/services/api'
import i18n, { setAppLocale } from '@/i18n'

const mockPush = vi.fn()
const mockSuccessToast = vi.fn()
const mockErrorToast = vi.fn()
const mockRoute = {
  params: {},
  query: {},
}

vi.mock('vue-router', () => ({
  useRoute: () => mockRoute,
  useRouter: () => ({ push: mockPush }),
}))

vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: mockSuccessToast, error: mockErrorToast }),
}))

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
  },
}))

function mountView() {
  return mount(ApplicationForm, {
    global: {
      plugins: [createPinia(), i18n],
      stubs: {
        RouterLink: { template: '<a><slot /></a>' },
      },
    },
  })
}

function isoDateWithOffset(days) {
  const date = new Date()
  date.setDate(date.getDate() + days)
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

describe('ApplicationForm', () => {
  beforeEach(() => {
    localStorage.clear()
    setAppLocale('en')
    setActivePinia(createPinia())
    vi.clearAllMocks()
    mockRoute.params = {}
    mockRoute.query = {}
  })

  afterEach(() => {
    setAppLocale('en')
    localStorage.clear()
  })

  it('renders dynamic form fields for the selected program and submits df payload keys', async () => {
    api.get.mockImplementation((url) => {
      if (typeof url === 'string' && url.includes('/check_eligibility/')) {
        return Promise.resolve({
          data: { eligible: true, message: 'All eligibility requirements met' },
        })
      }
      if (url === '/api/programs/') {
        return Promise.resolve({
          data: {
            results: [
              {
                id: 'program-1',
                name: 'Exchange Program',
                description: 'A dynamic program',
                start_date: '2026-09-01',
                end_date: '2027-01-15',
                application_form: 'form-1',
              },
            ],
          },
        })
      }

      if (url === '/api/application-forms/form-types/form-1/form_schema/') {
        return Promise.resolve({
          data: {
            id: 'form-1',
            name: 'Exchange Questions',
            description: 'Program-specific questions',
            schema: {
              properties: {
                motivation: {
                  type: 'string',
                  title: 'Motivation',
                  maxLength: 500,
                },
                language_level: {
                  type: 'string',
                  title: 'Language Level',
                  enum: ['Basic', 'Advanced'],
                },
                needs_housing: {
                  type: 'boolean',
                  title: 'Needs Housing',
                },
              },
              required: ['motivation', 'language_level'],
            },
            ui_schema: {},
            required_fields: ['motivation', 'language_level'],
          },
        })
      }

      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })

    api.post.mockResolvedValue({ data: { id: 'application-1' } })

    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="program-select"]').exists()).toBe(true)
    })

    await wrapper.find('[data-testid="program-select"]').setValue('program-1')

    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="dynamic-field-motivation"]').exists()).toBe(true)
    })

    await wrapper.find('[data-testid="dynamic-field-motivation"]').setValue('I want to represent my university abroad.')
    await wrapper.find('[data-testid="dynamic-field-language_level"]').setValue('Advanced')
    await wrapper.find('[data-testid="dynamic-field-needs_housing"]').setValue(true)
    await wrapper.find('form').trigger('submit.prevent')

    expect(api.post).toHaveBeenCalledWith('/api/applications/', {
      program: 'program-1',
      df_motivation: 'I want to represent my university abroad.',
      df_language_level: 'Advanced',
      df_needs_housing: true,
    })
    expect(mockSuccessToast).toHaveBeenCalledWith('Application created successfully!')
    expect(mockPush).toHaveBeenCalledWith({ name: 'ApplicationDetail', params: { id: 'application-1' } })
  })

  it('prefills dynamic form responses when editing an existing application', async () => {
    mockRoute.params = { id: 'application-1' }

    api.get.mockImplementation((url) => {
      if (typeof url === 'string' && url.includes('/check_eligibility/')) {
        return Promise.resolve({
          data: { eligible: true, message: 'All eligibility requirements met' },
        })
      }
      if (url === '/api/programs/') {
        return Promise.resolve({
          data: {
            results: [
              {
                id: 'program-1',
                name: 'Exchange Program',
                description: 'A dynamic program',
                start_date: '2026-09-01',
                end_date: '2027-01-15',
                application_form: 'form-1',
              },
            ],
          },
        })
      }

      if (url === '/api/applications/application-1/') {
        return Promise.resolve({
          data: {
            id: 'application-1',
            program: 'program-1',
            dynamic_form_submission: {
              id: 'submission-1',
              form_type: 'form-1',
              responses: {
                motivation: 'Preloaded answer',
                language_level: 'Advanced',
              },
            },
          },
        })
      }

      if (url === '/api/application-forms/form-types/form-1/form_schema/') {
        return Promise.resolve({
          data: {
            id: 'form-1',
            name: 'Exchange Questions',
            description: 'Program-specific questions',
            schema: {
              properties: {
                motivation: {
                  type: 'string',
                  title: 'Motivation',
                  maxLength: 500,
                },
                language_level: {
                  type: 'string',
                  title: 'Language Level',
                  enum: ['Basic', 'Advanced'],
                },
              },
              required: ['motivation'],
            },
            ui_schema: {},
            required_fields: ['motivation'],
          },
        })
      }

      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })

    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="dynamic-field-motivation"]').exists()).toBe(true)
    })

    expect(wrapper.find('[data-testid="dynamic-field-motivation"]').element.value).toBe('Preloaded answer')
    expect(wrapper.find('[data-testid="dynamic-field-language_level"]').element.value).toBe('Advanced')
  })

  it('disables new application creation when the application window is closed', async () => {
    api.get.mockImplementation((url) => {
      if (typeof url === 'string' && url.includes('/check_eligibility/')) {
        return Promise.resolve({
          data: { eligible: true, message: 'All eligibility requirements met' },
        })
      }
      return Promise.resolve({
        data: {
          results: [
            {
              id: 'program-closed',
              name: 'Closed Program',
              description: 'No longer accepting applications',
              start_date: isoDateWithOffset(30),
              end_date: isoDateWithOffset(120),
              application_deadline: isoDateWithOffset(-1),
              application_window_open: false,
              application_window_message: `Applications closed on ${isoDateWithOffset(-1)}.`,
            },
          ],
        },
      })
    })

    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="program-select"]').exists()).toBe(true)
    })

    await wrapper.find('[data-testid="program-select"]').setValue('program-closed')

    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="application-window-alert"]').exists()).toBe(true)
    })

    expect(wrapper.find('[data-testid="create-application-btn"]').element.disabled).toBe(true)
    expect(wrapper.find('[data-testid="save-draft-btn"]').element.disabled).toBe(true)
    expect(wrapper.text()).toContain('Applications closed')
    expect(api.post).not.toHaveBeenCalled()
  })

  it('uses applicationFormPage.notAvailable for missing program dates and duration', async () => {
    api.get.mockImplementation((url) => {
      if (typeof url === 'string' && url.includes('/check_eligibility/')) {
        return Promise.resolve({
          data: { eligible: true, message: 'All eligibility requirements met' },
        })
      }
      if (url === '/api/programs/') {
        return Promise.resolve({
          data: {
            results: [
              {
                id: 'program-no-dates',
                name: 'Open Program',
                description: 'No fixed dates',
                start_date: null,
                end_date: null,
                application_open_date: null,
                application_deadline: null,
                application_form: 'form-1',
              },
            ],
          },
        })
      }
      if (url === '/api/application-forms/form-types/form-1/form_schema/') {
        return Promise.resolve({
          data: {
            id: 'form-1',
            name: 'Questions',
            description: '',
            schema: { properties: {}, required: [] },
            ui_schema: {},
            required_fields: [],
          },
        })
      }
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })

    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="program-select"]').exists()).toBe(true)
    })
    await wrapper.find('[data-testid="program-select"]').setValue('program-no-dates')
    await vi.waitFor(() => {
      expect(wrapper.text()).toContain('Program information')
    })
    const na = i18n.global.t('applicationFormPage.notAvailable')
    expect(wrapper.text().split(na).length - 1).toBeGreaterThanOrEqual(3)
  })

  it('shows eligibility alert from check_eligibility when student is not yet eligible', async () => {
    api.get.mockImplementation((url) => {
      if (typeof url === 'string' && url.includes('/check_eligibility/')) {
        return Promise.resolve({
          data: {
            eligible: false,
            message:
              'Eligibility requirements not met:\n- Language requirement not met. Required: German, Your language: English',
          },
        })
      }
      if (url === '/api/programs/') {
        return Promise.resolve({
          data: {
            results: [
              {
                id: 'p-ineligible',
                name: 'DAAD Munich',
                description: 'Technical exchange',
                start_date: '2026-09-01',
                end_date: '2027-01-15',
                required_language: 'German',
                min_language_level: 'C1',
              },
            ],
          },
        })
      }
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })

    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="program-select"]').exists()).toBe(true)
    })
    await wrapper.find('[data-testid="program-select"]').setValue('p-ineligible')
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="eligibility-alert"]').exists()).toBe(true)
    })
    expect(wrapper.text()).toContain('German')
    expect(wrapper.text()).toContain('English')
  })
})
