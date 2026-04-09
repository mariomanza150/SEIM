<template>
  <div class="notifications-page" data-testid="notifications-page">
    <div class="container-fluid mt-4">
      <!-- Breadcrumb -->
      <nav :aria-label="t('notifications.breadcrumbAria')">
        <ol class="breadcrumb">
          <li class="breadcrumb-item">
            <router-link :to="{ name: 'Dashboard' }">{{ t('route.names.Dashboard') }}</router-link>
          </li>
          <li class="breadcrumb-item active" aria-current="page">{{ t('route.names.Notifications') }}</li>
        </ol>
      </nav>
      <!-- Header -->
      <div class="row mb-4">
        <div class="col-md-8">
          <h2 data-testid="notifications-heading">
            <i class="bi bi-bell me-2" aria-hidden="true"></i>{{ t('notifications.dropdownHeader') }}
          </h2>
          <p class="text-muted">{{ t('notifications.pageSubtitle') }}</p>
        </div>
        <div class="col-md-4 text-end">
          <button
            v-if="unreadCount > 0"
            type="button"
            class="btn btn-outline-primary"
            :disabled="markingAllRead"
            :aria-busy="markingAllRead ? 'true' : 'false'"
            :aria-label="t('notifications.markAllReadAria')"
            @click="markAllRead"
            data-testid="mark-all-read-btn"
          >
            <span v-if="markingAllRead">
              <span class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>
              {{ t('notifications.markingAllRead') }}
            </span>
            <span v-else>
              <i class="bi bi-check-all me-2" aria-hidden="true"></i>{{ t('notifications.markAllRead') }}
            </span>
          </button>
        </div>
      </div>

      <!-- Filters -->
      <div class="card mb-4">
        <div class="card-body">
          <div class="row g-3">
            <div class="col-md-4">
              <label class="form-label" for="notifications-filter-status">{{ t('notifications.filterReadStateLabel') }}</label>
              <select
                id="notifications-filter-status"
                v-model="filters.is_read"
                class="form-select"
                :aria-label="t('notifications.filterReadStateLabel')"
                @change="fetchNotifications"
              >
                <option value="">{{ t('notifications.filterAll') }}</option>
                <option value="false">{{ t('notifications.filterUnread') }}</option>
                <option value="true">{{ t('notifications.filterRead') }}</option>
              </select>
            </div>
            <div class="col-md-4">
              <label class="form-label" for="notifications-filter-category">{{ t('notifications.filterCategory') }}</label>
              <select
                id="notifications-filter-category"
                v-model="filters.category"
                class="form-select"
                :aria-label="t('notifications.filterCategory')"
                @change="fetchNotifications"
              >
                <option value="">{{ t('notifications.filterAll') }}</option>
                <option value="info">{{ t('notifications.categoryInfo') }}</option>
                <option value="success">{{ t('notifications.categorySuccess') }}</option>
                <option value="warning">{{ t('notifications.categoryWarning') }}</option>
                <option value="error">{{ t('notifications.categoryError') }}</option>
              </select>
            </div>
            <div class="col-md-4 d-flex align-items-end">
              <button
                type="button"
                class="btn btn-outline-secondary w-100"
                :aria-label="t('notifications.clearFilters')"
                @click="clearFilters"
              >
                <i class="bi bi-x-circle me-1" aria-hidden="true"></i>{{ t('notifications.clearFilters') }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-5" aria-live="polite">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">{{ t('notifications.loadingSpinner') }}</span>
        </div>
        <p class="mt-3 text-muted">{{ t('notifications.pageLoadingHint') }}</p>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="alert alert-danger" role="alert">
        <i class="bi bi-exclamation-triangle me-2" aria-hidden="true"></i>
        {{ error }}
      </div>

      <!-- Notifications List -->
      <div v-else-if="notifications.length > 0">
        <div class="list-group" role="list" :aria-label="t('notifications.dropdownHeader')">
          <div
            v-for="notification in notifications"
            :key="notification.id"
            role="listitem"
            class="list-group-item list-group-item-action"
            :class="{ 'bg-light': notification.is_read }"
          >
            <div class="d-flex w-100 justify-content-between align-items-start">
              <div class="flex-grow-1">
                <div class="d-flex align-items-center gap-2 mb-1">
                  <span
                    v-if="!notification.is_read"
                    class="badge rounded-pill bg-primary"
                    style="width: 8px; height: 8px; padding: 0"
                    :title="t('notifications.unreadBadgeTitle')"
                    aria-hidden="true"
                  ></span>
                  <h6 class="mb-1" :class="{ 'fw-bold': !notification.is_read }">
                    {{ notification.title || t('notifications.defaultTitle') }}
                  </h6>
                  <span class="badge" :class="categoryClass(notification.category)">
                    {{ formatCategory(notification.category) }}
                  </span>
                </div>
                <p class="mb-2 text-muted small">{{ notification.message }}</p>
                <div class="d-flex align-items-center gap-3 flex-wrap">
                  <span class="text-muted small">
                    <i class="bi bi-clock me-1" aria-hidden="true"></i>
                    {{ formatDate(notification.sent_at) }}
                  </span>
                  <template v-if="notification.action_url">
                    <router-link
                      v-if="isSpaUrl(notification.action_url)"
                      :to="normalizeSpaLocation(notification.action_url)"
                      class="btn btn-sm btn-outline-primary"
                      @click="markAsRead(notification)"
                    >
                      {{ notification.action_text || t('notifications.viewAction') }}
                    </router-link>
                    <a
                      v-else
                      :href="notification.action_url"
                      :target="isNewTabUrl(notification.action_url) ? '_blank' : null"
                      :rel="isNewTabUrl(notification.action_url) ? 'noopener noreferrer' : null"
                      class="btn btn-sm btn-outline-primary"
                      @click="markAsRead(notification)"
                    >
                      {{ notification.action_text || t('notifications.viewAction') }}
                    </a>
                  </template>
                  <button
                    v-if="!notification.is_read"
                    type="button"
                    class="btn btn-sm btn-outline-secondary"
                    :disabled="markingId === notification.id"
                    :aria-busy="markingId === notification.id ? 'true' : 'false'"
                    :aria-label="t('notifications.markAsReadAria')"
                    @click="markAsRead(notification)"
                    data-testid="mark-read-btn"
                  >
                    <span v-if="markingId === notification.id" class="spinner-border spinner-border-sm" aria-hidden="true"></span>
                    <span v-else><i class="bi bi-check me-1" aria-hidden="true"></i>{{ t('notifications.markAsRead') }}</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <nav v-if="pagination.count > pagination.pageSize" :aria-label="t('notifications.paginationAria')">
          <ul class="pagination justify-content-center mt-4">
            <li class="page-item" :class="{ disabled: !pagination.previous }">
              <button
                type="button"
                class="page-link"
                :disabled="!pagination.previous"
                :aria-label="t('notifications.previous')"
                @click="goToPage(pagination.currentPage - 1)"
              >
                {{ t('notifications.previous') }}
              </button>
            </li>
            <li
              v-for="page in totalPages"
              :key="page"
              class="page-item"
              :class="{ active: page === pagination.currentPage }"
            >
              <button
                type="button"
                class="page-link"
                :aria-label="t('notifications.pageNumberAria', { n: page })"
                :aria-current="page === pagination.currentPage ? 'page' : undefined"
                @click="goToPage(page)"
              >
                {{ page }}
              </button>
            </li>
            <li class="page-item" :class="{ disabled: !pagination.next }">
              <button
                type="button"
                class="page-link"
                :disabled="!pagination.next"
                :aria-label="t('notifications.next')"
                @click="goToPage(pagination.currentPage + 1)"
              >
                {{ t('notifications.next') }}
              </button>
            </li>
          </ul>
        </nav>
      </div>

      <!-- Empty State -->
      <div v-else class="card">
        <div class="card-body text-center py-5">
          <i class="bi bi-bell-slash display-1 text-muted" aria-hidden="true"></i>
          <h4 class="mt-3">{{ t('notifications.emptyTitle') }}</h4>
          <p class="text-muted">{{ t('notifications.emptyBody') }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useToast } from '@/composables/useToast'
import api from '@/services/api'
import { isNewTabUrl, isSpaUrl, normalizeSpaLocation } from '@/utils/navigation'

const { t, locale } = useI18n()
const { success, error: errorToast } = useToast()

const notifications = ref([])
const loading = ref(true)
const error = ref(null)
const markingId = ref(null)
const markingAllRead = ref(false)
const unreadCount = ref(0)

const filters = ref({
  is_read: '',
  category: '',
})

const pagination = ref({
  count: 0,
  next: null,
  previous: null,
  currentPage: 1,
  pageSize: 20,
})

const totalPages = computed(() => Math.ceil(pagination.value.count / pagination.value.pageSize))

async function fetchNotifications(page = 1) {
  try {
    loading.value = true
    error.value = null

    const params = { page, ordering: '-sent_at' }
    if (filters.value.is_read !== '') params.is_read = filters.value.is_read
    if (filters.value.category) params.category = filters.value.category

    const response = await api.get('/api/notifications/', { params })
    notifications.value = response.data.results || response.data

    if (response.data.count !== undefined) {
      pagination.value = {
        count: response.data.count,
        next: response.data.next,
        previous: response.data.previous,
        currentPage: page,
        pageSize: pagination.value.pageSize,
      }
    }
  } catch (err) {
    console.error('Failed to fetch notifications:', err)
    error.value = t('notifications.loadErrorDetail')
    errorToast(t('notifications.toastLoadFailed'))
  } finally {
    loading.value = false
  }
}

async function fetchUnreadCount() {
  try {
    const response = await api.get('/api/notifications/', {
      params: { is_read: false, page_size: 1 },
    })
    unreadCount.value = response.data.count ?? 0
  } catch (err) {
    console.warn('Failed to fetch unread count:', err)
  }
}

async function markAsRead(notification) {
  if (notification.is_read) return
  try {
    markingId.value = notification.id
    await api.post(`/api/notifications/${notification.id}/mark_read/`)
    notification.is_read = true
    unreadCount.value = Math.max(0, unreadCount.value - 1)
    success(t('notifications.toastMarkedRead'))
  } catch (err) {
    console.error('Failed to mark as read:', err)
    errorToast(t('notifications.toastMarkReadFailed'))
  } finally {
    markingId.value = null
  }
}

async function markAllRead() {
  try {
    markingAllRead.value = true
    await api.post('/api/notifications/mark_all_read/')
    notifications.value.forEach(n => { n.is_read = true })
    unreadCount.value = 0
    success(t('notifications.toastAllMarkedRead'))
  } catch (err) {
    console.error('Failed to mark all as read:', err)
    errorToast(t('notifications.toastMarkAllFailed'))
  } finally {
    markingAllRead.value = false
  }
}

function goToPage(page) {
  if (page >= 1 && page <= totalPages.value) {
    fetchNotifications(page)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

function clearFilters() {
  filters.value = { is_read: '', category: '' }
  fetchNotifications()
}

function categoryClass(category) {
  const classes = {
    info: 'bg-info',
    success: 'bg-success',
    warning: 'bg-warning',
    error: 'bg-danger',
  }
  return classes[category] || 'bg-secondary'
}

function formatCategory(category) {
  const map = {
    info: 'notifications.categoryInfo',
    success: 'notifications.categorySuccess',
    warning: 'notifications.categoryWarning',
    error: 'notifications.categoryError',
  }
  const key = map[category]
  return key ? t(key) : t('notifications.categoryInfo')
}

function formatDate(dateString) {
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
  const localeTag = locale.value === 'es' ? 'es' : 'en-US'
  return date.toLocaleDateString(localeTag, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

function onNotificationNew() {
  fetchNotifications()
  fetchUnreadCount()
}

onMounted(async () => {
  await fetchNotifications()
  await fetchUnreadCount()
  window.addEventListener('notification-new', onNotificationNew)
})

onUnmounted(() => {
  window.removeEventListener('notification-new', onNotificationNew)
})
</script>

<style scoped>
.notifications-page {
  min-height: 100vh;
  background-color: #f8f9fa;
}

.list-group-item {
  border-radius: 0.5rem;
  margin-bottom: 0.5rem;
  border: 1px solid rgba(0, 0, 0, 0.08);
}

.list-group-item.bg-light {
  opacity: 0.9;
}
</style>
