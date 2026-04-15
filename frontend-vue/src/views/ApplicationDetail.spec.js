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
    await wrapper.find('form').trigger('submit.prevent')
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
          points: 20,
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
    expect(wrapper.text()).toContain('Staff comparison tool only.')
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
    expect(wrapper.text()).toContain('70')
    expect(wrapper.text()).not.toContain(
      i18n.global.t('applicationDetailPage.scholarshipScoring.exportCohortCsv'),
    )
    mockAuthStore.userRole = 'coordinator'
  })
})
