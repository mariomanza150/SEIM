import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { reactive, ref } from 'vue'
import ApplicationDetail from './ApplicationDetail.vue'
import api from '@/services/api'
import i18n, { setAppLocale } from '@/i18n'

const mockPush = vi.fn()
const mockSuccessToast = vi.fn()
const mockErrorToast = vi.fn()
const mockConfirm = vi.fn().mockResolvedValue(true)
const routeParams = reactive({ id: 'test-app' })
const mockAuthStore = {
  userRole: 'coordinator',
  canUseStaffReviewQueue: true,
  isAdmin: false,
  user: {
    id: 'current-user',
  },
}

vi.mock('vue-router', () => ({
  useRoute: () => ({
    params: routeParams,
    get fullPath() {
      return `/applications/${routeParams.id}`
    },
  }),
  useRouter: () => ({
    push: (to) => {
      mockPush(to)
      if (to?.params?.id != null) {
        routeParams.id = String(to.params.id)
      }
    },
  }),
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockAuthStore,
}))

vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: mockSuccessToast, error: mockErrorToast }),
}))

vi.mock('@/composables/useConfirm', () => ({
  useConfirm: () => ({ confirm: mockConfirm }),
}))

const scholarshipsEnabledRef = ref(true)
vi.mock('@/composables/useFeatures', () => ({
  useFeatures: () => ({
    scholarshipsEnabled: scholarshipsEnabledRef,
    loadFeatures: vi.fn().mockResolvedValue({ scholarships_enabled: true }),
    features: { value: { scholarships_enabled: true } },
    loading: { value: false },
    error: { value: '' },
    updateFeatures: vi.fn(),
    _resetFeaturesState: vi.fn(),
  }),
}))

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn(),
    patch: vi.fn(),
    put: vi.fn(),
  },
}))

const applicationPayload = {
  id: 'test-app',
  created_at: '2026-04-08T10:00:00Z',
  updated_at: '2026-04-08T10:00:00Z',
  submitted_at: null,
  status: 'under_review',
  program: {
    name: 'Exchange Program',
    institution: 'Partner University',
    country: 'Mexico',
    duration: '1 semester',
    description: 'A test program',
  },
}

function mountView() {
  return mount(ApplicationDetail, {
    global: {
      plugins: [createPinia(), i18n],
      stubs: {
        DocumentUpload: {
          props: ['applicationId', 'checklist', 'preselectedTypeId'],
          template:
            '<div class="document-upload-stub" data-testid="document-upload-stub" :data-prefill="preselectedTypeId == null ? \'\' : String(preselectedTypeId)"></div>',
        },
        ApplicationSubjectsPanel: { template: '<div class="subjects-panel-stub"></div>' },
        RouterLink: { template: '<a><slot /></a>' },
      },
    },
  })
}

async function expandCollapsible(wrapper, testId) {
  const card = wrapper.find(`[data-testid="${testId}"]`)
  expect(card.exists()).toBe(true)
  const toggle = card.find('[data-testid="collapsible-card-toggle"]')
  if (toggle.attributes('aria-expanded') === 'false') {
    await toggle.trigger('click')
  }
}

async function flushPromises() {
  await Promise.resolve()
  await Promise.resolve()
  await new Promise((resolve) => setTimeout(resolve, 0))
}

describe('ApplicationDetail', () => {
  beforeEach(() => {
    localStorage.clear()
    sessionStorage.clear()
    setAppLocale('en')
    setActivePinia(createPinia())
    scholarshipsEnabledRef.value = true
    routeParams.id = 'test-app'
    mockAuthStore.userRole = 'coordinator'
    mockAuthStore.canUseStaffReviewQueue = true
    mockAuthStore.isAdmin = false
    mockAuthStore.user = { id: 'current-user' }
    mockConfirm.mockResolvedValue(true)
    vi.clearAllMocks()
  })

  afterEach(() => {
    setAppLocale('en')
    localStorage.clear()
    sessionStorage.clear()
  })

  it('renders existing comments with author metadata', async () => {
    const comments = [
      {
        id: 'comment-1',
        application: 'test-app',
        author: 'other-user',
        author_name: 'Coordinator User',
        author_role: 'coordinator',
        text: 'Please upload the missing transcript.',
        is_private: false,
        created_at: '2026-04-08T11:00:00Z',
      },
    ]

    api.get.mockImplementation((url) => {
      if (url === '/api/applications/test-app/') {
        return Promise.resolve({ data: applicationPayload })
      }
      if (url === '/api/documents/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/comments/') {
        return Promise.resolve({ data: { results: comments } })
      }
      if (url === '/api/timeline-events/') {
        return Promise.resolve({ data: { results: [] } })
      }
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })

    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.find('#commentText').exists()).toBe(true)
    })

    expect(wrapper.text()).toContain('Coordinator User')
    expect(wrapper.text()).toContain('Please upload the missing transcript.')
    expect(wrapper.find('#commentText').exists()).toBe(true)
    expect(wrapper.find('#privateComment').exists()).toBe(true)
    const crumb = wrapper.get('[aria-current="page"]')
    expect(crumb.classes()).toContain('seim-page-breadcrumb__item--truncate')
    expect(crumb.text()).toBe('Exchange Program')
    expect(crumb.get('.seim-page-breadcrumb__text').attributes('title')).toBe('Exchange Program')
  })

  it('submits a new comment and refreshes the list', async () => {
    let comments = []

    api.get.mockImplementation((url) => {
      if (url === '/api/applications/test-app/') {
        return Promise.resolve({ data: applicationPayload })
      }
      if (url === '/api/documents/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/comments/') {
        return Promise.resolve({ data: { results: comments } })
      }
      if (url === '/api/timeline-events/') {
        return Promise.resolve({ data: { results: [] } })
      }
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })

    api.post.mockImplementation((url, payload) => {
      if (url === '/api/comments/') {
        comments = [
          {
            id: 'comment-2',
            application: payload.application,
            author: 'current-user',
            author_name: 'Coordinator User',
            author_role: 'coordinator',
            text: payload.text,
            is_private: payload.is_private,
            created_at: '2026-04-08T12:00:00Z',
          },
        ]
        return Promise.resolve({ data: comments[0] })
      }
      return Promise.reject(new Error(`Unhandled POST ${url}`))
    })

    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.find('#commentText').exists()).toBe(true)
    })

    await wrapper.find('#commentText').setValue('Internal note for reviewers')
    await wrapper.find('#privateComment').setValue(true)
    await wrapper.find('[data-testid="comment-form"]').trigger('submit.prevent')
    await vi.waitFor(() => {
      expect(api.post).toHaveBeenCalled()
    })

    expect(api.post).toHaveBeenCalledWith('/api/comments/', {
      application: 'test-app',
      text: 'Internal note for reviewers',
      is_private: true,
    })
    expect(mockSuccessToast).toHaveBeenCalledWith('Comment posted successfully')
    expect(wrapper.text()).toContain('Internal note for reviewers')
    expect(wrapper.text()).toContain('Private')
  })

  it('uses applicationDetailPage.notAvailable for missing program location fields', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/test-app/') {
        return Promise.resolve({
          data: {
            ...applicationPayload,
            program: {
              name: 'Sparse Program',
              institution: '',
              country: null,
              duration: null,
              description: 'Desc',
            },
          },
        })
      }
      if (url === '/api/documents/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/comments/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/timeline-events/') {
        return Promise.resolve({ data: { results: [] } })
      }
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })

    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.text()).toContain('Sparse Program')
    })
    await expandCollapsible(wrapper, 'program-info-card')
    const na = i18n.global.t('applicationDetailPage.notAvailable')
    expect(wrapper.text().split(na).length - 1).toBeGreaterThanOrEqual(3)
  })

  it('uses program_name when program is only a FK id', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/test-app/') {
        return Promise.resolve({
          data: {
            ...applicationPayload,
            program: '11111111-1111-1111-1111-111111111111',
            program_name: 'API Program Label',
          },
        })
      }
      if (url === '/api/documents/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/comments/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/timeline-events/') {
        return Promise.resolve({ data: { results: [] } })
      }
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })

    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.text()).toContain('API Program Label')
    })
    expect(wrapper.text()).not.toContain('Exchange Program')
  })

  it('uses host_institution_name when program is only a FK id', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/test-app/') {
        return Promise.resolve({
          data: {
            ...applicationPayload,
            program: '11111111-1111-1111-1111-111111111111',
            program_name: 'DAAD Exchange',
            host_institution_name: 'Technical University of Munich',
            host_institution_country: 'Germany',
          },
        })
      }
      if (url === '/api/documents/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/comments/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/timeline-events/') {
        return Promise.resolve({ data: { results: [] } })
      }
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })

    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.text()).toContain('DAAD Exchange')
    })
    expect(wrapper.text()).toContain('Technical University of Munich')
    await expandCollapsible(wrapper, 'program-info-card')
    expect(wrapper.text()).toContain('Germany')
    expect(wrapper.find('[data-testid="program-duration"]').text()).toBe(
      i18n.global.t('applicationDetailPage.notAvailable'),
    )
  })

  it('formats program duration from start and end dates when program is a FK id', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/test-app/') {
        return Promise.resolve({
          data: {
            ...applicationPayload,
            program: '11111111-1111-1111-1111-111111111111',
            program_name: 'DAAD Exchange',
            host_institution_name: 'Technical University of Munich',
            host_institution_country: 'Germany',
            program_start_date: '2026-09-01',
            program_end_date: '2026-12-15',
          },
        })
      }
      if (url === '/api/documents/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/comments/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/timeline-events/') {
        return Promise.resolve({ data: { results: [] } })
      }
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })

    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.text()).toContain('DAAD Exchange')
    })
    await expandCollapsible(wrapper, 'program-info-card')
    expect(wrapper.find('[data-testid="program-duration"]').text()).toMatch(/Sep 1, 2026/)
    expect(wrapper.find('[data-testid="program-duration"]').text()).toMatch(/Dec 15, 2026/)
    expect(wrapper.find('[data-testid="program-duration"]').text()).not.toBe(
      i18n.global.t('applicationDetailPage.notAvailable'),
    )
  })

  it('shows scholarship scoring panel for coordinators when API returns score', async () => {
    const scholarshipScore = {
      ruleset_id: 'default_v1',
      ruleset_label: 'Default rubric',
      total_points: 88.5,
      max_points: 100,
      factors: [
        {
          id: 'academic',
          label: 'Academic record',
          points: 19.380000000000003,
          max_points: 25,
          detail: 'GPA (institutional scale): 3.50',
        },
      ],
      tie_breakers: ['total_points_desc', 'gpa_equivalent_desc'],
      flags: { withdrawn: false },
      disclaimer: 'Staff comparison tool only.',
    }
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/test-app/') {
        return Promise.resolve({
          data: {
            ...applicationPayload,
            program: '11111111-1111-1111-1111-111111111111',
            program_name: 'Exchange Program',
            scholarship_allocation_score: scholarshipScore,
          },
        })
      }
      if (url === '/api/documents/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/comments/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/timeline-events/') {
        return Promise.resolve({ data: { results: [] } })
      }
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })

    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="scholarship-score-panel"]').exists()).toBe(true)
    })
    expect(wrapper.text()).toContain('88.5')
    expect(wrapper.text()).toContain('19.38')
    expect(wrapper.text()).not.toContain('19.380000000000003')
    expect(wrapper.find('[data-testid="scholarship-disclaimer"]').text()).toBe(
      i18n.global.t('applicationDetailPage.scholarshipScoring.disclaimerStaff'),
    )
    expect(wrapper.find('[data-testid="scholarship-ruleset-label"]').text()).toBe(
      i18n.global.t('applicationDetailPage.scholarshipScoring.rulesetDefault'),
    )
    expect(wrapper.text()).toContain(i18n.global.t('applicationDetailPage.scholarshipScoring.factors.academic'))
    expect(wrapper.text()).not.toContain('default_v1')
  })

  it('shows scholarship estimate for students without cohort export buttons', async () => {
    mockAuthStore.userRole = 'student'
    mockAuthStore.canUseStaffReviewQueue = false
    const scholarshipScore = {
      ruleset_id: 'default_v1',
      ruleset_label: 'Default rubric',
      total_points: 70,
      max_points: 100,
      factors: [{ id: 'academic', label: 'Academic', points: 20, max_points: 25, detail: 'GPA' }],
      tie_breakers: ['total_points_desc'],
      flags: { withdrawn: false },
      disclaimer: 'Student disclaimer.',
    }
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/test-app/') {
        return Promise.resolve({
          data: {
            ...applicationPayload,
            program: '11111111-1111-1111-1111-111111111111',
            program_name: 'Exchange Program',
            scholarship_allocation_score: scholarshipScore,
          },
        })
      }
      if (url === '/api/documents/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/comments/') {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url === '/api/timeline-events/') {
        return Promise.resolve({ data: { results: [] } })
      }
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })

    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="scholarship-score-panel"]').exists()).toBe(true)
    })
    expect(wrapper.text()).toContain(i18n.global.t('applicationDetailPage.scholarshipScoring.studentTitle'))
    expect(wrapper.find('[data-testid="scholarship-disclaimer"]').text()).toBe(
      i18n.global.t('applicationDetailPage.scholarshipScoring.disclaimerStudent'),
    )
    expect(wrapper.text()).toContain('70')
    expect(wrapper.text()).not.toContain('default_v1')
    expect(wrapper.text()).not.toContain(
      i18n.global.t('applicationDetailPage.scholarshipScoring.exportCohortCsv'),
    )
    mockAuthStore.userRole = 'coordinator'
  })

  it('shows scholarship award panel for coordinators', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/test-app/') {
        return Promise.resolve({ data: { ...applicationPayload, scholarship_award: null } })
      }
      if (url === '/api/documents/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/comments/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/timeline-events/') return Promise.resolve({ data: { results: [] } })
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })
    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="scholarship-award-panel"]').exists()).toBe(true)
    })
    expect(wrapper.text()).toContain(i18n.global.t('applicationDetailPage.scholarshipAward.noneYet'))
    expect(wrapper.find('[data-testid="award-save"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="award-evidence-hint"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="scholarship-awards-export"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="scholarship-awards-export-xlsx"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="scholarship-awards-export-pdf"]').exists()).toBe(true)
  })

  it('hides scholarship score and award panels when feature is disabled', async () => {
    scholarshipsEnabledRef.value = false
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/test-app/') {
        return Promise.resolve({
          data: {
            ...applicationPayload,
            scholarship_allocation_score: {
              ruleset_id: 'default_v1',
              total_points: 10,
              max_points: 100,
              factors: [],
            },
            scholarship_award: null,
          },
        })
      }
      if (url === '/api/documents/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/comments/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/timeline-events/') return Promise.resolve({ data: { results: [] } })
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })
    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="application-detail-page"]').exists()).toBe(true)
    })
    expect(wrapper.find('[data-testid="scholarship-score-panel"]').exists()).toBe(false)
    expect(wrapper.find('[data-testid="scholarship-award-panel"]').exists()).toBe(false)
  })

  it('shows scholarship evidence gates when catalog types are missing', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/test-app/') {
        return Promise.resolve({
          data: {
            ...applicationPayload,
            scholarship_award: {
              status: 'disbursing',
              amount: '20000',
              currency: 'MXN',
              evidence_documents: [],
              evidence_gates: {
                awarded: { any_of: ['carta_beca'], configured: true, satisfied: false },
                disbursed: { any_of: ['recibo_beca'], configured: true, satisfied: false },
              },
              disbursements: [
                { id: 'd1', label: 'Fall', status: 'pending', amount: '10000' },
                { id: 'd2', label: 'Spring', status: 'pending', amount: '10000' },
              ],
            },
          },
        })
      }
      if (url === '/api/documents/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/comments/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/timeline-events/') return Promise.resolve({ data: { results: [] } })
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })
    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="award-evidence-gate"]').exists()).toBe(true)
    })
    expect(wrapper.find('[data-testid="award-evidence-gate"]').text()).toContain(
      i18n.global.t('applicationDetailPage.scholarshipAward.evidenceAwardedGate'),
    )
    expect(wrapper.find('[data-testid="award-evidence-gate"]').text()).toContain(
      i18n.global.t('applicationDetailPage.scholarshipAward.evidenceDisbursedGate'),
    )
    const disbursed = wrapper.find('[data-testid="award-status"]').find('option[value="disbursed"]')
    expect(disbursed.attributes('disabled')).toBeDefined()
    const rows = wrapper.findAll('[data-testid="award-disbursement-row"]')
    expect(rows).toHaveLength(2)
    expect(rows[0].text()).toContain(i18n.global.t('applicationDetailPage.scholarshipAward.disbursementStatus.pending'))
    expect(rows[0].text()).not.toMatch(/\bpending\b/)
  })

  it('shows uploaded documents as pending until staff validation', async () => {
    mockAuthStore.userRole = 'student'
    mockAuthStore.canUseStaffReviewQueue = false
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/test-app/') {
        return Promise.resolve({ data: applicationPayload })
      }
      if (url === '/api/documents/') {
        return Promise.resolve({
          data: {
            results: [
              {
                id: 'doc-pending',
                type: { id: 1, name: 'Transcript' },
                is_valid: false,
                validated_at: null,
              },
              {
                id: 'doc-invalid',
                type: { id: 2, name: 'Passport' },
                is_valid: false,
                validated_at: '2026-08-17T12:00:00Z',
              },
              {
                id: 'doc-valid',
                type: { id: 3, name: 'Motivation letter' },
                is_valid: true,
                validated_at: '2026-08-17T12:00:00Z',
              },
            ],
          },
        })
      }
      if (url === '/api/comments/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/timeline-events/') return Promise.resolve({ data: { results: [] } })
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })

    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.findAll('[data-testid="document-status-badge"]')).toHaveLength(3)
    })

    const badges = wrapper.findAll('[data-testid="document-status-badge"]')
    expect(badges[0].text()).toBe(i18n.global.t('applicationDetailPage.checklist.pending_review'))
    expect(badges[0].classes()).toContain('bg-warning')
    expect(badges[1].text()).toBe(i18n.global.t('applicationDetailPage.checklist.invalid'))
    expect(badges[1].classes()).toContain('bg-danger')
    expect(badges[2].text()).toBe(i18n.global.t('applicationDetailPage.checklist.approved'))
    expect(badges[2].classes()).toContain('bg-success')
    mockAuthStore.userRole = 'coordinator'
  })

  it('disables submit when host destination is required but incomplete', async () => {
    mockAuthStore.userRole = 'student'
    mockAuthStore.canUseStaffReviewQueue = false
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/test-app/') {
        return Promise.resolve({
          data: {
            ...applicationPayload,
            status: 'draft',
            document_checklist: { required_count: 0, complete: true },
            readiness: {
              score: 90,
              level: 'attention',
              headline: 'Host destination incomplete.',
              host_destination: { required: true, complete: false },
            },
          },
        })
      }
      if (url === '/api/documents/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/comments/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/timeline-events/') return Promise.resolve({ data: { results: [] } })
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })

    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="submit-application-btn"]').exists()).toBe(true)
    })
    const btn = wrapper.find('[data-testid="submit-application-btn"]')
    expect(btn.attributes('disabled')).toBeDefined()
    expect(btn.attributes('title')).toBe(
      i18n.global.t('applicationDetailPage.submitBlockedHostTitle')
    )
    mockAuthStore.userRole = 'coordinator'
  })

  it('disables submit when eligibility is incomplete', async () => {
    mockAuthStore.userRole = 'student'
    mockAuthStore.canUseStaffReviewQueue = false
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/test-app/') {
        return Promise.resolve({
          data: {
            ...applicationPayload,
            status: 'draft',
            document_checklist: { required_count: 0, complete: true },
            readiness: {
              score: 88,
              level: 'attention',
              headline: 'Eligibility requirements not met.',
              host_destination: { required: false, complete: true },
              eligibility: {
                complete: false,
                issues: ['Language proficiency below requirement. Required: B2, Your level: A2'],
              },
            },
          },
        })
      }
      if (url === '/api/documents/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/comments/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/timeline-events/') return Promise.resolve({ data: { results: [] } })
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })

    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="submit-application-btn"]').exists()).toBe(true)
    })
    const btn = wrapper.find('[data-testid="submit-application-btn"]')
    expect(btn.attributes('disabled')).toBeDefined()
    expect(btn.attributes('title')).toBe(
      i18n.global.t('applicationDetailPage.submitBlockedEligibilityTitle')
    )
    expect(wrapper.find('[data-testid="readiness-eligibility-issues"]').text()).toContain(
      'Language proficiency'
    )
    expect(wrapper.find('[data-testid="eligibility-fix-action"]').text()).toBe(
      i18n.global.t('eligibilityFix.openProfile'),
    )
    mockAuthStore.userRole = 'coordinator'
  })

  it('localizes eligibility issues from message_key', async () => {
    mockAuthStore.userRole = 'student'
    mockAuthStore.canUseStaffReviewQueue = false
    setAppLocale('es')
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/test-app/') {
        return Promise.resolve({
          data: {
            ...applicationPayload,
            status: 'draft',
            document_checklist: { required_count: 0, complete: true },
            readiness: {
              score: 88,
              level: 'attention',
              headline: 'Eligibility requirements not met.',
              host_destination: { required: false, complete: true },
              eligibility: {
                complete: false,
                issues: ['Language proficiency below requirement. Required: B2, Your level: A2'],
                rules: [
                  {
                    id: 'min_language_level',
                    passed: false,
                    skipped: false,
                    message_key: 'language_level_below',
                    message_params: { required: 'B2', student: 'A2' },
                    message: 'Language proficiency below requirement. Required: B2, Your level: A2',
                  },
                ],
              },
            },
          },
        })
      }
      if (url === '/api/documents/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/comments/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/timeline-events/') return Promise.resolve({ data: { results: [] } })
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })
    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="readiness-eligibility-issues"]').exists()).toBe(true)
    })
    expect(wrapper.find('[data-testid="readiness-eligibility-issues"]').text()).toContain(
      i18n.global.t('eligibilityRules.language_level_below', { required: 'B2', student: 'A2' }),
    )
    setAppLocale('en')
    mockAuthStore.userRole = 'coordinator'
  })

  it('localizes draft readiness headlines from structured fields', async () => {
    mockAuthStore.userRole = 'student'
    mockAuthStore.canUseStaffReviewQueue = false
    setAppLocale('es')
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/test-app/') {
        return Promise.resolve({
          data: {
            ...applicationPayload,
            status: 'draft',
            document_checklist: { required_count: 1, complete: false },
            readiness: {
              score: 88,
              level: 'attention',
              headline: '1 required document(s) missing; Eligibility requirements not met.',
              window_open: true,
              document_counts: { missing: 1, resubmit: 0, pending_review: 0, required: 2 },
              host_destination: { required: false, complete: true },
              eligibility: { complete: false, issues: [] },
              form_complete: true,
            },
          },
        })
      }
      if (url === '/api/documents/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/comments/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/timeline-events/') return Promise.resolve({ data: { results: [] } })
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })
    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="readiness-headline"]').exists()).toBe(true)
    })
    expect(wrapper.find('[data-testid="readiness-headline"]').text()).toBe(
      `${i18n.global.t('applicationDetailPage.readinessHeadline.draft.missingDocsOne', { n: 1 })}; ${i18n.global.t('applicationDetailPage.readinessHeadline.draft.eligibilityUnmet')}.`,
    )
    setAppLocale('en')
    mockAuthStore.userRole = 'coordinator'
  })

  it('localizes nominated readiness headline instead of a raw slug', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/test-app/') {
        return Promise.resolve({
          data: {
            ...applicationPayload,
            status: 'nominated',
            readiness: {
              score: 100,
              level: 'done',
              headline: 'Status: nominated.',
            },
          },
        })
      }
      if (url === '/api/documents/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/comments/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/timeline-events/') return Promise.resolve({ data: { results: [] } })
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })
    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="readiness-headline"]').exists()).toBe(true)
    })
    expect(wrapper.find('[data-testid="readiness-headline"]').text()).toBe(
      i18n.global.t('applicationDetailPage.readinessHeadline.nominated'),
    )
    expect(wrapper.find('[data-testid="readiness-headline"]').text()).not.toMatch(/Status: nominated/)
  })

  it('localizes generic status_change timeline events', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/test-app/') {
        return Promise.resolve({ data: applicationPayload })
      }
      if (url === '/api/documents/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/comments/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/timeline-events/') {
        return Promise.resolve({
          data: {
            results: [
              {
                id: 'ev-1',
                event_type: 'status_change',
                description: 'Application status changed to under_review',
                created_at: '2026-08-16T10:21:00Z',
              },
              {
                id: 'ev-2',
                event_type: 'status_nominated',
                description: 'Nomination matching set status to nominated.',
                created_at: '2026-08-18T23:48:00Z',
              },
            ],
          },
        })
      }
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })
    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="activity-timeline-card"]').exists()).toBe(true)
    })
    await expandCollapsible(wrapper, 'activity-timeline-card')
    await vi.waitFor(() => {
      expect(wrapper.findAll('[data-testid="timeline-event-heading"]').length).toBe(2)
    })
    const headings = wrapper.findAll('[data-testid="timeline-event-heading"]')
    expect(headings[0].text()).toBe(
      i18n.global.t('applicationDetailPage.timeline.statusChanged', {
        status: i18n.global.t('applicationDetailPage.status.under_review'),
      }),
    )
    expect(headings[1].text()).toBe(
      i18n.global.t('applicationDetailPage.timeline.statusChanged', {
        status: i18n.global.t('applicationDetailPage.status.nominated'),
      }),
    )
    expect(wrapper.findAll('[data-testid="timeline-event-description"]')[0].text()).not.toMatch(/under_review/)
    expect(wrapper.findAll('[data-testid="timeline-event-description"]')[1].text()).not.toMatch(/\bnominated\b/)
  })

  it('does not duplicate Application record created when API already has application_created (MQ-027)', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/test-app/') {
        return Promise.resolve({ data: applicationPayload })
      }
      if (url === '/api/documents/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/comments/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/timeline-events/') {
        return Promise.resolve({
          data: {
            results: [
              {
                id: 'ev-created',
                event_type: 'application_created',
                description: 'Application created for demo walkthrough.',
                created_at: '2026-08-16T10:21:00Z',
                created_by_name: 'Diego Lopez',
              },
            ],
          },
        })
      }
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })
    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="activity-timeline-card"]').exists()).toBe(true)
    })
    await expandCollapsible(wrapper, 'activity-timeline-card')
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="timeline-event-heading"]').exists()).toBe(true)
    })
    const createdLabels = wrapper
      .findAll('h6')
      .filter((node) => node.text() === i18n.global.t('applicationDetailPage.timelineCreated'))
    expect(createdLabels).toHaveLength(1)
    expect(wrapper.find('[data-testid="timeline-event-description"]').text()).toContain(
      'Application created for demo walkthrough.',
    )
  })

  it('shows human document type labels instead of slugs on the checklist', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/test-app/') {
        return Promise.resolve({
          data: {
            ...applicationPayload,
            status: 'draft',
            document_checklist: {
              required_count: 2,
              approved_count: 1,
              complete: false,
              items: [
                {
                  document_type_id: 1,
                  slug: 'transcript',
                  name: 'transcript',
                  description: 'Academic transcript',
                  status: 'resubmit_requested',
                  is_required: true,
                },
                {
                  document_type_id: 2,
                  slug: 'passport',
                  name: 'passport',
                  description: 'Passport or ID',
                  status: 'approved',
                  is_required: true,
                },
              ],
            },
          },
        })
      }
      if (url === '/api/documents/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/comments/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/timeline-events/') return Promise.resolve({ data: { results: [] } })
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })
    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="document-checklist-section-action"]').exists()).toBe(true)
    })
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="document-checklist-name"]').exists()).toBe(true)
    })
    expect(wrapper.find('[data-testid="document-checklist-name"]').text()).toBe('Academic transcript')
    const doneToggle = wrapper
      .find('[data-testid="document-checklist-section-done"]')
      .find('[data-testid="document-checklist-section-toggle"]')
    await doneToggle.trigger('click')
    await vi.waitFor(() => {
      expect(wrapper.findAll('[data-testid="document-checklist-name"]').length).toBe(2)
    })
    const names = wrapper.findAll('[data-testid="document-checklist-name"]').map((n) => n.text())
    expect(names).toEqual(['Academic transcript', 'Passport or ID'])
    expect(names).not.toContain('transcript')
    expect(names).not.toContain('passport')
  })

  it('defaults Needs action open and Pending review open for staff', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/test-app/') {
        return Promise.resolve({
          data: {
            ...applicationPayload,
            status: 'draft',
            document_checklist: {
              required_count: 4,
              approved_count: 2,
              complete: false,
              items: [
                {
                  document_type_id: 1,
                  slug: 'transcript',
                  name: 'Transcript',
                  status: 'missing',
                  is_required: true,
                },
                {
                  document_type_id: 2,
                  slug: 'passport',
                  name: 'Passport',
                  status: 'pending_review',
                  is_required: true,
                },
                {
                  document_type_id: 3,
                  slug: 'motivation',
                  name: 'Motivation letter',
                  status: 'approved',
                  is_required: true,
                },
                {
                  document_type_id: 4,
                  slug: 'photo',
                  name: 'Photo',
                  status: 'approved',
                  is_required: true,
                },
              ],
            },
          },
        })
      }
      if (url === '/api/documents/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/comments/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/timeline-events/') return Promise.resolve({ data: { results: [] } })
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })

    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="document-checklist-section-action"]').exists()).toBe(true)
    })

    const actionSection = wrapper.find('[data-testid="document-checklist-section-action"]')
    const pendingSection = wrapper.find('[data-testid="document-checklist-section-pending_review"]')
    const doneSection = wrapper.find('[data-testid="document-checklist-section-done"]')

    expect(actionSection.find('[data-testid="document-checklist-section-count"]').text()).toBe('1')
    expect(pendingSection.find('[data-testid="document-checklist-section-count"]').text()).toBe('1')
    expect(doneSection.find('[data-testid="document-checklist-section-count"]').text()).toBe('2')

    expect(actionSection.find('[data-testid="document-checklist-section-toggle"]').attributes('aria-expanded')).toBe('true')
    expect(pendingSection.find('[data-testid="document-checklist-section-toggle"]').attributes('aria-expanded')).toBe('true')
    expect(doneSection.find('[data-testid="document-checklist-section-toggle"]').attributes('aria-expanded')).toBe('false')

    expect(actionSection.find('[data-testid="document-checklist-section-panel"]').exists()).toBe(true)
    expect(pendingSection.find('[data-testid="document-checklist-section-panel"]').exists()).toBe(true)
    expect(doneSection.find('[data-testid="document-checklist-section-panel"]').exists()).toBe(false)
    expect(wrapper.findAll('[data-testid="document-checklist-item"]')).toHaveLength(2)
    expect(wrapper.text()).toContain(i18n.global.t('applicationDetailPage.checklistSections.action'))
    expect(wrapper.text()).toContain(i18n.global.t('applicationDetailPage.checklistSections.done'))

    const actionToggle = actionSection.find('[data-testid="document-checklist-section-toggle"]')
    const pendingToggle = pendingSection.find('[data-testid="document-checklist-section-toggle"]')
    const doneToggle = doneSection.find('[data-testid="document-checklist-section-toggle"]')

    await actionToggle.trigger('click')
    await vi.waitFor(() => {
      expect(actionSection.find('[data-testid="document-checklist-section-panel"]').exists()).toBe(false)
    })
    expect(actionToggle.attributes('aria-expanded')).toBe('false')
    expect(wrapper.findAll('[data-testid="document-checklist-item"]')).toHaveLength(1)

    await actionToggle.trigger('click')
    await vi.waitFor(() => {
      expect(actionSection.find('[data-testid="document-checklist-section-panel"]').exists()).toBe(true)
    })
    expect(actionToggle.attributes('aria-expanded')).toBe('true')
    expect(wrapper.findAll('[data-testid="document-checklist-item"]')).toHaveLength(2)

    expect(pendingToggle.attributes('aria-expanded')).toBe('true')

    await doneToggle.trigger('click')
    await vi.waitFor(() => {
      expect(doneSection.find('[data-testid="document-checklist-section-panel"]').exists()).toBe(true)
    })
    expect(doneToggle.attributes('aria-expanded')).toBe('true')
    expect(wrapper.findAll('[data-testid="document-checklist-item"]')).toHaveLength(4)

    await doneToggle.trigger('click')
    await vi.waitFor(() => {
      expect(doneSection.find('[data-testid="document-checklist-section-panel"]').exists()).toBe(false)
    })
    expect(doneToggle.attributes('aria-expanded')).toBe('false')
  })

  it('keeps Pending review collapsed by default for students', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/test-app/') {
        return Promise.resolve({
          data: {
            ...applicationPayload,
            status: 'draft',
            document_checklist: {
              required_count: 2,
              approved_count: 0,
              complete: false,
              items: [
                {
                  document_type_id: 1,
                  slug: 'transcript',
                  name: 'Transcript',
                  status: 'missing',
                  is_required: true,
                },
                {
                  document_type_id: 2,
                  slug: 'passport',
                  name: 'Passport',
                  status: 'pending_review',
                  is_required: true,
                },
              ],
            },
          },
        })
      }
      if (url === '/api/documents/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/comments/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/timeline-events/') return Promise.resolve({ data: { results: [] } })
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })
    mockAuthStore.userRole = 'student'
    mockAuthStore.canUseStaffReviewQueue = false
    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="document-checklist-section-action"]').exists()).toBe(true)
    })
    const actionSection = wrapper.find('[data-testid="document-checklist-section-action"]')
    const pendingSection = wrapper.find('[data-testid="document-checklist-section-pending_review"]')
    expect(actionSection.find('[data-testid="document-checklist-section-toggle"]').attributes('aria-expanded')).toBe('true')
    expect(pendingSection.find('[data-testid="document-checklist-section-toggle"]').attributes('aria-expanded')).toBe('false')
  })

  it('keeps all checklist sections collapsed by default for admins', async () => {
    mockAuthStore.userRole = 'admin'
    mockAuthStore.canUseStaffReviewQueue = true
    mockAuthStore.isAdmin = true
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/test-app/') {
        return Promise.resolve({
          data: {
            ...applicationPayload,
            status: 'under_review',
            document_checklist: {
              required_count: 3,
              approved_count: 1,
              complete: false,
              items: [
                {
                  document_type_id: 1,
                  slug: 'transcript',
                  name: 'Transcript',
                  status: 'missing',
                  is_required: true,
                },
                {
                  document_type_id: 2,
                  slug: 'passport',
                  name: 'Passport',
                  status: 'pending_review',
                  is_required: true,
                },
                {
                  document_type_id: 3,
                  slug: 'motivation',
                  name: 'Motivation letter',
                  status: 'approved',
                  is_required: true,
                },
              ],
            },
          },
        })
      }
      if (url === '/api/documents/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/comments/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/timeline-events/') return Promise.resolve({ data: { results: [] } })
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })

    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="document-checklist-section-action"]').exists()).toBe(true)
    })

    for (const sectionId of ['action', 'pending_review', 'done']) {
      const section = wrapper.find(`[data-testid="document-checklist-section-${sectionId}"]`)
      expect(section.exists()).toBe(true)
      expect(section.find('[data-testid="document-checklist-section-toggle"]').attributes('aria-expanded')).toBe(
        'false',
      )
      expect(section.find('[data-testid="document-checklist-section-panel"]').exists()).toBe(false)
    }
    expect(wrapper.findAll('[data-testid="document-checklist-item"]')).toHaveLength(0)
  })

  it('labels solicitud download as Download document and templates as Download template', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/test-app/') {
        return Promise.resolve({
          data: {
            ...applicationPayload,
            document_checklist: {
              required_count: 2,
              approved_count: 0,
              complete: false,
              items: [
                {
                  document_type_id: 1,
                  slug: 'solicitud_participacion',
                  name: 'Solicitud',
                  status: 'missing',
                  is_required: true,
                  due_now: true,
                },
                {
                  document_type_id: 2,
                  slug: 'transcript',
                  name: 'Transcript',
                  status: 'missing',
                  is_required: true,
                  has_template: true,
                  due_now: true,
                },
              ],
            },
          },
        })
      }
      if (url === '/api/documents/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/comments/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/timeline-events/') return Promise.resolve({ data: { results: [] } })
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })
    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="download-solicitud-pdf"]').exists()).toBe(true)
    })
    expect(wrapper.find('[data-testid="download-solicitud-pdf"]').text()).toContain(
      i18n.global.t('applicationDetailPage.downloadDocument'),
    )
    expect(wrapper.find('[data-testid="download-checklist-template"]').text()).toContain(
      i18n.global.t('applicationDetailPage.downloadTemplate'),
    )
  })

  it('expands checklist section and scrolls when progress rail link is clicked', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/test-app/') {
        return Promise.resolve({
          data: {
            ...applicationPayload,
            status: 'draft',
            document_checklist: {
              required_count: 2,
              approved_count: 1,
              complete: false,
              items: [
                {
                  document_type_id: 1,
                  slug: 'transcript',
                  name: 'Transcript',
                  status: 'missing',
                  is_required: true,
                  due_now: true,
                },
                {
                  document_type_id: 3,
                  slug: 'motivation',
                  name: 'Motivation letter',
                  status: 'approved',
                  is_required: true,
                  due_now: true,
                },
              ],
            },
          },
        })
      }
      if (url === '/api/documents/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/comments/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/timeline-events/') return Promise.resolve({ data: { results: [] } })
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })

    const scrollIntoView = vi.fn()
    Element.prototype.scrollIntoView = scrollIntoView

    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="document-checklist-section-action"]').exists()).toBe(true)
    })

    const actionSection = wrapper.find('[data-testid="document-checklist-section-action"]')
    await actionSection.find('[data-testid="document-checklist-section-toggle"]').trigger('click')
    await vi.waitFor(() => {
      expect(actionSection.find('[data-testid="document-checklist-section-panel"]').exists()).toBe(false)
    })

    await expandCollapsible(wrapper, 'document-progress-rail')
    const railLink = wrapper.find('[data-testid="document-progress-rail-due-item"] [data-testid="document-progress-rail-link"]')
    await railLink.trigger('click')
    await vi.waitFor(() => {
      expect(actionSection.find('[data-testid="document-checklist-section-panel"]').exists()).toBe(true)
    })
    expect(wrapper.find('#checklist-item-1').exists()).toBe(true)
    await vi.waitFor(() => {
      expect(scrollIntoView).toHaveBeenCalled()
    })
  })

  it('puts instructions-only checklist items in Instructions, not Completed', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/test-app/') {
        return Promise.resolve({
          data: {
            ...applicationPayload,
            status: 'draft',
            document_checklist: {
              required_count: 2,
              approved_count: 2,
              complete: true,
              items: [
                {
                  document_type_id: 1,
                  slug: 'reglamento',
                  name: 'Reglamento',
                  status: 'n_a',
                  submission_mode: 'instructions_only',
                  is_required: true,
                },
                {
                  document_type_id: 2,
                  slug: 'passport',
                  name: 'Passport',
                  status: 'approved',
                  is_required: true,
                },
              ],
            },
          },
        })
      }
      if (url === '/api/documents/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/comments/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/timeline-events/') return Promise.resolve({ data: { results: [] } })
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })

    mockAuthStore.userRole = 'student'
    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="document-checklist-section-instructions"]').exists()).toBe(true)
    })
    const instructionsSection = wrapper.find('[data-testid="document-checklist-section-instructions"]')
    const doneSection = wrapper.find('[data-testid="document-checklist-section-done"]')
    expect(instructionsSection.find('[data-testid="document-checklist-section-count"]').text()).toBe('1')
    expect(doneSection.find('[data-testid="document-checklist-section-count"]').text()).toBe('1')
    expect(wrapper.text()).toContain(i18n.global.t('applicationDetailPage.checklistSections.instructions'))

    await instructionsSection.find('[data-testid="document-checklist-section-toggle"]').trigger('click')
    await vi.waitFor(() => {
      expect(instructionsSection.find('[data-testid="document-checklist-name"]').exists()).toBe(true)
    })
    expect(instructionsSection.find('[data-testid="document-checklist-name"]').text()).toBe('Reglamento')
  })

  it('hides document upload for coordinators', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/test-app/') {
        return Promise.resolve({
          data: { ...applicationPayload, status: 'draft', document_checklist: { required_count: 0, complete: true } },
        })
      }
      if (url === '/api/documents/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/comments/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/timeline-events/') return Promise.resolve({ data: { results: [] } })
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })
    mockAuthStore.userRole = 'coordinator'
    const wrapper = mountView()
    await flushPromises()
    expect(wrapper.find('[data-testid="document-upload-card"]').exists()).toBe(false)
    expect(wrapper.find('.document-upload-stub').exists()).toBe(false)
  })

  it('shows document upload for students on draft applications', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/test-app/') {
        return Promise.resolve({
          data: { ...applicationPayload, status: 'draft', document_checklist: { required_count: 0, complete: true } },
        })
      }
      if (url === '/api/documents/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/comments/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/timeline-events/') return Promise.resolve({ data: { results: [] } })
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })
    mockAuthStore.userRole = 'student'
    const wrapper = mountView()
    await flushPromises()
    expect(wrapper.find('[data-testid="document-upload-card"]').exists()).toBe(true)
  })

  it('shows upload card and replace CTA for students on nominated apps with gaps', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/test-app/') {
        return Promise.resolve({
          data: {
            ...applicationPayload,
            status: 'nominated',
            document_checklist: {
              required_count: 2,
              approved_count: 0,
              complete: false,
              items: [
                {
                  document_type_id: 1,
                  slug: 'transcript',
                  name: 'Transcript',
                  status: 'invalid',
                  document_id: 'doc-invalid-1',
                  is_required: true,
                },
                {
                  document_type_id: 2,
                  slug: 'passport',
                  name: 'Passport',
                  status: 'missing',
                  is_required: true,
                },
              ],
            },
          },
        })
      }
      if (url === '/api/documents/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/comments/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/timeline-events/') return Promise.resolve({ data: { results: [] } })
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })
    mockAuthStore.userRole = 'student'
    mockAuthStore.canUseStaffReviewQueue = false
    const wrapper = mountView()
    await flushPromises()
    expect(wrapper.find('[data-testid="document-upload-card"]').exists()).toBe(true)
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="checklist-replace-cta"]').exists()).toBe(true)
    })
    expect(wrapper.find('[data-testid="checklist-replace-cta"]').text()).toContain(
      i18n.global.t('applicationDetailPage.replaceDocument'),
    )
    const uploadShortcuts = wrapper.findAll('[data-testid="checklist-upload-shortcut"]')
    expect(uploadShortcuts.length).toBeGreaterThanOrEqual(2)
    await uploadShortcuts[1].trigger('click')
    await flushPromises()
    expect(wrapper.find('[data-testid="document-upload-stub"]').attributes('data-prefill')).toBe('2')
  })

  it('hides checklist template download for approved items for students', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/test-app/') {
        return Promise.resolve({
          data: {
            ...applicationPayload,
            status: 'under_review',
            document_checklist: {
              required_count: 1,
              approved_count: 1,
              complete: true,
              items: [
                {
                  document_type_id: 5,
                  slug: 'learning_agreement',
                  name: 'Learning agreement',
                  status: 'approved',
                  has_template: true,
                  is_required: true,
                },
              ],
            },
          },
        })
      }
      if (url === '/api/documents/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/comments/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/timeline-events/') return Promise.resolve({ data: { results: [] } })
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })
    mockAuthStore.userRole = 'student'
    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="document-checklist-section-done"]').exists()).toBe(true)
    })
    await wrapper
      .find('[data-testid="document-checklist-section-done"]')
      .find('[data-testid="document-checklist-section-toggle"]')
      .trigger('click')
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="document-checklist-item"]').exists()).toBe(true)
    })
    expect(wrapper.find('[data-testid="download-checklist-template"]').exists()).toBe(false)
  })

  it('shows Invalid on the required-document checklist', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/test-app/') {
        return Promise.resolve({
          data: {
            ...applicationPayload,
            status: 'under_review',
            document_checklist: {
              required_count: 1,
              approved_count: 0,
              complete: false,
              items: [
                {
                  document_type_id: 1,
                  slug: 'transcript',
                  name: 'transcript',
                  status: 'invalid',
                  is_required: true,
                },
              ],
            },
          },
        })
      }
      if (url === '/api/documents/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/comments/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/timeline-events/') return Promise.resolve({ data: { results: [] } })
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })
    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="document-checklist-section-action"]').exists()).toBe(true)
    })
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="document-checklist-item"]').exists()).toBe(true)
    })
    expect(wrapper.find('[data-testid="document-checklist-item"]').text()).toContain(
      i18n.global.t('applicationDetailPage.checklist.invalid'),
    )
  })

  it('shows accepted file formats on checklist rows', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/test-app/') {
        return Promise.resolve({
          data: {
            ...applicationPayload,
            status: 'draft',
            document_checklist: {
              required_count: 1,
              approved_count: 0,
              complete: false,
              items: [
                {
                  document_type_id: 1,
                  slug: 'passport',
                  name: 'Passport',
                  status: 'missing',
                  is_required: true,
                  accepted_extensions: 'pdf',
                  max_file_size_mb: 5,
                },
              ],
            },
          },
        })
      }
      if (url === '/api/documents/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/comments/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/timeline-events/') return Promise.resolve({ data: { results: [] } })
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })
    mockAuthStore.userRole = 'student'
    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="document-checklist-accepted-hint"]').exists()).toBe(true)
    })
    expect(wrapper.find('[data-testid="document-checklist-accepted-hint"]').text()).toBe(
      'Accepted: PDF (max 5MB)',
    )
  })

  it('shows required-from and due-now checklist labels', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/test-app/') {
        return Promise.resolve({
          data: {
            ...applicationPayload,
            status: 'approved',
            document_checklist: {
              required_count: 2,
              approved_count: 0,
              complete: false,
              items: [
                {
                  document_type_id: 1,
                  slug: 'transcript',
                  name: 'Transcript',
                  status: 'missing',
                  is_required: true,
                  required_from_status: 'submitted',
                  due_now: true,
                },
                {
                  document_type_id: 2,
                  slug: 'santander',
                  name: 'Santander cover',
                  status: 'missing',
                  is_required: true,
                  required_from_status: 'completed',
                  due_now: false,
                },
              ],
            },
          },
        })
      }
      if (url === '/api/documents/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/comments/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/timeline-events/') return Promise.resolve({ data: { results: [] } })
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })
    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="document-checklist-section-action"]').exists()).toBe(true)
    })
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="document-checklist-due-now"]').exists()).toBe(true)
    })
    expect(wrapper.find('[data-testid="document-checklist-due-now"]').text()).toBe(
      i18n.global.t('applicationDetailPage.checklistDueNow'),
    )
    expect(wrapper.find('[data-testid="document-checklist-required-from"]').text()).toContain(
      i18n.global.t('applicationDetailPage.status.completed'),
    )
    expect(wrapper.find('[data-testid="document-progress-rail"]').exists()).toBe(true)
    expect(
      wrapper
        .find('[data-testid="document-progress-rail"] [data-testid="collapsible-card-toggle"]')
        .attributes('aria-expanded'),
    ).toBe('false')
    await expandCollapsible(wrapper, 'document-progress-rail')
    expect(wrapper.findAll('[data-testid="document-progress-rail-due-item"]')).toHaveLength(1)
    expect(wrapper.findAll('[data-testid="document-progress-rail-later-item"]')).toHaveLength(1)
  })

  it('keeps program info, subjects, timeline, and document progress collapsed by default', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/test-app/') {
        return Promise.resolve({
          data: {
            ...applicationPayload,
            document_checklist: {
              required_count: 1,
              approved_count: 0,
              complete: false,
              items: [
                {
                  document_type_id: 1,
                  slug: 'transcript',
                  name: 'Transcript',
                  status: 'missing',
                  due_now: true,
                  is_required: true,
                },
              ],
            },
          },
        })
      }
      if (url === '/api/documents/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/comments/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/timeline-events/') return Promise.resolve({ data: { results: [] } })
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })
    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="application-detail-page"]').exists()).toBe(true)
    })
    for (const testId of [
      'program-info-card',
      'application-subjects-card',
      'activity-timeline-card',
      'document-progress-rail',
    ]) {
      const card = wrapper.find(`[data-testid="${testId}"]`)
      expect(card.exists()).toBe(true)
      expect(card.find('[data-testid="collapsible-card-toggle"]').attributes('aria-expanded')).toBe(
        'false',
      )
      expect(card.find('[data-testid="collapsible-card-panel"]').exists()).toBe(false)
    }
  })

  it('shows review-queue prev/next when sessionStorage queue includes current id', async () => {
    sessionStorage.setItem(
      'seim.reviewQueue.nav',
      JSON.stringify({ ids: ['prev-app', 'test-app', 'next-app'], index: 1 }),
    )
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/test-app/') {
        return Promise.resolve({ data: applicationPayload })
      }
      if (url === '/api/documents/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/comments/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/timeline-events/') return Promise.resolve({ data: { results: [] } })
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })
    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="review-queue-nav"]').exists()).toBe(true)
    })
    expect(wrapper.find('[data-testid="review-queue-position"]').text()).toContain('2 of 3')
    await wrapper.find('[data-testid="review-queue-next"]').trigger('click')
    expect(mockPush).toHaveBeenCalledWith({ name: 'ApplicationDetail', params: { id: 'next-app' } })
  })

  it('hides review-queue prev/next for students even when sessionStorage has a queue', async () => {
    mockAuthStore.userRole = 'student'
    mockAuthStore.canUseStaffReviewQueue = false
    mockAuthStore.isAdmin = false
    sessionStorage.setItem(
      'seim.reviewQueue.nav',
      JSON.stringify({ ids: ['prev-app', 'test-app', 'next-app'], index: 1 }),
    )
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/test-app/') {
        return Promise.resolve({ data: applicationPayload })
      }
      if (url === '/api/documents/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/comments/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/timeline-events/') return Promise.resolve({ data: { results: [] } })
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })
    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="application-detail-page"]').exists()).toBe(true)
    })
    expect(wrapper.find('[data-testid="review-queue-nav"]').exists()).toBe(false)
  })

  it('reloads application on full-page queue next for admin (route id change, reused component)', async () => {
    mockAuthStore.userRole = 'admin'
    mockAuthStore.canUseStaffReviewQueue = true
    mockAuthStore.isAdmin = true
    sessionStorage.setItem(
      'seim.reviewQueue.nav',
      JSON.stringify({ ids: ['prev-app', 'test-app', 'next-app'], index: 1 }),
    )
    const nextPayload = {
      ...applicationPayload,
      id: 'next-app',
      program: { ...applicationPayload.program, name: 'Next Queue Program' },
    }
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/test-app/') {
        return Promise.resolve({ data: applicationPayload })
      }
      if (url === '/api/applications/next-app/') {
        return Promise.resolve({ data: nextPayload })
      }
      if (url === '/api/documents/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/comments/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/timeline-events/') return Promise.resolve({ data: { results: [] } })
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })
    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="review-queue-nav"]').exists()).toBe(true)
    })
    await wrapper.find('[data-testid="review-queue-next"]').trigger('click')
    expect(mockPush).toHaveBeenCalledWith({ name: 'ApplicationDetail', params: { id: 'next-app' } })
    expect(routeParams.id).toBe('next-app')
    await vi.waitFor(() => {
      expect(api.get).toHaveBeenCalledWith('/api/applications/next-app/')
    })
    await vi.waitFor(() => {
      expect(wrapper.text()).toContain('Next Queue Program')
    })
    expect(wrapper.find('[data-testid="review-queue-position"]').text()).toContain('3 of 3')
  })

  it('reloads application on full-page queue previous for admin', async () => {
    mockAuthStore.userRole = 'admin'
    mockAuthStore.canUseStaffReviewQueue = true
    mockAuthStore.isAdmin = true
    sessionStorage.setItem(
      'seim.reviewQueue.nav',
      JSON.stringify({ ids: ['prev-app', 'test-app', 'next-app'], index: 1 }),
    )
    const prevPayload = {
      ...applicationPayload,
      id: 'prev-app',
      program: { ...applicationPayload.program, name: 'Previous Queue Program' },
    }
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/test-app/') {
        return Promise.resolve({ data: applicationPayload })
      }
      if (url === '/api/applications/prev-app/') {
        return Promise.resolve({ data: prevPayload })
      }
      if (url === '/api/documents/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/comments/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/timeline-events/') return Promise.resolve({ data: { results: [] } })
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })
    const wrapper = mountView()
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="review-queue-prev"]').exists()).toBe(true)
    })
    await wrapper.find('[data-testid="review-queue-prev"]').trigger('click')
    expect(mockPush).toHaveBeenCalledWith({ name: 'ApplicationDetail', params: { id: 'prev-app' } })
    await vi.waitFor(() => {
      expect(wrapper.text()).toContain('Previous Queue Program')
    })
    expect(wrapper.find('[data-testid="review-queue-position"]').text()).toContain('1 of 3')
  })

  it('requires rejection note and confirm before marking document invalid', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/test-app/') {
        return Promise.resolve({ data: { ...applicationPayload, status: 'under_review' } })
      }
      if (url === '/api/documents/') {
        return Promise.resolve({
          data: {
            results: [
              {
                id: 'doc-9',
                type: { name: 'Transcript' },
                is_valid: false,
                validated_at: null,
              },
            ],
          },
        })
      }
      if (url === '/api/comments/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/timeline-events/') return Promise.resolve({ data: { results: [] } })
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })
    api.post.mockResolvedValue({ data: {} })
    const promptSpy = vi.spyOn(window, 'prompt').mockReturnValue('  Needs clearer scan  ')

    const wrapper = mountView()
    await flushPromises()
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="document-status-badge"]').exists()).toBe(true)
    })
    const invalidBtn = wrapper.findAll('button').find((b) => b.attributes('title') === i18n.global.t('applicationDetailPage.markInvalidTitle'))
    expect(invalidBtn).toBeTruthy()
    await invalidBtn.trigger('click')
    await flushPromises()

    expect(promptSpy).toHaveBeenCalled()
    expect(mockConfirm).toHaveBeenCalled()
    expect(api.post).toHaveBeenCalledWith('/api/documents/doc-9/validate_document/', {
      result: 'invalid',
      details: 'Needs clearer scan',
    })
    promptSpy.mockRestore()
  })

  it('blocks invalid mark when rejection note is empty', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/test-app/') {
        return Promise.resolve({ data: { ...applicationPayload, status: 'under_review' } })
      }
      if (url === '/api/documents/') {
        return Promise.resolve({
          data: {
            results: [
              {
                id: 'doc-9',
                type: { name: 'Transcript' },
                is_valid: false,
                validated_at: null,
              },
            ],
          },
        })
      }
      if (url === '/api/comments/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/timeline-events/') return Promise.resolve({ data: { results: [] } })
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })
    const promptSpy = vi.spyOn(window, 'prompt').mockReturnValue('   ')

    const wrapper = mountView()
    await flushPromises()
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="document-status-badge"]').exists()).toBe(true)
    })
    const invalidBtn = wrapper.findAll('button').find((b) => b.attributes('title') === i18n.global.t('applicationDetailPage.markInvalidTitle'))
    await invalidBtn.trigger('click')
    await flushPromises()

    expect(mockErrorToast).toHaveBeenCalledWith(i18n.global.t('applicationDetailPage.invalidNoteRequired'))
    expect(api.post).not.toHaveBeenCalled()
    promptSpy.mockRestore()
  })

  it('soft-confirms before marking document valid', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/applications/test-app/') {
        return Promise.resolve({ data: { ...applicationPayload, status: 'under_review' } })
      }
      if (url === '/api/documents/') {
        return Promise.resolve({
          data: {
            results: [
              {
                id: 'doc-9',
                type: { name: 'Transcript' },
                is_valid: false,
                validated_at: null,
              },
            ],
          },
        })
      }
      if (url === '/api/comments/') return Promise.resolve({ data: { results: [] } })
      if (url === '/api/timeline-events/') return Promise.resolve({ data: { results: [] } })
      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })
    api.post.mockResolvedValue({ data: {} })

    const wrapper = mountView()
    await flushPromises()
    await vi.waitFor(() => {
      expect(wrapper.find('[data-testid="document-status-badge"]').exists()).toBe(true)
    })
    const validBtn = wrapper.findAll('button').find((b) => b.attributes('title') === i18n.global.t('applicationDetailPage.markValidTitle'))
    await validBtn.trigger('click')
    await flushPromises()

    expect(mockConfirm).toHaveBeenCalled()
    expect(api.post).toHaveBeenCalledWith('/api/documents/doc-9/validate_document/', {
      result: 'valid',
      details: '',
    })
  })
})
