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
      if (url.includes('subject-plan-versions')) return Promise.resolve({ data: [] })
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
    expect(wrapper.find('[data-testid="catalog-subject-form"]').exists()).toBe(false)
    expect(wrapper.find('[data-testid="no-catalog-subjects-help"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="host-subject-select"]').exists()).toBe(false)
    await wrapper.find('#custom-name').setValue('Custom Algorithms')
    await wrapper.find('#custom-code').setValue('CUST1')
    await wrapper.find('[data-testid="add-custom-subject"]').trigger('click')
    await vi.waitFor(() => {
      expect(api.post).toHaveBeenCalled()
      expect(wrapper.find('[data-testid="subject-selections-table"]').exists()).toBe(true)
    })
    expect(wrapper.text()).toContain('Custom Algorithms')
  })

  it('shows catalog picker when host subjects exist and keeps custom entry', async () => {
    mockPanelGets({
      subjects: [{ id: 'subj-1', code: 'CS101', name: 'Intro CS', credits: 3 }],
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
      expect(wrapper.find('[data-testid="catalog-subject-form"]').exists()).toBe(true)
    })
    expect(wrapper.find('[data-testid="host-subject-select"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="custom-subject-form"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="no-catalog-subjects-help"]').exists()).toBe(false)
  })

  function mockPanelGets({
    selections = [],
    subjects = [],
    gradeScale = 'scale-1',
    gradeValues = [{ id: 'gv-1', label: 'HostA' }],
    planVersions = [],
  } = {}) {
    api.get.mockImplementation((url) => {
      if (url.includes('subject-plan-versions')) {
        return Promise.resolve({ data: planVersions })
      }
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

  it('shows previous subject plan versions read-only', async () => {
    mockPanelGets({
      selections: [
        {
          id: 'sel-1',
          custom_name: 'Algorithms',
          custom_code: 'CS101',
          credits: '6.00',
          grade_status: 'none',
        },
      ],
      planVersions: [
        {
          id: 'ver-1',
          version_number: 1,
          created_at: '2026-01-15T10:00:00Z',
          created_by_name: 'Plan Student',
          payload: [
            {
              custom_name: 'Old Course',
              custom_code: 'OLD1',
              home_course_code: 'H100',
              credits: '3.00',
              grade_status: 'none',
            },
          ],
        },
      ],
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
      expect(wrapper.find('[data-testid="subject-plan-versions"]').exists()).toBe(true)
    })
    expect(wrapper.find('[data-testid="subject-plan-version-1"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('Previous versions')
    expect(wrapper.text()).toContain('Old Course')
    expect(wrapper.find('[data-testid="subject-plan-versions-empty"]').exists()).toBe(false)
    expect(
      api.get.mock.calls.some(([url]) => String(url).includes('subject-plan-versions')),
    ).toBe(true)
  })

  it('shows empty state when no previous versions exist', async () => {
    mockPanelGets({
      selections: [],
      planVersions: [],
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
      expect(wrapper.find('[data-testid="subject-plan-versions-empty"]').exists()).toBe(true)
    })
    expect(wrapper.text()).toContain('No previous versions yet')
  })

  it('shows Spanish labels for previous versions', async () => {
    setAppLocale('es')
    mockPanelGets({ selections: [], planVersions: [] })
    const wrapper = mount(ApplicationSubjectsPanel, {
      props: {
        applicationId: 'app-1',
        applicationStatus: 'draft',
        hostInstitutionId: 'inst-1',
      },
      global: { plugins: [i18n] },
    })
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="subject-plan-versions-empty"]').exists()).toBe(true)
    })
    expect(wrapper.text()).toContain('Versiones anteriores')
    expect(wrapper.text()).toContain('Aún no hay versiones anteriores')
  })

  const selectionFixture = {
    id: 'sel-1',
    custom_name: 'Algorithms',
    custom_code: 'CS101',
    home_course_code: 'H101',
    home_course_label: 'Home Algos',
    credits: '6.00',
    grade_status: 'none',
    proposed_host_grade: 'gv-1',
  }

  it('renders phone cards for current selections while keeping the desktop table (student)', async () => {
    mockPanelGets({ selections: [selectionFixture] })
    const wrapper = mount(ApplicationSubjectsPanel, {
      props: {
        applicationId: 'app-1',
        applicationStatus: 'approved',
        hostInstitutionId: 'inst-1',
        isCoordinator: false,
      },
      global: { plugins: [i18n] },
      attachTo: document.body,
    })
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="subject-selections-table"]').exists()).toBe(true)
    })

    const desktopPane = wrapper.find('.seim-responsive-list > .d-none.d-md-block')
    const mobilePane = wrapper.find('.seim-responsive-list__mobile.d-md-none')
    expect(desktopPane.exists()).toBe(true)
    expect(mobilePane.exists()).toBe(true)
    expect(desktopPane.find('[data-testid="subject-selections-table"]').exists()).toBe(true)

    const card = wrapper.find('[data-testid="subject-selection-card-sel-1"]')
    expect(card.exists()).toBe(true)
    expect(wrapper.find('[data-testid="subject-selections-mobile-0"]').exists()).toBe(true)
    expect(card.text()).toContain('CS101')
    expect(card.text()).toContain('Algorithms')
    expect(card.text()).toContain('H101')
    expect(card.text()).toContain('Home Algos')
    expect(card.text()).toContain('6.00')

    const gradeSelect = wrapper.find('[data-testid="proposed-grade-mobile-sel-1"]')
    const removeBtn = wrapper.find('[data-testid="remove-subject-mobile-sel-1"]')
    expect(gradeSelect.exists()).toBe(true)
    expect(removeBtn.exists()).toBe(true)
    expect(gradeSelect.classes()).toContain('subject-selection-card__control')
    expect(removeBtn.classes()).toContain('subject-selection-card__control')
    expect(removeBtn.attributes('aria-label')).toBe('Remove subject')

    gradeSelect.element.focus()
    expect(document.activeElement).toBe(gradeSelect.element)
    removeBtn.element.focus()
    expect(document.activeElement).toBe(removeBtn.element)

    // Historical snapshots stay table-only (out of scope for phone cards).
    expect(wrapper.find('[data-testid="subject-plan-versions"] .seim-responsive-list').exists()).toBe(false)

    wrapper.unmount()
  })

  it('renders phone cards for coordinators without student grade inputs', async () => {
    mockPanelGets({
      selections: [
        {
          ...selectionFixture,
          grade_status: 'proposed',
          proposed_host_grade_label: 'HostA',
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
      attachTo: document.body,
    })
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="subject-selection-card-sel-1"]').exists()).toBe(true)
    })

    const card = wrapper.find('[data-testid="subject-selection-card-sel-1"]')
    expect(card.text()).toContain('HostA')
    expect(card.text()).toContain('HomeA')
    expect(card.text()).toContain('Proposed')
    expect(wrapper.find('[data-testid="proposed-grade-mobile-sel-1"]').exists()).toBe(false)
    expect(wrapper.find('[data-testid="remove-subject-mobile-sel-1"]').exists()).toBe(false)
    expect(wrapper.find('[data-testid="confirm-subject-grades"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="reject-subject-grades"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="propose-subject-grades"]').exists()).toBe(false)

    const notes = wrapper.find('#grade-notes')
    notes.element.focus()
    expect(document.activeElement).toBe(notes.element)

    wrapper.unmount()
  })

  it('wires mobile remove and grade change to existing handlers', async () => {
    mockPanelGets({ selections: [selectionFixture] })
    api.patch.mockResolvedValue({
      data: { ...selectionFixture, proposed_host_grade: 'gv-1' },
    })
    api.delete.mockResolvedValue({})
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
      expect(wrapper.find('[data-testid="proposed-grade-mobile-sel-1"]').exists()).toBe(true)
    })

    await wrapper.find('[data-testid="proposed-grade-mobile-sel-1"]').setValue('gv-1')
    await vi.waitFor(() => {
      expect(api.patch).toHaveBeenCalledWith(
        '/api/application-subject-selections/sel-1/',
        { proposed_host_grade: 'gv-1' },
      )
    })

    await wrapper.find('[data-testid="remove-subject-mobile-sel-1"]').trigger('click')
    await vi.waitFor(() => {
      expect(api.delete).toHaveBeenCalledWith('/api/application-subject-selections/sel-1/')
    })
  })
})
