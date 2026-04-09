/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import Notifications from './Notifications.vue'
import api from '@/services/api'
import i18n, { setAppLocale } from '@/i18n'

vi.mock('@/services/api', () => ({
  default: { get: vi.fn(), post: vi.fn() },
}))

const success = vi.fn()
const errorToast = vi.fn()

vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ success, error: errorToast }),
}))

function mockNotificationsListResponse(overrides = {}) {
  const data = {
    results: [],
    count: 0,
    next: null,
    previous: null,
    ...overrides,
  }
  return { data }
}

function setupDefaultGets({ list = mockNotificationsListResponse(), unreadCount = 0 } = {}) {
  api.get.mockImplementation((url, config) => {
    if (url !== '/api/notifications/') {
      return Promise.reject(new Error(`Unexpected GET ${url}`))
    }
    const params = config?.params || {}
    if (params.is_read === false && params.page_size === 1) {
      return Promise.resolve({ data: { count: unreadCount } })
    }
    return Promise.resolve(list)
  })
}

describe('Notifications', () => {
  beforeEach(() => {
    localStorage.clear()
    setAppLocale('en')
    vi.clearAllMocks()
    window.scrollTo = vi.fn()
    setupDefaultGets()
  })

  afterEach(() => {
    setAppLocale('en')
    localStorage.clear()
  })

  it('shows translated empty state', async () => {
    const wrapper = mount(Notifications, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.find('nav').attributes('aria-label')).toBe(i18n.global.t('notifications.breadcrumbAria'))
    expect(wrapper.find('[data-testid="notifications-heading"]').text()).toContain('Notifications')
    expect(wrapper.text()).toContain('No notifications')
    expect(wrapper.text()).toContain('Manage your notifications')
    expect(wrapper.text()).toContain('Clear filters')
  })

  it('shows load error when API fails', async () => {
    api.get.mockImplementation((url, config) => {
      if (url !== '/api/notifications/') {
        return Promise.reject(new Error(`Unexpected GET ${url}`))
      }
      const params = config?.params || {}
      if (params.is_read === false && params.page_size === 1) {
        return Promise.resolve({ data: { count: 0 } })
      }
      return Promise.reject(new Error('network'))
    })
    const wrapper = mount(Notifications, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.text()).toContain('Failed to load notifications')
    expect(errorToast).toHaveBeenCalledWith('Failed to load notifications')
  })

  it('renders notification row with mark-as-read and calls API', async () => {
    setupDefaultGets({
      list: mockNotificationsListResponse({
        results: [
          {
            id: 42,
            title: 'Doc approved',
            message: 'Your transcript was approved.',
            is_read: false,
            category: 'success',
            sent_at: new Date().toISOString(),
          },
        ],
        count: 1,
      }),
      unreadCount: 2,
    })
    api.post.mockResolvedValue({ data: {} })

    const wrapper = mount(Notifications, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.text()).toContain('Doc approved')
    expect(wrapper.text()).toContain('Success')
    const btn = wrapper.find('[data-testid="mark-read-btn"]')
    expect(btn.exists()).toBe(true)
    await btn.trigger('click')
    await flushPromises()
    expect(api.post).toHaveBeenCalledWith('/api/notifications/42/mark_read/')
    expect(success).toHaveBeenCalledWith('Notification marked as read')
  })

  it('shows pagination when count exceeds page size', async () => {
    setupDefaultGets({
      list: mockNotificationsListResponse({
        results: [{ id: 1, title: 'A', message: '', is_read: true, category: 'info', sent_at: '' }],
        count: 25,
        next: 'http://test/api/notifications/?page=2',
        previous: null,
      }),
    })
    const wrapper = mount(Notifications, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    const nav = wrapper.find('nav[aria-label="Notifications pagination"]')
    expect(nav.exists()).toBe(true)
    expect(wrapper.text()).toContain('Previous')
    expect(wrapper.text()).toContain('Next')
  })

  it('uses Spanish strings when locale is es', async () => {
    setAppLocale('es')
    const wrapper = mount(Notifications, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.findAll('nav')[0].attributes('aria-label')).toBe('Migas de pan')
    expect(wrapper.find('[data-testid="notifications-heading"]').text()).toContain('Notificaciones')
    expect(wrapper.text()).toContain('Sin notificaciones')
    expect(wrapper.text()).toContain('Gestiona tus notificaciones')
    expect(wrapper.text()).toContain('Limpiar filtros')
  })
})
