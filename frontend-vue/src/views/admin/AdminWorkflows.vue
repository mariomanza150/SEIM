<template>
  <div class="admin-workflows-page">
    <PageHeader :title="t('adminWorkflows.title')" :subtitle="t('adminWorkflows.subtitle')">
      <template #breadcrumb>
        <nav aria-label="Breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item">
              <router-link :to="{ name: 'Dashboard' }">{{ t('route.names.Dashboard') }}</router-link>
            </li>
            <li class="breadcrumb-item active">{{ t('route.names.AdminWorkflows') }}</li>
          </ol>
        </nav>
      </template>

      <template #actions>
        <button type="button" class="btn btn-outline-secondary" :disabled="loading" @click="fetchWorkflows">
          <i class="bi bi-arrow-clockwise me-1" aria-hidden="true"></i>{{ t('adminCommon.refresh') }}
        </button>
        <button type="button" class="btn btn-primary" @click="openCreate">
          <i class="bi bi-plus-circle me-1" aria-hidden="true"></i>{{ t('adminWorkflows.create') }}
        </button>
      </template>
    </PageHeader>

    <div class="card mb-3" data-testid="admin-workflows-filters">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-6">
            <label class="form-label">{{ t('adminCommon.searchLabel') }}</label>
            <input
              v-model="filters.search"
              class="form-control"
              type="text"
              :placeholder="t('adminWorkflows.searchPlaceholder')"
              @input="debouncedSearch"
            />
          </div>
          <div class="col-md-3">
            <label class="form-label">{{ t('adminWorkflows.filterActive') }}</label>
            <select v-model="filters.is_active" class="form-select" @change="fetchWorkflows">
              <option value="">{{ t('adminCommon.filterAll') }}</option>
              <option value="true">{{ t('adminCommon.yes') }}</option>
              <option value="false">{{ t('adminCommon.no') }}</option>
            </select>
          </div>
          <div class="col-md-3">
            <label class="form-label">{{ t('adminCommon.sortLabel') }}</label>
            <select v-model="filters.ordering" class="form-select" @change="fetchWorkflows">
              <option value="name">{{ t('adminWorkflows.sortNameAsc') }}</option>
              <option value="-created_at">{{ t('adminWorkflows.sortNewest') }}</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">{{ t('adminCommon.loading') }}</span>
      </div>
      <p class="mt-3 text-muted">{{ t('adminWorkflows.loadingList') }}</p>
    </div>

    <div v-else-if="error" class="alert alert-danger" role="alert">
      <i class="bi bi-exclamation-triangle me-2" aria-hidden="true"></i>
      {{ error }}
    </div>

    <div v-else class="card">
      <div class="card-header bg-transparent d-flex justify-content-between align-items-center flex-wrap gap-2">
        <div class="text-muted small">
          {{ workflows.length }}
        </div>
        <button type="button" class="btn btn-sm btn-outline-secondary" @click="resetFilters" :disabled="loading">
          <i class="bi bi-x-circle me-1" aria-hidden="true"></i>{{ t('adminCommon.resetFilters') }}
        </button>
      </div>
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0" data-testid="admin-workflows-table">
          <thead>
            <tr>
              <th scope="col">{{ t('adminWorkflows.columns.name') }}</th>
              <th scope="col" class="text-nowrap">{{ t('adminWorkflows.columns.active') }}</th>
              <th scope="col" class="text-nowrap">{{ t('adminWorkflows.columns.latestPublished') }}</th>
              <th scope="col" class="text-end">{{ t('adminCommon.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!workflows.length">
              <td colspan="4" class="text-muted text-center py-4">
                {{ t('adminWorkflows.empty') }}
              </td>
            </tr>
            <tr v-for="wf in workflows" :key="wf.id">
              <td class="min-w-0">
                <div class="fw-medium text-truncate">{{ wf.name }}</div>
                <div class="text-muted small text-truncate">{{ wf.description }}</div>
              </td>
              <td class="text-nowrap">
                <span class="badge" :class="wf.is_active ? 'bg-success' : 'bg-secondary'">
                  {{ wf.is_active ? t('adminCommon.yes') : t('adminCommon.no') }}
                </span>
              </td>
              <td class="text-nowrap small">
                <span v-if="wf.latest_published_version">
                  v{{ wf.latest_published_version.version }}
                </span>
                <span v-else class="text-muted">—</span>
              </td>
              <td class="text-end text-nowrap">
                <router-link
                  class="btn btn-sm btn-outline-primary"
                  :to="{ name: 'AdminWorkflowEditor', params: { id: wf.id } }"
                >
                  <i class="bi bi-pencil-square me-1" aria-hidden="true"></i>{{ t('adminWorkflows.openEditor') }}
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create -->
    <div v-if="create.open" class="modal-backdrop show"></div>
    <div v-if="create.open" class="modal d-block" tabindex="-1" role="dialog" aria-modal="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ t('adminWorkflows.create') }}</h5>
            <button type="button" class="btn-close" :aria-label="t('adminCommon.close')" @click="closeCreate" />
          </div>
          <div class="modal-body">
            <div v-if="create.error" class="alert alert-danger" role="alert">
              {{ create.error }}
            </div>
            <div class="mb-3">
              <label class="form-label">{{ t('adminWorkflows.fields.name') }}</label>
              <input v-model="create.form.name" class="form-control" type="text" />
            </div>
            <div class="mb-3">
              <label class="form-label">{{ t('adminWorkflows.fields.description') }}</label>
              <textarea v-model="create.form.description" class="form-control" rows="3" />
            </div>
            <div class="form-check">
              <input id="wfActive" v-model="create.form.is_active" class="form-check-input" type="checkbox" />
              <label class="form-check-label" for="wfActive">{{ t('adminWorkflows.fields.activeHelp') }}</label>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-outline-secondary" @click="closeCreate">
              {{ t('adminCommon.cancel') }}
            </button>
            <button type="button" class="btn btn-primary" :disabled="create.saving" @click="createWorkflow">
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
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useToast } from '@/composables/useToast'
import PageHeader from '@/components/PageHeader.vue'

const { t } = useI18n()
const { success, error: errorToast } = useToast()

const loading = ref(true)
const error = ref(null)
const workflows = ref([])

const filters = ref({
  search: '',
  is_active: '',
  ordering: 'name',
})

let searchTimeout = null
function debouncedSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => fetchWorkflows(), 400)
}

function resetFilters() {
  filters.value = { search: '', is_active: '', ordering: 'name' }
  fetchWorkflows()
}

const create = ref({
  open: false,
  saving: false,
  error: null,
  form: { name: '', description: '', is_active: true },
})

function normalizeApiList(data) {
  if (data && typeof data === 'object' && Array.isArray(data.results)) return data.results
  return Array.isArray(data) ? data : []
}

async function fetchWorkflows() {
  try {
    loading.value = true
    error.value = null
    const params = { ordering: filters.value.ordering }
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.is_active) params.is_active = filters.value.is_active
    const res = await api.get('/api/workflows/', { params })
    workflows.value = normalizeApiList(res.data)
  } catch (err) {
    console.error('Failed to fetch workflows:', err)
    error.value = t('adminWorkflows.loadError')
  } finally {
    loading.value = false
  }
}

function openCreate() {
  create.value = {
    open: true,
    saving: false,
    error: null,
    form: { name: '', description: '', is_active: true },
  }
}

function closeCreate() {
  create.value.open = false
}

async function createWorkflow() {
  create.value.error = null
  create.value.saving = true
  try {
    const res = await api.post('/api/workflows/', create.value.form)
    success(t('adminWorkflows.toastCreated'))
    closeCreate()
    await fetchWorkflows()
    // Optionally jump to editor
    // router.push({ name: 'AdminWorkflowEditor', params: { id: res.data.id } })
  } catch (err) {
    console.error('Failed to create workflow:', err)
    const detail = err.response?.data?.detail
    create.value.error = typeof detail === 'string' ? detail : t('adminWorkflows.createError')
    errorToast(t('adminWorkflows.createToastError'))
  } finally {
    create.value.saving = false
  }
}

onMounted(() => {
  fetchWorkflows()
})
</script>

<style scoped>
.admin-workflows-page {
  min-height: 60vh;
}
</style>

