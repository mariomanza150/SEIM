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
})
