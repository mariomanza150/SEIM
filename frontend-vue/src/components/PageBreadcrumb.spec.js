/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import PageBreadcrumb from './PageBreadcrumb.vue'
import i18n, { setAppLocale } from '@/i18n'

describe('PageBreadcrumb', () => {
  beforeEach(() => {
    setAppLocale('en')
  })

  afterEach(() => {
    setAppLocale('en')
  })

  it('renders links, truncates the last item with a tooltip, and keeps the full accessible name', () => {
    const longName = 'Very Long Exchange Program Name That Should Ellipsis'
    const wrapper = mount(PageBreadcrumb, {
      props: {
        ariaLabel: i18n.global.t('applicationsPage.breadcrumbAria'),
        items: [
          { to: { name: 'Dashboard' }, label: 'Dashboard' },
          { to: { name: 'Applications' }, label: 'Applications' },
          { label: longName, truncate: true },
        ],
      },
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })

    const nav = wrapper.get('nav')
    expect(nav.attributes('aria-label')).toBe('Breadcrumb')
    expect(nav.classes()).toContain('seim-page-breadcrumb')
    expect(wrapper.findAll('a')).toHaveLength(2)
    const current = wrapper.get('[aria-current="page"]')
    expect(current.classes()).toContain('seim-page-breadcrumb__item--truncate')
    expect(current.text()).toBe(longName)
    expect(current.get('.seim-page-breadcrumb__text').attributes('title')).toBe(longName)
  })

  it('uses Spanish aria-label from the caller', () => {
    setAppLocale('es')
    const wrapper = mount(PageBreadcrumb, {
      props: {
        ariaLabel: i18n.global.t('applicationsPage.breadcrumbAria'),
        items: [{ label: i18n.global.t('route.names.Applications') }],
      },
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    expect(wrapper.get('nav').attributes('aria-label')).toBe('Migas de pan')
  })
})
