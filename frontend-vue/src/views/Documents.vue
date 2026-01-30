<template>
  <div class="documents-page">
    <div class="container-fluid mt-4">
      <!-- Header -->
      <div class="row mb-4">
        <div class="col-md-8">
          <h2><i class="bi bi-folder me-2"></i>My Documents</h2>
          <p class="text-muted">Manage your uploaded documents for applications</p>
        </div>
      </div>

      <!-- Filters -->
      <div class="card mb-4">
        <div class="card-body">
          <div class="row g-3">
            <div class="col-md-4">
              <label class="form-label">Application</label>
              <select v-model="filters.application" class="form-select" @change="fetchDocuments">
                <option value="">All Applications</option>
                <option v-for="app in applications" :key="app.id" :value="app.id">
                  {{ app.program?.name || app.id }}
                </option>
              </select>
            </div>
            <div class="col-md-3">
              <label class="form-label">Document Type</label>
              <select v-model="filters.type" class="form-select" @change="fetchDocuments">
                <option value="">All Types</option>
                <option v-for="dt in documentTypes" :key="dt.id" :value="dt.id">
                  {{ dt.name }}
                </option>
              </select>
            </div>
            <div class="col-md-3">
              <label class="form-label">Status</label>
              <select v-model="filters.valid" class="form-select" @change="fetchDocuments">
                <option value="">All</option>
                <option value="true">Validated</option>
                <option value="false">Pending</option>
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
        <p class="mt-3 text-muted">Loading documents...</p>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="alert alert-danger">
        <i class="bi bi-exclamation-triangle me-2"></i>
        {{ error }}
      </div>

      <!-- Documents List -->
      <div v-else-if="documents.length > 0">
        <div class="table-responsive">
          <table class="table table-hover align-middle">
            <thead class="table-light">
              <tr>
                <th>Document</th>
                <th>Type</th>
                <th>Application</th>
                <th>Status</th>
                <th>Uploaded</th>
                <th class="text-end">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="doc in documents" :key="doc.id">
                <td>
                  <i class="bi bi-file-earmark me-2 text-primary"></i>
                  <span class="fw-medium">{{ fileName(doc.file) }}</span>
                </td>
                <td>
                  <span class="badge bg-secondary">{{ doc.type?.name || doc.type }}</span>
                </td>
                <td>
                  <router-link :to="`/applications/${doc.application}`" class="text-decoration-none">
                    {{ getApplicationName(doc.application) }}
                  </router-link>
                </td>
                <td>
                  <span class="badge" :class="doc.is_valid ? 'bg-success' : 'bg-warning'">
                    {{ doc.is_valid ? 'Validated' : 'Pending' }}
                  </span>
                </td>
                <td class="text-muted small">{{ formatDate(doc.created_at) }}</td>
                <td class="text-end">
                  <router-link
                    :to="`/documents/${doc.id}`"
                    class="btn btn-sm btn-outline-primary me-1"
                  >
                    <i class="bi bi-eye"></i>
                  </router-link>
                  <a
                    v-if="doc.file"
                    :href="resolveFileUrl(doc.file)"
                    target="_blank"
                    rel="noopener"
                    class="btn btn-sm btn-outline-secondary"
                    title="Download"
                  >
                    <i class="bi bi-download"></i>
                  </a>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <nav v-if="pagination.count > pagination.pageSize" aria-label="Documents pagination">
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
          <i class="bi bi-folder-x display-1 text-muted"></i>
          <h4 class="mt-3">No Documents Yet</h4>
          <p class="text-muted">Upload documents from your application detail page.</p>
          <router-link to="/applications" class="btn btn-primary mt-3">
            <i class="bi bi-file-earmark-text me-2"></i>Go to Applications
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import { resolveFileUrl } from '@/utils/apiUrl'
import api from '@/services/api'

const { error: errorToast } = useToast()

const documents = ref([])
const applications = ref([])
const documentTypes = ref([])
const loading = ref(true)
const error = ref(null)

const filters = ref({
  application: '',
  type: '',
  valid: '',
})

const pagination = ref({
  count: 0,
  next: null,
  previous: null,
  currentPage: 1,
  pageSize: 10,
})

const totalPages = computed(() => Math.ceil(pagination.value.count / pagination.value.pageSize))

async function fetchApplications() {
  try {
    const response = await api.get('/api/applications/', { params: { page_size: 100 } })
    applications.value = response.data.results || response.data
  } catch (err) {
    console.warn('Failed to fetch applications:', err)
  }
}

async function fetchDocumentTypes() {
  try {
    const response = await api.get('/api/document-types/')
    documentTypes.value = response.data.results || response.data
  } catch (err) {
    console.warn('Failed to fetch document types:', err)
  }
}

async function fetchDocuments(page = 1) {
  try {
    loading.value = true
    error.value = null

    const params = { page }
    if (filters.value.application) params.application = filters.value.application
    if (filters.value.type) params.type = filters.value.type
    if (filters.value.valid !== '') params.is_valid = filters.value.valid

    const response = await api.get('/api/documents/', { params })
    documents.value = response.data.results || response.data

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
    console.error('Failed to fetch documents:', err)
    error.value = 'Failed to load documents. Please try again.'
    errorToast('Failed to load documents')
  } finally {
    loading.value = false
  }
}

function goToPage(page) {
  if (page >= 1 && page <= totalPages.value) {
    fetchDocuments(page)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

function clearFilters() {
  filters.value = { application: '', type: '', valid: '' }
  fetchDocuments()
}

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

function formatDate(dateString) {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

onMounted(async () => {
  await Promise.all([fetchApplications(), fetchDocumentTypes()])
  await fetchDocuments()
})
</script>

<style scoped>
.documents-page {
  min-height: 100vh;
  background-color: #f8f9fa;
}

.table {
  background: white;
  border-radius: 0.5rem;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}
</style>
