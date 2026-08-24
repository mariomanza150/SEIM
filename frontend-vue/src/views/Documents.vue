<template>
  <div class="documents-page" data-testid="documents-page">
    <PageHeader
      :title="t('route.names.Documents')"
      :subtitle="isStaff ? t('documentsPage.subtitleStaff') : t('documentsPage.subtitleStudent')"
      icon-class="bi bi-folder"
      test-id="documents-heading"
    >
      <template #breadcrumb>
        <PageBreadcrumb
          :aria-label="t('documentsPage.breadcrumbAria')"
          :items="[
            { to: { name: 'Dashboard' }, label: t('route.names.Dashboard') },
            { label: t('route.names.Documents') },
          ]"
        />
      </template>
    </PageHeader>

      <CompactFilterBar :clear-label="t('documentsPage.clearFilters')" @clear="clearFilters">
        <template #primary>
            <div class="col-md-4">
              <label class="form-label">{{ t('documentsPage.applicationLabel') }}</label>
              <select v-model="filters.application" class="form-select" @change="() => fetchDocuments(1)">
                <option value="">{{ t('documentsPage.applicationOptionAll') }}</option>
                <option v-for="app in applications" :key="app.id" :value="app.id">
                  {{ applicationFilterLabel(app) }}
                </option>
              </select>
            </div>
            <div class="col-md-3">
              <label class="form-label">{{ t('documentsPage.documentTypeLabel') }}</label>
              <select v-model="filters.type" class="form-select" @change="() => fetchDocuments(1)">
                <option value="">{{ t('documentsPage.typeOptionAll') }}</option>
                <option v-for="dt in documentTypes" :key="dt.id" :value="dt.id">
                  {{ documentTypeLabel(dt, dt.name) }}
                </option>
              </select>
            </div>
            <div class="col-md-3">
              <label class="form-label">{{ t('documentsPage.statusLabel') }}</label>
              <select v-model="filters.valid" class="form-select" @change="() => fetchDocuments(1)">
                <option value="">{{ t('documentsPage.statusOptionAll') }}</option>
                <option value="true">{{ t('documentDetailPage.statusValidatedShort') }}</option>
                <option value="false">{{ t('documentDetailPage.statusPendingShort') }}</option>
              </select>
            </div>
        </template>
        <template v-if="isStaff" #advanced>
            <div class="d-flex flex-wrap gap-2">
              <button
                type="button"
                class="btn btn-sm"
                :class="filters.pending_review ? 'btn-warning' : 'btn-outline-warning'"
                data-testid="filter-pending-review"
                @click="togglePendingReview"
              >
                <i class="bi bi-hourglass-split me-1" aria-hidden="true"></i>{{ t('documentsPage.filterPendingReview') }}
              </button>
              <button
                type="button"
                class="btn btn-sm"
                :class="filters.overdue ? 'btn-danger' : 'btn-outline-danger'"
                data-testid="filter-overdue"
                @click="toggleOverdue"
              >
                <i class="bi bi-exclamation-triangle me-1" aria-hidden="true"></i>{{ t('documentsPage.filterOverdue') }}
              </button>
            </div>
        </template>
        <template v-if="isStaff" #presets>
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
        </template>
      </CompactFilterBar>

      <PageStateShell
        :loading="loading"
        :error="error"
        :empty="!documents.length"
        :empty-title="t('documentsPage.emptyTitle')"
        :empty-body="t('documentsPage.emptyBody')"
        empty-icon-class="bi bi-folder-x"
        skeleton="table"
        :loading-label="t('documentsPage.loadingSpinner')"
        :loading-hint="t('documentsPage.loadingList')"
        :skeleton-columns="6"
      >
      <ResponsiveList :items="documents" item-key="id" mobile-test-id="documents-mobile">
      <div v-if="documents.length > 0">
        <div class="table-responsive">
          <table class="table table-hover align-middle">
            <thead class="seim-table-head">
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
                  <span class="badge bg-secondary">{{
                    documentTypeLabel(doc.type, t('documentDetailPage.notAvailable'))
                  }}</span>
                </td>
                <td>
                  <router-link
                    :to="{ name: 'ApplicationDetail', params: { id: documentApplicationId(doc.application) } }"
                    class="text-decoration-none"
                  >
                    {{
                      documentApplicationProgramName(
                        doc.application,
                        applications,
                        t('documentDetailPage.unknownApplication'),
                      )
                    }}
                  </router-link>
                </td>
                <td>
                  <span class="badge" :class="doc.is_valid ? 'bg-success' : 'bg-warning'">
                    {{ doc.is_valid ? t('documentDetailPage.statusValidatedShort') : t('documentDetailPage.statusPendingShort') }}
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
                    rel="noopener noreferrer"
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
        <Pagination
          :count="pagination.count"
          :page-size="pagination.pageSize"
          :current-page="pagination.currentPage"
          :can-go-previous="!!pagination.previous"
          :can-go-next="!!pagination.next"
          :aria-label="t('documentsPage.paginationAria')"
          ul-class="mt-4"
          @page-change="goToPage"
        />
      </div>
      </ResponsiveList>

        <template #emptyActions>
          <router-link :to="{ name: 'Applications' }" class="btn btn-primary">
            <i class="bi bi-file-earmark-text me-2" aria-hidden="true"></i>{{ t('documentsPage.goToApplications') }}
          </router-link>
        </template>
      </PageStateShell>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onActivated } from 'vue'
import { useI18n } from 'vue-i18n'
import { useToast } from '@/composables/useToast'
import { useStaffSavedPresets } from '@/composables/useStaffSavedPresets'
import { useAuthStore } from '@/stores/auth'
import { resolveFileUrl } from '@/utils/apiUrl'
import api from '@/services/api'
import PageHeader from '@/components/PageHeader.vue'
import PageBreadcrumb from '@/components/PageBreadcrumb.vue'
import CompactFilterBar from '@/components/CompactFilterBar.vue'
import Pagination from '@/components/Pagination.vue'
import PageStateShell from '@/components/State/PageStateShell.vue'
import ResponsiveList from '@/components/ResponsiveList.vue'
import {
  applicationSelectLabel,
  documentApplicationId,
  documentApplicationProgramName,
  documentTypeLabel,
} from '@/utils/documentApi'
import { formatApplicationStatus } from '@/utils/formatters'
import {
  STAFF_SAVED_SEARCH_TYPE,
  deserializeDocumentListFilters,
  serializeDocumentListFilters,
} from '@/utils/staffListSearchPresets'
import { resolveListPage } from '@/utils/listPage'

defineOptions({ name: 'Documents' })

const { t, te, locale } = useI18n()

function applicationFilterLabel(app) {
  const formatStatus = (status) => formatApplicationStatus({ status, t, te })
  return applicationSelectLabel(app, '', applications.value, formatStatus)
}
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
  pending_review: false,
  overdue: false,
  ordering: '-created_at',
})

const pagination = ref({
  count: 0,
  next: null,
  previous: null,
  currentPage: 1,
  pageSize: 10,
})

async function fetchApplications() {
  try {
    const response = await api.get('/api/applications/', {
      params: { page_size: 100 },
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
  const pageNumber = resolveListPage(page)
  try {
    loading.value = true
    error.value = null

    const params = { page: pageNumber, ordering: filters.value.ordering || '-created_at' }
    if (filters.value.application) params.application = filters.value.application
    if (filters.value.type) params.type = filters.value.type
    if (filters.value.valid !== '') params.is_valid = filters.value.valid
    if (filters.value.pending_review) params.pending_review = true
    if (filters.value.overdue) params.overdue = true

    const response = await api.get('/api/documents/', { params })
    documents.value = response.data.results || response.data

    if (response.data.count !== undefined) {
      pagination.value = {
        count: response.data.count,
        next: response.data.next,
        previous: response.data.previous,
        currentPage: pageNumber,
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
  fetchDocuments(page)
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function clearFilters() {
  filters.value = {
    application: '',
    type: '',
    valid: '',
    pending_review: false,
    overdue: false,
    ordering: '-created_at',
  }
  fetchDocuments()
}

function togglePendingReview() {
  filters.value.pending_review = !filters.value.pending_review
  if (filters.value.pending_review) filters.value.valid = 'false'
  fetchDocuments(1)
}

function toggleOverdue() {
  filters.value.overdue = !filters.value.overdue
  fetchDocuments(1)
}

function applyDocPreset(p) {
  filters.value = deserializeDocumentListFilters(p.filters)
  pagination.value.currentPage = 1
  fetchDocuments(1)
}

function fileName(fileUrl) {
  if (!fileUrl) return t('documentDetailPage.fileUnknown')
  const parts = fileUrl.split('/')
  return decodeURIComponent(parts[parts.length - 1] || 'document')
}

function formatDate(dateString) {
  if (!dateString) return t('documentDetailPage.notAvailable')
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

onActivated(() => {
  fetchDocuments(pagination.value.currentPage)
})
</script>

<style scoped>
.documents-page {
  min-height: 100vh;
  background-color: var(--seim-app-bg);
}

.table {
  background: var(--seim-surface-bg);
  border-radius: 0.5rem;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}
</style>
