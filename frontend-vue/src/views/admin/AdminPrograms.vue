<template>
  <div class="admin-programs-page">
    <PageHeader :title="t('adminPrograms.title')">
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

      <template #subtitle>
        {{ t('adminPrograms.subtitle') }}
        <span class="d-block mt-1">{{ t('adminPrograms.destinationsHint') }}</span>
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
              <th scope="col" class="text-nowrap">{{ t('adminCommon.actions') }}</th>
              <th scope="col">{{ t('adminPrograms.columns.name') }}</th>
              <th scope="col" class="text-nowrap">{{ t('adminPrograms.columns.window') }}</th>
              <th scope="col" class="text-nowrap">{{ t('adminPrograms.columns.active') }}</th>
              <th scope="col" class="text-nowrap">{{ t('adminPrograms.columns.capacity') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!programs.length">
              <td colspan="5" class="text-muted text-center py-4">
                {{ t('adminPrograms.empty') }}
              </td>
            </tr>
            <tr v-for="p in programs" :key="p.id">
              <td class="text-nowrap">
                <button type="button" class="btn btn-sm btn-outline-secondary me-2" @click="openEdit(p)">
                  <i class="bi bi-pencil me-1" aria-hidden="true"></i>{{ t('adminCommon.edit') }}
                </button>
                <router-link
                  class="btn btn-sm btn-outline-secondary me-2"
                  :to="{ name: 'AdminProgramDestinations', params: { id: p.id } }"
                >
                  <i class="bi bi-geo-alt me-1" aria-hidden="true"></i>{{ t('adminPrograms.destinations') }}
                </router-link>
                <button type="button" class="btn btn-sm btn-outline-primary me-2" @click="cloneProgram(p)" :disabled="mutating">
                  <i class="bi bi-files me-1" aria-hidden="true"></i>{{ t('adminPrograms.clone') }}
                </button>
                <button type="button" class="btn btn-sm btn-outline-danger" @click="confirmDelete(p)" :disabled="mutating">
                  <i class="bi bi-trash me-1" aria-hidden="true"></i>{{ t('adminCommon.delete') }}
                </button>
              </td>
              <td class="program-name-cell min-w-0">
                <div class="fw-medium text-truncate">{{ p.name }}</div>
                <div
                  v-if="p.description"
                  class="program-description-wrap"
                >
                  <div
                    class="program-description text-muted small"
                    tabindex="0"
                    data-testid="admin-program-description"
                  >
                    {{ p.description }}
                  </div>
                </div>
              </td>
              <td class="text-nowrap small">
                <span class="badge" :class="p.application_window_open ? 'bg-success' : 'bg-secondary'">
                  {{ p.application_window_open ? t('adminPrograms.windowOpen') : t('adminPrograms.windowClosed') }}
                </span>
                <div class="text-muted small mt-1">{{ formatWindowDates(p) }}</div>
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
                <input v-model="editor.form.name" class="form-control" type="text" required />
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
                <textarea v-model="editor.form.description" class="form-control" rows="3" required></textarea>
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
                <input v-model="editor.form.start_date" class="form-control" type="date" required />
              </div>
              <div class="col-md-6">
                <label class="form-label">{{ t('adminPrograms.fields.endDate') }}</label>
                <input v-model="editor.form.end_date" class="form-control" type="date" required />
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
                <label class="form-label">{{ t('adminPrograms.fields.minSemester') }}</label>
                <input v-model.number="editor.form.min_semester" class="form-control" type="number" min="1" step="1" />
              </div>
              <div class="col-md-4">
                <label class="form-label">{{ t('adminPrograms.fields.minCredits') }}</label>
                <input v-model.number="editor.form.min_credits_approved_percent" class="form-control" type="number" min="0" max="100" step="0.01" />
              </div>
              <div class="col-md-6">
                <label class="form-label">{{ t('adminPrograms.fields.requiredLanguage') }}</label>
                <input v-model="editor.form.required_language" class="form-control" type="text" />
              </div>
              <div class="col-md-6">
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

              <div class="col-12">
                <label class="form-label">{{ t('adminPrograms.fields.eligibilityRuleset') }}</label>
                <select
                  v-model="editor.form.eligibility_ruleset"
                  class="form-select"
                  data-testid="admin-program-eligibility-ruleset"
                >
                  <option :value="null">{{ t('adminPrograms.fields.eligibilityRulesetNone') }}</option>
                  <option v-for="rs in visibleEligibilityRulesets" :key="rs.id" :value="rs.id">
                    {{ rs.name }}
                  </option>
                </select>
                <div class="form-text">{{ t('adminPrograms.fields.eligibilityRulesetHelp') }}</div>
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
                <label class="form-label">{{ t('adminPrograms.fields.fieldRequirements') }}</label>
                <p class="form-text mt-0">{{ t('adminPrograms.fields.fieldRequirementsHelp') }}</p>
                <div class="table-responsive">
                  <table class="table table-sm align-middle" data-testid="admin-program-field-requirements">
                    <thead>
                      <tr>
                        <th>{{ t('adminPrograms.fields.fieldSource') }}</th>
                        <th>{{ t('adminPrograms.fields.fieldKey') }}</th>
                        <th>{{ t('adminPrograms.fields.requiredFrom') }}</th>
                        <th></th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-if="!editor.form.field_requirements.length">
                        <td colspan="4" class="text-muted small">{{ t('adminPrograms.fields.fieldRequirementsEmpty') }}</td>
                      </tr>
                      <tr v-for="(row, idx) in editor.form.field_requirements" :key="`${row.source}-${row.field_key}-${idx}`">
                        <td>
                          <select
                            v-model="row.source"
                            class="form-select form-select-sm"
                            data-testid="admin-program-field-source"
                            @change="onFieldSourceChange(row)"
                          >
                            <option value="profile">{{ t('adminPrograms.fields.sourceProfile') }}</option>
                            <option value="application">{{ t('adminPrograms.fields.sourceApplication') }}</option>
                            <option value="form">{{ t('adminPrograms.fields.sourceForm') }}</option>
                          </select>
                        </td>
                        <td>
                          <select
                            v-model="row.field_key"
                            class="form-select form-select-sm"
                            data-testid="admin-program-field-key"
                          >
                            <option
                              v-if="row.source === 'form' && !fieldKeysForSource('form').length"
                              value=""
                              disabled
                            >
                              {{ t('adminPrograms.fields.noFormKeys') }}
                            </option>
                            <option v-for="key in fieldKeysForSource(row.source)" :key="key" :value="key">{{ key }}</option>
                          </select>
                        </td>
                        <td>
                          <select v-model="row.required_from_status" class="form-select form-select-sm">
                            <option :value="null">{{ t('adminPrograms.fields.optionalThroughout') }}</option>
                            <option v-for="st in fieldPipelineStatuses" :key="st" :value="st">
                              {{ t(`applicationDetailPage.status.${st}`) }}
                            </option>
                          </select>
                        </td>
                        <td class="text-end">
                          <button type="button" class="btn btn-sm btn-outline-danger" @click="editor.form.field_requirements.splice(idx, 1)">
                            {{ t('adminCommon.delete') }}
                          </button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <p class="form-text mb-0">{{ t('adminPrograms.fields.fieldRequirementsFormHelp') }}</p>
                <button type="button" class="btn btn-sm btn-outline-primary" data-testid="admin-program-add-field-req" @click="addFieldRequirement">
                  {{ t('adminPrograms.fields.addFieldRequirement') }}
                </button>
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
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useToast } from '@/composables/useToast'
import { useConfirm } from '@/composables/useConfirm'
import { formatDate } from '@/utils/formatters'
import PageHeader from '@/components/PageHeader.vue'

const { t, locale } = useI18n()
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

function formatWindowDate(dateString) {
  if (!dateString) return ''
  const value = /^\d{4}-\d{2}-\d{2}/.test(dateString)
    ? `${String(dateString).slice(0, 10)}T12:00:00`
    : dateString
  return formatDate({ dateString: value, locale: locale.value, fallback: '' })
}

function formatWindowDates(program) {
  const open = formatWindowDate(program.application_open_date)
  const close = formatWindowDate(program.application_deadline)
  if (open && close) return t('adminPrograms.windowRange', { open, close })
  if (open) return t('adminPrograms.windowFrom', { date: open })
  if (close) return t('adminPrograms.windowUntil', { date: close })
  return t('adminPrograms.windowAlways')
}

const cefrOptions = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
const fieldPipelineStatuses = ['draft', 'submitted', 'under_review', 'nominated', 'approved', 'completed']
const defaultFieldCatalog = {
  profile: ['passport_number', 'rfc', 'bank_institution', 'clabe'],
  application: ['host_institution', 'host_school', 'host_academic_program', 'host_destination'],
  form: [],
}

function formKeysFromSelectedForm() {
  const formId = editor.value.form.application_form
  const ft = formTypes.value.find((f) => String(f.id) === String(formId))
  const properties = ft?.schema?.properties
  if (!properties || typeof properties !== 'object') return []
  return Object.keys(properties)
}

function refreshFormCatalog() {
  const catalog = { ...(editor.value.form._catalog || defaultFieldCatalog) }
  catalog.form = formKeysFromSelectedForm()
  editor.value.form._catalog = catalog
}

function fieldKeysForSource(source) {
  const catalog = editor.value.form._catalog || defaultFieldCatalog
  if (source === 'application') return catalog.application || defaultFieldCatalog.application
  if (source === 'form') return catalog.form || []
  return catalog.profile || defaultFieldCatalog.profile
}

function onFieldSourceChange(row) {
  const keys = fieldKeysForSource(row.source)
  if (!keys.includes(row.field_key)) {
    row.field_key = keys[0] || ''
  }
}

function addFieldRequirement() {
  const keys = fieldKeysForSource('profile')
  editor.value.form.field_requirements.push({
    source: 'profile',
    field_key: keys[0] || 'clabe',
    required_from_status: 'approved',
  })
}

const formTypes = ref([])
const workflowVersions = ref([])
const coordinators = ref([])
const documentTypes = ref([])
const eligibilityRulesets = ref([])

const editor = ref({
  open: false,
  mode: 'create',
  id: null,
  saving: false,
  error: null,
  form: emptyProgramForm(),
})

watch(
  () => [editor.value.form.application_form, formTypes.value],
  () => {
    refreshFormCatalog()
  },
)

const visibleEligibilityRulesets = computed(() => {
  const selected = editor.value.form.eligibility_ruleset
  return eligibilityRulesets.value.filter((rs) => rs.is_active || rs.id === selected)
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
    min_semester: null,
    min_credits_approved_percent: null,
    required_language: '',
    min_language_level: '',
    min_age: null,
    max_age: null,
    auto_reject_ineligible: false,
    enrollment_capacity: null,
    waitlist_when_full: true,
    application_form: null,
    workflow_version: null,
    eligibility_ruleset: null,
    coordinators: [],
    required_document_types: [],
    field_requirements: [],
    _catalog: defaultFieldCatalog,
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
  const [ftRes, userRes, dtRes, wvRes, rsRes] = await Promise.all([
    api.get('/api/application-forms/form-types/', { params: { ordering: 'name' } }),
    api.get('/api/users/'),
    api.get('/api/document-types/', { params: { ordering: 'name' } }),
    api.get('/api/workflow-versions/', { params: { ordering: '-version' } }),
    api.get('/api/eligibility-rulesets/', { params: { ordering: 'name' } }),
  ])
  formTypes.value = normalizeApiList(ftRes.data)
  const allUsers = normalizeApiList(userRes.data)
  coordinators.value = allUsers.filter((u) => u.role === 'coordinator')
  documentTypes.value = normalizeApiList(dtRes.data)
  workflowVersions.value = normalizeApiList(wvRes.data).filter((v) => v.status === 'published')
  eligibilityRulesets.value = normalizeApiList(rsRes.data)
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
      min_semester: program.min_semester ?? null,
      min_credits_approved_percent: program.min_credits_approved_percent ?? null,
      required_language: program.required_language || '',
      min_language_level: program.min_language_level || '',
      min_age: program.min_age ?? null,
      max_age: program.max_age ?? null,
      auto_reject_ineligible: Boolean(program.auto_reject_ineligible),
      enrollment_capacity: program.enrollment_capacity ?? null,
      waitlist_when_full: Boolean(program.waitlist_when_full),
      application_form: program.application_form ?? null,
      workflow_version: program.workflow_version ?? null,
      eligibility_ruleset: program.eligibility_ruleset ?? null,
      coordinators: Array.isArray(program.coordinators) ? program.coordinators : [],
      required_document_types: Array.isArray(program.required_document_types) ? program.required_document_types : [],
      field_requirements: (program.field_requirements || []).map((row) => ({
        id: row.id,
        source: row.source,
        field_key: row.field_key,
        required_from_status: row.required_from_status || null,
      })),
      _catalog: {
        ...defaultFieldCatalog,
        ...(program.field_requirement_catalog || {}),
      },
    },
  }
  refreshFormCatalog()
}

function closeEditor() {
  editor.value.open = false
}

function formatApiError(err, fallback) {
  const data = err?.response?.data
  if (typeof data?.detail === 'string') return data.detail
  if (data && typeof data === 'object' && !Array.isArray(data)) {
    const parts = []
    for (const [key, value] of Object.entries(data)) {
      if (Array.isArray(value)) parts.push(`${key}: ${value.join(' ')}`)
      else if (typeof value === 'string') parts.push(`${key}: ${value}`)
    }
    if (parts.length) return parts.join(' ')
  }
  return fallback
}

function cleanProgramPayload(form) {
  const payload = { ...form }
  delete payload._catalog
  if (Array.isArray(payload.field_requirements)) {
    payload.field_requirements = payload.field_requirements.map((row) => ({
      id: row.id || undefined,
      source: row.source,
      field_key: row.field_key,
      required_from_status: row.required_from_status || null,
    }))
  }
  if (payload.required_language === '') payload.required_language = null
  if (payload.min_language_level === '') payload.min_language_level = null
  if (payload.application_open_date === '') payload.application_open_date = null
  if (payload.application_deadline === '') payload.application_deadline = null
  if (payload.start_date === '') payload.start_date = null
  if (payload.end_date === '') payload.end_date = null
  if (payload.application_form === '') payload.application_form = null
  if (payload.workflow_version === '') payload.workflow_version = null
  if (payload.eligibility_ruleset === '') payload.eligibility_ruleset = null
  if (payload.enrollment_capacity === '') payload.enrollment_capacity = null
  if (payload.min_gpa === '') payload.min_gpa = null
  if (payload.min_semester === '') payload.min_semester = null
  if (payload.min_credits_approved_percent === '') payload.min_credits_approved_percent = null
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
    editor.value.error = formatApiError(err, t('adminPrograms.saveError'))
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

.program-name-cell {
  position: relative;
  max-width: 28rem;
}

.program-name-cell:has(.program-description-wrap:hover),
.program-name-cell:has(.program-description-wrap:focus-within) {
  z-index: 5;
}

.program-description-wrap {
  position: relative;
}

.program-description {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 1;
  overflow: hidden;
  word-break: break-word;
  cursor: default;
}

.program-description-wrap:hover .program-description,
.program-description-wrap:focus-within .program-description {
  -webkit-line-clamp: unset;
  display: block;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  z-index: 4;
  padding: 0.35rem 0.5rem;
  background-color: var(--bs-body-bg);
  border: 1px solid var(--bs-border-color);
  border-radius: var(--bs-border-radius);
  box-shadow: var(--bs-box-shadow);
  white-space: pre-wrap;
}

.program-description:focus-visible {
  outline: 2px solid var(--bs-primary);
  outline-offset: 2px;
}
</style>

