/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import PageHeader from './PageHeader.vue'
import i18n, { setAppLocale } from '@/i18n'

function makeRouter(name = 'Dashboard') {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', name, component: { template: '<div />' } },
      { path: '/help', name: 'HelpCenter', component: { template: '<div />' } },
      { path: '/help/:slug', name: 'HelpArticle', component: { template: '<div />' } },
    ],
  })
}

describe('PageHeader contextual help', () => {
  beforeEach(() => {
    setAppLocale('en')
  })

  afterEach(() => {
    setAppLocale('en')
  })

  it('links ? to HelpCenter with the current route name as key', async () => {
    const router = makeRouter('Applications')
    await router.push({ name: 'Applications' })
    const wrapper = mount(PageHeader, {
      props: { title: 'Applications' },
      global: { plugins: [i18n, router] },
    })
    const help = wrapper.get('[data-testid="page-help"]')
    expect(help.text()).toBe('?')
    expect(help.attributes('aria-label')).toBe('Help for this page')
    expect(help.attributes('href')).toContain('key=Applications')
  })

  it('hides the help control when helpKey is false', async () => {
    const router = makeRouter('Dashboard')
    await router.push({ name: 'Dashboard' })
    const wrapper = mount(PageHeader, {
      props: { title: 'Help', helpKey: false },
      global: { plugins: [i18n, router] },
    })
    expect(wrapper.find('[data-testid="page-help"]').exists()).toBe(false)
  })
})
