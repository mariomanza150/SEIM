/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import NotFound from './NotFound.vue'
import i18n, { setAppLocale } from '@/i18n'

describe('NotFound', () => {
  beforeEach(() => {
    localStorage.clear()
    setAppLocale('en')
  })

  afterEach(() => {
    setAppLocale('en')
    localStorage.clear()
  })

  it('renders translated 404 copy and dashboard link', () => {
    const wrapper = mount(NotFound, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    expect(wrapper.text()).toContain('404')
    expect(wrapper.text()).toContain('Page Not Found')
    expect(wrapper.find('[data-testid="go-to-dashboard-link"]').text()).toContain('Go to Dashboard')
  })
})
