<template>
  <div class="admin-document-type-edit">
    <PageHeader :title="pageTitle" :subtitle="t('adminDocuments.editorSubtitle')">
      <template #breadcrumb>
        <PageBreadcrumb
          :aria-label="t('adminCommon.breadcrumbAria')"
          :items="[
            { to: { name: 'Dashboard' }, label: t('route.names.Dashboard') },
            { to: { name: 'AdminDocuments' }, label: t('route.names.AdminDocuments') },
            { label: pageTitle, truncate: true },
          ]"
        />
      </template>
      <template #actions>
        <button type="button" class="btn btn-outline-secondary" :disabled="saving" @click="load">
          <i class="bi bi-arrow-clockwise me-1" aria-hidden="true"></i>{{ t('adminCommon.refresh') }}
        </button>
        <button
          type="button"
          class="btn btn-primary"
          :disabled="saving || loading"
          data-testid="admin-document-type-save"
          @click="save"
        >
          <span v-if="saving" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true" />
          {{ t('adminCommon.save') }}
        </button>
      </template>
    </PageHeader>

    <PageStateShell
      :loading="loading"
      :error="error || ''"
      skeleton="none"
      :loading-label="t('adminCommon.loading')"
    >
    <div class="row g-4">
      <div class="col-lg-8">
        <div v-if="formError" class="alert alert-danger" role="alert">{{ formError }}</div>

        <div class="card mb-4">
          <div class="card-header">{{ t('adminDocuments.sections.identity') }}</div>
          <div class="card-body row g-3">
            <div class="col-md-8">
              <label class="form-label">{{ t('adminDocuments.fields.name') }}</label>
              <input v-model="form.name" class="form-control" type="text" data-testid="admin-document-type-name" />
            </div>
            <div class="col-md-4">
              <label class="form-label">{{ t('adminDocuments.fields.slug') }}</label>
              <input v-model="form.slug" class="form-control" type="text" />
            </div>
            <div class="col-12">
              <label class="form-label">{{ t('adminDocuments.fields.description') }}</label>
              <textarea v-model="form.description" class="form-control" rows="2" />
            </div>
            <div class="col-md-6">
              <label class="form-label">{{ t('adminDocuments.fields.submissionMode') }}</label>
              <select v-model="form.submission_mode" class="form-select">
                <option v-for="opt in submissionModes" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
              </select>
            </div>
            <div class="col-md-6">
              <label class="form-label">{{ t('adminDocuments.fields.allowsMultiple') }}</label>
              <div class="form-check mt-2">
                <input id="allowsMultiple" v-model="form.allows_multiple" class="form-check-input" type="checkbox" />
                <label class="form-check-label" for="allowsMultiple">{{ t('adminDocuments.fields.allowsMultipleHelp') }}</label>
              </div>
            </div>
          </div>
        </div>

        <div class="card mb-4">
          <div class="card-header">{{ t('adminDocuments.sections.instructions') }}</div>
          <div class="card-body row g-3">
            <div class="col-12">
              <label class="form-label">{{ t('adminDocuments.fields.instructions') }}</label>
              <textarea
                v-model="form.instructions"
                class="form-control"
                rows="5"
                data-testid="admin-document-type-instructions"
              />
              <div class="form-text">{{ t('adminDocuments.fields.instructionsHelp') }}</div>
            </div>
            <div class="col-12">
              <label class="form-label">{{ t('adminDocuments.fields.faq') }}</label>
              <textarea v-model="form.faq" class="form-control" rows="3" />
            </div>
          </div>
        </div>

        <div class="card mb-4">
          <div class="card-header">{{ t('adminDocuments.sections.constraints') }}</div>
          <div class="card-body row g-3">
            <div class="col-md-8">
              <label class="form-label">{{ t('adminDocuments.fields.acceptedExtensions') }}</label>
              <input
                v-model="form.accepted_extensions"
                class="form-control"
                type="text"
                :placeholder="t('adminDocuments.fields.acceptedExtensionsPlaceholder')"
              />
              <div class="form-text">{{ t('adminDocuments.fields.acceptedExtensionsHelp') }}</div>
            </div>
            <div class="col-md-4">
              <label class="form-label">{{ t('adminDocuments.fields.maxFileSizeMb') }}</label>
              <input v-model.number="form.max_file_size_mb" class="form-control" type="number" min="1" />
              <div class="form-text">{{ t('adminDocuments.fields.maxFileSizeMbHelp') }}</div>
            </div>
          </div>
        </div>

        <div class="card mb-4">
          <div class="card-header">{{ t('adminDocuments.sections.template') }}</div>
          <div class="card-body">
            <p class="small text-muted">{{ t('adminDocuments.fields.templateHelp') }}</p>
            <p v-if="hasTemplate" class="mb-2">
              <i class="bi bi-file-earmark-word me-1" aria-hidden="true"></i>
              {{ templateFilename || t('adminDocuments.templateAttached') }}
            </p>
            <p v-else class="text-muted small">{{ t('adminDocuments.noTemplate') }}</p>
            <div class="d-flex flex-wrap gap-2 align-items-center">
              <input
                ref="templateInput"
                class="form-control"
                type="file"
                accept=".docx,.doc,.pdf,.odt,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                data-testid="admin-document-type-template"
                @change="onTemplateChosen"
              />
              <button
                type="button"
                class="btn btn-outline-primary"
                :disabled="templateBusy || !pendingTemplate"
                @click="uploadTemplate"
              >
                {{ t('adminDocuments.uploadTemplate') }}
              </button>
              <button
                v-if="hasTemplate"
                type="button"
                class="btn btn-outline-danger"
                :disabled="templateBusy"
                @click="removeTemplate"
              >
                {{ t('adminDocuments.removeTemplate') }}
              </button>
            </div>
          </div>
        </div>

        <div class="card mb-4" data-testid="admin-document-requirements">
          <div class="card-header">{{ t('adminDocuments.sections.workflow') }}</div>
          <div class="card-body">
            <p class="small text-muted">{{ t('adminDocuments.workflowHelp') }}</p>
            <div class="row g-2 align-items-end mb-3">
              <div class="col-md-8">
                <label class="form-label">{{ t('adminDocuments.addProgram') }}</label>
                <select v-model="addProgramId" class="form-select" data-testid="admin-document-add-program">
                  <option value="">{{ t('adminCommon.notSet') }}</option>
                  <option v-for="p in availablePrograms" :key="p.id" :value="p.id">{{ p.name }}</option>
                </select>
              </div>
              <div class="col-md-4">
                <button type="button" class="btn btn-outline-primary w-100" :disabled="!addProgramId" @click="addRequirement">
                  {{ t('adminDocuments.addRequirement') }}
                </button>
              </div>
            </div>
            <div class="table-responsive">
              <table class="table table-sm align-middle mb-0">
                <thead>
                  <tr>
                    <th>{{ t('adminDocuments.req.program') }}</th>
                    <th>{{ t('adminDocuments.req.requiredFrom') }}</th>
                    <th>{{ t('adminDocuments.req.daysAfterStart') }}</th>
                    <th>{{ t('adminDocuments.req.daysBeforeDeadline') }}</th>
                    <th>{{ t('adminDocuments.req.absolute') }}</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="!form.program_requirements.length">
                    <td colspan="6" class="text-muted text-center py-3">{{ t('adminDocuments.req.empty') }}</td>
                  </tr>
                  <tr v-for="(req, idx) in form.program_requirements" :key="req.program">
                    <td>
                      <div class="fw-medium">{{ req.program_name }}</div>
                      <div class="small text-muted">
                        {{ t('adminDocuments.req.resolved', { date: req.resolved_deadline || t('adminCommon.notSet') }) }}
                      </div>
                      <textarea
                        v-model="req.instructions_override"
                        class="form-control form-control-sm mt-1"
                        rows="2"
                        :placeholder="t('adminDocuments.req.instructionsOverride')"
                      />
                    </td>
                    <td>
                      <select
                        v-model="req.required_from_status"
                        class="form-select form-select-sm"
                        data-testid="admin-document-required-from"
                        @change="onRequiredFromChange(req)"
                      >
                        <option value="">{{ t('adminDocuments.req.optionalThroughout') }}</option>
                        <option v-for="st in documentPipelineStatuses" :key="st" :value="st">
                          {{ t(`applicationDetailPage.status.${st}`) }}
                        </option>
                      </select>
                    </td>
                    <td>
                      <input v-model.number="req.deadline_days_after_program_start" class="form-control form-control-sm" type="number" min="0" />
                    </td>
                    <td>
                      <input v-model.number="req.deadline_days_before_program_deadline" class="form-control form-control-sm" type="number" min="0" />
                    </td>
                    <td>
                      <input v-model="req.deadline" class="form-control form-control-sm" type="date" />
                    </td>
                    <td class="text-end">
                      <button type="button" class="btn btn-sm btn-outline-danger" @click="removeRequirement(idx)">
                        {{ t('adminCommon.delete') }}
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <div class="col-lg-4">
        <div class="card mb-4">
          <div class="card-header">{{ t('adminDocuments.sections.mergeFields') }}</div>
          <div class="card-body">
            <p class="small text-muted">{{ t('adminDocuments.mergeFieldsHelp') }}</p>
            <div v-for="group in mergeFieldGroups" :key="group.key" class="mb-3">
              <div class="fw-semibold small text-uppercase text-muted mb-1">{{ group.label }}</div>
              <ul class="list-unstyled small mb-0">
                <li v-for="field in group.fields" :key="field.name" class="mb-1">
                  <code>{{ field.name }}</code>
                  <span class="text-muted"> — {{ field.description }}</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
        <div class="d-grid">
          <button type="button" class="btn btn-outline-danger" :disabled="saving" @click="confirmDelete">
            {{ t('adminDocuments.deleteType') }}
          </button>
        </div>
      </div>
    </div>
    </PageStateShell>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api'
import { useToast } from '@/composables/useToast'
import { useConfirm } from '@/composables/useConfirm'
import PageHeader from '@/components/PageHeader.vue'
import PageBreadcrumb from '@/components/PageBreadcrumb.vue'
import PageStateShell from '@/components/State/PageStateShell.vue'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const { success, error: errorToast } = useToast()
const { confirm } = useConfirm()

const loading = ref(true)
const saving = ref(false)
const error = ref(null)
const formError = ref(null)
const programs = ref([])
const mergeFields = ref([])
const addProgramId = ref('')
const templateInput = ref(null)
const pendingTemplate = ref(null)
const templateBusy = ref(false)
const hasTemplate = ref(false)
const templateFilename = ref('')

const form = ref(emptyForm())
const documentPipelineStatuses = ['submitted', 'under_review', 'nominated', 'approved', 'completed']

function normalizeRequirementRow(row) {
  const requiredFrom = row.is_required === false ? '' : (row.required_from_status || 'submitted')
  return {
    ...row,
    required_from_status: requiredFrom,
    is_required: Boolean(requiredFrom),
  }
}

function onRequiredFromChange(req) {
  req.is_required = Boolean(req.required_from_status)
}

const submissionModes = computed(() => [
  { value: 'upload', label: t('adminDocuments.modes.upload') },
  { value: 'template_download', label: t('adminDocuments.modes.template_download') },
  { value: 'system_generated', label: t('adminDocuments.modes.system_generated') },
  { value: 'instructions_only', label: t('adminDocuments.modes.instructions_only') },
])

const pageTitle = computed(() => form.value.name || t('adminDocuments.editorTitle'))

const availablePrograms = computed(() => {
  const used = new Set(form.value.program_requirements.map((r) => String(r.program)))
  return programs.value.filter((p) => !used.has(String(p.id)))
})

const mergeFieldGroups = computed(() => {
  const groups = [
    { key: 'student', label: t('adminDocuments.mergeGroups.student'), fields: [] },
    { key: 'program', label: t('adminDocuments.mergeGroups.program'), fields: [] },
    { key: 'application', label: t('adminDocuments.mergeGroups.application'), fields: [] },
  ]
  for (const field of mergeFields.value) {
    const group = groups.find((g) => g.key === field.group) || groups[0]
    group.fields.push(field)
  }
  return groups.filter((g) => g.fields.length)
})

function emptyForm() {
  return {
    name: '',
    slug: '',
    description: '',
    submission_mode: 'upload',
    instructions: '',
    faq: '',
    accepted_extensions: '',
    max_file_size_mb: null,
    allows_multiple: false,
    program_requirements: [],
  }
}

function normalizeApiList(data) {
  if (data && typeof data === 'object' && Array.isArray(data.results)) return data.results
  return Array.isArray(data) ? data : []
}

function emptyToNull(value) {
  if (value === '' || value === undefined || Number.isNaN(value)) return null
  return value
}

async function load() {
  loading.value = true
  error.value = null
  try {
    const [typeRes, programRes, fieldsRes] = await Promise.all([
      api.get(`/api/document-types/${route.params.id}/`),
      api.get('/api/programs/', { params: { ordering: 'name', page_size: 100 } }),
      api.get('/api/document-types/merge-fields/'),
    ])
    const dt = typeRes.data || {}
    form.value = {
      name: dt.name || '',
      slug: dt.slug || '',
      description: dt.description || '',
      submission_mode: dt.submission_mode || 'upload',
      instructions: dt.instructions || '',
      faq: dt.faq || '',
      accepted_extensions: dt.accepted_extensions || '',
      max_file_size_mb: dt.max_file_size_mb,
      allows_multiple: Boolean(dt.allows_multiple),
      program_requirements: (dt.program_requirements || []).map((row) => normalizeRequirementRow(row)),
    }
    hasTemplate.value = Boolean(dt.has_template)
    templateFilename.value = dt.template_filename || ''
    programs.value = normalizeApiList(programRes.data)
    mergeFields.value = fieldsRes.data?.fields || []
  } catch (err) {
    console.error('Failed to load document type:', err)
    error.value = t('adminDocuments.loadDetailError')
  } finally {
    loading.value = false
  }
}

function addRequirement() {
  const program = programs.value.find((p) => String(p.id) === String(addProgramId.value))
  if (!program) return
  form.value.program_requirements.push({
    program: program.id,
    program_name: program.name,
    is_required: true,
    required_from_status: 'submitted',
    deadline: null,
    deadline_days_before_program_deadline: null,
    deadline_days_after_program_start: null,
    instructions_override: '',
    sort_order: form.value.program_requirements.length,
    resolved_deadline: null,
  })
  addProgramId.value = ''
}

function removeRequirement(idx) {
  form.value.program_requirements.splice(idx, 1)
}

function onTemplateChosen(event) {
  pendingTemplate.value = event.target.files?.[0] || null
}

async function uploadTemplate() {
  if (!pendingTemplate.value) return
  templateBusy.value = true
  try {
    const data = new FormData()
    data.append('template_file', pendingTemplate.value)
    const res = await api.post(`/api/document-types/${route.params.id}/upload-template/`, data)
    hasTemplate.value = Boolean(res.data?.has_template)
    templateFilename.value = res.data?.template_filename || pendingTemplate.value.name
    pendingTemplate.value = null
    if (templateInput.value) templateInput.value.value = ''
    success(t('adminDocuments.toastTemplateUploaded'))
  } catch (err) {
    console.error('Template upload failed:', err)
    errorToast(t('adminDocuments.templateUploadError'))
  } finally {
    templateBusy.value = false
  }
}

async function removeTemplate() {
  templateBusy.value = true
  try {
    await api.delete(`/api/document-types/${route.params.id}/template/`)
    hasTemplate.value = false
    templateFilename.value = ''
    success(t('adminDocuments.toastTemplateRemoved'))
  } catch (err) {
    console.error('Template remove failed:', err)
    errorToast(t('adminDocuments.templateRemoveError'))
  } finally {
    templateBusy.value = false
  }
}

async function save() {
  formError.value = null
  saving.value = true
  try {
    const payload = {
      name: form.value.name,
      slug: form.value.slug || null,
      description: form.value.description,
      submission_mode: form.value.submission_mode,
      instructions: form.value.instructions,
      faq: form.value.faq,
      accepted_extensions: form.value.accepted_extensions,
      max_file_size_mb: emptyToNull(form.value.max_file_size_mb),
      allows_multiple: Boolean(form.value.allows_multiple),
      program_requirements: form.value.program_requirements.map((row, idx) => ({
        id: row.id || undefined,
        program: row.program,
        is_required: Boolean(row.required_from_status),
        required_from_status: row.required_from_status || null,
        deadline: emptyToNull(row.deadline),
        deadline_days_before_program_deadline: emptyToNull(row.deadline_days_before_program_deadline),
        deadline_days_after_program_start: emptyToNull(row.deadline_days_after_program_start),
        instructions_override: row.instructions_override || '',
        sort_order: idx,
      })),
    }
    const res = await api.patch(`/api/document-types/${route.params.id}/`, payload)
    form.value.program_requirements = (res.data.program_requirements || []).map((row) =>
      normalizeRequirementRow(row),
    )
    success(t('adminDocuments.toastSaved'))
  } catch (err) {
    console.error('Failed to save document type:', err)
    formError.value = t('adminDocuments.saveError')
    errorToast(t('adminDocuments.saveToastError'))
  } finally {
    saving.value = false
  }
}

async function confirmDelete() {
  const ok = await confirm({
    title: t('adminCommon.delete'),
    message: t('adminDocuments.deleteConfirm', { name: form.value.name || '' }),
    confirmText: t('adminCommon.delete'),
    cancelText: t('adminCommon.cancel'),
    variant: 'danger',
  })
  if (!ok) return
  saving.value = true
  try {
    await api.delete(`/api/document-types/${route.params.id}/`)
    success(t('adminDocuments.toastDeleted'))
    await router.push({ name: 'AdminDocuments' })
  } catch (err) {
    console.error('Failed to delete document type:', err)
    errorToast(t('adminDocuments.deleteToastError'))
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  load()
})
</script>

<style scoped>
.admin-document-type-edit {
  min-height: 60vh;
}
</style>
