<template>
  <div class="application-subjects-panel" data-testid="subjects-section">
    <h5 v-if="showHeading" class="mb-2">
      <i class="bi bi-journal-text me-2"></i>{{ t('applicationSubjects.title') }}
      <span class="badge text-bg-secondary ms-2">{{ t('applicationSubjects.optionalBadge') }}</span>
    </h5>
    <p v-if="showHeading" class="text-muted small mb-3">{{ t('applicationSubjects.help') }}</p>

    <div v-if="!applicationId" class="alert alert-light border mb-0" data-testid="subjects-save-first">
      {{ t('applicationSubjects.saveFirst') }}
    </div>

    <template v-else>
      <div v-if="error" class="alert alert-danger py-2" role="alert">{{ error }}</div>

      <div v-if="canEditMapping" class="row g-2 align-items-end mb-3">
        <div class="col-md-5">
          <label class="form-label" for="subject-catalog-pick">{{ t('applicationSubjects.hostSubjectLabel') }}</label>
          <select
            id="subject-catalog-pick"
            v-model="catalogDraft.host_subject"
            class="form-select"
            data-testid="host-subject-select"
          >
            <option value="">{{ t('applicationSubjects.selectHostSubject') }}</option>
            <option v-for="subj in availableHostSubjects" :key="subj.id" :value="subj.id">
              {{ formatHostSubjectOption(subj) }}
            </option>
          </select>
          <div v-if="!hostSubjects.length && !hostSubjectsLoading" class="form-text">
            {{ t('applicationSubjects.noHostSubjects') }}
          </div>
        </div>
        <div class="col-md-3">
          <label class="form-label" for="home-course-code">{{ t('applicationSubjects.homeCourseCodeLabel') }}</label>
          <input id="home-course-code" v-model="catalogDraft.home_course_code" type="text" class="form-control" maxlength="64">
        </div>
        <div class="col-md-4">
          <label class="form-label" for="home-course-label">{{ t('applicationSubjects.homeCourseLabelLabel') }}</label>
          <input id="home-course-label" v-model="catalogDraft.home_course_label" type="text" class="form-control" maxlength="255">
        </div>
        <div class="col-12">
          <button
            type="button"
            class="btn btn-outline-primary btn-sm"
            :disabled="!catalogDraft.host_subject || saving"
            data-testid="add-subject-selection"
            @click="addCatalogSelection"
          >
            <i class="bi bi-plus-lg me-1"></i>{{ t('applicationSubjects.addSubjectSelection') }}
          </button>
        </div>
      </div>

      <div v-if="canEditMapping" class="border rounded p-3 mb-3" data-testid="custom-subject-form">
        <div class="fw-medium mb-2">{{ t('applicationSubjects.customTitle') }}</div>
        <div class="row g-2 align-items-end">
          <div class="col-md-2">
            <label class="form-label" for="custom-code">{{ t('applicationSubjects.customCodeLabel') }}</label>
            <input id="custom-code" v-model="customDraft.custom_code" type="text" class="form-control" maxlength="64">
          </div>
          <div class="col-md-4">
            <label class="form-label" for="custom-name">{{ t('applicationSubjects.customNameLabel') }}</label>
            <input id="custom-name" v-model="customDraft.custom_name" type="text" class="form-control" maxlength="255">
          </div>
          <div class="col-md-2">
            <label class="form-label" for="custom-credits">{{ t('applicationSubjects.customCreditsLabel') }}</label>
            <input id="custom-credits" v-model="customDraft.custom_credits" type="number" min="0" step="0.5" class="form-control">
          </div>
          <div class="col-md-2">
            <label class="form-label" for="custom-home-code">{{ t('applicationSubjects.homeCourseCodeLabel') }}</label>
            <input id="custom-home-code" v-model="customDraft.home_course_code" type="text" class="form-control" maxlength="64">
          </div>
          <div class="col-md-2">
            <label class="form-label" for="custom-home-label">{{ t('applicationSubjects.homeCourseLabelLabel') }}</label>
            <input id="custom-home-label" v-model="customDraft.home_course_label" type="text" class="form-control" maxlength="255">
          </div>
          <div class="col-12">
            <button
              type="button"
              class="btn btn-outline-primary btn-sm"
              :disabled="!customDraft.custom_name || saving"
              data-testid="add-custom-subject"
              @click="addCustomSelection"
            >
              <i class="bi bi-plus-lg me-1"></i>{{ t('applicationSubjects.addCustomSubject') }}
            </button>
          </div>
        </div>
      </div>

      <div v-if="loading" class="form-text">{{ t('applicationSubjects.loadingSelections') }}</div>
      <div
        v-else-if="!selections.length"
        class="alert alert-light border small mb-3"
        data-testid="subjects-empty"
      >
        {{ t('applicationSubjects.empty') }}
      </div>
      <div v-else class="table-responsive mb-3">
        <table class="table table-sm align-middle" data-testid="subject-selections-table">
          <thead>
            <tr>
              <th>{{ t('applicationSubjects.hostSubjectLabel') }}</th>
              <th>{{ t('applicationSubjects.homeCourseCodeLabel') }}</th>
              <th>{{ t('applicationSubjects.homeCourseLabelLabel') }}</th>
              <th>{{ t('applicationSubjects.creditsLabel') }}</th>
              <th v-if="showGradeColumns">{{ t('applicationSubjects.hostGradeLabel') }}</th>
              <th v-if="showGradeColumns">{{ t('applicationSubjects.homeGradeLabel') }}</th>
              <th>{{ t('applicationSubjects.statusLabel') }}</th>
              <th class="text-end">{{ t('applicationSubjects.actionsLabel') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="sel in selections" :key="sel.id">
              <td>{{ hostCourseLabel(sel) }}</td>
              <td>{{ sel.home_course_code || '—' }}</td>
              <td>{{ sel.home_course_label || '—' }}</td>
              <td>{{ sel.credits ?? sel.custom_credits ?? sel.host_subject_detail?.credits ?? '—' }}</td>
              <td v-if="showGradeColumns">
                <select
                  v-if="canProposeGrades && sel.grade_status !== 'confirmed'"
                  class="form-select form-select-sm"
                  :value="sel.proposed_host_grade || ''"
                  :data-testid="`proposed-grade-${sel.id}`"
                  @change="onProposedGradeChange(sel, $event.target.value)"
                >
                  <option value="">{{ t('applicationSubjects.selectGrade') }}</option>
                  <option v-for="gv in hostGradeValues" :key="gv.id" :value="gv.id">
                    {{ gv.label }}
                  </option>
                </select>
                <span v-else>
                  {{ sel.confirmed_host_grade_label || sel.proposed_host_grade_label || '—' }}
                </span>
              </td>
              <td v-if="showGradeColumns">
                {{ sel.home_grade_label || '—' }}
              </td>
              <td>
                <span class="badge" :class="gradeStatusBadge(sel.grade_status)">
                  {{ t(`applicationSubjects.gradeStatus.${sel.grade_status || 'none'}`) }}
                </span>
              </td>
              <td class="text-end">
                <button
                  v-if="canEditMapping"
                  type="button"
                  class="btn btn-outline-danger btn-sm"
                  :disabled="saving"
                  :data-testid="`remove-subject-${sel.id}`"
                  @click="removeSelection(sel)"
                >
                  <i class="bi bi-trash"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="d-flex flex-wrap gap-2 mb-2">
        <button
          type="button"
          class="btn btn-outline-secondary btn-sm"
          :disabled="cartaDownloading"
          data-testid="download-carta-homologacion"
          @click="downloadCarta"
        >
          <i class="bi bi-file-earmark-pdf me-1"></i>
          {{ t('applicationSubjects.downloadCarta') }}
        </button>
        <button
          v-if="canProposeGrades"
          type="button"
          class="btn btn-primary btn-sm"
          :disabled="saving || !hasProposedGrade"
          data-testid="propose-subject-grades"
          @click="proposeGrades"
        >
          {{ t('applicationSubjects.submitGrades') }}
        </button>
        <button
          v-if="isCoordinator && canConfirm"
          type="button"
          class="btn btn-success btn-sm"
          :disabled="saving"
          data-testid="confirm-subject-grades"
          @click="confirmGrades"
        >
          {{ t('applicationSubjects.confirmGrades') }}
        </button>
        <button
          v-if="isCoordinator && canReject"
          type="button"
          class="btn btn-outline-warning btn-sm"
          :disabled="saving"
          data-testid="reject-subject-grades"
          @click="rejectGrades"
        >
          {{ t('applicationSubjects.rejectGrades') }}
        </button>
      </div>
      <div v-if="isCoordinator && canReject" class="mb-2">
        <label class="form-label" for="grade-notes">{{ t('applicationSubjects.confirmationNotes') }}</label>
        <textarea id="grade-notes" v-model="confirmationNotes" class="form-control form-control-sm" rows="2"></textarea>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useToast } from '@/composables/useToast'

const GRADEABLE = new Set(['approved', 'nominated', 'completed'])

const props = defineProps({
  applicationId: { type: [String, Number], default: '' },
  applicationStatus: { type: String, default: '' },
  hostInstitutionId: { type: [String, Number], default: '' },
  isCoordinator: { type: Boolean, default: false },
  showHeading: { type: Boolean, default: true },
})

const emit = defineEmits(['updated'])

const { t } = useI18n()
const { success, error: errorToast } = useToast()

const loading = ref(false)
const saving = ref(false)
const cartaDownloading = ref(false)
const hostSubjectsLoading = ref(false)
const error = ref('')
const selections = ref([])
const hostSubjects = ref([])
const hostGradeValues = ref([])
const confirmationNotes = ref('')
const catalogDraft = ref({ host_subject: '', home_course_code: '', home_course_label: '' })
const customDraft = ref({
  custom_code: '',
  custom_name: '',
  custom_credits: '',
  home_course_code: '',
  home_course_label: '',
})

const gradesLocked = computed(() =>
  selections.value.some((s) => s.grade_status === 'proposed' || s.grade_status === 'confirmed'),
)
const canEditMapping = computed(() => Boolean(props.applicationId) && !gradesLocked.value)
const showGradeColumns = computed(() =>
  GRADEABLE.has(props.applicationStatus) || selections.value.some((s) => s.grade_status && s.grade_status !== 'none'),
)
const canProposeGrades = computed(() =>
  Boolean(props.applicationId)
  && GRADEABLE.has(props.applicationStatus)
  && selections.value.some((s) => s.grade_status !== 'confirmed'),
)
const hasProposedGrade = computed(() =>
  selections.value.some((s) => s.proposed_host_grade && s.grade_status !== 'confirmed'),
)
const canConfirm = computed(() =>
  selections.value.some((s) => s.grade_status === 'proposed' || s.proposed_host_grade),
)
const canReject = computed(() =>
  selections.value.some((s) => s.grade_status === 'proposed' || s.grade_status === 'confirmed'),
)

const availableHostSubjects = computed(() => {
  const selectedIds = new Set(
    selections.value.filter((s) => s.host_subject).map((s) => String(s.host_subject)),
  )
  return hostSubjects.value.filter((s) => !selectedIds.has(String(s.id)))
})

function formatHostSubjectOption(subj) {
  if (!subj || typeof subj !== 'object') return String(subj || '')
  const code = subj.code ? `${subj.code} — ` : ''
  const credits = subj.credits != null && subj.credits !== '' ? ` (${subj.credits})` : ''
  return `${code}${subj.name || ''}${credits}`
}

function hostCourseLabel(sel) {
  if (sel.host_course_code || sel.host_course_name) {
    const code = sel.host_course_code ? `${sel.host_course_code} — ` : ''
    return `${code}${sel.host_course_name || ''}`.trim() || '—'
  }
  if (sel.custom_name) {
    const code = sel.custom_code ? `${sel.custom_code} — ` : ''
    return `${code}${sel.custom_name}`
  }
  return formatHostSubjectOption(sel.host_subject_detail || sel.host_subject)
}

function gradeStatusBadge(status) {
  if (status === 'confirmed') return 'bg-success'
  if (status === 'proposed') return 'bg-warning text-dark'
  if (status === 'rejected') return 'bg-danger'
  return 'bg-secondary'
}

function unwrapList(data) {
  if (Array.isArray(data)) return data
  if (data && Array.isArray(data.results)) return data.results
  return []
}

async function fetchSelections() {
  if (!props.applicationId) {
    selections.value = []
    return
  }
  loading.value = true
  try {
    const { data } = await api.get('/api/application-subject-selections/', {
      params: { application: props.applicationId },
    })
    selections.value = unwrapList(data)
  } catch (err) {
    console.error('Failed to load subject selections:', err)
    selections.value = []
  } finally {
    loading.value = false
  }
}

async function fetchAvailableSubjects() {
  if (!props.applicationId) {
    hostSubjects.value = []
    return
  }
  hostSubjectsLoading.value = true
  try {
    const { data } = await api.get(`/api/applications/${props.applicationId}/available-subjects/`)
    hostSubjects.value = unwrapList(data)
  } catch (err) {
    console.error('Failed to load available subjects:', err)
    hostSubjects.value = []
  } finally {
    hostSubjectsLoading.value = false
  }
}

async function fetchHostGradeValues() {
  hostGradeValues.value = []
  if (!props.hostInstitutionId || !props.applicationId) return
  try {
    const { data } = await api.get(`/api/host-institutions/${props.hostInstitutionId}/`)
    const scaleId = data.grade_scale
    if (!scaleId) return
    const values = await api.get('/api/grades/values/', { params: { grade_scale: scaleId } })
    hostGradeValues.value = unwrapList(values.data)
  } catch (err) {
    console.error('Failed to load host grade values:', err)
  }
}

async function addCatalogSelection() {
  if (!props.applicationId || !catalogDraft.value.host_subject) return
  saving.value = true
  error.value = ''
  try {
    const { data } = await api.post('/api/application-subject-selections/', {
      application: props.applicationId,
      host_subject: catalogDraft.value.host_subject,
      home_course_code: catalogDraft.value.home_course_code || '',
      home_course_label: catalogDraft.value.home_course_label || '',
    })
    selections.value = [...selections.value, data]
    catalogDraft.value = { host_subject: '', home_course_code: '', home_course_label: '' }
    success(t('applicationSubjects.toastAdded'))
    emit('updated')
  } catch (err) {
    console.error('Failed to add subject:', err)
    errorToast(t('applicationSubjects.toastAddFailed'))
  } finally {
    saving.value = false
  }
}

async function addCustomSelection() {
  if (!props.applicationId || !customDraft.value.custom_name) return
  saving.value = true
  error.value = ''
  try {
    const payload = {
      application: props.applicationId,
      custom_code: customDraft.value.custom_code || '',
      custom_name: customDraft.value.custom_name,
      home_course_code: customDraft.value.home_course_code || '',
      home_course_label: customDraft.value.home_course_label || '',
    }
    if (customDraft.value.custom_credits !== '' && customDraft.value.custom_credits != null) {
      payload.custom_credits = customDraft.value.custom_credits
    }
    const { data } = await api.post('/api/application-subject-selections/', payload)
    selections.value = [...selections.value, data]
    customDraft.value = {
      custom_code: '',
      custom_name: '',
      custom_credits: '',
      home_course_code: '',
      home_course_label: '',
    }
    success(t('applicationSubjects.toastAdded'))
    emit('updated')
  } catch (err) {
    console.error('Failed to add custom subject:', err)
    errorToast(t('applicationSubjects.toastAddFailed'))
  } finally {
    saving.value = false
  }
}

async function removeSelection(sel) {
  if (!sel?.id) return
  saving.value = true
  try {
    await api.delete(`/api/application-subject-selections/${sel.id}/`)
    selections.value = selections.value.filter((s) => s.id !== sel.id)
    success(t('applicationSubjects.toastRemoved'))
    emit('updated')
  } catch (err) {
    console.error('Failed to remove subject:', err)
    errorToast(t('applicationSubjects.toastRemoveFailed'))
  } finally {
    saving.value = false
  }
}

async function onProposedGradeChange(sel, gradeId) {
  saving.value = true
  try {
    const { data } = await api.patch(`/api/application-subject-selections/${sel.id}/`, {
      proposed_host_grade: gradeId || null,
    })
    selections.value = selections.value.map((s) => (s.id === sel.id ? data : s))
  } catch (err) {
    console.error('Failed to save proposed grade:', err)
    errorToast(t('applicationSubjects.toastGradeSaveFailed'))
  } finally {
    saving.value = false
  }
}

async function downloadCarta() {
  if (!props.applicationId) return
  cartaDownloading.value = true
  try {
    const response = await api.get(`/api/applications/${props.applicationId}/carta-homologacion/`, {
      responseType: 'blob',
    })
    const blob = new Blob([response.data], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `carta_homologacion_${props.applicationId}.pdf`
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    success(
      selections.value.length
        ? t('applicationSubjects.toastCartaDownloaded')
        : t('applicationSubjects.toastCartaEmpty'),
    )
  } catch (err) {
    console.error('Failed to download carta:', err)
    errorToast(t('applicationSubjects.toastCartaFailed'))
  } finally {
    cartaDownloading.value = false
  }
}

async function proposeGrades() {
  saving.value = true
  try {
    await api.post(`/api/applications/${props.applicationId}/propose-subject-grades/`)
    await fetchSelections()
    success(t('applicationSubjects.toastProposed'))
    emit('updated')
  } catch (err) {
    console.error('Failed to propose grades:', err)
    errorToast(err.response?.data?.error || t('applicationSubjects.toastProposeFailed'))
  } finally {
    saving.value = false
  }
}

async function confirmGrades() {
  saving.value = true
  try {
    await api.post(`/api/applications/${props.applicationId}/confirm-subject-grades/`, {
      notes: confirmationNotes.value,
    })
    await fetchSelections()
    success(t('applicationSubjects.toastConfirmed'))
    emit('updated')
  } catch (err) {
    console.error('Failed to confirm grades:', err)
    errorToast(err.response?.data?.error || t('applicationSubjects.toastConfirmFailed'))
  } finally {
    saving.value = false
  }
}

async function rejectGrades() {
  saving.value = true
  try {
    await api.post(`/api/applications/${props.applicationId}/reject-subject-grades/`, {
      notes: confirmationNotes.value,
    })
    await fetchSelections()
    success(t('applicationSubjects.toastRejected'))
    emit('updated')
  } catch (err) {
    console.error('Failed to reject grades:', err)
    errorToast(err.response?.data?.error || t('applicationSubjects.toastRejectFailed'))
  } finally {
    saving.value = false
  }
}

watch(
  () => [props.applicationId, props.hostInstitutionId],
  async () => {
    await Promise.all([fetchSelections(), fetchAvailableSubjects(), fetchHostGradeValues()])
  },
  { immediate: true },
)
</script>
