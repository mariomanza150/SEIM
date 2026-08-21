/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import HelpCenter from './HelpCenter.vue'
import i18n, { setAppLocale } from '@/i18n'
import { fetchHelpArticles } from '@/services/help'

vi.mock('@/services/help', () => ({
  fetchHelpArticles: vi.fn(),
  unwrapHelpArticles: (data) => (Array.isArray(data) ? data : data?.results || []),
}))

vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ error: vi.fn() }),
}))

const sampleArticles = [
  {
    slug: 'start-application',
    title: 'Find a program',
    introduction: 'How to apply',
    topic: 'applications',
    contextual_keys: ['Applications'],
  },
  {
    slug: 'dashboard-overview',
    title: 'Using the dashboard',
    introduction: 'Overview',
    topic: 'getting_started',
    contextual_keys: ['Dashboard'],
  },
]

function makeRouter(query = {}) {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/help', name: 'HelpCenter', component: HelpCenter },
      { path: '/help/:slug', name: 'HelpArticle', component: { template: '<div data-testid="article-stub" />' } },
      { path: '/', name: 'Dashboard', component: { template: '<div />' } },
    ],
  })
}

async function mountHelp(query = {}) {
  const router = makeRouter()
  await router.push({ name: 'HelpCenter', query })
  const wrapper = mount(HelpCenter, {
    global: { plugins: [i18n, router] },
  })
  await flushPromises()
  return { wrapper, router }
}

describe('HelpCenter', () => {
  beforeEach(() => {
    setAppLocale('en')
    vi.clearAllMocks()
    fetchHelpArticles.mockResolvedValue({ data: { results: sampleArticles } })
  })

  afterEach(() => {
    setAppLocale('en')
  })

  it('renders grouped articles', async () => {
    const { wrapper } = await mountHelp()
    expect(wrapper.get('[data-testid="help-center-page"]').text()).toContain('Help')
    expect(wrapper.text()).toContain('Find a program')
    expect(wrapper.text()).toContain('Using the dashboard')
    expect(wrapper.text()).toContain('Applications')
    expect(wrapper.text()).toContain('Getting started')
  })

  it('shows empty state when there are no articles', async () => {
    fetchHelpArticles.mockResolvedValue({ data: { results: [] } })
    const { wrapper } = await mountHelp()
    expect(wrapper.get('[data-testid="help-center-empty"]').text()).toContain('No articles found')
  })

  it('redirects to the article when key matches a single result', async () => {
    fetchHelpArticles.mockResolvedValue({
      data: { results: [sampleArticles[1]] },
    })
    const { router } = await mountHelp({ key: 'Dashboard' })
    await flushPromises()
    expect(router.currentRoute.value.name).toBe('HelpArticle')
    expect(router.currentRoute.value.params.slug).toBe('dashboard-overview')
  })
})
