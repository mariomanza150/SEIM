/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import HelpCenter from './HelpCenter.vue'
import i18n, { setAppLocale } from '@/i18n'
import { fetchHelpArticles } from '@/services/help'
import { useProductTour } from '@/composables/useProductTour'

vi.mock('@/services/help', () => ({
  fetchHelpArticles: vi.fn(),
  unwrapHelpArticles: (data) => (Array.isArray(data) ? data : data?.results || []),
}))

vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ error: vi.fn() }),
}))

const authStoreMock = {
  isAuthenticated: true,
  user: { id: 3, email: 'student@example.edu' },
  isAdmin: false,
  canUseStaffReviewQueue: false,
  canUsePartnerPortal: false,
}

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => authStoreMock,
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

function makeRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/help', name: 'HelpCenter', component: HelpCenter },
      { path: '/help/:slug', name: 'HelpArticle', component: { template: '<div data-testid="article-stub" />' } },
      { path: '/', name: 'Dashboard', component: { template: '<div />' } },
      { path: '/applications', name: 'Applications', component: { template: '<div />' } },
      { path: '/applications/new', name: 'ApplicationNew', component: { template: '<div />' } },
      { path: '/documents', name: 'Documents', component: { template: '<div />' } },
      { path: '/review', name: 'CoordinatorReviewQueue', component: { template: '<div />' } },
      { path: '/partner', name: 'PartnerPortal', component: { template: '<div />' } },
      { path: '/admin/programs', name: 'AdminPrograms', component: { template: '<div />' } },
    ],
  })
}

async function mountHelp(query = {}) {
  const pinia = createPinia()
  setActivePinia(pinia)
  const router = makeRouter()
  await router.push({ name: 'HelpCenter', query })
  const wrapper = mount(HelpCenter, {
    global: { plugins: [i18n, router, pinia] },
  })
  await flushPromises()
  return { wrapper, router, pinia }
}

describe('HelpCenter', () => {
  beforeEach(() => {
    setAppLocale('en')
    vi.clearAllMocks()
    fetchHelpArticles.mockResolvedValue({ data: { results: sampleArticles } })
    authStoreMock.canUsePartnerPortal = false
    authStoreMock.canUseStaffReviewQueue = false
    authStoreMock.isAdmin = false
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

  it('wires Start walkthrough CTA to navigate and request a page tour', async () => {
    const { wrapper, router } = await mountHelp()
    const cta = wrapper.get('[data-testid="help-start-walkthrough-start-application"]')
    await cta.trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.name).toBe('Applications')
    expect(useProductTour().pendingPageId.value).toBe('applications')
  })

  it('shows role-filtered page tour buttons on the walkthrough card', async () => {
    const { wrapper } = await mountHelp()
    expect(wrapper.get('[data-testid="help-walkthrough-card"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="help-start-page-tour-applications"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="help-start-page-tour-review-queue"]').exists()).toBe(false)
  })

  it('applies search query via the search controls', async () => {
    const { wrapper, router } = await mountHelp()
    const input = wrapper.get('[data-testid="help-search"]')
    await input.setValue('upload')
    await wrapper.get('[data-testid="help-search-submit"]').trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.query.q).toBe('upload')
    expect(fetchHelpArticles).toHaveBeenCalledWith(
      expect.objectContaining({ q: 'upload' }),
    )
  })

  it('clears search from the empty-state action', async () => {
    fetchHelpArticles.mockResolvedValue({ data: { results: [] } })
    const { wrapper, router } = await mountHelp({ q: 'missing-topic' })
    expect(wrapper.find('[data-testid="help-clear-search"]').exists()).toBe(true)
    await wrapper.get('[data-testid="help-clear-search"]').trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.query.q).toBeUndefined()
  })

  it('shows contextual banner when a key matches multiple articles', async () => {
    fetchHelpArticles.mockResolvedValue({
      data: {
        results: [
          { ...sampleArticles[0], contextual_keys: ['Applications'] },
          { ...sampleArticles[1], contextual_keys: ['Applications'] },
        ],
      },
    })
    const { wrapper } = await mountHelp({ key: 'Applications' })
    expect(wrapper.find('[data-testid="help-contextual-banner"]').exists()).toBe(true)
  })

  it('groups unknown topics after the ordered topics', async () => {
    fetchHelpArticles.mockResolvedValue({
      data: {
        results: [
          {
            slug: 'custom-topic-guide',
            title: 'Custom topic guide',
            introduction: 'Extra help',
            topic: 'custom_topic',
            contextual_keys: [],
          },
          sampleArticles[0],
        ],
      },
    })
    const { wrapper } = await mountHelp()
    expect(wrapper.find('[data-testid="help-topic-applications"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="help-topic-custom_topic"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('Custom topic guide')
  })

  it('shows load error state when articles fail to fetch', async () => {
    fetchHelpArticles.mockRejectedValue(new Error('offline'))
    const { wrapper } = await mountHelp()
    expect(wrapper.find('[data-testid="help-center-error"]').exists()).toBe(true)
    expect(wrapper.text()).toContain(i18n.global.t('help.loadError'))
  })

  it('replays the welcome tour from the walkthrough card', async () => {
    const { wrapper } = await mountHelp()
    await wrapper.get('[data-testid="help-replay-welcome-tour"]').trigger('click')
    await flushPromises()
    expect(useProductTour().open.value).toBe(true)
  })

  it('shows review-queue page tour for staff roles', async () => {
    authStoreMock.canUseStaffReviewQueue = true
    const { wrapper } = await mountHelp()
    expect(wrapper.find('[data-testid="help-start-page-tour-review-queue"]').exists()).toBe(true)
  })
})
