/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import HelpArticle from './HelpArticle.vue'
import i18n, { setAppLocale } from '@/i18n'
import { fetchHelpArticle, fetchHelpArticles } from '@/services/help'
import { useProductTour } from '@/composables/useProductTour'

vi.mock('@/services/help', () => ({
  fetchHelpArticle: vi.fn(),
  fetchHelpArticles: vi.fn(),
  unwrapHelpArticles: (data) => (Array.isArray(data) ? data : data?.results || []),
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

async function mountArticle(slug = 'start-application') {
  const pinia = createPinia()
  setActivePinia(pinia)
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/help', name: 'HelpCenter', component: { template: '<div />' } },
      { path: '/help/:slug', name: 'HelpArticle', component: HelpArticle },
      { path: '/', name: 'Dashboard', component: { template: '<div />' } },
      { path: '/applications', name: 'Applications', component: { template: '<div />' } },
      { path: '/applications/new', name: 'ApplicationNew', component: { template: '<div />' } },
    ],
  })
  await router.push({ name: 'HelpArticle', params: { slug } })
  const wrapper = mount(HelpArticle, {
    global: { plugins: [i18n, router, pinia] },
  })
  await flushPromises()
  return { wrapper, router, pinia }
}

describe('HelpArticle', () => {
  beforeEach(() => {
    setAppLocale('en')
    vi.clearAllMocks()
    fetchHelpArticle.mockResolvedValue({
      data: {
        slug: 'start-application',
        title: 'Find a program',
        introduction: 'How to apply',
        topic: 'applications',
        contextual_keys: ['ApplicationNew'],
        body_html: '<p>Safe copy</p><script>alert(1)</script>',
      },
    })
    fetchHelpArticles.mockResolvedValue({
      data: {
        results: [
          { slug: 'start-application', title: 'Find a program', topic: 'applications' },
          { slug: 'track-status', title: 'Track status', topic: 'applications' },
        ],
      },
    })
  })

  afterEach(() => {
    setAppLocale('en')
  })

  it('renders sanitized body and related articles', async () => {
    const { wrapper } = await mountArticle()
    expect(wrapper.get('[data-testid="help-article-page"]').text()).toContain('Find a program')
    const body = wrapper.get('[data-testid="help-article-body"]')
    expect(body.text()).toContain('Safe copy')
    expect(body.html()).not.toContain('script')
    expect(wrapper.get('[data-testid="help-related"]').text()).toContain('Track status')
    expect(wrapper.get('[data-testid="help-related"]').text()).not.toContain('Find a program')
  })

  it('shows unavailable state on 404', async () => {
    fetchHelpArticle.mockRejectedValue({ response: { status: 404 } })
    const { wrapper } = await mountArticle('missing')
    expect(wrapper.get('[data-testid="help-article-unavailable"]').text()).toContain('Article not available')
  })

  it('wires Start walkthrough CTA from the article contextual key', async () => {
    const { wrapper, router } = await mountArticle()
    const cta = wrapper.get('[data-testid="help-article-start-walkthrough"]')
    await cta.trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.name).toBe('ApplicationNew')
    expect(useProductTour().pendingPageId.value).toBe('application-form')
  })
})
