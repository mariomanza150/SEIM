/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import i18n, { setAppLocale } from '@/i18n'
import { useNotifications } from './useNotifications'
import api from '@/services/api'

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn(),
  },
}))

function mountComposable() {
  let expose
  const Comp = defineComponent({
    setup() {
      expose = useNotifications()
      return () => null
    },
  })
  mount(Comp, { global: { plugins: [i18n] } })
  return expose
}

describe('useNotifications', () => {
  beforeEach(() => {
    setAppLocale('en')
    vi.clearAllMocks()
  })

  afterEach(() => {
    setAppLocale('en')
    vi.useRealTimers()
  })

  it('fetchUnreadCount calls notifications endpoint and returns count', async () => {
    api.get.mockResolvedValue({ data: { count: 7 } })
    const n = mountComposable()
    await expect(n.fetchUnreadCount()).resolves.toBe(7)
    expect(api.get).toHaveBeenCalledWith('/api/notifications/', { params: { is_read: false, page_size: 1 } })
  })

  it('markAsRead posts mark_read endpoint', async () => {
    api.post.mockResolvedValue({ data: {} })
    const n = mountComposable()
    await n.markAsRead(123)
    expect(api.post).toHaveBeenCalledWith('/api/notifications/123/mark_read/')
  })

  it('dismissNotification deletes via delete_notification action', async () => {
    api.delete.mockResolvedValue({ data: {} })
    const n = mountComposable()
    await n.dismissNotification(55)
    expect(api.delete).toHaveBeenCalledWith('/api/notifications/55/delete_notification/')
  })

  it('formatTimestampDropdown uses relative time for recent notifications', async () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-01-01T00:00:30.000Z'))
    const n = mountComposable()
    expect(n.formatTimestampDropdown('2026-01-01T00:00:00.000Z')).toBe('Just now')
  })

  it('fetchNotifications normalizes array and paginated payloads', async () => {
    const n = mountComposable()
    api.get.mockResolvedValueOnce({ data: [{ id: 1 }, { id: 2 }] })
    await expect(n.fetchNotifications({ page: 2, pageSize: 10 })).resolves.toEqual({
      results: [{ id: 1 }, { id: 2 }],
      count: 2,
      next: null,
      previous: null,
    })
    expect(api.get).toHaveBeenCalledWith('/api/notifications/', {
      params: { page: 2, ordering: '-sent_at', page_size: 10 },
    })

    api.get.mockResolvedValueOnce({
      data: { results: [{ id: 9 }], count: 9, next: 'n', previous: 'p' },
    })
    await expect(n.fetchNotifications({ filters: { is_read: false } })).resolves.toEqual({
      results: [{ id: 9 }],
      count: 9,
      next: 'n',
      previous: 'p',
    })
  })

  it('fetchNotifications treats empty payloads as an empty page', async () => {
    api.get.mockResolvedValue({ data: null })
    const n = mountComposable()
    await expect(n.fetchNotifications()).resolves.toEqual({
      results: [],
      count: 0,
      next: null,
      previous: null,
    })
  })

  it('markAsRead and dismissNotification no-op without an id', async () => {
    const n = mountComposable()
    await n.markAsRead()
    await n.dismissNotification(null)
    expect(api.post).not.toHaveBeenCalled()
    expect(api.delete).not.toHaveBeenCalled()
  })

  it('markAllRead posts the mark_all_read endpoint', async () => {
    api.post.mockResolvedValue({ data: {} })
    const n = mountComposable()
    await n.markAllRead()
    expect(api.post).toHaveBeenCalledWith('/api/notifications/mark_all_read/')
  })

  it('formats dropdown and page timestamps across relative buckets', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-03-15T12:00:00.000Z'))
    const n = mountComposable()

    expect(n.formatTimestampDropdown('')).toBe('')
    expect(n.formatTimestampDropdown('2026-03-15T11:50:00.000Z')).toBe('10m ago')
    expect(n.formatTimestampDropdown('2026-03-15T09:00:00.000Z')).toBe('3h ago')
    expect(n.formatTimestampDropdown('2026-03-10T12:00:00.000Z')).toMatch(/Mar/)

    expect(n.formatTimestampPage('')).toBe('N/A')
    expect(n.formatTimestampPage('2026-03-15T11:59:30.000Z')).toBe('Just now')
    expect(n.formatTimestampPage('2026-03-15T11:30:00.000Z')).toBe('30m ago')
    expect(n.formatTimestampPage('2026-03-15T08:00:00.000Z')).toBe('4h ago')
    expect(n.formatTimestampPage('2026-03-13T12:00:00.000Z')).toBe('2d ago')
    expect(n.formatTimestampPage('2026-02-01T12:00:00.000Z')).toMatch(/2026/)
  })

  it('uses Spanish locale tags for absolute dates when locale is es', () => {
    setAppLocale('es')
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-03-15T12:00:00.000Z'))
    const n = mountComposable()
    expect(n.formatTimestampDropdown('2026-01-05T12:00:00.000Z')).toBeTruthy()
    expect(n.formatTimestampPage('2026-01-05T12:00:00.000Z')).toBeTruthy()
  })
})

