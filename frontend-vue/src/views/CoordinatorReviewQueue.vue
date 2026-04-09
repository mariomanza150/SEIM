<template>
  <div class="review-queue-page">
    <div class="container-fluid mt-4">
      <nav aria-label="breadcrumb">
        <ol class="breadcrumb">
          <li class="breadcrumb-item">
            <router-link :to="{ name: 'Dashboard' }">Dashboard</router-link>
          </li>
          <li class="breadcrumb-item active">Review queue</li>
        </ol>
      </nav>

      <div class="row mb-4">
        <div class="col-md-8">
          <h2><i class="bi bi-clipboard-check me-2"></i>Application review queue</h2>
          <p class="text-muted">Filter applications that need coordinator attention</p>
        </div>
        <div class="col-md-4 text-end d-flex align-items-start justify-content-end gap-2">
          <router-link :to="{ name: 'Applications' }" class="btn btn-outline-secondary">
            <i class="bi bi-person-lines-fill me-1"></i>My applications
          </router-link>
        </div>
      </div>

      <div class="card mb-4" data-testid="review-queue-filters">
        <div class="card-body">
          <div class="row g-3 align-items-end">
            <div class="col-md-4">
              <label class="form-label">Search</label>
              <input
                v-model="filters.search"
                type="text"
                class="form-control"
                placeholder="Student, email, program, status…"
                @input="debouncedSearch"
                data-testid="review-queue-search"
              />
            </div>
            <div class="col-md-8">
              <label class="form-label d-block">Quick filters</label>
              <div class="d-flex flex-wrap gap-2">
                <div class="form-check form-check-inline">
                  <input
                    id="fq-pending"
                    v-model="filters.pending_review"
                    class="form-check-input"
                    type="checkbox"
                    @change="fetchApplications"
                  />
                  <label class="form-check-label" for="fq-pending">Pending review</label>
                </div>
                <div class="form-check form-check-inline">
                  <input
                    id="fq-resubmit"
                    v-model="filters.needs_document_resubmit"
                    class="form-check-input"
                    type="checkbox"
                    @change="fetchApplications"
                  />
                  <label class="form-check-label" for="fq-resubmit">Document resubmit</label>
                </div>
                <div class="form-check form-check-inline">
                  <input
                    id="fq-assigned"
                    v-model="filters.assigned_to_me"
                    class="form-check-input"
                    type="checkbox"
                    @change="fetchApplications"
                  />
                  <label class="form-check-label" for="fq-assigned">Assigned to me</label>
                </div>
              </div>
            </div>
            <div class="col-md-3">
              <label class="form-label">Status</label>
              <select v-model="filters.status" class="form-select" @change="fetchApplications">
                <option value="">All statuses</option>
                <option value="draft">Draft</option>
                <option value="submitted">Submitted</option>
                <option value="under_review">Under review</option>
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
                <option value="completed">Completed</option>
              </select>
            </div>
            <div class="col-md-3">
              <label class="form-label">Sort</label>
              <select v-model="filters.ordering" class="form-select" @change="fetchApplications">
                <option value="-submitted_at">Recently submitted</option>
                <option value="-created_at">Newest</option>
                <option value="created_at">Oldest</option>
              </select>
            </div>
            <div class="col-md-2">
              <button type="button" class="btn btn-outline-secondary w-100" @click="clearFilters">
                Clear
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading…</span>
        </div>
      </div>
      <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
      <div v-else-if="applications.length === 0" class="card">
        <div class="card-body text-center py-5 text-muted">No applications match these filters.</div>
      </div>
      <div v-else class="table-responsive card">
        <table class="table table-hover mb-0">
          <thead class="table-light">
            <tr>
              <th>Student</th>
              <th>Program</th>
              <th>Status</th>
              <th>Coordinator</th>
              <th>Submitted</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="app in applications" :key="app.id">
              <td>
                <div class="fw-medium">{{ app.student_display_name || '—' }}</div>
                <div class="small text-muted">{{ app.student_email }}</div>
              </td>
              <td>{{ app.program_name || app.program?.name || '—' }}</td>
              <td>
                <span class="badge" :class="statusClass(app.status)">{{ formatStatus(app.status) }}</span>
              </td>
              <td class="small">
                {{ app.assigned_coordinator_name || (app.effective_coordinator?.full_name) || '—' }}
              </td>
              <td class="small text-muted">{{ formatDate(app.submitted_at) }}</td>
              <td class="text-end">
                <router-link
                  :to="{ name: 'ApplicationDetail', params: { id: app.id } }"
                  class="btn btn-sm btn-outline-primary"
                  data-testid="review-queue-open-detail"
                >
                  Open
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <nav
        v-if="!loading && pagination.count > pagination.pageSize"
        class="mt-3"
        aria-label="Review queue pagination"
      >
        <ul class="pagination justify-content-center">
          <li class="page-item" :class="{ disabled: !pagination.previous }">
            <button type="button" class="page-link" @click="goToPage(pagination.currentPage - 1)">
              Previous
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
              Next
            </button>
          </li>
        </ul>
      </nav>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import api from '@/services/api'

const { error: errorToast } = useToast()

const applications = ref([])
const loading = ref(true)
const error = ref(null)

const filters = ref({
  search: '',
  status: '',
  ordering: '-submitted_at',
  pending_review: false,
  needs_document_resubmit: false,
  assigned_to_me: false,
})

const pagination = ref({
  count: 0,
  next: null,
  previous: null,
  currentPage: 1,
  pageSize: 20,
})

const totalPages = computed(() => Math.ceil(pagination.value.count / pagination.value.pageSize) || 1)

let searchTimeout = null
function debouncedSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => fetchApplications(), 400)
}

async function fetchApplications(page = 1) {
  try {
    loading.value = true
    error.value = null
    const params = {
      page,
      ordering: filters.value.ordering,
    }
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.status) params.status = filters.value.status
    if (filters.value.pending_review) params.pending_review = 'true'
    if (filters.value.needs_document_resubmit) params.needs_document_resubmit = 'true'
    if (filters.value.assigned_to_me) params.assigned_to_me = 'true'

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
    console.error(err)
    error.value = 'Failed to load applications.'
    errorToast(error.value)
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
    ordering: '-submitted_at',
    pending_review: false,
    needs_document_resubmit: false,
    assigned_to_me: false,
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
  return status ? status.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase()) : '—'
}

function formatDate(dateString) {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

onMounted(() => fetchApplications())
</script>

<style scoped>
.review-queue-page {
  min-height: 100vh;
  background-color: #f8f9fa;
}
</style>
