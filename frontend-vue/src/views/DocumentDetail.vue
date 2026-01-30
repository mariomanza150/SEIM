<template>
  <div class="document-detail">
    <div class="container-fluid mt-4">
      <!-- Breadcrumb -->
      <nav aria-label="breadcrumb">
        <ol class="breadcrumb">
          <li class="breadcrumb-item">
            <router-link to="/dashboard">Dashboard</router-link>
          </li>
          <li class="breadcrumb-item">
            <router-link to="/documents">Documents</router-link>
          </li>
          <li class="breadcrumb-item active">{{ document?.type?.name || 'Loading...' }}</li>
        </ol>
      </nav>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-3 text-muted">Loading document...</p>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="alert alert-danger">
        <i class="bi bi-exclamation-triangle me-2"></i>
        {{ error }}
        <router-link to="/documents" class="btn btn-sm btn-outline-danger ms-3">
          Back to Documents
        </router-link>
      </div>

      <!-- Document Details -->
      <div v-else-if="document">
        <div class="row">
          <div class="col-lg-8">
            <div class="card mb-4">
              <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0">
                  <i class="bi bi-file-earmark me-2"></i>
                  {{ fileName(document.file) }}
                </h5>
                <span class="badge fs-6" :class="document.is_valid ? 'bg-success' : 'bg-warning'">
                  {{ document.is_valid ? 'Validated' : 'Pending Validation' }}
                </span>
              </div>
              <div class="card-body">
                <div class="row mb-3">
                  <div class="col-md-6">
                    <label class="text-muted small">Document Type</label>
                    <p class="fw-bold">{{ document.type?.name || document.type }}</p>
                  </div>
                  <div class="col-md-6">
                    <label class="text-muted small">Application</label>
                    <p>
                      <router-link :to="`/applications/${document.application}`">
                        {{ getApplicationName(document.application) }}
                      </router-link>
                    </p>
                  </div>
                </div>
                <div class="row mb-3">
                  <div class="col-md-6">
                    <label class="text-muted small">Uploaded By</label>
                    <p class="fw-bold">{{ document.uploaded_by || 'N/A' }}</p>
                  </div>
                  <div class="col-md-6">
                    <label class="text-muted small">Uploaded At</label>
                    <p class="fw-bold">{{ formatDateTime(document.created_at) }}</p>
                  </div>
                </div>
                <div v-if="document.validated_at" class="row mb-3">
                  <div class="col-md-6">
                    <label class="text-muted small">Validated At</label>
                    <p class="fw-bold">{{ formatDateTime(document.validated_at) }}</p>
                  </div>
                </div>

                <!-- Download -->
                <div class="mt-4 pt-3 border-top">
                  <a
                    v-if="document.file"
                    :href="resolveFileUrl(document.file)"
                    target="_blank"
                    rel="noopener"
                    class="btn btn-primary"
                  >
                    <i class="bi bi-download me-2"></i>Download Document
                  </a>
                </div>
              </div>
            </div>
          </div>

          <div class="col-lg-4">
            <div class="card mb-4">
              <div class="card-header">
                <h6 class="mb-0">Quick Actions</h6>
              </div>
              <div class="card-body">
                <div class="d-grid gap-2">
                  <a
                    v-if="document.file"
                    :href="resolveFileUrl(document.file)"
                    target="_blank"
                    rel="noopener"
                    class="btn btn-outline-primary"
                  >
                    <i class="bi bi-download me-2"></i>Download
                  </a>
                  <router-link
                    :to="`/applications/${document.application}`"
                    class="btn btn-outline-secondary"
                  >
                    <i class="bi bi-file-earmark-text me-2"></i>View Application
                  </router-link>
                  <router-link to="/documents" class="btn btn-outline-secondary">
                    <i class="bi bi-arrow-left me-2"></i>Back to Documents
                  </router-link>
                </div>
              </div>
            </div>

            <div class="card">
              <div class="card-header">
                <h6 class="mb-0">Document Info</h6>
              </div>
              <div class="card-body">
                <div class="mb-3">
                  <label class="text-muted small">Document ID</label>
                  <p class="small font-monospace">{{ document.id }}</p>
                </div>
                <div class="mb-3">
                  <label class="text-muted small">Status</label>
                  <p>
                    <span class="badge" :class="document.is_valid ? 'bg-success' : 'bg-warning'">
                      {{ document.is_valid ? 'Validated' : 'Pending' }}
                    </span>
                  </p>
                </div>
                <div class="mb-3">
                  <label class="text-muted small">Last Updated</label>
                  <p>{{ formatDateTime(document.updated_at) }}</p>
                </div>
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
import { useRoute } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { resolveFileUrl } from '@/utils/apiUrl'
import api from '@/services/api'

const route = useRoute()
const { error: errorToast } = useToast()

const document = ref(null)
const applications = ref([])
const loading = ref(true)
const error = ref(null)

function fileName(fileUrl) {
  if (!fileUrl) return 'Unknown'
  const parts = fileUrl.split('/')
  return decodeURIComponent(parts[parts.length - 1] || 'document')
}

function getApplicationName(appId) {
  if (typeof appId === 'object' && appId?.program?.name) return appId.program.name
  const app = applications.value.find(a => a.id === appId)
  return app?.program?.name || appId || 'Unknown'
}

function formatDateTime(dateString) {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

async function fetchDocument() {
  try {
    loading.value = true
    error.value = null
    const response = await api.get(`/api/documents/${route.params.id}/`)
    document.value = response.data
  } catch (err) {
    console.error('Failed to fetch document:', err)
    error.value = 'Failed to load document. Please try again.'
    errorToast('Failed to load document')
  } finally {
    loading.value = false
  }
}

async function fetchApplications() {
  try {
    const response = await api.get('/api/applications/', { params: { page_size: 100 } })
    applications.value = response.data.results || response.data
  } catch (err) {
    console.warn('Failed to fetch applications:', err)
  }
}

onMounted(async () => {
  await fetchApplications()
  await fetchDocument()
})
</script>

<style scoped>
.document-detail {
  min-height: 100vh;
  background-color: #f8f9fa;
}

.card {
  border: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}
</style>
