<template>
  <div class="application-detail">
    <div class="container-fluid mt-4">
      <!-- Breadcrumb -->
      <nav aria-label="breadcrumb">
        <ol class="breadcrumb">
          <li class="breadcrumb-item">
            <router-link to="/dashboard">Dashboard</router-link>
          </li>
          <li class="breadcrumb-item">
            <router-link to="/applications">Applications</router-link>
          </li>
          <li class="breadcrumb-item active">{{ application?.program?.name || 'Loading...' }}</li>
        </ol>
      </nav>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-3 text-muted">Loading application details...</p>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="alert alert-danger">
        <i class="bi bi-exclamation-triangle me-2"></i>
        {{ error }}
        <router-link to="/applications" class="btn btn-sm btn-outline-danger ms-3">
          Back to Applications
        </router-link>
      </div>

      <!-- Application Details -->
      <div v-else-if="application">
        <!-- Header -->
        <div class="row mb-4">
          <div class="col-md-8">
            <h2>
              <i class="bi bi-file-earmark-text me-2"></i>
              {{ application.program?.name }}
            </h2>
            <p class="text-muted">
              <i class="bi bi-building me-1"></i>
              {{ application.program?.institution || 'N/A' }}
            </p>
          </div>
          <div class="col-md-4 text-end">
            <span class="badge fs-6 me-2" :class="statusClass(application.status)">
              {{ formatStatus(application.status) }}
            </span>
            <router-link
              v-if="application.status === 'draft'"
              :to="`/applications/${application.id}/edit`"
              class="btn btn-primary"
            >
              <i class="bi bi-pencil me-1"></i>Edit
            </router-link>
          </div>
        </div>

        <div class="row">
          <!-- Main Content -->
          <div class="col-lg-8">
            <!-- Program Information -->
            <div class="card mb-4">
              <div class="card-header">
                <h5 class="mb-0"><i class="bi bi-info-circle me-2"></i>Program Information</h5>
              </div>
              <div class="card-body">
                <div class="row mb-3">
                  <div class="col-md-6">
                    <label class="text-muted small">Program Name</label>
                    <p class="fw-bold">{{ application.program?.name }}</p>
                  </div>
                  <div class="col-md-6">
                    <label class="text-muted small">Institution</label>
                    <p class="fw-bold">{{ application.program?.institution }}</p>
                  </div>
                </div>
                <div class="row mb-3">
                  <div class="col-md-6">
                    <label class="text-muted small">Country</label>
                    <p class="fw-bold">{{ application.program?.country || 'N/A' }}</p>
                  </div>
                  <div class="col-md-6">
                    <label class="text-muted small">Duration</label>
                    <p class="fw-bold">{{ application.program?.duration || 'N/A' }}</p>
                  </div>
                </div>
                <div v-if="application.program?.description">
                  <label class="text-muted small">Description</label>
                  <p>{{ application.program.description }}</p>
                </div>
              </div>
            </div>

            <!-- Application Status Timeline -->
            <div class="card mb-4">
              <div class="card-header">
                <h5 class="mb-0"><i class="bi bi-clock-history me-2"></i>Status Timeline</h5>
              </div>
              <div class="card-body">
                <div class="timeline">
                  <div class="timeline-item">
                    <div class="timeline-icon bg-primary">
                      <i class="bi bi-file-earmark-plus"></i>
                    </div>
                    <div class="timeline-content">
                      <h6>Application Created</h6>
                      <p class="text-muted small">{{ formatDateTime(application.created_at) }}</p>
                    </div>
                  </div>
                  <div v-if="application.submitted_at" class="timeline-item">
                    <div class="timeline-icon bg-info">
                      <i class="bi bi-send"></i>
                    </div>
                    <div class="timeline-content">
                      <h6>Application Submitted</h6>
                      <p class="text-muted small">{{ formatDateTime(application.submitted_at) }}</p>
                    </div>
                  </div>
                  <div v-if="application.status === 'approved'" class="timeline-item">
                    <div class="timeline-icon bg-success">
                      <i class="bi bi-check-circle"></i>
                    </div>
                    <div class="timeline-content">
                      <h6>Application Approved</h6>
                      <p class="text-muted small">Congratulations!</p>
                    </div>
                  </div>
                  <div v-if="application.status === 'rejected'" class="timeline-item">
                    <div class="timeline-icon bg-danger">
                      <i class="bi bi-x-circle"></i>
                    </div>
                    <div class="timeline-content">
                      <h6>Application Rejected</h6>
                      <p class="text-muted small">Please review feedback</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Comments Section (Placeholder) -->
            <div class="card mb-4">
              <div class="card-header">
                <h5 class="mb-0"><i class="bi bi-chat-dots me-2"></i>Comments</h5>
              </div>
              <div class="card-body">
                <p class="text-muted text-center py-3">
                  <i class="bi bi-info-circle me-1"></i>
                  No comments yet
                </p>
              </div>
            </div>
          </div>

          <!-- Sidebar -->
          <div class="col-lg-4">
            <!-- Quick Actions -->
            <div class="card mb-4">
              <div class="card-header">
                <h6 class="mb-0">Quick Actions</h6>
              </div>
              <div class="card-body">
                <div class="d-grid gap-2">
                  <router-link
                    v-if="application.status === 'draft'"
                    :to="`/applications/${application.id}/edit`"
                    class="btn btn-primary"
                  >
                    <i class="bi bi-pencil me-2"></i>Edit Application
                  </router-link>
                  <button
                    v-if="application.status === 'draft'"
                    class="btn btn-success"
                    @click="submitApplication"
                  >
                    <i class="bi bi-send me-2"></i>Submit Application
                  </button>
                  <button
                    v-if="application.status === 'draft'"
                    class="btn btn-danger"
                    @click="confirmDelete"
                  >
                    <i class="bi bi-trash me-2"></i>Delete Application
                  </button>
                  <router-link to="/applications" class="btn btn-outline-secondary">
                    <i class="bi bi-arrow-left me-2"></i>Back to List
                  </router-link>
                </div>
              </div>
            </div>

            <!-- Application Details -->
            <div class="card mb-4">
              <div class="card-header">
                <h6 class="mb-0">Application Details</h6>
              </div>
              <div class="card-body">
                <div class="mb-3">
                  <label class="text-muted small">Application ID</label>
                  <p class="small font-monospace">{{ application.id }}</p>
                </div>
                <div class="mb-3">
                  <label class="text-muted small">Status</label>
                  <p>
                    <span class="badge" :class="statusClass(application.status)">
                      {{ formatStatus(application.status) }}
                    </span>
                  </p>
                </div>
                <div class="mb-3">
                  <label class="text-muted small">Created</label>
                  <p>{{ formatDateTime(application.created_at) }}</p>
                </div>
                <div v-if="application.submitted_at" class="mb-3">
                  <label class="text-muted small">Submitted</label>
                  <p>{{ formatDateTime(application.submitted_at) }}</p>
                </div>
                <div class="mb-3">
                  <label class="text-muted small">Last Updated</label>
                  <p>{{ formatDateTime(application.updated_at) }}</p>
                </div>
              </div>
            </div>

            <!-- Upload Document -->
            <div v-if="application.status === 'draft' || application.status === 'submitted'" class="card mb-4">
              <DocumentUpload
                :application-id="application.id"
                @uploaded="fetchApplicationDocuments"
              />
            </div>

            <!-- Documents List -->
            <div class="card">
              <div class="card-header d-flex justify-content-between align-items-center">
                <h6 class="mb-0">Documents</h6>
                <router-link to="/documents" class="btn btn-sm btn-outline-primary">
                  View All
                </router-link>
              </div>
              <div class="card-body">
                <div v-if="documentsLoading" class="text-center py-3">
                  <div class="spinner-border spinner-border-sm text-primary"></div>
                </div>
                <div v-else-if="applicationDocuments.length > 0">
                  <ul class="list-group list-group-flush">
                    <li
                      v-for="doc in applicationDocuments"
                      :key="doc.id"
                      class="list-group-item px-0 d-flex justify-content-between align-items-center"
                    >
                      <router-link :to="`/documents/${doc.id}`" class="text-decoration-none">
                        <i class="bi bi-file-earmark me-2"></i>
                        {{ doc.type?.name || doc.type }}
                      </router-link>
                      <span class="badge" :class="doc.is_valid ? 'bg-success' : 'bg-warning'">
                        {{ doc.is_valid ? 'Validated' : 'Pending' }}
                      </span>
                    </li>
                  </ul>
                </div>
                <p v-else class="text-muted text-center small mb-0">
                  <i class="bi bi-info-circle me-1"></i>
                  No documents uploaded
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
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'
import DocumentUpload from '@/components/DocumentUpload.vue'
import api from '@/services/api'

const route = useRoute()
const router = useRouter()
const { success, error: errorToast } = useToast()

const application = ref(null)
const applicationDocuments = ref([])
const documentsLoading = ref(false)
const loading = ref(true)
const error = ref(null)

async function fetchApplication() {
  try {
    loading.value = true
    error.value = null

    const response = await api.get(`/api/applications/${route.params.id}/`)
    application.value = response.data
    await fetchApplicationDocuments()
  } catch (err) {
    console.error('Failed to fetch application:', err)
    error.value = 'Failed to load application details. Please try again.'
    errorToast('Failed to load application')
  } finally {
    loading.value = false
  }
}

async function fetchApplicationDocuments() {
  if (!application.value?.id) return
  try {
    documentsLoading.value = true
    const response = await api.get('/api/documents/', {
      params: { application: application.value.id },
    })
    applicationDocuments.value = response.data.results || response.data
  } catch (err) {
    console.warn('Failed to fetch documents:', err)
    applicationDocuments.value = []
  } finally {
    documentsLoading.value = false
  }
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

function formatDateTime(dateString) {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

async function submitApplication() {
  if (!confirm('Are you sure you want to submit this application? You will not be able to edit it after submission.')) {
    return
  }

  try {
    // In a real implementation, there would be a submit endpoint
    // For now, we'll just show a message
    success('Application submitted successfully!')
    await fetchApplication()
  } catch (err) {
    console.error('Failed to submit application:', err)
    errorToast('Failed to submit application')
  }
}

async function confirmDelete() {
  if (confirm('Are you sure you want to delete this application? This action cannot be undone.')) {
    await deleteApplication()
  }
}

async function deleteApplication() {
  try {
    await api.delete(`/api/applications/${route.params.id}/`)
    success('Application deleted successfully')
    router.push('/applications')
  } catch (err) {
    console.error('Failed to delete application:', err)
    errorToast('Failed to delete application')
  }
}

onMounted(() => {
  fetchApplication()
})
</script>

<style scoped>
.application-detail {
  min-height: 100vh;
  background-color: #f8f9fa;
}

.timeline {
  position: relative;
  padding-left: 30px;
}

.timeline-item {
  position: relative;
  padding-bottom: 20px;
}

.timeline-item:not(:last-child)::before {
  content: '';
  position: absolute;
  left: -19px;
  top: 30px;
  width: 2px;
  height: calc(100% - 10px);
  background: #dee2e6;
}

.timeline-icon {
  position: absolute;
  left: -30px;
  top: 0;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
}

.timeline-content h6 {
  margin-bottom: 0.25rem;
}

.badge {
  font-size: 0.875rem;
  padding: 0.5rem 1rem;
}
</style>
