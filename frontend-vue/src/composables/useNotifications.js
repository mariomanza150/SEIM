import { useI18n } from 'vue-i18n'
import api from '@/services/api'

function normalizeNotificationListPayload(payload) {
  if (!payload) return { results: [], count: 0, next: null, previous: null }
  if (Array.isArray(payload)) {
    return { results: payload, count: payload.length, next: null, previous: null }
  }
  return {
    results: payload.results ?? [],
    count: payload.count ?? (Array.isArray(payload.results) ? payload.results.length : 0),
    next: payload.next ?? null,
    previous: payload.previous ?? null,
  }
}

function localeTagForNotifications(localeValue) {
  return localeValue === 'es' ? 'es' : 'en-US'
}

export function useNotifications() {
  const { t, locale } = useI18n()

  async function fetchNotifications({ page = 1, pageSize, ordering = '-sent_at', filters = {} } = {}) {
    const params = { page, ordering, ...filters }
    if (pageSize) params.page_size = pageSize
    const { data } = await api.get('/api/notifications/', { params })
    return normalizeNotificationListPayload(data)
  }

  async function fetchUnreadCount() {
    const { data } = await api.get('/api/notifications/', {
      params: { is_read: false, page_size: 1 },
    })
    return data?.count ?? 0
  }

  async function markAsRead(notificationId) {
    if (!notificationId) return
    await api.post(`/api/notifications/${notificationId}/mark_read/`)
  }

  async function markAllRead() {
    await api.post('/api/notifications/mark_all_read/')
  }

  function formatTimestampDropdown(dateString) {
    if (!dateString) return ''
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    if (diffMins < 1) return t('notifications.timeJustNow')
    if (diffMins < 60) return t('notifications.timeMinutesAgo', { n: diffMins })
    const diffHours = Math.floor(diffMins / 60)
    if (diffHours < 24) return t('notifications.timeHoursAgo', { n: diffHours })
    return date.toLocaleDateString(localeTagForNotifications(locale.value), { month: 'short', day: 'numeric' })
  }

  function formatTimestampPage(dateString) {
    if (!dateString) return t('notifications.notAvailable')
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    if (diffMins < 1) return t('notifications.timeJustNow')
    if (diffMins < 60) return t('notifications.timeMinutesAgo', { n: diffMins })
    const diffHours = Math.floor(diffMins / 60)
    if (diffHours < 24) return t('notifications.timeHoursAgo', { n: diffHours })
    const diffDays = Math.floor(diffHours / 24)
    if (diffDays < 7) return t('notifications.timeDaysAgo', { n: diffDays })
    return date.toLocaleDateString(localeTagForNotifications(locale.value), {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  return {
    fetchNotifications,
    fetchUnreadCount,
    markAsRead,
    markAllRead,
    formatTimestampDropdown,
    formatTimestampPage,
  }
}

