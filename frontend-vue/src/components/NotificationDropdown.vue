<template>
  <li class="nav-item dropdown">
    <a
      class="nav-link dropdown-toggle position-relative"
      href="#"
      id="notificationDropdown"
      role="button"
      data-bs-toggle="dropdown"
      aria-expanded="false"
      aria-haspopup="menu"
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
          :class="{ 'seim-notification-unread': !notification.is_read }"
        >
          <div class="d-flex w-100 justify-content-between align-items-start">
            <div class="flex-grow-1 min-w-0">
              <span class="d-block text-truncate fw-medium" :class="{ 'fw-bold': !notification.is_read }">
                {{ notification.title || t('notifications.defaultTitle') }}
              </span>
              <span class="d-block text-muted small text-truncate">{{ notification.message }}</span>
              <span class="d-block text-muted small mt-1">{{ formatTimestampDropdown(notification.sent_at) }}</span>
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
import { isNewTabUrl, isSpaUrl, normalizeSpaLocation } from '@/utils/navigation'
import { Dropdown } from 'bootstrap'
import { useNotifications } from '@/composables/useNotifications'

const { t } = useI18n()
const { fetchNotifications, fetchUnreadCount, markAsRead: apiMarkAsRead, formatTimestampDropdown } = useNotifications()

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

function closeDropdown() {
  const toggle = document.getElementById('notificationDropdown')
  if (!toggle) return
  const instance = Dropdown.getInstance(toggle) || new Dropdown(toggle)
  instance.hide()
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

html[data-theme='dark'] .dropdown-item.notification-item:hover {
  background-color: rgba(255, 255, 255, 0.06);
}
</style>
