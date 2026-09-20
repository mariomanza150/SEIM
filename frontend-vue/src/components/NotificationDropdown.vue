<template>
  <li class="nav-item dropdown seim-notification-nav" ref="rootEl">
    <button
      type="button"
      class="nav-link dropdown-toggle position-relative seim-nav-icon-btn"
      id="notificationDropdown"
      data-testid="notifications-menu"
      :class="{ show: open }"
      :aria-expanded="open ? 'true' : 'false'"
      aria-haspopup="menu"
      :aria-label="t('notifications.dropdownAria')"
      @click="onToggle"
    >
      <i class="bi bi-bell fs-5" aria-hidden="true"></i>
      <span
        v-if="unreadCount > 0"
        class="badge rounded-pill bg-danger seim-notification-badge"
        data-testid="notifications-badge"
      >
        {{ unreadCount > 99 ? '99+' : unreadCount }}
      </span>
    </button>
    <ul
      class="dropdown-menu dropdown-menu-end notification-dropdown"
      :class="{ show: open }"
      aria-labelledby="notificationDropdown"
      data-testid="notifications-dropdown-menu"
    >
      <li class="dropdown-header d-flex justify-content-between align-items-center px-3 py-2 border-bottom gap-2">
        <span class="fw-bold text-truncate">{{ t('notifications.dropdownHeader') }}</span>
        <router-link :to="{ name: 'Notifications' }" class="btn btn-sm btn-link p-0 flex-shrink-0" @click="close">
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
          :class="{ 'seim-notification-unread': !notification.is_read }"
        >
          <div class="d-flex w-100 justify-content-between align-items-start gap-2">
            <div class="flex-grow-1 min-w-0">
              <span class="d-block text-truncate fw-medium" :class="{ 'fw-bold': !notification.is_read }">
                {{ displayTitle(notification) }}
              </span>
              <span class="d-block text-muted small text-truncate">{{ displayMessage(notification) }}</span>
              <span class="d-block text-muted small mt-1">{{ formatTimestampDropdown(notification.sent_at) }}</span>
            </div>
            <button
              type="button"
              class="btn-close btn-close-sm flex-shrink-0 mt-1"
              data-testid="notification-dismiss"
              :aria-label="t('notifications.dismissAria')"
              @click.stop="dismiss(notification)"
            ></button>
          </div>
          <div class="mt-2 d-flex flex-wrap gap-2">
            <router-link
              v-if="notification.action_url && isSpaUrl(notification.action_url)"
              :to="normalizeSpaLocation(notification.action_url)"
              class="btn btn-sm btn-outline-primary"
              @click="markAsRead(notification); close()"
            >
              {{ displayAction(notification) }}
            </router-link>
            <a
              v-else-if="notification.action_url"
              :href="notification.action_url"
              :target="isNewTabUrl(notification.action_url) ? '_blank' : null"
              :rel="isNewTabUrl(notification.action_url) ? 'noopener noreferrer' : null"
              class="btn btn-sm btn-outline-primary"
              @click="markAsRead(notification); close()"
            >
              {{ displayAction(notification) }}
            </a>
            <button
              v-if="!notification.is_read"
              type="button"
              class="btn btn-sm btn-outline-secondary"
              data-testid="notification-mark-read"
              :aria-label="t('notifications.markAsReadAria')"
              @click.stop="markAsRead(notification)"
            >
              {{ t('notifications.markAsRead') }}
            </button>
          </div>
        </li>
      </template>
      <li class="dropdown-footer border-top">
        <router-link :to="{ name: 'Notifications' }" class="dropdown-item text-center py-2" @click="close">
          <i class="bi bi-bell me-2"></i>{{ t('notifications.allNotificationsLink') }}
        </router-link>
      </li>
    </ul>
  </li>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { isNewTabUrl, isSpaUrl, normalizeSpaLocation } from '@/utils/navigation'
import { useNavDropdown } from '@/composables/useNavDropdown'
import { useNotifications } from '@/composables/useNotifications'
import {
  formatNotificationAction,
  formatNotificationMessage,
  formatNotificationTitle,
} from '@/utils/notificationCopy'

const { t, te } = useI18n()
const i18nCtx = { t, te }

function displayTitle(notification) {
  return formatNotificationTitle(notification?.title, i18nCtx) || t('notifications.defaultTitle')
}

function displayMessage(notification) {
  return formatNotificationMessage(notification?.message, i18nCtx)
}

function displayAction(notification) {
  return formatNotificationAction(notification?.action_text, i18nCtx) || t('notifications.viewAction')
}
const {
  fetchNotifications,
  fetchUnreadCount,
  markAsRead: apiMarkAsRead,
  dismissNotification: apiDismiss,
  formatTimestampDropdown,
} = useNotifications()
const { open, rootEl, toggle, close } = useNavDropdown()

const recent = ref([])
const unreadCount = ref(0)
const loading = ref(false)

async function fetchRecent() {
  try {
    loading.value = true
    const [list, count] = await Promise.all([
      fetchNotifications({ pageSize: 5, ordering: '-sent_at' }),
      fetchUnreadCount(),
    ])
    recent.value = list.results
    unreadCount.value = count
  } catch (err) {
    console.warn('Failed to fetch notifications:', err)
  } finally {
    loading.value = false
  }
}

async function onToggle(event) {
  toggle(event)
  if (open.value) await fetchRecent()
}

async function markAsRead(notification) {
  if (notification.is_read) return
  try {
    await apiMarkAsRead(notification.id)
    notification.is_read = true
    unreadCount.value = Math.max(0, unreadCount.value - 1)
  } catch (err) {
    console.warn('Failed to mark as read:', err)
  }
}

async function dismiss(notification) {
  try {
    await apiDismiss(notification.id)
    if (!notification.is_read) {
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    }
    recent.value = recent.value.filter((n) => n.id !== notification.id)
  } catch (err) {
    console.warn('Failed to dismiss notification:', err)
  }
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
.seim-notification-nav {
  position: relative;
}

.seim-nav-icon-btn {
  background: transparent;
  border: 0;
  padding-right: 0.85rem;
}

.seim-notification-badge {
  position: absolute;
  top: 0.2rem;
  right: 0.15rem;
  font-size: 0.65rem;
  transform: none;
  /* Keep badge inside the button so it does not push past the viewport edge. */
}

.notification-dropdown {
  /* Open toward the page interior (left) from the right-side bell. */
  right: 0;
  left: auto;
  width: min(22rem, calc(100vw - 1.5rem));
  min-width: 0;
  max-width: min(22rem, calc(100vw - 1.5rem));
  max-height: min(400px, calc(100vh - 5rem));
  overflow-x: hidden;
  overflow-y: auto;
  box-sizing: border-box;
}

.notification-item {
  white-space: normal;
  max-width: 100%;
}

.btn-close-sm {
  width: 0.65rem;
  height: 0.65rem;
  padding: 0.45rem;
  background-size: 0.55em;
  opacity: 0.55;
}

.btn-close-sm:hover {
  opacity: 1;
}

.dropdown-item.notification-item:hover {
  background-color: var(--bg-tertiary, rgba(0, 0, 0, 0.05));
}

html[data-theme='dark'] .dropdown-item.notification-item:hover {
  background-color: var(--bg-tertiary, rgba(255, 255, 255, 0.06));
}
</style>
