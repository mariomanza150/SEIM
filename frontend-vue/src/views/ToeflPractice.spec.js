/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import ToeflPractice from './ToeflPractice.vue'
import api from '@/services/api'
import i18n, { setAppLocale } from '@/i18n'

vi.mock('@/services/api', () => ({
  default: { get: vi.fn(), post: vi.fn() },
}))

const sampleAttempts = [
  {
    id: 'att-1',
    external_session_id: 'sess-abc',
    exam_code: 'director_extracted',
    earned: 8,
    total: 10,
    percent: 80,
    weakest: [{ name: 'verbs' }],
    completed_at: '2026-08-30T18:00:00Z',
    created_at: '2026-08-30T18:00:00Z',
  },
]

function makeRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/toefl-practice', name: 'ToeflPractice', component: ToeflPractice },
      { path: '/', name: 'Dashboard', component: { template: '<div />' } },
    ],
  })
}

async function mountPage(query = {}) {
  const router = makeRouter()
  await router.push({ name: 'ToeflPractice', query })
  const wrapper = mount(ToeflPractice, {
    global: {
      plugins: [i18n, router],
      stubs: {
        PageHeader: {
          template: '<div><slot name="actions" /><slot name="breadcrumb" /></div>',
        },
        PageBreadcrumb: { template: '<nav />' },
        PageStateShell: {
          template: `
            <div>
              <div v-if="empty" data-testid="toefl-empty">
                <slot name="emptyActions" />
              </div>
              <div v-else-if="error" data-testid="toefl-load-error">{{ error }}</div>
              <slot v-else />
            </div>
          `,
          props: ['loading', 'error', 'empty', 'emptyBody', 'emptyTestId', 'loadingLabel', 'skeleton', 'skeletonColumns', 'skeletonRows'],
        },
      },
    },
  })
  await flushPromises()
  return { wrapper, router }
}

describe('ToeflPractice', () => {
  beforeEach(() => {
    setAppLocale('en')
    vi.clearAllMocks()
    vi.stubGlobal('location', { ...window.location, assign: vi.fn() })
    api.get.mockResolvedValue({ data: { results: sampleAttempts } })
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    vi.useRealTimers()
  })

  it('renders practice history', async () => {
    const { wrapper } = await mountPage()
    expect(wrapper.find('[data-testid="toefl-attempts-table"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('director_extracted')
    expect(wrapper.text()).toContain('8/10')
    expect(wrapper.find('[data-testid="toefl-disclaimer"]').exists()).toBe(true)
  })

  it('shows empty state when there are no attempts', async () => {
    api.get.mockResolvedValue({ data: { results: [] } })
    const { wrapper } = await mountPage()
    expect(wrapper.find('[data-testid="toefl-empty"]').exists()).toBe(true)
  })

  it('maps 503 launch errors to config message', async () => {
    api.post.mockRejectedValue({
      response: { status: 503, data: { detail: 'TOEFL callback/return URLs are not configured' } },
    })
    const { wrapper } = await mountPage()
    await wrapper.find('[data-testid="toefl-start-practice"]').trigger('click')
    await flushPromises()
    expect(wrapper.find('[data-testid="toefl-error"]').text()).toMatch(/not configured/i)
    expect(window.location.assign).not.toHaveBeenCalled()
  })

  it('redirects to launch_url on start', async () => {
    api.post.mockResolvedValue({
      data: { launch_url: 'https://example.test/toefl/launch?token=abc', token: 'abc' },
    })
    const { wrapper } = await mountPage()
    await wrapper.find('[data-testid="toefl-start-practice"]').trigger('click')
    await flushPromises()
    expect(api.post).toHaveBeenCalledWith('/api/toefl/launch/', { n: 20 })
    expect(window.location.assign).toHaveBeenCalledWith(
      'https://example.test/toefl/launch?token=abc',
    )
  })

  it('highlights returned session and clears sync notice when found', async () => {
    vi.useFakeTimers()
    api.get.mockResolvedValue({ data: { results: sampleAttempts } })
    const { wrapper } = await mountPage({ session_id: 'sess-abc' })
    await flushPromises()
    expect(wrapper.find('[data-testid="toefl-return-notice"]').exists()).toBe(true)
    const row = wrapper.find('[data-session-id="sess-abc"]')
    expect(row.classes()).toContain('table-success')
    expect(wrapper.find('[data-testid="toefl-return-notice"]').text()).toMatch(/saved/i)
  })

  it('loads attempt detail when a row is expanded', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/toefl/attempts/') {
        return Promise.resolve({ data: { results: sampleAttempts } })
      }
      if (url === '/api/toefl/attempts/att-1/') {
        return Promise.resolve({
          data: {
            ...sampleAttempts[0],
            categories: [{ name: 'verbs', earned: 1, total: 2 }],
            items: [{ question_id: 'q1', category: 'verbs', is_correct: false }],
          },
        })
      }
      return Promise.reject(new Error(`unexpected ${url}`))
    })
    const { wrapper } = await mountPage()
    await wrapper.find('[data-testid="toefl-expand-row"]').trigger('click')
    await flushPromises()
    expect(wrapper.find('[data-testid="toefl-detail-categories"]').text()).toContain('verbs')
    expect(wrapper.find('[data-testid="toefl-detail-items"]').text()).toContain('q1')
  })
})
