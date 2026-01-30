<template>
  <div class="notifications-page">
    <div class="container-fluid mt-4">
      <!-- Header -->
      <div class="row mb-4">
        <div class="col-md-8">
          <h2><i class="bi bi-bell me-2"></i>Notifications</h2>
          <p class="text-muted">Manage your notifications</p>
        </div>
        <div class="col-md-4 text-end">
          <button
            v-if="unreadCount > 0"
            class="btn btn-outline-primary"
            :disabled="markingAllRead"
            @click="markAllRead"
          >
            <span v-if="markingAllRead">
              <span class="spinner-border spinner-border-sm me-2"></span>
              Marking...
            </span>
            <span v-else>
              <i class="bi bi-check-all me-2"></i>Mark All as Read
            </span>
          </button>
        </div>
      </div>

      <!-- Filters -->
      <div class="card mb-4">
        <div class="card-body">
          <div class="row g-3">
            <div class="col-md-4">
              <label class="form-label">Status</label>
              <select v-model="filters.is_read" class="form-select" @change="fetchNotifications">
                <option value="">All</option>
                <option value="false">Unread</option>
                <option value="true">Read</option>
              </select>
            </div>
            <div class="col-md-4">
              <label class="form-label">Category</label>
              <select v-model="filters.category" class="form-select" @change="fetchNotifications">
                <option value="">All</option>
                <option value="info">Information</option>
                <option value="success">Success</option>
                <option value="warning">Warning</option>
                <option value="error">Error</option>
              </select>
            </div>
            <div class="col-md-4 d-flex align-items-end">
              <button class="btn btn-outline-secondary w-100" @click="clearFilters">
                <i class="bi bi-x-circle me-1"></i>Clear Filters
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-3 text-muted">Loading notifications...</p>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="alert alert-danger">
        <i class="bi bi-exclamation-triangle me-2"></i>
        {{ error }}
      </div>

      <!-- Notifications List -->
      <div v-else-if="notifications.length > 0">
        <div class="list-group">
          <div
            v-for="notification in notifications"
            :key="notification.id"
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
                    title="Unread"
                  ></span>
                  <h6 class="mb-1" :class="{ 'fw-bold': !notification.is_read }">
                    {{ notification.title || 'Notification' }}
                  </h6>
                  <span class="badge" :class="categoryClass(notification.category)">
                    {{ formatCategory(notification.category) }}
                  </span>
                </div>
                <p class="mb-2 text-muted small">{{ notification.message }}</p>
                <div class="d-flex align-items-center gap-3">
                  <span class="text-muted small">
                    <i class="bi bi-clock me-1"></i>
                    {{ formatDate(notification.sent_at) }}
                  </span>
                  <template v-if="notification.action_url">
                    <router-link
                      v-if="isInternalUrl(notification.action_url)"
                      :to="notification.action_url"
                      class="btn btn-sm btn-outline-primary"
                      @click="markAsRead(notification)"
                    >
                      {{ notification.action_text || 'View' }}
                    </router-link>
                    <a
                      v-else
                      :href="notification.action_url"
                      target="_blank"
                      rel="noopener"
                      class="btn btn-sm btn-outline-primary"
                      @click="markAsRead(notification)"
                    >
                      {{ notification.action_text || 'View' }}
                    </a>
                  </template>
                  <button
                    v-if="!notification.is_read"
                    type="button"
                    class="btn btn-sm btn-outline-secondary"
                    :disabled="markingId === notification.id"
                    @click="markAsRead(notification)"
                  >
                    <span v-if="markingId === notification.id" class="spinner-border spinner-border-sm"></span>
                    <span v-else><i class="bi bi-check me-1"></i>Mark as Read</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <nav v-if="pagination.count > pagination.pageSize" aria-label="Notifications pagination">
          <ul class="pagination justify-content-center mt-4">
            <li class="page-item" :class="{ disabled: !pagination.previous }">
              <button class="page-link" @click="goToPage(pagination.currentPage - 1)">
                Previous
              </button>
            </li>
            <li
              v-for="page in totalPages"
              :key="page"
              class="page-item"
              :class="{ active: page === pagination.currentPage }"
            >
              <button class="page-link" @click="goToPage(page)">{{ page }}</button>
            </li>
            <li class="page-item" :class="{ disabled: !pagination.next }">
              <button class="page-link" @click="goToPage(pagination.currentPage + 1)">
                Next
              </button>
            </li>
          </ul>
        </nav>
      </div>

      <!-- Empty State -->
      <div v-else class="card">
        <div class="card-body text-center py-5">
          <i class="bi bi-bell-slash display-1 text-muted"></i>
          <h4 class="mt-3">No Notifications</h4>
          <p class="text-muted">You're all caught up! No notifications to display.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import api from '@/services/api'

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
    error.value = 'Failed to load notifications. Please try again.'
    errorToast('Failed to load notifications')
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
    success('Notification marked as read')
  } catch (err) {
    console.error('Failed to mark as read:', err)
    errorToast('Failed to mark as read')
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
    success('All notifications marked as read')
  } catch (err) {
    console.error('Failed to mark all as read:', err)
    errorToast('Failed to mark all as read')
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
  return category ? category.charAt(0).toUpperCase() + category.slice(1) : 'Info'
}

function formatDate(dateString) {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `${diffHours}h ago`
  const diffDays = Math.floor(diffHours / 24)
  if (diffDays < 7) return `${diffDays}d ago`
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

function isInternalUrl(url) {
  if (!url) return false
  return url.startsWith('/') && !url.startsWith('//')
}

onMounted(async () => {
  await fetchNotifications()
  await fetchUnreadCount()
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
