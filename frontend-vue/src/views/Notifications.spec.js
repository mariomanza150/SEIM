/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import Notifications from './Notifications.vue'
import api from '@/services/api'
import i18n, { setAppLocale } from '@/i18n'

vi.mock('@/services/api', () => ({
  default: { get: vi.fn(), post: vi.fn(), delete: vi.fn() },
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
    expect(wrapper.find('[data-testid="compact-filter-clear"]').attributes('aria-label')).toBe(
      i18n.global.t('notifications.clearFilters'),
    )
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

  it('dismisses a notification from the list', async () => {
    setupDefaultGets({
      list: mockNotificationsListResponse({
        results: [
          {
            id: 42,
            title: 'Doc approved',
            message: 'Your document was approved',
            is_read: true,
            category: 'success',
            sent_at: new Date().toISOString(),
          },
        ],
        count: 1,
      }),
      unreadCount: 0,
    })
    api.delete.mockResolvedValue({})

    const wrapper = mount(Notifications, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    const btn = wrapper.find('[data-testid="dismiss-notification-btn"]')
    expect(btn.exists()).toBe(true)
    await btn.trigger('click')
    await flushPromises()
    expect(api.delete).toHaveBeenCalledWith('/api/notifications/42/delete_notification/')
    expect(success).toHaveBeenCalledWith('Notification dismissed')
    expect(wrapper.text()).not.toContain('Doc approved')
  })

  it('status filter refetch sends numeric page 1', async () => {
    setupDefaultGets({
      list: mockNotificationsListResponse({
        results: [
          {
            id: 1,
            title: 'Unread',
            message: 'Hello',
            is_read: false,
            category: 'info',
            sent_at: new Date().toISOString(),
          },
        ],
        count: 1,
      }),
      unreadCount: 1,
    })
    const wrapper = mount(Notifications, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    api.get.mockClear()
    setupDefaultGets()
    await wrapper.get('#notifications-filter-status').setValue('false')
    await wrapper.get('#notifications-filter-status').trigger('change')
    await flushPromises()
    const listCalls = api.get.mock.calls.filter(([, cfg]) => cfg?.params?.page_size !== 1)
    expect(listCalls.length).toBeGreaterThan(0)
    for (const [, cfg] of listCalls) {
      expect(cfg.params.page).toBe(1)
    }
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
    expect(wrapper.text()).toContain(i18n.global.t('pagination.previous'))
    expect(wrapper.text()).toContain(i18n.global.t('pagination.next'))
    const ariaLabels = nav.findAll('button').map((b) => b.attributes('aria-label'))
    expect(ariaLabels).toContain(i18n.global.t('pagination.pageNumberAria', { n: 1 }))
    expect(ariaLabels).toContain(i18n.global.t('pagination.pageNumberAria', { n: 2 }))
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

  it('localizes stored English status-update copy (MQ-033)', async () => {
    setAppLocale('es')
    setupDefaultGets({
      list: mockNotificationsListResponse({
        results: [
          {
            id: 7,
            title: 'Application Status Update',
            message:
              'Your application for Program Alpha status has changed to under_review.',
            is_read: false,
            category: 'info',
            sent_at: new Date().toISOString(),
            action_url: '/seim/applications/1',
            action_text: 'View Application',
          },
        ],
        count: 1,
      }),
      unreadCount: 1,
    })
    const wrapper = mount(Notifications, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.text()).toContain('Actualización de estado de la solicitud')
    expect(wrapper.text()).toContain('En revisión')
    expect(wrapper.text()).not.toContain('under_review')
    expect(wrapper.text()).toContain('Ver solicitud')
  })

  it('marks all unread notifications as read', async () => {
    setupDefaultGets({
      list: mockNotificationsListResponse({
        results: [
          {
            id: 1,
            title: 'Ready for review',
            message: 'A document is waiting.',
            is_read: false,
            category: 'warning',
            sent_at: new Date().toISOString(),
          },
        ],
        count: 1,
      }),
      unreadCount: 3,
    })
    api.post.mockResolvedValue({ data: {} })
    const wrapper = mount(Notifications, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    await wrapper.get('[data-testid="mark-all-read-btn"]').trigger('click')
    await flushPromises()
    expect(api.post).toHaveBeenCalledWith('/api/notifications/mark_all_read/')
    expect(success).toHaveBeenCalledWith(i18n.global.t('notifications.toastAllMarkedRead'))
    expect(wrapper.find('[data-testid="mark-all-read-btn"]').exists()).toBe(false)
  })

  it('toasts when mark-all-read fails', async () => {
    setupDefaultGets({
      list: mockNotificationsListResponse({
        results: [
          {
            id: 1,
            title: 'Ready for review',
            message: 'A document is waiting.',
            is_read: false,
            category: 'info',
            sent_at: new Date().toISOString(),
          },
        ],
        count: 1,
      }),
      unreadCount: 1,
    })
    api.post.mockRejectedValue(new Error('offline'))
    const wrapper = mount(Notifications, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    await wrapper.get('[data-testid="mark-all-read-btn"]').trigger('click')
    await flushPromises()
    expect(errorToast).toHaveBeenCalledWith(i18n.global.t('notifications.toastMarkAllFailed'))
  })

  it('filters by category and clears filters', async () => {
    setupDefaultGets({
      list: mockNotificationsListResponse({
        results: [
          {
            id: 1,
            title: 'Warning item',
            message: 'Check this',
            is_read: true,
            category: 'warning',
            sent_at: new Date().toISOString(),
          },
        ],
        count: 1,
      }),
    })
    const wrapper = mount(Notifications, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    api.get.mockClear()
    setupDefaultGets()
    await wrapper.get('#notifications-filter-category').setValue('warning')
    await wrapper.get('#notifications-filter-category').trigger('change')
    await flushPromises()
    const filtered = api.get.mock.calls.filter(([, cfg]) => cfg?.params?.page_size !== 1)
    expect(filtered.at(-1)[1].params).toMatchObject({ category: 'warning', page: 1 })

    api.get.mockClear()
    setupDefaultGets()
    await wrapper.get('[data-testid="compact-filter-clear"]').trigger('click')
    await flushPromises()
    const cleared = api.get.mock.calls.filter(([, cfg]) => cfg?.params?.page_size !== 1)
    expect(cleared.at(-1)[1].params).toMatchObject({ page: 1 })
    expect(cleared.at(-1)[1].params.category).toBeUndefined()
  })

  it('refreshes when a notification-new window event fires', async () => {
    setupDefaultGets()
    mount(Notifications, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    api.get.mockClear()
    setupDefaultGets({ unreadCount: 2 })
    window.dispatchEvent(new Event('notification-new'))
    await flushPromises()
    expect(api.get).toHaveBeenCalled()
  })

  it('renders unknown categories with the info badge fallback', async () => {
    setupDefaultGets({
      list: mockNotificationsListResponse({
        results: [
          {
            id: 8,
            title: 'System note',
            message: 'Maintenance window',
            is_read: true,
            category: 'custom',
            sent_at: new Date().toISOString(),
          },
        ],
        count: 1,
      }),
    })
    const wrapper = mount(Notifications, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    expect(wrapper.find('.badge.bg-secondary').exists()).toBe(true)
    expect(wrapper.text()).toContain(i18n.global.t('notifications.categoryInfo'))
  })

  it('toasts when dismiss fails', async () => {
    setupDefaultGets({
      list: mockNotificationsListResponse({
        results: [
          {
            id: 42,
            title: 'Keep me',
            message: 'Still here',
            is_read: true,
            category: 'info',
            sent_at: new Date().toISOString(),
          },
        ],
        count: 1,
      }),
    })
    api.delete.mockRejectedValue(new Error('offline'))
    const wrapper = mount(Notifications, {
      global: {
        plugins: [i18n],
        stubs: { RouterLink: { template: '<a><slot /></a>' } },
      },
    })
    await flushPromises()
    await wrapper.get('[data-testid="dismiss-notification-btn"]').trigger('click')
    await flushPromises()
    expect(errorToast).toHaveBeenCalledWith(i18n.global.t('notifications.toastDismissFailed'))
    expect(wrapper.text()).toContain('Keep me')
  })
})
