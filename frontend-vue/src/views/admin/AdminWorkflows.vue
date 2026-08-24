<template>
  <div class="admin-workflows-page">
    <PageHeader :title="t('adminWorkflows.title')" :subtitle="t('adminWorkflows.subtitle')">
      <template #breadcrumb>
        <PageBreadcrumb
          :aria-label="t('adminCommon.breadcrumbAria')"
          :items="[
            { to: { name: 'Dashboard' }, label: t('route.names.Dashboard') },
            { label: t('route.names.AdminWorkflows') },
          ]"
        />
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

    <CompactFilterBar test-id="admin-workflows-filters" @clear="clearFilters">
      <template #primary>
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
      </template>
      <template #advanced>
        <div class="col-md-4">
          <label class="form-label">{{ t('adminCommon.sortLabel') }}</label>
          <select v-model="filters.ordering" class="form-select" @change="fetchWorkflows">
            <option value="name">{{ t('adminWorkflows.sortNameAsc') }}</option>
            <option value="-created_at">{{ t('adminWorkflows.sortNewest') }}</option>
          </select>
        </div>
      </template>
    </CompactFilterBar>

    <PageStateShell
      :loading="loading"
      :error="error || ''"
      :empty="!workflows.length"
      :empty-title="t('adminWorkflows.empty')"
      skeleton="table"
      :loading-label="t('adminWorkflows.loadingList')"
      :skeleton-columns="4"
    >
    <div class="card">
      <ResponsiveList :items="workflows" :columns="mobileColumns" mobile-test-id="admin-workflows-mobile">
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
                  data-testid="admin-workflows-open-editor"
                >
                  <i class="bi bi-pencil-square me-1" aria-hidden="true"></i>{{ t('adminWorkflows.openEditor') }}
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <template #col-name="{ item }">
        <div class="fw-medium">{{ item.name }}</div>
        <div v-if="item.description" class="text-muted small">{{ item.description }}</div>
      </template>
      <template #col-active="{ item }">
        <span class="badge" :class="item.is_active ? 'bg-success' : 'bg-secondary'">
          {{ item.is_active ? t('adminCommon.yes') : t('adminCommon.no') }}
        </span>
      </template>
      <template #col-latestPublished="{ item }">
        <span v-if="item.latest_published_version">v{{ item.latest_published_version.version }}</span>
        <span v-else class="text-muted">—</span>
      </template>
      <template #actions="{ item }">
        <router-link
          class="btn btn-sm btn-outline-primary"
          :to="{ name: 'AdminWorkflowEditor', params: { id: item.id } }"
          data-testid="admin-workflows-open-editor"
        >
          <i class="bi bi-pencil-square me-1" aria-hidden="true"></i>{{ t('adminWorkflows.openEditor') }}
        </router-link>
      </template>
      </ResponsiveList>
    </div>
    </PageStateShell>

    <FormModal
      :open="create.open"
      :title="t('adminWorkflows.create')"
      :error="create.error || ''"
      :saving="create.saving"
      size="md"
      @close="closeCreate"
      @submit="createWorkflow"
    >
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
    </FormModal>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useToast } from '@/composables/useToast'
import CompactFilterBar from '@/components/CompactFilterBar.vue'
import ResponsiveList from '@/components/ResponsiveList.vue'
import PageHeader from '@/components/PageHeader.vue'
import PageBreadcrumb from '@/components/PageBreadcrumb.vue'
import PageStateShell from '@/components/State/PageStateShell.vue'
import FormModal from '@/components/FormModal.vue'

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

const mobileColumns = computed(() => [
  { key: 'name', label: t('adminWorkflows.columns.name') },
  { key: 'active', label: t('adminWorkflows.columns.active') },
  { key: 'latestPublished', label: t('adminWorkflows.columns.latestPublished') },
])

let searchTimeout = null
function debouncedSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => fetchWorkflows(), 400)
}

function clearFilters() {
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

