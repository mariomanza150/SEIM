<template>
  <div class="admin-application-edit-page" data-testid="admin-application-edit-page">
    <PageHeader :title="t('route.names.AdminApplicationEdit')">
      <template #breadcrumb>
        <nav aria-label="Breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item">
              <router-link :to="{ name: 'Dashboard' }">{{ t('route.names.Dashboard') }}</router-link>
            </li>
            <li class="breadcrumb-item active">{{ t('route.names.AdminApplicationEdit') }}</li>
          </ol>
        </nav>
      </template>
    </PageHeader>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">{{ t('adminCommon.loading') }}</span>
      </div>
      <p class="mt-3 text-muted">{{ t('adminApplicationEdit.loading') }}</p>
    </div>

    <div v-else-if="error" class="alert alert-danger" role="alert">
      <i class="bi bi-exclamation-triangle me-2" aria-hidden="true"></i>
      {{ error }}
    </div>

    <div v-else-if="application" class="row g-3">
      <div class="col-lg-8">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center flex-wrap gap-2">
            <div class="min-w-0">
              <div class="fw-medium text-truncate">
                {{ application.program_name || application.program?.name || t('adminApplicationEdit.unknownProgram') }}
              </div>
              <div class="text-muted small text-truncate">
                {{ t('adminApplicationEdit.applicationId', { id: application.id }) }}
              </div>
            </div>
            <div class="d-flex align-items-center gap-2">
              <span class="badge" :class="statusClass(application.status)">
                {{ application.status || t('adminApplicationEdit.unknownStatus') }}
              </span>
              <button type="button" class="btn btn-sm btn-outline-secondary" :disabled="mutating" @click="reload">
                <i class="bi bi-arrow-clockwise me-1" aria-hidden="true"></i>{{ t('adminCommon.refresh') }}
              </button>
            </div>
          </div>
          <div class="card-body">
            <div class="row g-3">
              <div class="col-md-6">
                <div class="text-muted small">{{ t('adminApplicationEdit.student') }}</div>
                <div class="fw-medium">
                  {{ application.student_display_name || application.student_email || application.student }}
                </div>
              </div>
              <div class="col-md-6">
                <div class="text-muted small">{{ t('adminApplicationEdit.submittedAt') }}</div>
                <div class="fw-medium">{{ application.submitted_at || t('adminApplicationEdit.notAvailable') }}</div>
              </div>

              <div class="col-md-6">
                <label class="form-label">{{ t('adminApplicationEdit.assignedCoordinator') }}</label>
                <select v-model="edit.assigned_coordinator" class="form-select" :disabled="mutating">
                  <option :value="null">{{ t('adminCommon.notSet') }}</option>
                  <option v-for="u in coordinators" :key="u.id" :value="u.id">
                    {{ u.username }} ({{ u.email }})
                  </option>
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label">{{ t('adminApplicationEdit.withdrawn') }}</label>
                <div class="form-check mt-2">
                  <input id="withdrawn" v-model="edit.withdrawn" class="form-check-input" type="checkbox" :disabled="mutating" />
                  <label class="form-check-label" for="withdrawn">{{ t('adminApplicationEdit.withdrawnHelp') }}</label>
                </div>
              </div>
            </div>

            <div class="mt-3 d-flex justify-content-end">
              <button type="button" class="btn btn-primary" :disabled="mutating" @click="saveEdits">
                <span v-if="mutating" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true" />
                {{ t('adminCommon.save') }}
              </button>
            </div>
          </div>
        </div>

        <div class="card mt-3">
          <div class="card-header fw-medium">{{ t('adminApplicationEdit.timeline') }}</div>
          <div class="card-body">
            <div v-if="timelineLoading" class="text-center py-3">
              <div class="spinner-border spinner-border-sm text-primary" role="status" aria-hidden="true" />
            </div>
            <div v-else-if="timelineError" class="alert alert-warning small mb-0">
              {{ timelineError }}
            </div>
            <ul v-else class="list-group list-group-flush">
              <li v-for="evt in timelineEvents" :key="evt.id" class="list-group-item">
                <div class="d-flex justify-content-between align-items-start gap-3">
                  <div class="min-w-0">
                    <div class="fw-medium text-truncate">{{ evt.event_type }}</div>
                    <div class="text-muted small text-break">{{ evt.description }}</div>
                  </div>
                  <div class="text-muted small text-nowrap">{{ evt.created_at }}</div>
                </div>
              </li>
              <li v-if="!timelineEvents.length" class="list-group-item text-muted">
                {{ t('adminApplicationEdit.timelineEmpty') }}
              </li>
            </ul>
          </div>
        </div>
      </div>

      <div class="col-lg-4">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center gap-2">
            <div class="fw-medium">{{ t('adminApplicationEdit.workflow') }}</div>
            <span v-if="workflow.instance" class="badge bg-secondary">{{ workflow.instance.workflow_definition }}</span>
          </div>
          <div class="card-body">
            <div v-if="workflowLoading" class="text-center py-3">
              <div class="spinner-border spinner-border-sm text-primary" role="status" aria-hidden="true" />
            </div>
            <div v-else-if="workflowError" class="alert alert-warning small mb-0">
              {{ workflowError }}
            </div>
            <div v-else>
              <p v-if="!workflow.available_actions?.length" class="text-muted mb-2">
                {{ t('adminApplicationEdit.noWorkflowActions') }}
              </p>
              <div v-else class="d-grid gap-2">
                <button
                  v-for="a in workflow.available_actions"
                  :key="a.id"
                  type="button"
                  class="btn btn-outline-primary"
                  :disabled="mutating"
                  @click="triggerWorkflowAction(a)"
                >
                  {{ a.name || a.spec_id || a.id }}
                </button>
              </div>

              <details class="mt-3">
                <summary class="text-muted small">{{ t('adminApplicationEdit.workflowDebug') }}</summary>
                <pre class="small mb-0 mt-2">{{ workflow }}</pre>
              </details>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useToast } from '@/composables/useToast'
import PageHeader from '@/components/PageHeader.vue'

const { t } = useI18n()
const route = useRoute()
const { success, error: errorToast } = useToast()

const loading = ref(true)
const error = ref(null)
const mutating = ref(false)
const application = ref(null)

const coordinators = ref([])
const edit = ref({
  assigned_coordinator: null,
  withdrawn: false,
})

const workflowLoading = ref(false)
const workflowError = ref(null)
const workflow = ref({ instance: null, available_actions: [] })

const timelineEvents = ref([])
const timelineLoading = ref(false)
const timelineError = ref(null)

function normalizeApiList(data) {
  if (data && typeof data === 'object' && Array.isArray(data.results)) return data.results
  return Array.isArray(data) ? data : []
}

function statusClass(status) {
  const classes = {
    draft: 'bg-secondary',
    submitted: 'bg-info',
    under_review: 'bg-warning',
    approved: 'bg-success',
    rejected: 'bg-danger',
    completed: 'bg-primary',
    cancelled: 'bg-dark',
    waitlist: 'bg-secondary',
  }
  return classes[status] || 'bg-secondary'
}

async function fetchApplication() {
  const id = route.params.id
  const res = await api.get(`/api/applications/${id}/`)
  application.value = res.data
  edit.value.assigned_coordinator = res.data.assigned_coordinator ?? null
  edit.value.withdrawn = Boolean(res.data.withdrawn)
}

async function fetchCoordinators() {
  const res = await api.get('/api/users/')
  coordinators.value = normalizeApiList(res.data).filter((u) => u.role === 'coordinator')
}

async function fetchWorkflow() {
  const id = route.params.id
  workflowLoading.value = true
  workflowError.value = null
  try {
    const res = await api.get(`/api/applications/${id}/workflow/`)
    workflow.value = res.data
  } catch (err) {
    const msg = err.response?.data?.detail
    workflowError.value = typeof msg === 'string' ? msg : t('adminApplicationEdit.workflowLoadError')
  } finally {
    workflowLoading.value = false
  }
}

async function fetchTimeline() {
  const id = route.params.id
  timelineLoading.value = true
  timelineError.value = null
  try {
    const res = await api.get('/api/timeline-events/', { params: { application: id, ordering: 'created_at' } })
    timelineEvents.value = normalizeApiList(res.data)
  } catch (err) {
    console.warn('Failed to fetch timeline events:', err)
    timelineEvents.value = []
    timelineError.value = t('adminApplicationEdit.timelineLoadError')
  } finally {
    timelineLoading.value = false
  }
}

async function reload() {
  loading.value = true
  error.value = null
  try {
    await Promise.all([fetchApplication(), fetchWorkflow(), fetchTimeline()])
  } catch (err) {
    console.error('Failed to reload admin application:', err)
    error.value = t('adminApplicationEdit.loadError')
  } finally {
    loading.value = false
  }
}

async function saveEdits() {
  mutating.value = true
  try {
    await api.patch(`/api/applications/${application.value.id}/`, {
      assigned_coordinator: edit.value.assigned_coordinator,
      withdrawn: Boolean(edit.value.withdrawn),
    })
    success(t('adminApplicationEdit.toastSaved'))
    await reload()
  } catch (err) {
    console.error('Failed to save application edits:', err)
    errorToast(t('adminApplicationEdit.saveToastError'))
  } finally {
    mutating.value = false
  }
}

async function triggerWorkflowAction(actionRow) {
  mutating.value = true
  try {
    await api.post(`/api/applications/${application.value.id}/workflow/action/`, {
      action: actionRow.id,
      payload: {},
    })
    success(t('adminApplicationEdit.toastWorkflowAction'))
    await reload()
  } catch (err) {
    console.error('Failed to trigger workflow action:', err)
    const msg = err.response?.data?.detail
    errorToast(typeof msg === 'string' ? msg : t('adminApplicationEdit.workflowActionToastError'))
  } finally {
    mutating.value = false
  }
}

onMounted(async () => {
  try {
    await Promise.all([fetchCoordinators(), reload()])
  } catch (err) {
    console.error('Admin application edit init failed:', err)
    error.value = t('adminApplicationEdit.loadError')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.admin-application-edit-page {
  min-height: 70vh;
}

pre {
  white-space: pre-wrap;
  word-break: break-word;
  background: rgba(0, 0, 0, 0.03);
  padding: 0.75rem;
  border-radius: 0.5rem;
}
</style>

