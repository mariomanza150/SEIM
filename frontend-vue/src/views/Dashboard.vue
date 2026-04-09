<template>
  <div class="dashboard" data-testid="dashboard-page">
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
      <div class="container-fluid">
        <router-link class="navbar-brand" :to="{ name: 'Dashboard' }">SEIM</router-link>
        <button
          class="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarNav"
        >
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav ms-auto align-items-center">
             <NotificationDropdown />
             
             <!-- Admin Buttons (only for admin users) -->
             <li class="nav-item" v-if="authStore.isAdmin">
               <a class="nav-link" href="/seim/admin/" target="_blank" rel="noopener noreferrer">
                 <i class="bi bi-gear-wide-connected me-1"></i> Django Admin
               </a>
             </li>
             <li class="nav-item" v-if="authStore.isAdmin">
               <a class="nav-link" href="/cms/" target="_blank" rel="noopener noreferrer">
                 <i class="bi bi-layout-wtf me-1"></i> CMS Admin
               </a>
             </li>
             
             <li class="nav-item dropdown">
              <a
                class="nav-link dropdown-toggle"
                href="#"
                id="userDropdown"
                role="button"
                data-bs-toggle="dropdown"
              >
                <i class="bi bi-person-circle me-1"></i>
                {{ userName }}
              </a>
              <ul class="dropdown-menu dropdown-menu-end">
                <li><router-link :to="{ name: 'Profile' }" class="dropdown-item">Profile</router-link></li>
                <li><router-link :to="{ name: 'Settings' }" class="dropdown-item">Settings</router-link></li>
                <li><hr class="dropdown-divider" /></li>
                <li>
                  <a class="dropdown-item" href="#" @click.prevent="handleLogout" data-testid="logout-link">
                    Logout
                  </a>
                </li>
              </ul>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <div class="container-fluid mt-4">
      <div class="row">
        <!-- Sidebar -->
        <div class="col-md-3 col-lg-2">
          <div class="list-group">
            <router-link :to="{ name: 'Dashboard' }" class="list-group-item list-group-item-action active">
              <i class="bi bi-house-door me-2"></i>Dashboard
            </router-link>
            <router-link :to="{ name: 'Applications' }" class="list-group-item list-group-item-action">
              <i class="bi bi-file-earmark-text me-2"></i>Applications
            </router-link>
            <router-link
              v-if="authStore.canUseStaffReviewQueue"
              :to="{ name: 'CoordinatorReviewQueue' }"
              class="list-group-item list-group-item-action"
            >
              <i class="bi bi-clipboard-check me-2"></i>Review queue
            </router-link>
            <router-link :to="{ name: 'Documents' }" class="list-group-item list-group-item-action">
              <i class="bi bi-folder me-2"></i>Documents
            </router-link>
            <router-link :to="{ name: 'Notifications' }" class="list-group-item list-group-item-action">
              <i class="bi bi-bell me-2"></i>Notifications
            </router-link>
            <router-link :to="{ name: 'Settings' }" class="list-group-item list-group-item-action">
              <i class="bi bi-gear me-2"></i>Settings
            </router-link>
          </div>
        </div>

        <!-- Dashboard Content -->
        <div class="col-md-9 col-lg-10">
          <div class="row mb-4">
            <div class="col">
              <h2>Welcome, {{ userName }}!</h2>
              <p class="text-muted">Here's what's happening with your exchange program.</p>
            </div>
          </div>

          <!-- Stats Cards -->
          <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-3 text-muted">Loading dashboard...</p>
          </div>

          <div v-else class="row mb-4">
            <div class="col-md-3 mb-3">
              <router-link :to="{ name: 'Applications' }" class="text-decoration-none">
                <div class="card text-center card-hover">
                  <div class="card-body">
                    <i class="bi bi-file-earmark-text fs-1 text-primary"></i>
                    <h3 class="mt-2">{{ stats.applications }}</h3>
                    <p class="text-muted mb-0">Applications</p>
                  </div>
                </div>
              </router-link>
            </div>
            <div class="col-md-3 mb-3">
              <router-link :to="{ name: 'Documents' }" class="text-decoration-none">
                <div class="card text-center card-hover">
                  <div class="card-body">
                    <i class="bi bi-folder fs-1 text-success"></i>
                    <h3 class="mt-2">{{ stats.documents }}</h3>
                    <p class="text-muted mb-0">Documents</p>
                  </div>
                </div>
              </router-link>
            </div>
            <div class="col-md-3 mb-3">
              <router-link :to="{ name: 'Notifications' }" class="text-decoration-none">
                <div class="card text-center card-hover">
                  <div class="card-body">
                    <i class="bi bi-bell fs-1 text-warning"></i>
                    <h3 class="mt-2">{{ stats.notifications }}</h3>
                    <p class="text-muted mb-0">Notifications</p>
                  </div>
                </div>
              </router-link>
            </div>
            <div class="col-md-3 mb-3">
              <component
                :is="authStore.canUseStaffReviewQueue ? 'router-link' : 'div'"
                v-bind="
                  authStore.canUseStaffReviewQueue
                    ? { to: { name: 'CoordinatorReviewQueue' }, class: 'text-decoration-none' }
                    : {}
                "
              >
                <div class="card text-center" :class="{ 'card-hover': authStore.canUseStaffReviewQueue }">
                  <div class="card-body">
                    <i class="bi bi-clock-history fs-1 text-info"></i>
                    <h3 class="mt-2">{{ stats.pending }}</h3>
                    <p class="text-muted mb-0">Pending Tasks</p>
                  </div>
                </div>
              </component>
            </div>
          </div>

          <!-- Next steps -->
          <div v-if="!loading" class="card">
            <div class="card-header d-flex justify-content-between align-items-center flex-wrap gap-2">
              <h5 class="mb-0">What needs your attention</h5>
              <span v-if="nextStepsLoading" class="text-muted small">
                <span class="spinner-border spinner-border-sm me-1" role="status" />
                Updating…
              </span>
            </div>
            <div class="card-body">
              <div v-if="error" class="alert alert-warning alert-dismissible fade show" role="alert">
                <i class="bi bi-exclamation-triangle me-2"></i>
                {{ error }}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
              </div>
              <p v-if="nextStepsError" class="text-warning small mb-3">{{ nextStepsError }}</p>
              <ul v-if="nextSteps.length" class="list-group list-group-flush border rounded">
                <li
                  v-for="row in nextSteps"
                  :key="row.id"
                  class="list-group-item list-group-item-action d-flex justify-content-between align-items-start gap-3 py-3"
                >
                  <div class="min-w-0">
                    <div class="fw-medium">{{ row.title }}</div>
                    <div v-if="row.subtitle" class="text-muted small text-break">{{ row.subtitle }}</div>
                  </div>
                  <div class="flex-shrink-0">
                    <router-link
                      v-if="row.spaRoute"
                      :to="row.spaRoute"
                      class="btn btn-sm btn-primary"
                    >
                      Open
                    </router-link>
                    <a
                      v-else-if="row.href"
                      :href="row.href"
                      class="btn btn-sm btn-outline-primary"
                    >
                      Open
                    </a>
                    <router-link v-else :to="{ name: 'Notifications' }" class="btn btn-sm btn-outline-secondary">
                      View
                    </router-link>
                  </div>
                </li>
              </ul>
              <p v-else-if="!nextStepsLoading" class="text-muted mb-0">
                You are all caught up. New tasks will show here when you have draft applications, document
                actions, reviews, or unread notifications.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import NotificationDropdown from '@/components/NotificationDropdown.vue'
import api from '@/services/api'
import { fetchDashboardNextSteps } from '@/utils/dashboardNextSteps'

const router = useRouter()
const authStore = useAuthStore()
const { success, error: errorToast } = useToast()

const userName = computed(() => authStore.userName)
const loading = ref(true)
const error = ref(null)
const nextSteps = ref([])
const nextStepsLoading = ref(false)
const nextStepsError = ref(null)

// Dashboard stats from API
const stats = ref({
  applications: 0,
  documents: 0,
  notifications: 0,
  pending: 0,
})

function onApplicationSync() {
  loadNextSteps()
  fetchDashboardStats({ soft: true })
}

async function fetchDashboardStats(options = {}) {
  const soft = options.soft === true
  try {
    if (!soft) {
      loading.value = true
      error.value = null
    }
    const response = await api.get('/api/accounts/dashboard/stats/')
    stats.value = response.data
  } catch (err) {
    if (!soft) {
      error.value = 'Failed to load dashboard statistics'
      errorToast('Unable to load dashboard statistics')
    }
  } finally {
    if (!soft) {
      loading.value = false
    }
  }
}

async function loadNextSteps() {
  try {
    nextStepsLoading.value = true
    nextStepsError.value = null
    nextSteps.value = await fetchDashboardNextSteps(api, {
      userRole: authStore.userRole,
      canUseStaffReviewQueue: authStore.canUseStaffReviewQueue,
    })
  } catch {
    nextStepsError.value = 'Could not load suggested next steps.'
  } finally {
    nextStepsLoading.value = false
  }
}

async function handleLogout() {
  await authStore.logout()
  success('You have been logged out successfully')
  router.push({ name: 'Login' })
}

onMounted(async () => {
  await fetchDashboardStats()
  await loadNextSteps()
  window.addEventListener('seim-application-sync', onApplicationSync)
})

onUnmounted(() => {
  window.removeEventListener('seim-application-sync', onApplicationSync)
})
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background-color: #f8f9fa;
}

.navbar {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.list-group-item {
  border: none;
  border-radius: 0.5rem;
  margin-bottom: 0.25rem;
}

.list-group-item.active {
  background-color: #667eea;
  border-color: #667eea;
}

.card {
  border: none;
  border-radius: 0.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}
</style>
