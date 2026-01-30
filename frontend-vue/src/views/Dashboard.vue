<template>
  <div class="dashboard">
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
      <div class="container-fluid">
        <a class="navbar-brand" href="#">SEIM</a>
        <button
          class="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarNav"
        >
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav ms-auto">
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
                <li><a class="dropdown-item" href="#">Profile</a></li>
                <li><a class="dropdown-item" href="#">Settings</a></li>
                <li><hr class="dropdown-divider" /></li>
                <li>
                  <a class="dropdown-item" href="#" @click.prevent="handleLogout">
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
            <router-link to="/dashboard" class="list-group-item list-group-item-action active">
              <i class="bi bi-house-door me-2"></i>Dashboard
            </router-link>
            <router-link to="/applications" class="list-group-item list-group-item-action">
              <i class="bi bi-file-earmark-text me-2"></i>Applications
            </router-link>
            <a href="#" class="list-group-item list-group-item-action">
              <i class="bi bi-folder me-2"></i>Documents
            </a>
            <a href="#" class="list-group-item list-group-item-action">
              <i class="bi bi-bell me-2"></i>Notifications
            </a>
            <a href="#" class="list-group-item list-group-item-action">
              <i class="bi bi-gear me-2"></i>Settings
            </a>
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
              <router-link to="/applications" class="text-decoration-none">
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
              <div class="card text-center">
                <div class="card-body">
                  <i class="bi bi-folder fs-1 text-success"></i>
                  <h3 class="mt-2">{{ stats.documents }}</h3>
                  <p class="text-muted mb-0">Documents</p>
                </div>
              </div>
            </div>
            <div class="col-md-3 mb-3">
              <div class="card text-center">
                <div class="card-body">
                  <i class="bi bi-bell fs-1 text-warning"></i>
                  <h3 class="mt-2">{{ stats.notifications }}</h3>
                  <p class="text-muted mb-0">Notifications</p>
                </div>
              </div>
            </div>
            <div class="col-md-3 mb-3">
              <div class="card text-center">
                <div class="card-body">
                  <i class="bi bi-clock-history fs-1 text-info"></i>
                  <h3 class="mt-2">{{ stats.pending }}</h3>
                  <p class="text-muted mb-0">Pending Tasks</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Recent Activity -->
          <div v-if="!loading" class="card">
            <div class="card-header">
              <h5 class="mb-0">Recent Activity</h5>
            </div>
            <div class="card-body">
              <div v-if="error" class="alert alert-warning alert-dismissible fade show" role="alert">
                <i class="bi bi-exclamation-triangle me-2"></i>
                {{ error }}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
              </div>
              <p class="text-muted">No recent activity to display.</p>
              <p class="small">
                <i class="bi bi-info-circle me-1"></i>
                Your applications, documents, and notifications will appear here.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import api from '@/services/api'

const router = useRouter()
const authStore = useAuthStore()
const { success, error: errorToast } = useToast()

const userName = computed(() => authStore.userName)
const loading = ref(true)
const error = ref(null)

// Dashboard stats from API
const stats = ref({
  applications: 0,
  documents: 0,
  notifications: 0,
  pending: 0,
})

async function fetchDashboardStats() {
  try {
    loading.value = true
    error.value = null
    
    const response = await api.get('/api/accounts/dashboard/stats/')
    stats.value = response.data
    
    console.log('Dashboard stats loaded:', response.data)
  } catch (err) {
    console.error('Failed to load dashboard stats:', err)
    error.value = 'Failed to load dashboard statistics'
    errorToast('Unable to load dashboard statistics')
    // Don't block UI on stats error - show 0s
  } finally {
    loading.value = false
  }
}

async function handleLogout() {
  await authStore.logout()
  success('You have been logged out successfully')
  router.push('/login')
}

onMounted(async () => {
  console.log('Dashboard mounted. User:', authStore.user)
  await fetchDashboardStats()
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
