/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import NotificationDropdown from './NotificationDropdown.vue'
import api from '@/services/api'
import i18n, { setAppLocale } from '@/i18n'

vi.mock('@/services/api', () => ({
  default: { get: vi.fn() },
}))

describe('NotificationDropdown', () => {
  beforeEach(() => {
    localStorage.clear()
    setAppLocale('en')
    vi.clearAllMocks()
    api.get.mockImplementation((_url, opts) => {
      const p = opts?.params || {}
      if (p.is_read === false) {
        return Promise.resolve({ data: { count: 0, results: [] } })
      }
      return Promise.resolve({ data: { results: [], count: 0 } })
    })
  })

  afterEach(() => {
    setAppLocale('en')
    localStorage.clear()
  })

  it('shows translated empty state and toggle aria-label', async () => {
    const wrapper = mount(NotificationDropdown, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.find('#notificationDropdown').attributes('aria-label')).toBe('Notifications menu')
    expect(wrapper.text()).toContain('Notifications')
    expect(wrapper.text()).toContain('View all')
    expect(wrapper.text()).toContain('No notifications')
    expect(api.get).toHaveBeenCalled()
  })

  it('uses Spanish strings when locale is es', async () => {
    setAppLocale('es')
    const wrapper = mount(NotificationDropdown, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.text()).toContain('Notificaciones')
    expect(wrapper.text()).toContain('Sin notificaciones')
  })
})
