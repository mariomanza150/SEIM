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

  function mockPanelGets({
    selections = [],
    subjects = [],
    gradeScale = 'scale-1',
    gradeValues = [{ id: 'gv-1', label: 'HostA' }],
  } = {}) {
    api.get.mockImplementation((url) => {
      if (url.includes('available-subjects')) return Promise.resolve({ data: subjects })
      if (url.includes('application-subject-selections')) {
        return Promise.resolve({ data: selections })
      }
      if (url.includes('/api/host-institutions/')) {
        return Promise.resolve({ data: { grade_scale: gradeScale } })
      }
      if (url.includes('/api/grades/values/')) {
        return Promise.resolve({ data: gradeValues })
      }
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })
  }

  it('hides mapping and grade edits when confirmed, and only coordinators confirm/reject', async () => {
    mockPanelGets({
      selections: [
        {
          id: 'sel-1',
          custom_name: 'Algorithms',
          custom_code: 'CS101',
          credits: '6.00',
          grade_status: 'confirmed',
          proposed_host_grade: 'gv-1',
          proposed_host_grade_label: 'HostA',
          confirmed_host_grade_label: 'HostA',
          home_grade_label: 'HomeA',
        },
      ],
    })
    const wrapper = mount(ApplicationSubjectsPanel, {
      props: {
        applicationId: 'app-1',
        applicationStatus: 'approved',
        hostInstitutionId: 'inst-1',
        isCoordinator: true,
      },
      global: { plugins: [i18n] },
    })
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="subject-selections-table"]').exists()).toBe(true)
    })
    expect(wrapper.find('[data-testid="add-custom-subject"]').exists()).toBe(false)
    expect(wrapper.find('[data-testid="proposed-grade-sel-1"]').exists()).toBe(false)
    expect(wrapper.find('[data-testid="propose-subject-grades"]').exists()).toBe(false)
    expect(wrapper.find('[data-testid="confirm-subject-grades"]').exists()).toBe(false)
    expect(wrapper.find('[data-testid="reject-subject-grades"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('HostA')
    expect(wrapper.text()).toContain('HomeA')
  })

  it('lets students propose grades and hides coordinator actions', async () => {
    mockPanelGets({
      selections: [
        {
          id: 'sel-1',
          custom_name: 'Algorithms',
          custom_code: 'CS101',
          credits: '6.00',
          grade_status: 'none',
          proposed_host_grade: 'gv-1',
        },
      ],
    })
    const wrapper = mount(ApplicationSubjectsPanel, {
      props: {
        applicationId: 'app-1',
        applicationStatus: 'approved',
        hostInstitutionId: 'inst-1',
        isCoordinator: false,
      },
      global: { plugins: [i18n] },
    })
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="propose-subject-grades"]').exists()).toBe(true)
    })
    expect(wrapper.find('[data-testid="proposed-grade-sel-1"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="confirm-subject-grades"]').exists()).toBe(false)
    expect(wrapper.find('[data-testid="reject-subject-grades"]').exists()).toBe(false)
    expect(api.get.mock.calls.some(([url]) => String(url).includes('/api/grades/values/by_scale/'))).toBe(true)
  })

  it('warns when the host institution has no grade scale', async () => {
    mockPanelGets({
      selections: [
        {
          id: 'sel-1',
          custom_name: 'Algorithms',
          grade_status: 'none',
        },
      ],
      gradeScale: null,
      gradeValues: [],
    })
    const wrapper = mount(ApplicationSubjectsPanel, {
      props: {
        applicationId: 'app-1',
        applicationStatus: 'approved',
        hostInstitutionId: 'inst-1',
      },
      global: { plugins: [i18n] },
    })
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="missing-host-grade-scale"]').exists()).toBe(true)
    })
    expect(wrapper.find('[data-testid="propose-subject-grades"]').exists()).toBe(false)
    expect(wrapper.find('[data-testid="proposed-grade-sel-1"]').exists()).toBe(false)
  })

  it('shows confirm (not propose) for coordinators after the student submits', async () => {
    mockPanelGets({
      selections: [
        {
          id: 'sel-1',
          custom_name: 'Algorithms',
          grade_status: 'proposed',
          proposed_host_grade: 'gv-1',
          proposed_host_grade_label: 'HostA',
        },
      ],
    })
    const wrapper = mount(ApplicationSubjectsPanel, {
      props: {
        applicationId: 'app-1',
        applicationStatus: 'approved',
        hostInstitutionId: 'inst-1',
        isCoordinator: true,
      },
      global: { plugins: [i18n] },
    })
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="confirm-subject-grades"]').exists()).toBe(true)
    })
    expect(wrapper.find('[data-testid="propose-subject-grades"]').exists()).toBe(false)
    expect(wrapper.find('[data-testid="reject-subject-grades"]').exists()).toBe(true)
    expect(wrapper.find('#grade-notes').exists()).toBe(true)
  })
})
