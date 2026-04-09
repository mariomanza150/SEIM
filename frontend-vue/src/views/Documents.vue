<template>
  <div class="documents-page" data-testid="documents-page">
    <div class="container-fluid mt-4">
      <!-- Breadcrumb -->
      <nav :aria-label="t('documentsPage.breadcrumbAria')">
        <ol class="breadcrumb">
          <li class="breadcrumb-item">
            <router-link :to="{ name: 'Dashboard' }">{{ t('route.names.Dashboard') }}</router-link>
          </li>
          <li class="breadcrumb-item active">{{ t('route.names.Documents') }}</li>
        </ol>
      </nav>
      <!-- Header -->
      <div class="row mb-4">
        <div class="col-md-8">
          <h2 data-testid="documents-heading"><i class="bi bi-folder me-2"></i>{{ t('route.names.Documents') }}</h2>
          <p class="text-muted">
            {{ isStaff ? t('documentsPage.subtitleStaff') : t('documentsPage.subtitleStudent') }}
          </p>
        </div>
      </div>

      <!-- Filters -->
      <div class="card mb-4">
        <div class="card-body">
          <div class="row g-3">
            <div class="col-md-4">
              <label class="form-label">{{ t('documentsPage.applicationLabel') }}</label>
              <select v-model="filters.application" class="form-select" @change="fetchDocuments">
                <option value="">{{ t('documentsPage.applicationOptionAll') }}</option>
                <option v-for="app in applications" :key="app.id" :value="app.id">
                  {{ app.program?.name || app.id }}
                </option>
              </select>
            </div>
            <div class="col-md-3">
              <label class="form-label">{{ t('documentsPage.documentTypeLabel') }}</label>
              <select v-model="filters.type" class="form-select" @change="fetchDocuments">
                <option value="">{{ t('documentsPage.typeOptionAll') }}</option>
                <option v-for="dt in documentTypes" :key="dt.id" :value="dt.id">
                  {{ dt.name }}
                </option>
              </select>
            </div>
            <div class="col-md-3">
              <label class="form-label">{{ t('documentsPage.statusLabel') }}</label>
              <select v-model="filters.valid" class="form-select" @change="fetchDocuments">
                <option value="">{{ t('documentsPage.statusOptionAll') }}</option>
                <option value="true">{{ t('documentsPage.statusValidated') }}</option>
                <option value="false">{{ t('documentsPage.statusPending') }}</option>
              </select>
            </div>
            <div class="col-md-2 d-flex align-items-end">
              <button type="button" class="btn btn-outline-secondary w-100" @click="clearFilters">
                <i class="bi bi-x-circle me-1"></i>{{ t('documentsPage.clearFilters') }}
              </button>
            </div>
            <div v-if="isStaff" class="col-12 border-top pt-3 mt-2">
              <div class="d-flex flex-wrap align-items-end gap-2 mb-2">
                <div class="flex-grow-1" style="min-width: 200px">
                  <label class="form-label small text-muted mb-1">{{ t('documentsPage.presetSaveLabel') }}</label>
                  <div class="input-group input-group-sm">
                    <input v-model="newPresetName" type="text" class="form-control" :placeholder="t('documentsPage.presetNamePlaceholder')" />
                    <button
                      type="button"
                      class="btn btn-outline-primary"
                      :disabled="!newPresetName.trim() || presetsLoading"
                      @click="savePreset(() => serializeDocumentListFilters(filters))"
                    >
                      {{ t('documentsPage.presetSave') }}
                    </button>
                  </div>
                </div>
                <div class="form-check mb-1">
                  <input id="doc-preset-def" v-model="saveAsDefault" class="form-check-input" type="checkbox" />
                  <label class="form-check-label small" for="doc-preset-def">{{ t('documentsPage.presetDefaultCheckbox') }}</label>
                </div>
              </div>
              <div v-if="savedPresets.length" class="small">
                <span class="text-muted me-2">{{ t('documentsPage.presetSavedPrefix') }}</span>
                <span
                  v-for="p in savedPresets"
                  :key="p.id"
                  class="d-inline-flex align-items-center gap-1 me-3 mb-1"
                >
                  <button type="button" class="btn btn-link btn-sm p-0" @click="applyDocPreset(p)">{{ p.name }}</button>
                  <i
                    v-if="p.is_default"
                    class="bi bi-star-fill text-warning"
                    :title="t('documentsPage.presetDefaultTitle')"
                    :aria-label="t('documentsPage.presetDefaultAria')"
                  ></i>
                  <button
                    v-else
                    type="button"
                    class="btn btn-link btn-sm p-0 text-secondary"
                    :title="t('documentsPage.presetSetDefaultTitle')"
                    :aria-label="t('documentsPage.presetSetDefaultAria')"
                    @click="setDefaultPreset(p)"
                  >
                    <i class="bi bi-star"></i>
                  </button>
                  <button
                    type="button"
                    class="btn btn-link btn-sm p-0 text-danger"
                    :title="t('documentsPage.presetRemoveTitle')"
                    :aria-label="t('documentsPage.presetRemoveAria')"
                    @click="deletePreset(p)"
                  >
                    <i class="bi bi-trash"></i>
                  </button>
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">{{ t('documentsPage.loadingSpinner') }}</span>
        </div>
        <p class="mt-3 text-muted">{{ t('documentsPage.loadingList') }}</p>
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
                <th>{{ t('documentsPage.colDocument') }}</th>
                <th>{{ t('documentsPage.colType') }}</th>
                <th>{{ t('documentsPage.colApplication') }}</th>
                <th>{{ t('documentsPage.colStatus') }}</th>
                <th>{{ t('documentsPage.colUploaded') }}</th>
                <th class="text-end">{{ t('documentsPage.colActions') }}</th>
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
                  <router-link :to="{ name: 'ApplicationDetail', params: { id: doc.application } }" class="text-decoration-none">
                    {{ getApplicationName(doc.application) }}
                  </router-link>
                </td>
                <td>
                  <span class="badge" :class="doc.is_valid ? 'bg-success' : 'bg-warning'">
                    {{ doc.is_valid ? t('documentsPage.statusValidated') : t('documentsPage.statusPending') }}
                  </span>
                </td>
                <td class="text-muted small">{{ formatDate(doc.created_at) }}</td>
                <td class="text-end">
                  <router-link
                    :to="{ name: 'DocumentDetail', params: { id: doc.id } }"
                    class="btn btn-sm btn-outline-primary me-1"
                    data-testid="document-detail-link"
                    :aria-label="t('documentsPage.viewDetailAria')"
                  >
                    <i class="bi bi-eye" aria-hidden="true"></i>
                  </router-link>
                  <a
                    v-if="doc.file"
                    :href="resolveFileUrl(doc.file)"
                    target="_blank"
                    rel="noopener"
                    class="btn btn-sm btn-outline-secondary"
                    :title="t('documentsPage.downloadTitle')"
                    :aria-label="t('documentsPage.downloadTitle')"
                  >
                    <i class="bi bi-download" aria-hidden="true"></i>
                  </a>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <nav v-if="pagination.count > pagination.pageSize" :aria-label="t('documentsPage.paginationAria')">
          <ul class="pagination justify-content-center mt-4">
            <li class="page-item" :class="{ disabled: !pagination.previous }">
              <button type="button" class="page-link" @click="goToPage(pagination.currentPage - 1)">
                {{ t('documentsPage.previous') }}
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
                {{ t('documentsPage.next') }}
              </button>
            </li>
          </ul>
        </nav>
      </div>

      <!-- Empty State -->
      <div v-else class="card">
        <div class="card-body text-center py-5">
          <i class="bi bi-folder-x display-1 text-muted"></i>
          <h4 class="mt-3">{{ t('documentsPage.emptyTitle') }}</h4>
          <p class="text-muted">{{ t('documentsPage.emptyBody') }}</p>
          <router-link :to="{ name: 'Applications' }" class="btn btn-primary mt-3">
            <i class="bi bi-file-earmark-text me-2"></i>{{ t('documentsPage.goToApplications') }}
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
import { useStaffSavedPresets } from '@/composables/useStaffSavedPresets'
import { useAuthStore } from '@/stores/auth'
import { resolveFileUrl } from '@/utils/apiUrl'
import api from '@/services/api'
import {
  STAFF_SAVED_SEARCH_TYPE,
  deserializeDocumentListFilters,
  serializeDocumentListFilters,
} from '@/utils/staffListSearchPresets'

const { t, locale } = useI18n()
const { error: errorToast } = useToast()
const authStore = useAuthStore()
const isStaff = computed(() => authStore.canUseStaffReviewQueue)

const {
  savedPresets,
  newPresetName,
  saveAsDefault,
  presetsLoading,
  loadPresets,
  savePreset,
  deletePreset,
  setDefaultPreset,
} = useStaffSavedPresets(STAFF_SAVED_SEARCH_TYPE.APPLICATION_DOCUMENT)

const documents = ref([])
const applications = ref([])
const documentTypes = ref([])
const loading = ref(true)
const error = ref(null)

const filters = ref({
  application: '',
  type: '',
  valid: '',
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

async function fetchApplications() {
  try {
    const response = await api.get('/api/applications/', {
      params: { page_size: isStaff.value ? 200 : 100 },
    })
    applications.value = response.data.results || response.data
  } catch {
    applications.value = []
  }
}

async function fetchDocumentTypes() {
  try {
    const response = await api.get('/api/document-types/')
    documentTypes.value = response.data.results || response.data
  } catch {
    documentTypes.value = []
  }
}

async function fetchDocuments(page = 1) {
  try {
    loading.value = true
    error.value = null

    const params = { page, ordering: filters.value.ordering || '-created_at' }
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
  } catch {
    error.value = t('documentsPage.loadError')
    errorToast(t('documentsPage.loadToastError'))
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
  filters.value = { application: '', type: '', valid: '', ordering: '-created_at' }
  fetchDocuments()
}

function applyDocPreset(p) {
  filters.value = deserializeDocumentListFilters(p.filters)
  pagination.value.currentPage = 1
  fetchDocuments(1)
}

function fileName(fileUrl) {
  if (!fileUrl) return t('documentsPage.fileUnknown')
  const parts = fileUrl.split('/')
  return decodeURIComponent(parts[parts.length - 1] || 'document')
}

function getApplicationName(appId) {
  if (typeof appId === 'object' && appId?.program?.name) return appId.program.name
  const app = applications.value.find(a => a.id === appId)
  return app?.program?.name || appId || t('documentsPage.unknownApplication')
}

function formatDate(dateString) {
  if (!dateString) return t('documentsPage.notAvailable')
  const date = new Date(dateString)
  const localeTag = locale.value === 'es' ? 'es' : 'en-US'
  return date.toLocaleDateString(localeTag, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

onMounted(async () => {
  await Promise.all([fetchApplications(), fetchDocumentTypes()])
  if (isStaff.value) {
    await loadPresets()
    const def = savedPresets.value.find((p) => p.is_default)
    if (def) {
      filters.value = deserializeDocumentListFilters(def.filters)
    }
  }
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
