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

  it('formatTimestampDropdown uses relative time for recent notifications', async () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-01-01T00:00:30.000Z'))
    const n = mountComposable()
    expect(n.formatTimestampDropdown('2026-01-01T00:00:00.000Z')).toBe('Just now')
  })
})

