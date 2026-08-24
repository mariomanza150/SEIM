<template>
  <div class="admin-dynforms-page">
    <PageHeader :title="t('adminDynforms.title')" :subtitle="t('adminDynforms.subtitle')">
      <template #breadcrumb>
        <PageBreadcrumb
          :aria-label="t('adminCommon.breadcrumbAria')"
          :items="[
            { to: { name: 'Dashboard' }, label: t('route.names.Dashboard') },
            { label: t('route.names.AdminDynforms') },
          ]"
        />
      </template>
      <template #actions>
        <button type="button" class="btn btn-outline-secondary" :disabled="loading" @click="fetchForms">
          <i class="bi bi-arrow-clockwise me-1" aria-hidden="true"></i>{{ t('adminCommon.refresh') }}
        </button>
        <button type="button" class="btn btn-primary" data-testid="dynforms-create" @click="openCreate">
          <i class="bi bi-plus-circle me-1" aria-hidden="true"></i>{{ t('adminDynforms.create') }}
        </button>
      </template>
    </PageHeader>

    <CompactFilterBar test-id="admin-dynforms-filters" @clear="clearFilters">
      <template #primary>
        <div class="col-md-6">
          <label class="form-label">{{ t('adminCommon.searchLabel') }}</label>
          <input
            v-model="filters.search"
            class="form-control"
            type="text"
            :placeholder="t('adminForms.searchPlaceholder')"
            @input="debouncedSearch"
          />
        </div>
        <div class="col-md-3">
          <label class="form-label">{{ t('adminForms.filterType') }}</label>
          <select v-model="filters.form_type" class="form-select" @change="fetchForms">
            <option value="">{{ t('adminCommon.filterAll') }}</option>
            <option v-for="opt in formTypeOptions" :key="opt.value" :value="opt.value">
              {{ opt.label }}
            </option>
          </select>
        </div>
      </template>
      <template #advanced>
        <div class="col-md-4">
          <label class="form-label">{{ t('adminCommon.sortLabel') }}</label>
          <select v-model="filters.ordering" class="form-select" @change="fetchForms">
            <option value="name">{{ t('adminForms.sortNameAsc') }}</option>
            <option value="-created_at">{{ t('adminForms.sortNewest') }}</option>
          </select>
        </div>
      </template>
    </CompactFilterBar>

    <PageStateShell
      :loading="loading"
      :error="error || ''"
      :empty="!forms.length"
      :empty-title="t('adminDynforms.empty')"
      skeleton="table"
      :loading-label="t('adminCommon.loading')"
      :skeleton-columns="4"
    >
    <div class="card">
      <ResponsiveList :items="forms" :columns="mobileColumns" mobile-test-id="admin-dynforms-mobile">
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0" data-testid="dynforms-table">
          <thead>
            <tr>
              <th>{{ t('adminForms.columns.name') }}</th>
              <th>{{ t('adminForms.columns.type') }}</th>
              <th>{{ t('adminForms.columns.fields') }}</th>
              <th class="text-end">{{ t('adminCommon.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="ft in forms" :key="ft.id">
              <td>
                <div class="fw-medium">{{ ft.name }}</div>
                <div class="text-muted small">{{ ft.description }}</div>
              </td>
              <td><span class="badge bg-secondary">{{ ft.form_type }}</span></td>
              <td>{{ ft.field_count ?? 0 }}</td>
              <td class="text-end text-nowrap">
                <router-link
                  class="btn btn-sm btn-primary me-2"
                  :to="{ name: 'AdminDynformEditor', params: { id: String(ft.id) } }"
                  data-testid="dynforms-open-builder"
                >
                  {{ t('adminDynforms.openBuilder') }}
                </router-link>
                <button type="button" class="btn btn-sm btn-outline-danger" :disabled="mutating" @click="confirmDelete(ft)">
                  {{ t('adminCommon.delete') }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <template #col-name="{ item }">
        <div class="fw-medium">{{ item.name }}</div>
        <div v-if="item.description" class="text-muted small">{{ item.description }}</div>
      </template>
      <template #col-type="{ item }">
        <span class="badge bg-secondary">{{ item.form_type }}</span>
      </template>
      <template #col-fields="{ item }">{{ item.field_count ?? 0 }}</template>
      <template #actions="{ item }">
        <router-link
          class="btn btn-sm btn-primary"
          :to="{ name: 'AdminDynformEditor', params: { id: String(item.id) } }"
          data-testid="dynforms-open-builder"
        >
          {{ t('adminDynforms.openBuilder') }}
        </router-link>
        <button type="button" class="btn btn-sm btn-outline-danger" :disabled="mutating" @click="confirmDelete(item)">
          {{ t('adminCommon.delete') }}
        </button>
      </template>
      </ResponsiveList>
    </div>
    </PageStateShell>

    <FormModal
      :open="creator.open"
      :title="t('adminDynforms.create')"
      :error="creator.error || ''"
      :saving="creator.saving"
      :submit-label="t('adminDynforms.createAndBuild')"
      size="md"
      @close="closeCreator"
      @submit="createForm"
    >
      <label class="form-label">{{ t('adminForms.fields.name') }}</label>
      <input v-model="creator.form.name" class="form-control mb-3" type="text" data-testid="dynforms-create-name" />
      <label class="form-label">{{ t('adminForms.fields.type') }}</label>
      <select v-model="creator.form.form_type" class="form-select mb-3">
        <option v-for="opt in formTypeOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
      </select>
      <label class="form-label">{{ t('adminForms.fields.description') }}</label>
      <textarea v-model="creator.form.description" class="form-control" rows="2" />
    </FormModal>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import CompactFilterBar from '@/components/CompactFilterBar.vue'
import ResponsiveList from '@/components/ResponsiveList.vue'
import PageHeader from '@/components/PageHeader.vue'
import PageBreadcrumb from '@/components/PageBreadcrumb.vue'
import PageStateShell from '@/components/State/PageStateShell.vue'
import FormModal from '@/components/FormModal.vue'
import api from '@/services/api'
import { useConfirm } from '@/composables/useConfirm'
import { useToast } from '@/composables/useToast'

const { t } = useI18n()
const router = useRouter()
const { confirm } = useConfirm()
const { success, error: errorToast } = useToast()

const loading = ref(true)
const error = ref(null)
const forms = ref([])
const mutating = ref(false)
const filters = ref({ search: '', form_type: '', ordering: 'name' })

const mobileColumns = computed(() => [
  { key: 'name', label: t('adminForms.columns.name') },
  { key: 'type', label: t('adminForms.columns.type') },
  { key: 'fields', label: t('adminForms.columns.fields') },
])

const formTypeOptions = [
  { value: 'application', label: 'Application' },
  { value: 'survey', label: 'Survey' },
  { value: 'feedback', label: 'Feedback' },
  { value: 'custom', label: 'Custom' },
]
const creator = ref({
  open: false,
  saving: false,
  error: null,
  form: { name: '', form_type: 'application', description: '' },
})

function normalizeApiList(data) {
  if (data && typeof data === 'object' && Array.isArray(data.results)) return data.results
  return Array.isArray(data) ? data : []
}

let searchTimeout = null
function debouncedSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => fetchForms(), 400)
}

function clearFilters() {
  filters.value = { search: '', form_type: '', ordering: 'name' }
  fetchForms()
}

async function fetchForms() {
  loading.value = true
  error.value = null
  try {
    const params = { ordering: filters.value.ordering }
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.form_type) params.form_type = filters.value.form_type
    const response = await api.get('/api/application-forms/form-types/', { params })
    forms.value = normalizeApiList(response.data)
  } catch {
    error.value = t('adminDynforms.loadError')
  } finally {
    loading.value = false
  }
}

function openCreate() {
  creator.value = {
    open: true,
    saving: false,
    error: null,
    form: { name: '', form_type: 'application', description: '' },
  }
}

function closeCreator() {
  creator.value.open = false
}

async function createForm() {
  creator.value.saving = true
  creator.value.error = null
  try {
    const response = await api.post('/api/application-forms/form-types/', {
      name: creator.value.form.name,
      form_type: creator.value.form.form_type,
      description: creator.value.form.description,
      is_active: true,
      schema: { type: 'object', properties: {}, required: [] },
      ui_schema: {},
      step_definitions: [],
    })
    success(t('adminDynforms.toastCreated'))
    await router.push({ name: 'AdminDynformEditor', params: { id: String(response.data.id) } })
  } catch {
    creator.value.error = t('adminDynforms.createError')
    errorToast(t('adminDynforms.createError'))
  } finally {
    creator.value.saving = false
  }
}

async function confirmDelete(row) {
  const ok = await confirm({
    title: t('adminCommon.delete'),
    message: t('adminForms.deleteConfirm', { name: row?.name || '' }),
    confirmText: t('adminCommon.delete'),
    cancelText: t('adminCommon.cancel'),
    variant: 'danger',
  })
  if (!ok) return
  mutating.value = true
  try {
    await api.delete(`/api/application-forms/form-types/${row.id}/`)
    success(t('adminForms.toastDeleted'))
    await fetchForms()
  } catch {
    errorToast(t('adminForms.deleteToastError'))
  } finally {
    mutating.value = false
  }
}

onMounted(fetchForms)
</script>
