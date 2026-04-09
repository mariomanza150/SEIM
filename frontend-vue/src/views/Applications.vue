<template>
  <div class="applications-page">
    <!-- Header -->
    <div class="container-fluid mt-4">
      <!-- Breadcrumb -->
      <nav aria-label="breadcrumb">
        <ol class="breadcrumb">
          <li class="breadcrumb-item">
            <router-link :to="{ name: 'Dashboard' }">Dashboard</router-link>
          </li>
          <li class="breadcrumb-item active">Applications</li>
        </ol>
      </nav>
      <div class="row mb-4">
        <div class="col-md-8">
          <h2><i class="bi bi-file-earmark-text me-2"></i>My Applications</h2>
          <p class="text-muted">Manage your exchange program applications</p>
        </div>
        <div class="col-md-4 text-end">
          <router-link :to="{ name: 'ApplicationNew' }" class="btn btn-primary">
            <i class="bi bi-plus-circle me-2"></i>New Application
          </router-link>
        </div>
      </div>

      <!-- Filters -->
      <div class="card mb-4" data-testid="applications-filters">
        <div class="card-body">
          <div class="row g-3">
            <div class="col-md-4">
              <label class="form-label">Search</label>
              <input
                v-model="filters.search"
                type="text"
                class="form-control"
                placeholder="Search programs..."
                @input="debouncedSearch"
                data-testid="applications-search"
              />
            </div>
            <div class="col-md-3">
              <label class="form-label">Status</label>
              <select v-model="filters.status" class="form-select" @change="fetchApplications" data-testid="applications-filter-status">
                <option value="">All Statuses</option>
                <option value="draft">Draft</option>
                <option value="submitted">Submitted</option>
                <option value="under_review">Under Review</option>
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
                <option value="completed">Completed</option>
              </select>
            </div>
            <div class="col-md-3">
              <label class="form-label">Sort By</label>
              <select v-model="filters.ordering" class="form-select" @change="fetchApplications" data-testid="applications-filter-ordering">
                <option value="-created_at">Newest First</option>
                <option value="created_at">Oldest First</option>
                <option value="-submitted_at">Recently Submitted</option>
              </select>
            </div>
            <div class="col-md-2 d-flex align-items-end">
              <button class="btn btn-outline-secondary w-100" @click="clearFilters">
                <i class="bi bi-x-circle me-1"></i>Clear
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
        <p class="mt-3 text-muted">Loading applications...</p>
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
                  <h5 class="card-title mb-0">{{ application.program?.name || 'Unknown Program' }}</h5>
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
                    <span class="small text-muted">Readiness</span>
                    <span class="badge" :class="readinessLevelBadgeClass(application.readiness.level)">
                      {{ application.readiness.score }}%
                    </span>
                  </div>
                  <p class="small text-muted mb-0 mt-1">{{ application.readiness.headline }}</p>
                </div>

                <p class="card-text text-muted small mb-3">
                  <i class="bi bi-building me-1"></i>
                  {{ application.program?.institution || 'N/A' }}
                </p>

                <div class="row small text-muted mb-3">
                  <div class="col-6">
                    <i class="bi bi-calendar me-1"></i>
                    Created: {{ formatDate(application.created_at) }}
                  </div>
                  <div v-if="application.submitted_at" class="col-6">
                    <i class="bi bi-send me-1"></i>
                    Submitted: {{ formatDate(application.submitted_at) }}
                  </div>
                </div>

                <div class="d-flex justify-content-between align-items-center">
                  <router-link
                    :to="{ name: 'ApplicationDetail', params: { id: application.id } }"
                    class="btn btn-sm btn-outline-primary"
                    data-testid="application-detail-link"
                  >
                    <i class="bi bi-eye me-1"></i>View Details
                  </router-link>
                  
                  <div>
                    <router-link
                      v-if="application.status === 'draft'"
                      :to="{ name: 'ApplicationEdit', params: { id: application.id } }"
                      class="btn btn-sm btn-outline-secondary me-2"
                    >
                      <i class="bi bi-pencil"></i>
                    </router-link>
                    <button
                      v-if="application.status === 'draft'"
                      class="btn btn-sm btn-outline-danger"
                      @click="confirmDelete(application)"
                    >
                      <i class="bi bi-trash"></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <nav v-if="pagination.count > pagination.pageSize" aria-label="Applications pagination">
          <ul class="pagination justify-content-center">
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
          <i class="bi bi-inbox display-1 text-muted"></i>
          <h4 class="mt-3">No Applications Yet</h4>
          <p class="text-muted">Start your exchange journey by creating your first application!</p>
          <router-link :to="{ name: 'ApplicationNew' }" class="btn btn-primary mt-3">
            <i class="bi bi-plus-circle me-2"></i>Create Application
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'
import api from '@/services/api'
import { readinessLevelBadgeClass } from '@/utils/applicationReadiness'

const router = useRouter()
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
    error.value = 'Failed to load applications. Please try again.'
    errorToast('Failed to load applications')
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
  return status ? status.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase()) : 'Unknown'
}

function formatDate(dateString) {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

async function confirmDelete(application) {
  if (confirm(`Are you sure you want to delete this application for "${application.program?.name}"?`)) {
    await deleteApplication(application.id)
  }
}

async function deleteApplication(id) {
  try {
    await api.delete(`/api/applications/${id}/`)
    success('Application deleted successfully')
    fetchApplications(pagination.value.currentPage)
  } catch (err) {
    console.error('Failed to delete application:', err)
    errorToast('Failed to delete application')
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
