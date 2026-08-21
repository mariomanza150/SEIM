import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ApplicationDetail from './ApplicationDetail.vue'
import api from '@/services/api'
import i18n, { setAppLocale } from '@/i18n'

const mockPush = vi.fn()
const mockSuccessToast = vi.fn()
const mockErrorToast = vi.fn()
const mockAuthStore = {
  userRole: 'coordinator',
  user: {
    id: 'current-user',
  },
}

vi.mock('vue-router', () => ({
  useRoute: () => ({ params: { id: 'test-app' } }),
  useRouter: () => ({ push: mockPush }),
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockAuthStore,
}))

vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success: mockSuccessToast, error: mockErrorToast }),
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
        DocumentUpload: { template: '<div class="document-upload-stub"></div>' },
        ApplicationSubjectsPanel: { template: '<div class="subjects-panel-stub"></div>' },
        RouterLink: { template: '<a><slot /></a>' },
      },
    },
  })
}

async function flushPromises() {
  await Promise.resolve()
  await Promise.resolve()
  await new Promise((resolve) => setTimeout(resolve, 0))
}

describe('ApplicationDetail', () => {
  beforeEach(() => {
    localStorage.clear()
    setAppLocale('en')
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  afterEach(() => {
    setAppLocale('en')
    localStorage.clear()
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
    expect(badges[0].text()).toBe(i18n.global.t('applicationDetailPage.docPending'))
    expect(badges[0].classes()).toContain('bg-warning')
    expect(badges[1].text()).toBe(i18n.global.t('applicationDetailPage.docInvalid'))
    expect(badges[1].classes()).toContain('bg-danger')
    expect(badges[2].text()).toBe(i18n.global.t('applicationDetailPage.docValid'))
    expect(badges[2].classes()).toContain('bg-success')
    mockAuthStore.userRole = 'coordinator'
  })

  it('disables submit when host destination is required but incomplete', async () => {
    mockAuthStore.userRole = 'student'
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
    mockAuthStore.userRole = 'coordinator'
  })

  it('localizes eligibility issues from message_key', async () => {
    mockAuthStore.userRole = 'student'
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
      expect(wrapper.findAll('[data-testid="document-checklist-name"]').length).toBe(2)
    })
    const names = wrapper.findAll('[data-testid="document-checklist-name"]').map((n) => n.text())
    expect(names).toEqual(['Academic transcript', 'Passport or ID'])
    expect(names).not.toContain('transcript')
    expect(names).not.toContain('passport')
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
      expect(wrapper.find('[data-testid="document-checklist-item"]').exists()).toBe(true)
    })
    expect(wrapper.find('[data-testid="document-checklist-item"]').text()).toContain(
      i18n.global.t('applicationDetailPage.checklist.invalid'),
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
      expect(wrapper.find('[data-testid="document-checklist-due-now"]').exists()).toBe(true)
    })
    expect(wrapper.find('[data-testid="document-checklist-due-now"]').text()).toBe(
      i18n.global.t('applicationDetailPage.checklistDueNow'),
    )
    expect(wrapper.find('[data-testid="document-checklist-required-from"]').text()).toContain(
      i18n.global.t('applicationDetailPage.status.completed'),
    )
  })
})
