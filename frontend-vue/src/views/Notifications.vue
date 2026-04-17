<template>
  <div class="notifications-page" data-testid="notifications-page">
    <PageHeader
      :title="t('notifications.dropdownHeader')"
      :subtitle="t('notifications.pageSubtitle')"
      icon-class="bi bi-bell"
      test-id="notifications-heading"
    >
      <template #breadcrumb>
        <nav :aria-label="t('notifications.breadcrumbAria')">
          <ol class="breadcrumb">
            <li class="breadcrumb-item">
              <router-link :to="{ name: 'Dashboard' }">{{ t('route.names.Dashboard') }}</router-link>
            </li>
            <li class="breadcrumb-item active" aria-current="page">{{ t('route.names.Notifications') }}</li>
          </ol>
        </nav>
      </template>
      <template #actions>
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
      </template>
    </PageHeader>

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
      <LoadingState
        v-if="loading"
        :spinner-label="t('notifications.loadingSpinner')"
        :hint="t('notifications.pageLoadingHint')"
      />

      <!-- Error -->
      <ErrorAlert v-else-if="error" :message="error" />

      <!-- Notifications List -->
      <div v-else-if="notifications.length > 0">
        <div class="list-group" role="list" :aria-label="t('notifications.dropdownHeader')">
          <div
            v-for="notification in notifications"
            :key="notification.id"
            role="listitem"
            class="list-group-item list-group-item-action"
            :class="{ 'seim-notification-unread': !notification.is_read }"
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
        <Pagination
          :count="pagination.count"
          :page-size="pagination.pageSize"
          :current-page="pagination.currentPage"
          :can-go-previous="!!pagination.previous"
          :can-go-next="!!pagination.next"
          :aria-label="t('notifications.paginationAria')"
          ul-class="mt-4"
          @page-change="goToPage"
        />
      </div>

      <!-- Empty State -->
      <EmptyState
        v-else
        icon-class="bi bi-bell-slash"
        :title="t('notifications.emptyTitle')"
        :body="t('notifications.emptyBody')"
      />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useToast } from '@/composables/useToast'
import { isNewTabUrl, isSpaUrl, normalizeSpaLocation } from '@/utils/navigation'
import PageHeader from '@/components/PageHeader.vue'
import { useNotifications } from '@/composables/useNotifications'
import Pagination from '@/components/Pagination.vue'
import LoadingState from '@/components/State/LoadingState.vue'
import ErrorAlert from '@/components/State/ErrorAlert.vue'
import EmptyState from '@/components/State/EmptyState.vue'

const { t } = useI18n()
const { success, error: errorToast } = useToast()
const {
  fetchNotifications: apiFetchNotifications,
  fetchUnreadCount: apiFetchUnreadCount,
  markAsRead: apiMarkAsRead,
  markAllRead: apiMarkAllRead,
  formatTimestampPage,
} = useNotifications()

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

async function fetchNotifications(page = 1) {
  try {
    loading.value = true
    error.value = null
    const list = await apiFetchNotifications({
      page,
      ordering: '-sent_at',
      filters: {
        ...(filters.value.is_read !== '' ? { is_read: filters.value.is_read } : {}),
        ...(filters.value.category ? { category: filters.value.category } : {}),
      },
    })

    notifications.value = list.results
    pagination.value = {
      count: list.count,
      next: list.next,
      previous: list.previous,
      currentPage: page,
      pageSize: pagination.value.pageSize,
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
    unreadCount.value = await apiFetchUnreadCount()
  } catch (err) {
    console.warn('Failed to fetch unread count:', err)
  }
}

async function markAsRead(notification) {
  if (notification.is_read) return
  try {
    markingId.value = notification.id
    await apiMarkAsRead(notification.id)
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
    await apiMarkAllRead()
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
  fetchNotifications(page)
  window.scrollTo({ top: 0, behavior: 'smooth' })
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
  return formatTimestampPage(dateString)
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
  background-color: var(--seim-app-bg);
}

.list-group-item {
  border-radius: 0.5rem;
  margin-bottom: 0.5rem;
  border: 1px solid rgba(0, 0, 0, 0.08);
}

.list-group-item.seim-notification-unread {
  border-width: 2px;
}
</style>
