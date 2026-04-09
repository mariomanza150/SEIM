<template>
  <li class="nav-item dropdown">
    <a
      class="nav-link dropdown-toggle position-relative"
      href="#"
      id="notificationDropdown"
      role="button"
      data-bs-toggle="dropdown"
      aria-expanded="false"
      :aria-label="t('notifications.dropdownAria')"
    >
      <i class="bi bi-bell fs-5"></i>
      <span
        v-if="unreadCount > 0"
        class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger"
        style="font-size: 0.65rem"
      >
        {{ unreadCount > 99 ? '99+' : unreadCount }}
      </span>
    </a>
    <ul class="dropdown-menu dropdown-menu-end notification-dropdown" aria-labelledby="notificationDropdown">
      <li class="dropdown-header d-flex justify-content-between align-items-center px-3 py-2 border-bottom">
        <span class="fw-bold">{{ t('notifications.dropdownHeader') }}</span>
        <router-link :to="{ name: 'Notifications' }" class="btn btn-sm btn-link p-0" @click="closeDropdown">
          {{ t('notifications.viewAll') }}
        </router-link>
      </li>
      <li v-if="loading" class="px-3 py-4 text-center text-muted small">
        <div class="spinner-border spinner-border-sm me-2"></div>
        {{ t('notifications.dropdownLoading') }}
      </li>
      <li v-else-if="recent.length === 0" class="px-3 py-4 text-center text-muted small">
        {{ t('notifications.dropdownEmpty') }}
      </li>
      <template v-else>
        <li
          v-for="notification in recent"
          :key="notification.id"
          class="dropdown-item notification-item py-2"
          :class="{ 'bg-light': notification.is_read }"
        >
          <div class="d-flex w-100 justify-content-between align-items-start">
            <div class="flex-grow-1 min-w-0">
              <span class="d-block text-truncate fw-medium" :class="{ 'fw-bold': !notification.is_read }">
                {{ notification.title || t('notifications.defaultTitle') }}
              </span>
              <span class="d-block text-muted small text-truncate">{{ notification.message }}</span>
              <span class="d-block text-muted small mt-1">{{ formatTime(notification.sent_at) }}</span>
            </div>
          </div>
          <div class="mt-2">
            <router-link
              v-if="notification.action_url && isSpaUrl(notification.action_url)"
              :to="normalizeSpaLocation(notification.action_url)"
              class="btn btn-sm btn-outline-primary btn-sm"
              @click="markAsRead(notification); closeDropdown()"
            >
              {{ notification.action_text || t('notifications.viewAction') }}
            </router-link>
            <a
              v-else-if="notification.action_url"
              :href="notification.action_url"
              :target="isNewTabUrl(notification.action_url) ? '_blank' : null"
              :rel="isNewTabUrl(notification.action_url) ? 'noopener noreferrer' : null"
              class="btn btn-sm btn-outline-primary"
              @click="markAsRead(notification); closeDropdown()"
            >
              {{ notification.action_text || t('notifications.viewAction') }}
            </a>
          </div>
        </li>
      </template>
      <li class="dropdown-footer border-top">
        <router-link :to="{ name: 'Notifications' }" class="dropdown-item text-center py-2" @click="closeDropdown">
          <i class="bi bi-bell me-2"></i>{{ t('notifications.allNotificationsLink') }}
        </router-link>
      </li>
    </ul>
  </li>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { isNewTabUrl, isSpaUrl, normalizeSpaLocation } from '@/utils/navigation'

const { t, locale } = useI18n()

const recent = ref([])
const unreadCount = ref(0)
const loading = ref(false)

async function fetchRecent() {
  try {
    loading.value = true
    const [listRes, countRes] = await Promise.all([
      api.get('/api/notifications/', {
        params: { page_size: 5, ordering: '-sent_at' },
      }),
      api.get('/api/notifications/', {
        params: { is_read: false, page_size: 1 },
      }),
    ])
    recent.value = listRes.data.results || listRes.data
    unreadCount.value = countRes.data.count ?? 0
  } catch (err) {
    console.warn('Failed to fetch notifications:', err)
  } finally {
    loading.value = false
  }
}

async function markAsRead(notification) {
  if (notification.is_read) return
  try {
    await api.post(`/api/notifications/${notification.id}/mark_read/`)
    notification.is_read = true
    unreadCount.value = Math.max(0, unreadCount.value - 1)
  } catch (err) {
    console.warn('Failed to mark as read:', err)
  }
}

function formatTime(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  if (diffMins < 1) return t('notifications.timeJustNow')
  if (diffMins < 60) return t('notifications.timeMinutesAgo', { n: diffMins })
  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return t('notifications.timeHoursAgo', { n: diffHours })
  const localeTag = locale.value === 'es' ? 'es' : 'en-US'
  return date.toLocaleDateString(localeTag, { month: 'short', day: 'numeric' })
}

function closeDropdown() {
  document.querySelector('#notificationDropdown')?.click()
}

onMounted(() => {
  fetchRecent()
  window.addEventListener('notification-new', fetchRecent)
})

onUnmounted(() => {
  window.removeEventListener('notification-new', fetchRecent)
})

defineExpose({ refresh: fetchRecent })
</script>

<style scoped>
.notification-dropdown {
  min-width: 320px;
  max-height: 400px;
  overflow-y: auto;
}

.notification-item {
  white-space: normal;
  max-width: 100%;
}

.dropdown-item.notification-item:hover {
  background-color: rgba(0, 0, 0, 0.05);
}
</style>
