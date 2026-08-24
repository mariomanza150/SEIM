import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import en from '@/locales/en.json'
import PageStateShell from '@/components/State/PageStateShell.vue'

const i18n = createI18n({ legacy: false, locale: 'en', messages: { en } })

function mountShell(props = {}, options = {}) {
  return mount(PageStateShell, {
    props,
    global: { plugins: [i18n] },
    ...options,
  })
}

describe('PageStateShell', () => {
  it('shows loading state', () => {
    const wrapper = mountShell({ loading: true, skeleton: 'none' })
    expect(wrapper.find('[role="status"]').exists()).toBe(true)
  })

  it('shows error alert', () => {
    const wrapper = mountShell({ loading: false, error: 'Something failed' })
    expect(wrapper.find('[role="alert"]').text()).toContain('Something failed')
  })

  it('shows empty state', () => {
    const wrapper = mountShell({ loading: false, empty: true, emptyTitle: 'Nothing here' })
    expect(wrapper.find('[role="status"]').text()).toContain('Nothing here')
  })

  it('renders default slot when ready', () => {
    const wrapper = mountShell(
      { loading: false, empty: false },
      { slots: { default: '<p data-testid="content">Ready</p>' } },
    )
    expect(wrapper.find('[data-testid="content"]').exists()).toBe(true)
  })

  it('shows table skeleton when loading with skeleton=table', () => {
    const wrapper = mountShell({ loading: true, skeleton: 'table' })
    expect(wrapper.find('table').exists()).toBe(true)
  })
})
