<template>
  <div class="admin-forms-page">
    <PageHeader :title="t('adminForms.title')" :subtitle="t('adminForms.subtitle')">
      <template #breadcrumb>
        <PageBreadcrumb
          :aria-label="t('adminCommon.breadcrumbAria')"
          :items="[
            { to: { name: 'Dashboard' }, label: t('route.names.Dashboard') },
            { label: t('route.names.AdminForms') },
          ]"
        />
      </template>

      <template #actions>
        <button type="button" class="btn btn-outline-secondary" :disabled="loading" @click="fetchForms">
          <i class="bi bi-arrow-clockwise me-1" aria-hidden="true"></i>{{ t('adminCommon.refresh') }}
        </button>
        <button type="button" class="btn btn-primary" @click="openCreate">
          <i class="bi bi-plus-circle me-1" aria-hidden="true"></i>{{ t('adminForms.create') }}
        </button>
      </template>
    </PageHeader>

    <CompactFilterBar test-id="admin-forms-filters" @clear="clearFilters">
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
      :empty-title="t('adminForms.empty')"
      skeleton="table"
      :loading-label="t('adminForms.loadingList')"
      :skeleton-columns="5"
    >
    <div class="card">
      <ResponsiveList :items="forms" :columns="mobileColumns" mobile-test-id="admin-forms-mobile">
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0" data-testid="admin-forms-table">
          <thead>
            <tr>
              <th scope="col">{{ t('adminForms.columns.name') }}</th>
              <th scope="col" class="text-nowrap">{{ t('adminForms.columns.type') }}</th>
              <th scope="col" class="text-nowrap">{{ t('adminForms.columns.active') }}</th>
              <th scope="col" class="text-nowrap">{{ t('adminForms.columns.fields') }}</th>
              <th scope="col" class="text-end">{{ t('adminCommon.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="ft in forms" :key="ft.id">
              <td class="min-w-0">
                <div class="fw-medium text-truncate">{{ ft.name }}</div>
                <div class="text-muted small text-truncate">{{ ft.description }}</div>
              </td>
              <td class="text-nowrap">
                <span class="badge bg-secondary">{{ ft.form_type }}</span>
              </td>
              <td class="text-nowrap">
                <span class="badge" :class="ft.is_active ? 'bg-success' : 'bg-secondary'">
                  {{ ft.is_active ? t('adminCommon.yes') : t('adminCommon.no') }}
                </span>
              </td>
              <td class="text-nowrap small">
                {{ ft.field_count ?? 0 }}
              </td>
              <td class="text-end text-nowrap">
                <router-link
                  class="btn btn-sm btn-primary me-2"
                  :to="{ name: 'AdminDynformEditor', params: { id: String(ft.id) } }"
                  data-testid="admin-forms-open-builder"
                >
                  {{ t('adminForms.openBuilder') }}
                </router-link>
                <button type="button" class="btn btn-sm btn-outline-secondary me-2" @click="openEdit(ft)">
                  <i class="bi bi-pencil me-1" aria-hidden="true"></i>{{ t('adminCommon.edit') }}
                </button>
                <button type="button" class="btn btn-sm btn-outline-danger" @click="confirmDelete(ft)" :disabled="mutating">
                  <i class="bi bi-trash me-1" aria-hidden="true"></i>{{ t('adminCommon.delete') }}
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
      <template #col-active="{ item }">
        <span class="badge" :class="item.is_active ? 'bg-success' : 'bg-secondary'">
          {{ item.is_active ? t('adminCommon.yes') : t('adminCommon.no') }}
        </span>
      </template>
      <template #col-fields="{ item }">{{ item.field_count ?? 0 }}</template>
      <template #actions="{ item }">
        <router-link
          class="btn btn-sm btn-primary"
          :to="{ name: 'AdminDynformEditor', params: { id: String(item.id) } }"
          data-testid="admin-forms-open-builder"
        >
          {{ t('adminForms.openBuilder') }}
        </router-link>
        <button type="button" class="btn btn-sm btn-outline-secondary" @click="openEdit(item)">
          <i class="bi bi-pencil me-1" aria-hidden="true"></i>{{ t('adminCommon.edit') }}
        </button>
        <button type="button" class="btn btn-sm btn-outline-danger" @click="confirmDelete(item)" :disabled="mutating">
          <i class="bi bi-trash me-1" aria-hidden="true"></i>{{ t('adminCommon.delete') }}
        </button>
      </template>
      </ResponsiveList>
    </div>
    </PageStateShell>

    <FormModal
      :open="editor.open"
      :title="editor.mode === 'create' ? t('adminForms.create') : t('adminForms.editTitle')"
      :error="editor.error || ''"
      :saving="editor.saving"
      size="xl"
      @close="closeEditor"
      @submit="saveForm"
    >
      <div class="row g-3">
              <div class="col-md-6">
                <label class="form-label">{{ t('adminForms.fields.name') }}</label>
                <input v-model="editor.form.name" class="form-control" type="text" />
              </div>
              <div class="col-md-3">
                <label class="form-label">{{ t('adminForms.fields.type') }}</label>
                <select v-model="editor.form.form_type" class="form-select">
                  <option v-for="opt in formTypeOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
                </select>
              </div>
              <div class="col-md-3">
                <label class="form-label">{{ t('adminForms.fields.active') }}</label>
                <div class="form-check mt-2">
                  <input id="formActive" v-model="editor.form.is_active" class="form-check-input" type="checkbox" />
                  <label class="form-check-label" for="formActive">{{ t('adminForms.fields.activeHelp') }}</label>
                </div>
              </div>

              <div class="col-12">
                <label class="form-label">{{ t('adminForms.fields.description') }}</label>
                <textarea v-model="editor.form.description" class="form-control" rows="2" />
              </div>

              <div class="col-12">
                <label class="form-label">{{ t('adminForms.fields.schema') }}</label>
                <textarea v-model="editor.form.schema_text" class="form-control font-monospace" rows="10" />
                <div class="form-text">{{ t('adminForms.fields.schemaHelp') }}</div>
              </div>

              <div class="col-12">
                <label class="form-label">{{ t('adminForms.fields.uiSchema') }}</label>
                <textarea v-model="editor.form.ui_schema_text" class="form-control font-monospace" rows="8" />
                <div class="form-text">{{ t('adminForms.fields.uiSchemaHelp') }}</div>
              </div>

              <div class="col-12">
                <label class="form-label">{{ t('adminForms.fields.steps') }}</label>
                <textarea v-model="editor.form.step_definitions_text" class="form-control font-monospace" rows="8" />
                <div class="form-text">{{ t('adminForms.fields.stepsHelp') }}</div>
              </div>
      </div>
    </FormModal>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useToast } from '@/composables/useToast'
import { useConfirm } from '@/composables/useConfirm'
import CompactFilterBar from '@/components/CompactFilterBar.vue'
import ResponsiveList from '@/components/ResponsiveList.vue'
import PageHeader from '@/components/PageHeader.vue'
import PageBreadcrumb from '@/components/PageBreadcrumb.vue'
import PageStateShell from '@/components/State/PageStateShell.vue'
import FormModal from '@/components/FormModal.vue'

const { t } = useI18n()
const { success, error: errorToast } = useToast()
const { confirm } = useConfirm()

const loading = ref(true)
const error = ref(null)
const forms = ref([])
const mutating = ref(false)

const filters = ref({
  search: '',
  form_type: '',
  ordering: 'name',
})

const mobileColumns = computed(() => [
  { key: 'name', label: t('adminForms.columns.name') },
  { key: 'type', label: t('adminForms.columns.type') },
  { key: 'active', label: t('adminForms.columns.active') },
  { key: 'fields', label: t('adminForms.columns.fields') },
])

function clearFilters() {
  filters.value = { search: '', form_type: '', ordering: 'name' }
  fetchForms()
}

const formTypeOptions = [
  { value: 'application', label: 'Application' },
  { value: 'survey', label: 'Survey' },
  { value: 'feedback', label: 'Feedback' },
  { value: 'custom', label: 'Custom' },
]

const editor = ref({
  open: false,
  mode: 'create',
  id: null,
  saving: false,
  error: null,
  form: emptyForm(),
})

function emptyForm() {
  return {
    name: '',
    form_type: 'application',
    description: '',
    is_active: true,
    schema_text: JSON.stringify({ type: 'object', properties: {}, required: [] }, null, 2),
    ui_schema_text: JSON.stringify({}, null, 2),
    step_definitions_text: JSON.stringify([], null, 2),
  }
}

function normalizeApiList(data) {
  if (data && typeof data === 'object' && Array.isArray(data.results)) return data.results
  return Array.isArray(data) ? data : []
}

let searchTimeout = null
function debouncedSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => fetchForms(), 400)
}

async function fetchForms() {
  try {
    loading.value = true
    error.value = null
    const params = { ordering: filters.value.ordering }
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.form_type) params.form_type = filters.value.form_type
    const response = await api.get('/api/application-forms/form-types/', { params })
    forms.value = normalizeApiList(response.data)
  } catch (err) {
    console.error('Failed to fetch form types:', err)
    error.value = t('adminForms.loadError')
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editor.value = {
    open: true,
    mode: 'create',
    id: null,
    saving: false,
    error: null,
    form: emptyForm(),
  }
}

async function openEdit(row) {
  editor.value = {
    open: true,
    mode: 'edit',
    id: row.id,
    saving: false,
    error: null,
    form: emptyForm(),
  }
  try {
    const response = await api.get(`/api/application-forms/form-types/${row.id}/`)
    const ft = response.data || {}
    editor.value.form = {
      name: ft.name || '',
      form_type: ft.form_type || 'application',
      description: ft.description || '',
      is_active: Boolean(ft.is_active),
      schema_text: JSON.stringify(ft.schema || {}, null, 2),
      ui_schema_text: JSON.stringify(ft.ui_schema || {}, null, 2),
      step_definitions_text: JSON.stringify(ft.step_definitions || [], null, 2),
    }
  } catch (err) {
    console.error('Failed to load form type:', err)
    editor.value.error = t('adminForms.loadDetailError')
  }
}

function closeEditor() {
  editor.value.open = false
}

function parseJson(text, labelKey) {
  const raw = (text ?? '').trim()
  if (!raw) return null
  try {
    return JSON.parse(raw)
  } catch {
    throw new Error(t(labelKey))
  }
}

async function saveForm() {
  editor.value.error = null
  editor.value.saving = true
  try {
    const payload = {
      name: editor.value.form.name,
      form_type: editor.value.form.form_type,
      description: editor.value.form.description,
      is_active: Boolean(editor.value.form.is_active),
      schema: parseJson(editor.value.form.schema_text, 'adminForms.jsonInvalidSchema'),
      ui_schema: parseJson(editor.value.form.ui_schema_text, 'adminForms.jsonInvalidUiSchema'),
      step_definitions: parseJson(editor.value.form.step_definitions_text, 'adminForms.jsonInvalidSteps') || [],
    }

    if (editor.value.mode === 'create') {
      await api.post('/api/application-forms/form-types/', payload)
      success(t('adminForms.toastCreated'))
    } else {
      await api.patch(`/api/application-forms/form-types/${editor.value.id}/`, payload)
      success(t('adminForms.toastSaved'))
    }
    closeEditor()
    await fetchForms()
  } catch (err) {
    console.error('Failed to save form type:', err)
    editor.value.error = err instanceof Error ? err.message : t('adminForms.saveError')
    errorToast(t('adminForms.saveToastError'))
  } finally {
    editor.value.saving = false
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
  } catch (err) {
    console.error('Failed to delete form type:', err)
    errorToast(t('adminForms.deleteToastError'))
  } finally {
    mutating.value = false
  }
}

onMounted(() => {
  fetchForms()
})
</script>

<style scoped>
.admin-forms-page {
  min-height: 60vh;
}
</style>

