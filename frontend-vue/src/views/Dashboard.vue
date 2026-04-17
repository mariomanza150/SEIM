<template>
  <div class="dashboard" data-testid="dashboard-page">
    <PageHeader :title="t('dashboard.welcomeUser', { name: userName })" :subtitle="t('dashboard.tagline')" />

    <!-- Stats Cards -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">{{ t('dashboard.loadingSpinner') }}</span>
      </div>
      <p class="mt-3 text-muted">{{ t('dashboard.loadingDashboard') }}</p>
    </div>

    <div v-else class="row mb-4">
      <div class="col-md-3 mb-3">
        <router-link :to="{ name: 'Applications' }" class="text-decoration-none">
          <div class="card text-center card-hover">
            <div class="card-body">
              <i class="bi bi-file-earmark-text fs-1 text-primary"></i>
              <h3 class="mt-2">{{ stats.applications }}</h3>
              <p class="text-muted mb-0">{{ t('route.names.Applications') }}</p>
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
              <p class="text-muted mb-0">{{ t('route.names.Documents') }}</p>
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
              <p class="text-muted mb-0">{{ t('route.names.Notifications') }}</p>
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
              <p class="text-muted mb-0">{{ t('dashboard.statPending') }}</p>
            </div>
          </div>
        </component>
      </div>
    </div>

    <!-- Next steps -->
    <div v-if="!loading" class="card">
      <div class="card-header d-flex justify-content-between align-items-center flex-wrap gap-2">
        <h5 class="mb-0">{{ t('dashboard.nextStepsTitle') }}</h5>
        <span v-if="nextStepsLoading" class="text-muted small">
          <span class="spinner-border spinner-border-sm me-1" role="status" />
          {{ t('dashboard.nextStepsUpdating') }}
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
                {{ t('dashboard.open') }}
              </router-link>
              <a
                v-else-if="row.href"
                :href="row.href"
                class="btn btn-sm btn-outline-primary"
              >
                {{ t('dashboard.open') }}
              </a>
              <router-link v-else :to="{ name: 'Notifications' }" class="btn btn-sm btn-outline-secondary">
                {{ t('dashboard.view') }}
              </router-link>
            </div>
          </li>
        </ul>
        <p v-else-if="!nextStepsLoading" class="text-muted mb-0">
          {{ t('dashboard.allCaughtUp') }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import api from '@/services/api'
import { fetchDashboardNextSteps } from '@/utils/dashboardNextSteps'
import PageHeader from '@/components/PageHeader.vue'

const { t } = useI18n()
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
      error.value = t('dashboard.statsLoadError')
      errorToast(t('dashboard.statsToastError'))
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
      t,
    })
  } catch {
    nextStepsError.value = t('dashboard.nextStepsLoadError')
  } finally {
    nextStepsLoading.value = false
  }
}

// Logout + nav/theme toggles live in AppShell

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
  background-color: var(--seim-app-bg);
}

.card {
  border: none;
  border-radius: 0.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}
</style>
