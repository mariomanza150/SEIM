<template>
  <div class="admin-programs-page">
    <PageHeader :title="t('adminPrograms.title')" :subtitle="t('adminPrograms.subtitle')">
      <template #breadcrumb>
        <nav aria-label="Breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item">
              <router-link :to="{ name: 'Dashboard' }">{{ t('route.names.Dashboard') }}</router-link>
            </li>
            <li class="breadcrumb-item active">{{ t('route.names.AdminPrograms') }}</li>
          </ol>
        </nav>
      </template>

      <template #actions>
        <button type="button" class="btn btn-outline-secondary" :disabled="loading" @click="fetchPrograms">
          <i class="bi bi-arrow-clockwise me-1" aria-hidden="true"></i>{{ t('adminCommon.refresh') }}
        </button>
        <button type="button" class="btn btn-primary" @click="openCreate">
          <i class="bi bi-plus-circle me-1" aria-hidden="true"></i>{{ t('adminPrograms.create') }}
        </button>
      </template>
    </PageHeader>

    <div class="card mb-3" data-testid="admin-programs-filters">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-6">
            <label class="form-label">{{ t('adminCommon.searchLabel') }}</label>
            <input
              v-model="filters.search"
              class="form-control"
              type="text"
              :placeholder="t('adminPrograms.searchPlaceholder')"
              @input="debouncedSearch"
            />
          </div>
          <div class="col-md-3">
            <label class="form-label">{{ t('adminPrograms.filterActive') }}</label>
            <select v-model="filters.is_active" class="form-select" @change="fetchPrograms">
              <option value="">{{ t('adminCommon.filterAll') }}</option>
              <option value="true">{{ t('adminCommon.yes') }}</option>
              <option value="false">{{ t('adminCommon.no') }}</option>
            </select>
          </div>
          <div class="col-md-3">
            <label class="form-label">{{ t('adminCommon.sortLabel') }}</label>
            <select v-model="filters.ordering" class="form-select" @change="fetchPrograms">
              <option value="name">{{ t('adminPrograms.sortNameAsc') }}</option>
              <option value="-created_at">{{ t('adminPrograms.sortNewest') }}</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">{{ t('adminCommon.loading') }}</span>
      </div>
      <p class="mt-3 text-muted">{{ t('adminPrograms.loadingList') }}</p>
    </div>

    <div v-else-if="error" class="alert alert-danger" role="alert">
      <i class="bi bi-exclamation-triangle me-2" aria-hidden="true"></i>
      {{ error }}
    </div>

    <div v-else class="card">
      <div class="card-header bg-transparent d-flex justify-content-between align-items-center flex-wrap gap-2">
        <div class="text-muted small">
          {{ programs.length }}
        </div>
        <button type="button" class="btn btn-sm btn-outline-secondary" @click="resetFilters" :disabled="loading">
          <i class="bi bi-x-circle me-1" aria-hidden="true"></i>{{ t('adminCommon.resetFilters') }}
        </button>
      </div>
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0" data-testid="admin-programs-table">
          <thead>
            <tr>
              <th scope="col">{{ t('adminPrograms.columns.name') }}</th>
              <th scope="col" class="text-nowrap">{{ t('adminPrograms.columns.window') }}</th>
              <th scope="col" class="text-nowrap">{{ t('adminPrograms.columns.active') }}</th>
              <th scope="col" class="text-nowrap">{{ t('adminPrograms.columns.capacity') }}</th>
              <th scope="col" class="text-end">{{ t('adminCommon.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!programs.length">
              <td colspan="5" class="text-muted text-center py-4">
                {{ t('adminPrograms.empty') }}
              </td>
            </tr>
            <tr v-for="p in programs" :key="p.id">
              <td class="min-w-0">
                <div class="fw-medium text-truncate">{{ p.name }}</div>
                <div class="text-muted small text-truncate">{{ p.description }}</div>
              </td>
              <td class="text-nowrap small">
                <span class="badge" :class="p.application_window_open ? 'bg-success' : 'bg-secondary'">
                  {{ p.application_window_open ? t('adminPrograms.windowOpen') : t('adminPrograms.windowClosed') }}
                </span>
                <div class="text-muted small mt-1">{{ p.application_window_message }}</div>
              </td>
              <td class="text-nowrap">
                <span class="badge" :class="p.is_active ? 'bg-success' : 'bg-secondary'">
                  {{ p.is_active ? t('adminCommon.yes') : t('adminCommon.no') }}
                </span>
              </td>
              <td class="text-nowrap small">
                <span v-if="p.enrollment_capacity == null" class="text-muted">{{ t('adminPrograms.capacityUnlimited') }}</span>
                <span v-else>
                  {{ p.enrollment_seats_occupied }} / {{ p.enrollment_capacity }}
                  <span class="text-muted">({{ t('adminPrograms.capacityRemaining', { n: p.enrollment_slots_remaining ?? 0 }) }})</span>
                </span>
              </td>
              <td class="text-end text-nowrap">
                <button type="button" class="btn btn-sm btn-outline-secondary me-2" @click="openEdit(p)">
                  <i class="bi bi-pencil me-1" aria-hidden="true"></i>{{ t('adminCommon.edit') }}
                </button>
                <button type="button" class="btn btn-sm btn-outline-primary me-2" @click="cloneProgram(p)" :disabled="mutating">
                  <i class="bi bi-files me-1" aria-hidden="true"></i>{{ t('adminPrograms.clone') }}
                </button>
                <button type="button" class="btn btn-sm btn-outline-danger" @click="confirmDelete(p)" :disabled="mutating">
                  <i class="bi bi-trash me-1" aria-hidden="true"></i>{{ t('adminCommon.delete') }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Editor -->
    <div v-if="editor.open" class="modal-backdrop show"></div>
    <div v-if="editor.open" class="modal d-block" tabindex="-1" role="dialog" aria-modal="true">
      <div class="modal-dialog modal-lg modal-dialog-scrollable">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              {{ editor.mode === 'create' ? t('adminPrograms.create') : t('adminPrograms.editTitle') }}
            </h5>
            <button type="button" class="btn-close" :aria-label="t('adminCommon.close')" @click="closeEditor" />
          </div>
          <div class="modal-body">
            <div v-if="editor.error" class="alert alert-danger" role="alert">
              {{ editor.error }}
            </div>

            <div class="row g-3">
              <div class="col-md-8">
                <label class="form-label">{{ t('adminPrograms.fields.name') }}</label>
                <input v-model="editor.form.name" class="form-control" type="text" />
              </div>
              <div class="col-md-4">
                <label class="form-label">{{ t('adminPrograms.fields.active') }}</label>
                <div class="form-check mt-2">
                  <input id="isActive" v-model="editor.form.is_active" class="form-check-input" type="checkbox" />
                  <label class="form-check-label" for="isActive">{{ t('adminPrograms.fields.activeHelp') }}</label>
                </div>
              </div>

              <div class="col-12">
                <label class="form-label">{{ t('adminPrograms.fields.description') }}</label>
                <textarea v-model="editor.form.description" class="form-control" rows="3"></textarea>
              </div>

              <div class="col-md-6">
                <label class="form-label">{{ t('adminPrograms.fields.applicationOpenDate') }}</label>
                <input v-model="editor.form.application_open_date" class="form-control" type="date" />
              </div>
              <div class="col-md-6">
                <label class="form-label">{{ t('adminPrograms.fields.applicationDeadline') }}</label>
                <input v-model="editor.form.application_deadline" class="form-control" type="date" />
              </div>
              <div class="col-md-6">
                <label class="form-label">{{ t('adminPrograms.fields.startDate') }}</label>
                <input v-model="editor.form.start_date" class="form-control" type="date" />
              </div>
              <div class="col-md-6">
                <label class="form-label">{{ t('adminPrograms.fields.endDate') }}</label>
                <input v-model="editor.form.end_date" class="form-control" type="date" />
              </div>

              <div class="col-md-6">
                <label class="form-label">{{ t('adminPrograms.fields.applicationForm') }}</label>
                <select v-model="editor.form.application_form" class="form-select">
                  <option :value="null">{{ t('adminCommon.notSet') }}</option>
                  <option v-for="ft in formTypes" :key="ft.id" :value="ft.id">{{ ft.name }}</option>
                </select>
              </div>

              <div class="col-md-6">
                <label class="form-label">{{ t('adminPrograms.fields.workflowVersion') }}</label>
                <select v-model="editor.form.workflow_version" class="form-select">
                  <option :value="null">{{ t('adminCommon.notSet') }}</option>
                  <option v-for="wv in workflowVersions" :key="wv.id" :value="wv.id">
                    {{ wv.definition_name }} v{{ wv.version }}
                  </option>
                </select>
                <div class="form-text">{{ t('adminPrograms.fields.workflowVersionHelp') }}</div>
              </div>

              <div class="col-md-6">
                <label class="form-label">{{ t('adminPrograms.fields.recurring') }}</label>
                <div class="form-check mt-2">
                  <input id="recurring" v-model="editor.form.recurring" class="form-check-input" type="checkbox" />
                  <label class="form-check-label" for="recurring">{{ t('adminPrograms.fields.recurringHelp') }}</label>
                </div>
              </div>

              <div class="col-md-6">
                <label class="form-label">{{ t('adminPrograms.fields.capacity') }}</label>
                <input v-model.number="editor.form.enrollment_capacity" class="form-control" type="number" min="0" />
              </div>
              <div class="col-md-6">
                <label class="form-label">{{ t('adminPrograms.fields.waitlist') }}</label>
                <div class="form-check mt-2">
                  <input id="waitlist" v-model="editor.form.waitlist_when_full" class="form-check-input" type="checkbox" />
                  <label class="form-check-label" for="waitlist">{{ t('adminPrograms.fields.waitlistHelp') }}</label>
                </div>
              </div>

              <div class="col-md-4">
                <label class="form-label">{{ t('adminPrograms.fields.minGpa') }}</label>
                <input v-model.number="editor.form.min_gpa" class="form-control" type="number" step="0.01" min="0" />
              </div>
              <div class="col-md-4">
                <label class="form-label">{{ t('adminPrograms.fields.requiredLanguage') }}</label>
                <input v-model="editor.form.required_language" class="form-control" type="text" />
              </div>
              <div class="col-md-4">
                <label class="form-label">{{ t('adminPrograms.fields.minLanguageLevel') }}</label>
                <select v-model="editor.form.min_language_level" class="form-select">
                  <option value="">{{ t('adminCommon.notSet') }}</option>
                  <option v-for="opt in cefrOptions" :key="opt" :value="opt">{{ opt }}</option>
                </select>
              </div>

              <div class="col-md-6">
                <label class="form-label">{{ t('adminPrograms.fields.minAge') }}</label>
                <input v-model.number="editor.form.min_age" class="form-control" type="number" min="0" />
              </div>
              <div class="col-md-6">
                <label class="form-label">{{ t('adminPrograms.fields.maxAge') }}</label>
                <input v-model.number="editor.form.max_age" class="form-control" type="number" min="0" />
              </div>

              <div class="col-md-6">
                <label class="form-label">{{ t('adminPrograms.fields.coordinators') }}</label>
                <select v-model="editor.form.coordinators" class="form-select" multiple>
                  <option v-for="u in coordinators" :key="u.id" :value="u.id">
                    {{ (u.first_name || u.last_name) ? `${u.first_name || ''} ${u.last_name || ''}`.trim() : u.username }}
                    <span v-if="u.email">({{ u.email }})</span>
                  </option>
                </select>
                <div class="form-text">{{ t('adminPrograms.fields.coordinatorsHelp') }}</div>
              </div>

              <div class="col-md-6">
                <label class="form-label">{{ t('adminPrograms.fields.requiredDocs') }}</label>
                <select v-model="editor.form.required_document_types" class="form-select" multiple>
                  <option v-for="dt in documentTypes" :key="dt.id" :value="dt.id">{{ dt.name }}</option>
                </select>
                <div class="form-text">{{ t('adminPrograms.fields.requiredDocsHelp') }}</div>
              </div>

              <div class="col-12">
                <div class="form-check mt-2">
                  <input id="autoReject" v-model="editor.form.auto_reject_ineligible" class="form-check-input" type="checkbox" />
                  <label class="form-check-label" for="autoReject">{{ t('adminPrograms.fields.autoReject') }}</label>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-outline-secondary" @click="closeEditor">
              {{ t('adminCommon.cancel') }}
            </button>
            <button type="button" class="btn btn-primary" :disabled="editor.saving" @click="saveProgram">
              <span v-if="editor.saving" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true" />
              {{ t('adminCommon.save') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useToast } from '@/composables/useToast'
import { useConfirm } from '@/composables/useConfirm'
import PageHeader from '@/components/PageHeader.vue'

const { t } = useI18n()
const { success, error: errorToast } = useToast()
const { confirm } = useConfirm()

const loading = ref(true)
const error = ref(null)
const programs = ref([])
const mutating = ref(false)

const filters = ref({
  search: '',
  is_active: '',
  ordering: 'name',
})

function resetFilters() {
  filters.value = { search: '', is_active: '', ordering: 'name' }
  fetchPrograms()
}

const cefrOptions = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']

const formTypes = ref([])
const workflowVersions = ref([])
const coordinators = ref([])
const documentTypes = ref([])

const editor = ref({
  open: false,
  mode: 'create',
  id: null,
  saving: false,
  error: null,
  form: emptyProgramForm(),
})

function emptyProgramForm() {
  return {
    name: '',
    description: '',
    is_active: true,
    recurring: false,
    application_open_date: null,
    application_deadline: null,
    start_date: null,
    end_date: null,
    min_gpa: null,
    required_language: '',
    min_language_level: '',
    min_age: null,
    max_age: null,
    auto_reject_ineligible: false,
    enrollment_capacity: null,
    waitlist_when_full: true,
    application_form: null,
    workflow_version: null,
    coordinators: [],
    required_document_types: [],
  }
}

function normalizeApiList(data) {
  if (data && typeof data === 'object' && Array.isArray(data.results)) return data.results
  return Array.isArray(data) ? data : []
}

let searchTimeout = null
function debouncedSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => fetchPrograms(), 400)
}

async function fetchPrograms() {
  try {
    loading.value = true
    error.value = null
    const params = { ordering: filters.value.ordering }
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.is_active) params.is_active = filters.value.is_active
    const response = await api.get('/api/programs/', { params })
    programs.value = normalizeApiList(response.data)
  } catch (err) {
    console.error('Failed to fetch programs:', err)
    error.value = t('adminPrograms.loadError')
  } finally {
    loading.value = false
  }
}

async function fetchEditorOptions() {
  const [ftRes, userRes, dtRes, wvRes] = await Promise.all([
    api.get('/api/application-forms/form-types/', { params: { ordering: 'name' } }),
    api.get('/api/users/'),
    api.get('/api/document-types/', { params: { ordering: 'name' } }),
    api.get('/api/workflow-versions/', { params: { ordering: '-version' } }),
  ])
  formTypes.value = normalizeApiList(ftRes.data)
  const allUsers = normalizeApiList(userRes.data)
  coordinators.value = allUsers.filter((u) => u.role === 'coordinator')
  documentTypes.value = normalizeApiList(dtRes.data)
  workflowVersions.value = normalizeApiList(wvRes.data).filter((v) => v.status === 'published')
}

function openCreate() {
  editor.value = {
    open: true,
    mode: 'create',
    id: null,
    saving: false,
    error: null,
    form: emptyProgramForm(),
  }
}

function openEdit(program) {
  editor.value = {
    open: true,
    mode: 'edit',
    id: program.id,
    saving: false,
    error: null,
    form: {
      name: program.name || '',
      description: program.description || '',
      is_active: Boolean(program.is_active),
      recurring: Boolean(program.recurring),
      application_open_date: program.application_open_date || null,
      application_deadline: program.application_deadline || null,
      start_date: program.start_date || null,
      end_date: program.end_date || null,
      min_gpa: program.min_gpa ?? null,
      required_language: program.required_language || '',
      min_language_level: program.min_language_level || '',
      min_age: program.min_age ?? null,
      max_age: program.max_age ?? null,
      auto_reject_ineligible: Boolean(program.auto_reject_ineligible),
      enrollment_capacity: program.enrollment_capacity ?? null,
      waitlist_when_full: Boolean(program.waitlist_when_full),
      application_form: program.application_form ?? null,
      workflow_version: program.workflow_version ?? null,
      coordinators: Array.isArray(program.coordinators) ? program.coordinators : [],
      required_document_types: Array.isArray(program.required_document_types) ? program.required_document_types : [],
    },
  }
}

function closeEditor() {
  editor.value.open = false
}

function cleanProgramPayload(form) {
  const payload = { ...form }
  if (payload.required_language === '') payload.required_language = null
  if (payload.min_language_level === '') payload.min_language_level = null
  if (payload.application_open_date === '') payload.application_open_date = null
  if (payload.application_deadline === '') payload.application_deadline = null
  if (payload.start_date === '') payload.start_date = null
  if (payload.end_date === '') payload.end_date = null
  if (payload.application_form === '') payload.application_form = null
  if (payload.workflow_version === '') payload.workflow_version = null
  if (payload.enrollment_capacity === '') payload.enrollment_capacity = null
  if (payload.min_gpa === '') payload.min_gpa = null
  if (payload.min_age === '') payload.min_age = null
  if (payload.max_age === '') payload.max_age = null
  return payload
}

async function saveProgram() {
  editor.value.error = null
  editor.value.saving = true
  try {
    const payload = cleanProgramPayload(editor.value.form)
    if (editor.value.mode === 'create') {
      await api.post('/api/programs/', payload)
      success(t('adminPrograms.toastCreated'))
    } else {
      await api.patch(`/api/programs/${editor.value.id}/`, payload)
      success(t('adminPrograms.toastSaved'))
    }
    closeEditor()
    await fetchPrograms()
  } catch (err) {
    console.error('Failed to save program:', err)
    const detail = err.response?.data?.detail
    editor.value.error = typeof detail === 'string' ? detail : t('adminPrograms.saveError')
    errorToast(t('adminPrograms.saveToastError'))
  } finally {
    editor.value.saving = false
  }
}

async function cloneProgram(program) {
  if (!program?.id) return
  const ok = await confirm({
    title: t('adminPrograms.clone'),
    message: t('adminPrograms.cloneConfirm', { name: program.name || '' }),
    confirmText: t('adminPrograms.clone'),
    cancelText: t('adminCommon.cancel'),
    variant: 'primary',
  })
  if (!ok) return
  mutating.value = true
  try {
    await api.post(`/api/programs/${program.id}/clone/`)
    success(t('adminPrograms.toastCloned'))
    await fetchPrograms()
  } catch (err) {
    console.error('Failed to clone program:', err)
    errorToast(t('adminPrograms.cloneToastError'))
  } finally {
    mutating.value = false
  }
}

async function confirmDelete(program) {
  const name = program?.name || ''
  const ok = await confirm({
    title: t('adminCommon.delete'),
    message: t('adminPrograms.deleteConfirm', { name }),
    confirmText: t('adminCommon.delete'),
    cancelText: t('adminCommon.cancel'),
    variant: 'danger',
  })
  if (!ok) return
  mutating.value = true
  try {
    await api.delete(`/api/programs/${program.id}/`)
    success(t('adminPrograms.toastDeleted'))
    await fetchPrograms()
  } catch (err) {
    console.error('Failed to delete program:', err)
    errorToast(t('adminPrograms.deleteToastError'))
  } finally {
    mutating.value = false
  }
}

onMounted(async () => {
  await Promise.all([fetchEditorOptions(), fetchPrograms()])
})
</script>

<style scoped>
.admin-programs-page {
  min-height: 60vh;
}
</style>

