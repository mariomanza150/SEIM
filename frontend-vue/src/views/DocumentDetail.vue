<template>
  <div class="document-detail">
    <div class="container-fluid mt-4">
      <nav :aria-label="t('documentDetailPage.breadcrumbAria')">
        <ol class="breadcrumb">
          <li class="breadcrumb-item">
            <router-link :to="{ name: 'Dashboard' }">{{ t('route.names.Dashboard') }}</router-link>
          </li>
          <li class="breadcrumb-item">
            <router-link :to="{ name: 'Documents' }">{{ t('route.names.Documents') }}</router-link>
          </li>
          <li class="breadcrumb-item active" aria-current="page">
            {{
              loading
                ? t('documentDetailPage.loadingType')
                : documentTypeLabel(document?.type, '') ||
                  fileName(document?.file) ||
                  t('documentDetailPage.fileUnknown')
            }}
          </li>
        </ol>
      </nav>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">{{ t('documentDetailPage.loadingSpinner') }}</span>
        </div>
        <p class="mt-3 text-muted">{{ t('documentDetailPage.loadingDocument') }}</p>
      </div>

      <div v-else-if="error" class="alert alert-danger">
        <i class="bi bi-exclamation-triangle me-2"></i>
        {{ error }}
        <router-link :to="{ name: 'Documents' }" class="btn btn-sm btn-outline-danger ms-3">
          {{ t('documentDetailPage.backToDocuments') }}
        </router-link>
      </div>

      <div v-else-if="document" data-testid="document-detail-page">
        <div
          v-for="req in openResubmissions"
          :key="req.id"
          class="alert alert-warning d-flex justify-content-between align-items-start"
          role="alert"
        >
          <div>
            <strong>{{ t('documentDetailPage.resubmissionTitle') }}</strong>
            <p class="mb-0 mt-1 small">{{ req.reason }}</p>
            <span class="text-muted small">{{
              t('documentDetailPage.requestedBy', { name: req.requested_by || '—' })
            }}</span>
          </div>
          <button
            v-if="isStaff"
            type="button"
            class="btn btn-sm btn-outline-secondary shrink-0"
            :disabled="actionBusy"
            @click="resolveResubmission(req)"
          >
            {{ t('documentDetailPage.markAddressed') }}
          </button>
        </div>

        <div class="row">
          <div class="col-lg-8">
            <div v-if="document.file" class="card mb-4" data-testid="document-preview-card">
              <div class="card-header">
                <h6 class="mb-0"><i class="bi bi-eye me-2"></i>{{ t('documentDetailPage.previewHeading') }}</h6>
              </div>
              <div class="card-body">
                <p v-if="previewKind === 'none'" class="text-muted small mb-0">
                  {{ t('documentDetailPage.previewNoneHint') }}
                </p>
                <div v-else-if="previewLoading" class="text-center py-5 text-muted">
                  {{ t('documentDetailPage.previewLoading') }}
                </div>
                <div v-else-if="previewError" class="alert alert-warning small mb-0">{{ previewError }}</div>
                <template v-else-if="previewObjectUrl">
                  <iframe
                    v-if="previewKind === 'pdf'"
                    :src="previewObjectUrl"
                    :title="t('documentDetailPage.previewIframeTitle')"
                    class="w-100 border rounded preview-frame"
                  />
                  <img
                    v-else-if="previewKind === 'image'"
                    :src="previewObjectUrl"
                    :alt="t('documentDetailPage.previewImageAlt')"
                    class="img-fluid border rounded"
                  />
                </template>
                <div v-if="previewContextLines.length" class="mt-3 pt-3 border-top small">
                  <div class="fw-semibold mb-2">{{ t('documentDetailPage.reviewContext') }}</div>
                  <ul class="mb-0 ps-3">
                    <li v-for="(line, i) in previewContextLines" :key="i">{{ line }}</li>
                  </ul>
                </div>
              </div>
            </div>

            <div class="card mb-4">
              <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0">
                  <i class="bi bi-file-earmark me-2"></i>
                  {{ fileName(document.file) }}
                </h5>
                <span class="badge fs-6" :class="document.is_valid ? 'bg-success' : 'bg-warning'">
                  {{
                    document.is_valid
                      ? t('documentDetailPage.validated')
                      : t('documentDetailPage.pendingValidation')
                  }}
                </span>
              </div>
              <div class="card-body">
                <div class="row mb-3">
                  <div class="col-md-6">
                    <label class="text-muted small">{{ t('documentDetailPage.labelDocumentType') }}</label>
                    <p class="fw-bold">{{ documentTypeLabel(document.type, t('documentDetailPage.notAvailable')) }}</p>
                  </div>
                  <div class="col-md-6">
                    <label class="text-muted small">{{ t('documentDetailPage.labelApplication') }}</label>
                    <p>
                      <router-link
                        :to="{ name: 'ApplicationDetail', params: { id: documentApplicationId(document.application) } }"
                      >
                        {{
                          documentApplicationProgramName(
                            document.application,
                            applications,
                            t('documentDetailPage.unknownApplication'),
                          )
                        }}
                      </router-link>
                    </p>
                  </div>
                </div>
                <div class="row mb-3">
                  <div class="col-md-6">
                    <label class="text-muted small">{{ t('documentDetailPage.labelUploadedBy') }}</label>
                    <p class="fw-bold">{{ document.uploaded_by || t('documentDetailPage.notAvailable') }}</p>
                  </div>
                  <div class="col-md-6">
                    <label class="text-muted small">{{ t('documentDetailPage.labelUploadedAt') }}</label>
                    <p class="fw-bold">{{ formatDateTime(document.created_at) }}</p>
                  </div>
                </div>
                <div v-if="document.validated_at" class="row mb-3">
                  <div class="col-md-6">
                    <label class="text-muted small">{{ t('documentDetailPage.labelValidatedAt') }}</label>
                    <p class="fw-bold">{{ formatDateTime(document.validated_at) }}</p>
                  </div>
                </div>

                <div class="mt-4 pt-3 border-top">
                  <a
                    v-if="document.file"
                    :href="resolveFileUrl(document.file)"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="btn btn-primary"
                  >
                    <i class="bi bi-download me-2"></i>{{ t('documentDetailPage.downloadDocument') }}
                  </a>
                </div>

                <div v-if="isStudent" class="mt-4 pt-3 border-top">
                  <h6 class="mb-2">{{ t('documentDetailPage.replaceFileHeading') }}</h6>
                  <p class="small text-muted mb-2">
                    {{ t('documentDetailPage.replaceFileHint') }}
                  </p>
                  <input
                    ref="replaceInput"
                    type="file"
                    class="form-control form-control-sm mb-2"
                    accept=".pdf,.jpg,.jpeg,.png,application/pdf,image/jpeg,image/png"
                  />
                  <button
                    type="button"
                    class="btn btn-outline-primary btn-sm"
                    :disabled="actionBusy"
                    @click="submitReplaceFile"
                  >
                    {{ t('documentDetailPage.uploadReplacement') }}
                  </button>
                </div>
              </div>
            </div>

            <div class="card mb-4">
              <div class="card-header">
                <h6 class="mb-0">{{ t('documentDetailPage.reviewHistory') }}</h6>
              </div>
              <div class="card-body">
                <p v-if="!orderedValidations.length" class="text-muted small mb-0">
                  {{ t('documentDetailPage.noValidationsYet') }}
                </p>
                <ul v-else class="list-group list-group-flush">
                  <li
                    v-for="v in orderedValidations"
                    :key="v.id"
                    class="list-group-item px-0"
                  >
                    <div class="d-flex justify-content-between">
                      <span class="badge" :class="v.result === 'valid' ? 'bg-success' : 'bg-secondary'">
                        {{ v.result }}
                      </span>
                      <span class="small text-muted">{{ formatDateTime(v.validated_at || v.created_at) }}</span>
                    </div>
                    <div v-if="v.validator_name" class="small text-muted mt-1">
                      {{ t('documentDetailPage.byValidator', { name: v.validator_name }) }}
                    </div>
                    <div v-if="v.details" class="small mt-1">{{ v.details }}</div>
                  </li>
                </ul>
              </div>
            </div>

            <div class="card mb-4">
              <div class="card-header">
                <h6 class="mb-0">{{ t('documentDetailPage.commentsHeading') }}</h6>
              </div>
              <div class="card-body">
                <div v-if="!document.comments?.length" class="text-muted small mb-3">
                  {{ t('documentDetailPage.noCommentsYet') }}
                </div>
                <div v-for="c in document.comments" :key="c.id" class="border-bottom pb-2 mb-2">
                  <div class="d-flex justify-content-between">
                    <strong class="small">{{ c.author }}</strong>
                    <span class="small text-muted">{{ formatDateTime(c.created_at) }}</span>
                  </div>
                  <span v-if="c.is_private" class="badge bg-secondary small">{{
                    t('documentDetailPage.staffOnlyBadge')
                  }}</span>
                  <p class="small mb-0 mt-1">{{ c.text }}</p>
                </div>
                <div class="mt-3">
                  <label class="form-label small">{{ t('documentDetailPage.addCommentLabel') }}</label>
                  <textarea
                    v-model="newComment"
                    class="form-control form-control-sm mb-2"
                    rows="3"
                    :placeholder="t('documentDetailPage.commentPlaceholder')"
                  />
                  <div v-if="isStaff" class="form-check mb-2">
                    <input id="privComment" v-model="commentPrivate" class="form-check-input" type="checkbox" />
                    <label class="form-check-label small" for="privComment">{{
                      t('documentDetailPage.privateStaffCheckbox')
                    }}</label>
                  </div>
                  <button
                    type="button"
                    class="btn btn-primary btn-sm"
                    :disabled="actionBusy || !newComment.trim()"
                    @click="postComment"
                  >
                    {{ t('documentDetailPage.postComment') }}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div class="col-lg-4">
            <div v-if="isStaff" class="card mb-4">
              <div class="card-header">
                <h6 class="mb-0">{{ t('documentDetailPage.coordinatorActions') }}</h6>
              </div>
              <div class="card-body">
                <label class="form-label small">{{ t('documentDetailPage.requestResubmissionLabel') }}</label>
                <textarea
                  v-model="resubmitReason"
                  class="form-control form-control-sm mb-2"
                  rows="2"
                  :placeholder="t('documentDetailPage.resubmitReasonPlaceholder')"
                />
                <button
                  type="button"
                  class="btn btn-warning btn-sm w-100 mb-3"
                  :disabled="actionBusy || !resubmitReason.trim()"
                  @click="requestResubmission"
                >
                  {{ t('documentDetailPage.requestResubmission') }}
                </button>

                <label class="form-label small">{{ t('documentDetailPage.validationLabel') }}</label>
                <textarea
                  v-model="validationNote"
                  class="form-control form-control-sm mb-2"
                  rows="2"
                  :placeholder="t('documentDetailPage.validationNotePlaceholder')"
                />
                <div class="d-grid gap-2">
                  <button
                    type="button"
                    class="btn btn-success btn-sm"
                    :disabled="actionBusy"
                    @click="validateDoc('valid')"
                  >
                    {{ t('documentDetailPage.markValid') }}
                  </button>
                  <button
                    type="button"
                    class="btn btn-outline-danger btn-sm"
                    :disabled="actionBusy"
                    @click="validateDoc('invalid')"
                  >
                    {{ t('documentDetailPage.markInvalid') }}
                  </button>
                </div>
              </div>
            </div>

            <div class="card mb-4">
              <div class="card-header">
                <h6 class="mb-0">{{ t('documentDetailPage.quickActions') }}</h6>
              </div>
              <div class="card-body">
                <div class="d-grid gap-2">
                  <a
                    v-if="document.file"
                    :href="resolveFileUrl(document.file)"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="btn btn-outline-primary"
                  >
                    <i class="bi bi-download me-2"></i>{{ t('documentDetailPage.download') }}
                  </a>
                  <router-link
                    :to="{ name: 'ApplicationDetail', params: { id: documentApplicationId(document.application) } }"
                    class="btn btn-outline-secondary"
                  >
                    <i class="bi bi-file-earmark-text me-2"></i>{{ t('documentDetailPage.viewApplication') }}
                  </router-link>
                  <router-link :to="{ name: 'Documents' }" class="btn btn-outline-secondary">
                    <i class="bi bi-arrow-left me-2"></i>{{ t('documentDetailPage.backToDocumentsShort') }}
                  </router-link>
                </div>
              </div>
            </div>

            <div class="card">
              <div class="card-header">
                <h6 class="mb-0">{{ t('documentDetailPage.documentInfo') }}</h6>
              </div>
              <div class="card-body">
                <div class="mb-3">
                  <label class="text-muted small">{{ t('documentDetailPage.documentId') }}</label>
                  <p class="small font-monospace">{{ document.id }}</p>
                </div>
                <div class="mb-3">
                  <label class="text-muted small">{{ t('documentDetailPage.statusLabel') }}</label>
                  <p>
                    <span class="badge" :class="document.is_valid ? 'bg-success' : 'bg-warning'">
                      {{
                        document.is_valid
                          ? t('documentDetailPage.statusValidatedShort')
                          : t('documentDetailPage.statusPendingShort')
                      }}
                    </span>
                  </p>
                </div>
                <div class="mb-3">
                  <label class="text-muted small">{{ t('documentDetailPage.lastUpdated') }}</label>
                  <p>{{ formatDateTime(document.updated_at) }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useToast } from '@/composables/useToast'
import { resolveFileUrl } from '@/utils/apiUrl'
import {
  documentApplicationId,
  documentApplicationProgramName,
  documentTypeLabel,
} from '@/utils/documentApi'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const { t, locale } = useI18n()
const authStore = useAuthStore()
const toast = useToast()

const document = ref(null)
const applications = ref([])
const loading = ref(true)
const error = ref(null)
const actionBusy = ref(false)
const newComment = ref('')
const commentPrivate = ref(false)
const resubmitReason = ref('')
const validationNote = ref('')
const replaceInput = ref(null)

const isStaff = computed(() => {
  const r = authStore.userRole
  return r === 'coordinator' || r === 'admin'
})
const isStudent = computed(() => authStore.userRole === 'student')

const openResubmissions = computed(() =>
  (document.value?.resubmission_requests || []).filter((x) => !x.resolved)
)

const orderedValidations = computed(() => {
  const list = [...(document.value?.validations || [])]
  return list.sort((a, b) =>
    String(a.validated_at || a.created_at || '').localeCompare(
      String(b.validated_at || b.created_at || '')
    )
  )
})

const latestInvalidValidation = computed(() => {
  const list = [...(document.value?.validations || [])]
  const bad = list.filter((v) => String(v.result || '').toLowerCase() !== 'valid')
  if (!bad.length) return null
  bad.sort((a, b) =>
    String(b.validated_at || b.created_at || '').localeCompare(
      String(a.validated_at || a.created_at || '')
    )
  )
  return bad[0]
})

const previewObjectUrl = ref(null)
const previewLoading = ref(false)
const previewError = ref(null)

const previewKind = computed(() => {
  const name = fileName(document.value?.file || '').toLowerCase()
  if (name.endsWith('.pdf')) return 'pdf'
  if (/\.(jpe?g|png|gif|webp)$/i.test(name)) return 'image'
  return 'none'
})

const previewContextLines = computed(() => {
  const lines = []
  for (const req of openResubmissions.value) {
    lines.push(t('documentDetailPage.previewContextResubmission', { reason: req.reason || '' }))
  }
  const inv = latestInvalidValidation.value
  if (inv?.details) {
    lines.push(t('documentDetailPage.previewContextReviewNote', { note: inv.details }))
  } else if (inv && String(inv.result || '').toLowerCase() !== 'valid') {
    lines.push(t('documentDetailPage.previewContextValidation', { result: inv.result }))
  }
  return lines
})

function revokePreviewUrl() {
  if (previewObjectUrl.value) {
    URL.revokeObjectURL(previewObjectUrl.value)
    previewObjectUrl.value = null
  }
}

async function loadPreview() {
  revokePreviewUrl()
  previewError.value = null
  if (!document.value?.id || previewKind.value === 'none') {
    previewLoading.value = false
    return
  }
  previewLoading.value = true
  try {
    const res = await api.get(`/api/documents/${document.value.id}/preview/`, {
      responseType: 'blob',
    })
    previewObjectUrl.value = URL.createObjectURL(res.data)
  } catch (e) {
    console.error(e)
    previewError.value = t('documentDetailPage.previewError')
  } finally {
    previewLoading.value = false
  }
}

function fileName(fileUrl) {
  if (!fileUrl) return t('documentDetailPage.fileUnknown')
  const parts = fileUrl.split('/')
  return decodeURIComponent(parts[parts.length - 1] || t('documentDetailPage.fileFallback'))
}

function formatDateTime(dateString) {
  if (!dateString) return t('documentDetailPage.notAvailable')
  const loc = locale.value === 'es' ? 'es' : 'en-US'
  return new Date(dateString).toLocaleString(loc, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

async function fetchDocument() {
  try {
    loading.value = true
    error.value = null
    const response = await api.get(`/api/documents/${route.params.id}/`)
    document.value = response.data
    await loadPreview()
  } catch (err) {
    console.error('Failed to fetch document:', err)
    error.value = t('documentDetailPage.loadError')
    toast.error(t('documentDetailPage.loadToastError'))
  } finally {
    loading.value = false
  }
}

async function fetchApplications() {
  try {
    const response = await api.get('/api/applications/', { params: { page_size: 100 } })
    applications.value = response.data.results || response.data
  } catch (err) {
    console.warn('Failed to fetch applications:', err)
  }
}

async function postComment() {
  if (!document.value || !newComment.value.trim()) return
  actionBusy.value = true
  try {
    await api.post('/api/document-comments/', {
      document: document.value.id,
      text: newComment.value.trim(),
      is_private: isStaff.value ? commentPrivate.value : false,
    })
    newComment.value = ''
    commentPrivate.value = false
    toast.success(t('documentDetailPage.toastCommentPosted'))
    await fetchDocument()
  } catch (err) {
    console.error(err)
    toast.error(err.response?.data?.detail || t('documentDetailPage.toastCommentError'))
  } finally {
    actionBusy.value = false
  }
}

async function requestResubmission() {
  if (!document.value || !resubmitReason.value.trim()) return
  actionBusy.value = true
  try {
    await api.post('/api/document-resubmissions/', {
      document: document.value.id,
      reason: resubmitReason.value.trim(),
      resolved: false,
    })
    resubmitReason.value = ''
    toast.success(t('documentDetailPage.toastResubmitRequested'))
    await fetchDocument()
  } catch (err) {
    console.error(err)
    const msg =
      err.response?.data?.detail ||
      (typeof err.response?.data === 'string' ? err.response.data : null) ||
      t('documentDetailPage.toastResubmitError')
    toast.error(msg)
  } finally {
    actionBusy.value = false
  }
}

async function resolveResubmission(req) {
  actionBusy.value = true
  try {
    await api.patch(`/api/document-resubmissions/${req.id}/`, { resolved: true })
    toast.success(t('documentDetailPage.toastMarkedAddressed'))
    await fetchDocument()
  } catch (err) {
    console.error(err)
    toast.error(err.response?.data?.detail || t('documentDetailPage.toastUpdateRequestError'))
  } finally {
    actionBusy.value = false
  }
}

async function validateDoc(result) {
  if (!document.value) return
  actionBusy.value = true
  try {
    await api.post(`/api/documents/${document.value.id}/validate_document/`, {
      result,
      details: validationNote.value.trim(),
    })
    validationNote.value = ''
    toast.success(
      result === 'valid'
        ? t('documentDetailPage.toastMarkedValid')
        : t('documentDetailPage.toastMarkedInvalid')
    )
    await fetchDocument()
  } catch (err) {
    console.error(err)
    toast.error(err.response?.data?.detail || t('documentDetailPage.toastValidationFailed'))
  } finally {
    actionBusy.value = false
  }
}

async function submitReplaceFile() {
  if (!document.value || !replaceInput.value?.files?.length) {
    toast.error(t('documentDetailPage.toastChooseFile'))
    return
  }
  const fd = new FormData()
  fd.append('file', replaceInput.value.files[0])
  actionBusy.value = true
  try {
    await api.patch(`/api/documents/${document.value.id}/`, fd)
    replaceInput.value.value = ''
    toast.success(t('documentDetailPage.toastFileUpdated'))
    await fetchDocument()
  } catch (err) {
    console.error(err)
    const d = err.response?.data
    const msg =
      (typeof d === 'object' && d && (d.detail || d.file?.[0])) ||
      (typeof d === 'string' ? d : null) ||
      t('documentDetailPage.toastReplaceError')
    toast.error(msg)
  } finally {
    actionBusy.value = false
  }
}

function onApplicationSyncEvent(ev) {
  const d = ev.detail
  if (!document.value?.id || !d?.applicationId) return
  const targetApp = String(d.applicationId)
  const thisApp = documentApplicationId(document.value.application)
  const thisDoc = String(document.value.id)
  if (d.documentId && String(d.documentId) === thisDoc) {
    fetchDocument()
    return
  }
  if (targetApp === thisApp) {
    fetchDocument()
  }
}

onMounted(async () => {
  await authStore.checkAuth()
  await fetchApplications()
  await fetchDocument()
  if (typeof window !== 'undefined') {
    window.addEventListener('seim-application-sync', onApplicationSyncEvent)
  }
})

onUnmounted(() => {
  revokePreviewUrl()
  if (typeof window !== 'undefined') {
    window.removeEventListener('seim-application-sync', onApplicationSyncEvent)
  }
})
</script>

<style scoped>
.document-detail {
  min-height: 100vh;
  background-color: #f8f9fa;
}

.card {
  border: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.shrink-0 {
  flex-shrink: 0;
}

.preview-frame {
  min-height: 420px;
  height: 65vh;
}
</style>
