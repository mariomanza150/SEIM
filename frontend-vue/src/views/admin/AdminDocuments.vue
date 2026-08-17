<template>
  <div class="admin-documents-page">
    <PageHeader :title="t('adminDocuments.title')" :subtitle="t('adminDocuments.subtitle')">
      <template #breadcrumb>
        <nav aria-label="Breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item">
              <router-link :to="{ name: 'Dashboard' }">{{ t('route.names.Dashboard') }}</router-link>
            </li>
            <li class="breadcrumb-item active">{{ t('route.names.AdminDocuments') }}</li>
          </ol>
        </nav>
      </template>

      <template #actions>
        <button type="button" class="btn btn-outline-secondary" :disabled="loading" @click="fetchTypes">
          <i class="bi bi-arrow-clockwise me-1" aria-hidden="true"></i>{{ t('adminCommon.refresh') }}
        </button>
        <button type="button" class="btn btn-primary" data-testid="admin-documents-create" @click="openCreate">
          <i class="bi bi-plus-circle me-1" aria-hidden="true"></i>{{ t('adminDocuments.create') }}
        </button>
      </template>
    </PageHeader>

    <div class="card mb-3" data-testid="admin-documents-filters">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-6">
            <label class="form-label">{{ t('adminCommon.searchLabel') }}</label>
            <input
              v-model="filters.search"
              class="form-control"
              type="text"
              :placeholder="t('adminDocuments.searchPlaceholder')"
              @input="debouncedSearch"
            />
          </div>
          <div class="col-md-3">
            <label class="form-label">{{ t('adminDocuments.filterMode') }}</label>
            <select v-model="filters.submission_mode" class="form-select" @change="fetchTypes">
              <option value="">{{ t('adminCommon.filterAll') }}</option>
              <option v-for="opt in submissionModes" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>
          </div>
          <div class="col-md-3">
            <label class="form-label">{{ t('adminCommon.sortLabel') }}</label>
            <select v-model="filters.ordering" class="form-select" @change="fetchTypes">
              <option value="name">{{ t('adminDocuments.sortNameAsc') }}</option>
              <option value="-id">{{ t('adminDocuments.sortNewest') }}</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">{{ t('adminCommon.loading') }}</span>
      </div>
      <p class="mt-3 text-muted">{{ t('adminDocuments.loadingList') }}</p>
    </div>

    <div v-else-if="error" class="alert alert-danger" role="alert">
      <i class="bi bi-exclamation-triangle me-2" aria-hidden="true"></i>
      {{ error }}
    </div>

    <div v-else class="card">
      <div class="card-header bg-transparent d-flex justify-content-between align-items-center flex-wrap gap-2">
        <div class="text-muted small">{{ types.length }}</div>
        <button type="button" class="btn btn-sm btn-outline-secondary" :disabled="loading" @click="resetFilters">
          <i class="bi bi-x-circle me-1" aria-hidden="true"></i>{{ t('adminCommon.resetFilters') }}
        </button>
      </div>
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0" data-testid="admin-documents-table">
          <thead>
            <tr>
              <th scope="col">{{ t('adminDocuments.columns.name') }}</th>
              <th scope="col" class="text-nowrap">{{ t('adminDocuments.columns.mode') }}</th>
              <th scope="col" class="text-nowrap">{{ t('adminDocuments.columns.constraints') }}</th>
              <th scope="col" class="text-nowrap">{{ t('adminDocuments.columns.programs') }}</th>
              <th scope="col" class="text-end">{{ t('adminCommon.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!types.length">
              <td colspan="5" class="text-muted text-center py-4">{{ t('adminDocuments.empty') }}</td>
            </tr>
            <tr v-for="dt in types" :key="dt.id">
              <td class="min-w-0">
                <div class="fw-medium text-truncate">{{ dt.name }}</div>
                <div class="text-muted small text-truncate">{{ dt.slug || dt.description }}</div>
              </td>
              <td class="text-nowrap">
                <span class="badge bg-secondary">{{ modeLabel(dt.submission_mode) }}</span>
                <span v-if="dt.has_template" class="badge bg-info text-dark ms-1">
                  {{ t('adminDocuments.templateBadge') }}
                </span>
              </td>
              <td class="text-nowrap small">
                <span v-if="dt.accepted_extensions">{{ dt.accepted_extensions }}</span>
                <span v-else class="text-muted">{{ t('adminDocuments.defaultTypes') }}</span>
                <span class="text-muted"> · {{ dt.max_file_size_mb || 10 }} MB</span>
              </td>
              <td class="text-nowrap small">{{ dt.requirement_count ?? 0 }}</td>
              <td class="text-end text-nowrap">
                <router-link
                  class="btn btn-sm btn-outline-primary"
                  :to="{ name: 'AdminDocumentTypeEdit', params: { id: String(dt.id) } }"
                  data-testid="admin-documents-open-editor"
                >
                  <i class="bi bi-pencil-square me-1" aria-hidden="true"></i>{{ t('adminDocuments.openEditor') }}
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="create.open" class="modal-backdrop show"></div>
    <div v-if="create.open" class="modal d-block" tabindex="-1" role="dialog" aria-modal="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ t('adminDocuments.create') }}</h5>
            <button type="button" class="btn-close" :aria-label="t('adminCommon.close')" @click="closeCreate" />
          </div>
          <div class="modal-body">
            <div v-if="create.error" class="alert alert-danger" role="alert">{{ create.error }}</div>
            <div class="mb-3">
              <label class="form-label">{{ t('adminDocuments.fields.name') }}</label>
              <input v-model="create.form.name" class="form-control" type="text" data-testid="admin-documents-create-name" />
            </div>
            <div class="mb-3">
              <label class="form-label">{{ t('adminDocuments.fields.description') }}</label>
              <textarea v-model="create.form.description" class="form-control" rows="3" />
            </div>
            <div class="mb-0">
              <label class="form-label">{{ t('adminDocuments.fields.submissionMode') }}</label>
              <select v-model="create.form.submission_mode" class="form-select">
                <option v-for="opt in submissionModes" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
              </select>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-outline-secondary" @click="closeCreate">
              {{ t('adminCommon.cancel') }}
            </button>
            <button
              type="button"
              class="btn btn-primary"
              :disabled="create.saving"
              data-testid="admin-documents-create-save"
              @click="createType"
            >
              <span v-if="create.saving" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true" />
              {{ t('adminCommon.save') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import api from '@/services/api'
import { useToast } from '@/composables/useToast'
import PageHeader from '@/components/PageHeader.vue'

const { t } = useI18n()
const { success, error: errorToast } = useToast()
const router = useRouter()

const loading = ref(true)
const error = ref(null)
const types = ref([])

const filters = ref({
  search: '',
  submission_mode: '',
  ordering: 'name',
})

const submissionModes = computed(() => [
  { value: 'upload', label: t('adminDocuments.modes.upload') },
  { value: 'template_download', label: t('adminDocuments.modes.template_download') },
  { value: 'system_generated', label: t('adminDocuments.modes.system_generated') },
  { value: 'instructions_only', label: t('adminDocuments.modes.instructions_only') },
])

function modeLabel(value) {
  const hit = submissionModes.value.find((opt) => opt.value === value)
  return hit ? hit.label : value || '—'
}

let searchTimeout = null
function debouncedSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => fetchTypes(), 400)
}

function resetFilters() {
  filters.value = { search: '', submission_mode: '', ordering: 'name' }
  fetchTypes()
}

const create = ref({
  open: false,
  saving: false,
  error: null,
  form: { name: '', description: '', submission_mode: 'upload' },
})

function normalizeApiList(data) {
  if (data && typeof data === 'object' && Array.isArray(data.results)) return data.results
  return Array.isArray(data) ? data : []
}

async function fetchTypes() {
  try {
    loading.value = true
    error.value = null
    const params = { ordering: filters.value.ordering }
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.submission_mode) params.submission_mode = filters.value.submission_mode
    const res = await api.get('/api/document-types/', { params })
    types.value = normalizeApiList(res.data)
  } catch (err) {
    console.error('Failed to fetch document types:', err)
    error.value = t('adminDocuments.loadError')
  } finally {
    loading.value = false
  }
}

function openCreate() {
  create.value = {
    open: true,
    saving: false,
    error: null,
    form: { name: '', description: '', submission_mode: 'upload' },
  }
}

function closeCreate() {
  create.value.open = false
}

async function createType() {
  create.value.error = null
  create.value.saving = true
  try {
    const res = await api.post('/api/document-types/', create.value.form)
    success(t('adminDocuments.toastCreated'))
    closeCreate()
    await router.push({ name: 'AdminDocumentTypeEdit', params: { id: String(res.data.id) } })
  } catch (err) {
    console.error('Failed to create document type:', err)
    const detail = err.response?.data?.detail || err.response?.data?.name
    create.value.error = Array.isArray(detail) ? detail[0] : (detail || t('adminDocuments.createError'))
    errorToast(t('adminDocuments.createToastError'))
  } finally {
    create.value.saving = false
  }
}

onMounted(() => {
  fetchTypes()
})
</script>

<style scoped>
.admin-documents-page {
  min-height: 60vh;
}
</style>
