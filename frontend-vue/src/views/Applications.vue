<template>
  <div class="applications-page">
    <!-- Header -->
    <div class="container-fluid mt-4">
      <!-- Breadcrumb -->
      <nav :aria-label="t('applicationsPage.breadcrumbAria')">
        <ol class="breadcrumb">
          <li class="breadcrumb-item">
            <router-link :to="{ name: 'Dashboard' }">{{ t('route.names.Dashboard') }}</router-link>
          </li>
          <li class="breadcrumb-item active">{{ t('route.names.Applications') }}</li>
        </ol>
      </nav>
      <div class="row mb-4">
        <div class="col-md-8">
          <h2><i class="bi bi-file-earmark-text me-2"></i>{{ t('applicationsPage.title') }}</h2>
          <p class="text-muted">{{ t('applicationsPage.tagline') }}</p>
        </div>
        <div class="col-md-4 text-end d-flex flex-wrap gap-2 justify-content-md-end">
          <router-link :to="{ name: 'ProgramCompare' }" class="btn btn-outline-secondary">
            <i class="bi bi-columns-gap me-1"></i>{{ t('applicationsPage.comparePrograms') }}
          </router-link>
          <router-link :to="{ name: 'ApplicationNew' }" class="btn btn-primary">
            <i class="bi bi-plus-circle me-2"></i>{{ t('applicationsPage.newApplication') }}
          </router-link>
        </div>
      </div>

      <!-- Filters -->
      <div class="card mb-4" data-testid="applications-filters">
        <div class="card-body">
          <div class="row g-3">
            <div class="col-md-4">
              <label class="form-label">{{ t('applicationsPage.searchLabel') }}</label>
              <input
                v-model="filters.search"
                type="text"
                class="form-control"
                :placeholder="t('applicationsPage.searchPlaceholder')"
                @input="debouncedSearch"
                data-testid="applications-search"
              />
            </div>
            <div class="col-md-3">
              <label class="form-label">{{ t('applicationsPage.statusLabel') }}</label>
              <select v-model="filters.status" class="form-select" @change="fetchApplications" data-testid="applications-filter-status">
                <option value="">{{ t('applicationsPage.statusOptionAll') }}</option>
                <option value="draft">{{ t('applicationsPage.status.draft') }}</option>
                <option value="submitted">{{ t('applicationsPage.status.submitted') }}</option>
                <option value="under_review">{{ t('applicationsPage.status.under_review') }}</option>
                <option value="approved">{{ t('applicationsPage.status.approved') }}</option>
                <option value="rejected">{{ t('applicationsPage.status.rejected') }}</option>
                <option value="completed">{{ t('applicationsPage.status.completed') }}</option>
              </select>
            </div>
            <div class="col-md-3">
              <label class="form-label">{{ t('applicationsPage.sortLabel') }}</label>
              <select v-model="filters.ordering" class="form-select" @change="fetchApplications" data-testid="applications-filter-ordering">
                <option value="-created_at">{{ t('applicationsPage.sortNewest') }}</option>
                <option value="created_at">{{ t('applicationsPage.sortOldest') }}</option>
                <option value="-submitted_at">{{ t('applicationsPage.sortRecentlySubmitted') }}</option>
              </select>
            </div>
            <div class="col-md-2 d-flex align-items-end">
              <button class="btn btn-outline-secondary w-100" @click="clearFilters">
                <i class="bi bi-x-circle me-1"></i>{{ t('applicationsPage.clearFilters') }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">{{ t('applicationsPage.loadingSpinner') }}</span>
        </div>
        <p class="mt-3 text-muted">{{ t('applicationsPage.loadingList') }}</p>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="alert alert-danger">
        <i class="bi bi-exclamation-triangle me-2"></i>
        {{ error }}
      </div>

      <!-- Applications List -->
      <div v-else-if="applications.length > 0">
        <div class="row">
          <div v-for="application in applications" :key="application.id" class="col-md-6 mb-4">
            <div class="card application-card h-100">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-start mb-3">
                  <h5 class="card-title mb-0">{{ application.program?.name || t('applicationsPage.unknownProgram') }}</h5>
                  <span class="badge" :class="statusClass(application.status)">
                    {{ formatStatus(application.status) }}
                  </span>
                </div>

                <div
                  v-if="application.readiness && application.status === 'draft'"
                  class="mb-3"
                  data-testid="application-readiness-summary"
                >
                  <div class="d-flex align-items-center gap-2 flex-wrap">
                    <span class="small text-muted">{{ t('applicationsPage.readinessLabel') }}</span>
                    <span class="badge" :class="readinessLevelBadgeClass(application.readiness.level)">
                      {{ application.readiness.score }}%
                    </span>
                  </div>
                  <p class="small text-muted mb-0 mt-1">{{ application.readiness.headline }}</p>
                </div>

                <p class="card-text text-muted small mb-3">
                  <i class="bi bi-building me-1"></i>
                  {{ application.program?.institution || t('applicationsPage.notAvailable') }}
                </p>

                <div class="row small text-muted mb-3">
                  <div class="col-6">
                    <i class="bi bi-calendar me-1"></i>
                    {{ t('applicationsPage.created') }}: {{ formatDate(application.created_at) }}
                  </div>
                  <div v-if="application.submitted_at" class="col-6">
                    <i class="bi bi-send me-1"></i>
                    {{ t('applicationsPage.submitted') }}: {{ formatDate(application.submitted_at) }}
                  </div>
                </div>

                <div class="d-flex justify-content-between align-items-center">
                  <router-link
                    :to="{ name: 'ApplicationDetail', params: { id: application.id } }"
                    class="btn btn-sm btn-outline-primary"
                    data-testid="application-detail-link"
                  >
                    <i class="bi bi-eye me-1"></i>{{ t('applicationsPage.viewDetails') }}
                  </router-link>
                  
                  <div>
                    <router-link
                      v-if="application.status === 'draft'"
                      :to="{ name: 'ApplicationEdit', params: { id: application.id } }"
                      class="btn btn-sm btn-outline-secondary me-2"
                      :aria-label="t('applicationsPage.editAria')"
                    >
                      <i class="bi bi-pencil" aria-hidden="true"></i>
                    </router-link>
                    <button
                      v-if="application.status === 'draft'"
                      type="button"
                      class="btn btn-sm btn-outline-danger"
                      :aria-label="t('applicationsPage.deleteAria')"
                      @click="confirmDelete(application)"
                    >
                      <i class="bi bi-trash" aria-hidden="true"></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <nav v-if="pagination.count > pagination.pageSize" :aria-label="t('applicationsPage.paginationAria')">
          <ul class="pagination justify-content-center">
            <li class="page-item" :class="{ disabled: !pagination.previous }">
              <button type="button" class="page-link" @click="goToPage(pagination.currentPage - 1)">
                {{ t('applicationsPage.previous') }}
              </button>
            </li>
            <li
              v-for="page in totalPages"
              :key="page"
              class="page-item"
              :class="{ active: page === pagination.currentPage }"
            >
              <button type="button" class="page-link" @click="goToPage(page)">{{ page }}</button>
            </li>
            <li class="page-item" :class="{ disabled: !pagination.next }">
              <button type="button" class="page-link" @click="goToPage(pagination.currentPage + 1)">
                {{ t('applicationsPage.next') }}
              </button>
            </li>
          </ul>
        </nav>
      </div>

      <!-- Empty State -->
      <div v-else class="card">
        <div class="card-body text-center py-5">
          <i class="bi bi-inbox display-1 text-muted"></i>
          <h4 class="mt-3">{{ t('applicationsPage.emptyTitle') }}</h4>
          <p class="text-muted">{{ t('applicationsPage.emptyBody') }}</p>
          <router-link :to="{ name: 'ApplicationNew' }" class="btn btn-primary mt-3">
            <i class="bi bi-plus-circle me-2"></i>{{ t('applicationsPage.createApplication') }}
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useToast } from '@/composables/useToast'
import api from '@/services/api'
import { readinessLevelBadgeClass } from '@/utils/applicationReadiness'

const { t, te, locale } = useI18n()
const { success, error: errorToast } = useToast()

const applications = ref([])
const loading = ref(true)
const error = ref(null)

const filters = ref({
  search: '',
  status: '',
  ordering: '-created_at',
})

const pagination = ref({
  count: 0,
  next: null,
  previous: null,
  currentPage: 1,
  pageSize: 10,
})

const totalPages = computed(() => Math.ceil(pagination.value.count / pagination.value.pageSize))

let searchTimeout = null
function debouncedSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    fetchApplications()
  }, 500)
}

async function fetchApplications(page = 1) {
  try {
    loading.value = true
    error.value = null

    const params = {
      page,
      ordering: filters.value.ordering,
    }

    if (filters.value.search) {
      params.search = filters.value.search
    }
    if (filters.value.status) {
      params.status = filters.value.status
    }

    const response = await api.get('/api/applications/', { params })
    
    applications.value = response.data.results || response.data
    
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
    console.error('Failed to fetch applications:', err)
    error.value = t('applicationsPage.loadError')
    errorToast(t('applicationsPage.loadToastError'))
  } finally {
    loading.value = false
  }
}

function goToPage(page) {
  if (page >= 1 && page <= totalPages.value) {
    fetchApplications(page)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

function clearFilters() {
  filters.value = {
    search: '',
    status: '',
    ordering: '-created_at',
  }
  fetchApplications()
}

function statusClass(status) {
  const classes = {
    draft: 'bg-secondary',
    submitted: 'bg-info',
    under_review: 'bg-warning',
    approved: 'bg-success',
    rejected: 'bg-danger',
    completed: 'bg-primary',
  }
  return classes[status] || 'bg-secondary'
}

function formatStatus(status) {
  if (!status) return t('applicationsPage.status.unknown')
  const key = `applicationsPage.status.${status}`
  if (te(key)) return t(key)
  return String(status).replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())
}

function formatDate(dateString) {
  if (!dateString) return t('applicationsPage.notAvailable')
  const date = new Date(dateString)
  const localeTag = locale.value === 'es' ? 'es' : 'en-US'
  return date.toLocaleDateString(localeTag, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

async function confirmDelete(application) {
  const name = application.program?.name || t('applicationsPage.unknownProgram')
  if (confirm(t('applicationsPage.deleteConfirm', { name }))) {
    await deleteApplication(application.id)
  }
}

async function deleteApplication(id) {
  try {
    await api.delete(`/api/applications/${id}/`)
    success(t('applicationsPage.deletedToast'))
    fetchApplications(pagination.value.currentPage)
  } catch (err) {
    console.error('Failed to delete application:', err)
    errorToast(t('applicationsPage.deleteToastError'))
  }
}

onMounted(() => {
  fetchApplications()
})
</script>

<style scoped>
.applications-page {
  min-height: 100vh;
  background-color: #f8f9fa;
}

.application-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  border: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.application-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.badge {
  font-size: 0.75rem;
  padding: 0.35rem 0.65rem;
}
</style>
