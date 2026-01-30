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
            <a href="#" class="list-group-item list-group-item-action active">
              <i class="bi bi-house-door me-2"></i>Dashboard
            </a>
            <a href="#" class="list-group-item list-group-item-action">
              <i class="bi bi-file-earmark-text me-2"></i>Applications
            </a>
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
          <div class="row mb-4">
            <div class="col-md-3 mb-3">
              <div class="card text-center">
                <div class="card-body">
                  <i class="bi bi-file-earmark-text fs-1 text-primary"></i>
                  <h3 class="mt-2">{{ stats.applications }}</h3>
                  <p class="text-muted mb-0">Applications</p>
                </div>
              </div>
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
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0">Recent Activity</h5>
            </div>
            <div class="card-body">
              <div v-if="loading" class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
              </div>
              <div v-else-if="error" class="alert alert-danger">
                {{ error }}
              </div>
              <div v-else>
                <p class="text-muted">No recent activity to display.</p>
                <p class="small">
                  This is a placeholder. Once the API is connected, real data will appear here.
                </p>
              </div>
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

const router = useRouter()
const authStore = useAuthStore()

const userName = computed(() => authStore.userName)
const loading = ref(false)
const error = ref(null)

// Mock stats - replace with real API calls
const stats = ref({
  applications: 0,
  documents: 0,
  notifications: 0,
  pending: 0,
})

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}

onMounted(async () => {
  // TODO: Fetch dashboard data from API
  console.log('Dashboard mounted. User:', authStore.user)
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
