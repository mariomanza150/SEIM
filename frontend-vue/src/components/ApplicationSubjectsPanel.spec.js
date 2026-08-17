import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ApplicationSubjectsPanel from './ApplicationSubjectsPanel.vue'
import api from '@/services/api'
import i18n, { setAppLocale } from '@/i18n'

vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: vi.fn(), error: vi.fn() }),
}))

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  },
}))

describe('ApplicationSubjectsPanel', () => {
  beforeEach(() => {
    setAppLocale('en')
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('prompts to save first when there is no application id', () => {
    const wrapper = mount(ApplicationSubjectsPanel, {
      props: { applicationId: '', applicationStatus: 'draft' },
      global: { plugins: [i18n] },
    })
    expect(wrapper.find('[data-testid="subjects-save-first"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="add-custom-subject"]').exists()).toBe(false)
  })

  it('adds a custom host course and lists it', async () => {
    api.get.mockImplementation((url) => {
      if (url.includes('available-subjects')) return Promise.resolve({ data: [] })
      if (url.includes('application-subject-selections')) return Promise.resolve({ data: [] })
      if (url.includes('/api/host-institutions/')) return Promise.resolve({ data: { grade_scale: null } })
      if (url.includes('/api/grades/values/')) return Promise.resolve({ data: [] })
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })
    api.post.mockResolvedValue({
      data: {
        id: 'sel-1',
        custom_name: 'Custom Algorithms',
        custom_code: 'CUST1',
        home_course_code: 'H101',
        home_course_label: 'Algos',
        credits: '4.00',
        grade_status: 'none',
      },
    })

    const wrapper = mount(ApplicationSubjectsPanel, {
      props: {
        applicationId: 'app-1',
        applicationStatus: 'draft',
        hostInstitutionId: 'inst-1',
      },
      global: { plugins: [i18n] },
    })
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="add-custom-subject"]').exists()).toBe(true)
    })
    await wrapper.find('#custom-name').setValue('Custom Algorithms')
    await wrapper.find('#custom-code').setValue('CUST1')
    await wrapper.find('[data-testid="add-custom-subject"]').trigger('click')
    await vi.waitFor(() => {
      expect(api.post).toHaveBeenCalled()
      expect(wrapper.find('[data-testid="subject-selections-table"]').exists()).toBe(true)
    })
    expect(wrapper.text()).toContain('Custom Algorithms')
  })
})
