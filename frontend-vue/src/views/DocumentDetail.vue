<template>
  <div class="document-detail">
    <div class="container-fluid mt-4">
      <nav aria-label="breadcrumb">
        <ol class="breadcrumb">
          <li class="breadcrumb-item">
            <router-link :to="{ name: 'Dashboard' }">Dashboard</router-link>
          </li>
          <li class="breadcrumb-item">
            <router-link :to="{ name: 'Documents' }">Documents</router-link>
          </li>
          <li class="breadcrumb-item active">{{ document?.type?.name || 'Loading...' }}</li>
        </ol>
      </nav>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-3 text-muted">Loading document...</p>
      </div>

      <div v-else-if="error" class="alert alert-danger">
        <i class="bi bi-exclamation-triangle me-2"></i>
        {{ error }}
        <router-link :to="{ name: 'Documents' }" class="btn btn-sm btn-outline-danger ms-3">
          Back to Documents
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
            <strong>Resubmission requested</strong>
            <p class="mb-0 mt-1 small">{{ req.reason }}</p>
            <span class="text-muted small">Requested by {{ req.requested_by }}</span>
          </div>
          <button
            v-if="isStaff"
            type="button"
            class="btn btn-sm btn-outline-secondary shrink-0"
            :disabled="actionBusy"
            @click="resolveResubmission(req)"
          >
            Mark addressed
          </button>
        </div>

        <div class="row">
          <div class="col-lg-8">
            <div v-if="document.file" class="card mb-4" data-testid="document-preview-card">
              <div class="card-header">
                <h6 class="mb-0"><i class="bi bi-eye me-2"></i>Preview</h6>
              </div>
              <div class="card-body">
                <p v-if="previewKind === 'none'" class="text-muted small mb-0">
                  Inline preview supports PDF and common images. Use Download to open this file.
                </p>
                <div v-else-if="previewLoading" class="text-center py-5 text-muted">Loading preview…</div>
                <div v-else-if="previewError" class="alert alert-warning small mb-0">{{ previewError }}</div>
                <template v-else-if="previewObjectUrl">
                  <iframe
                    v-if="previewKind === 'pdf'"
                    :src="previewObjectUrl"
                    title="Document preview"
                    class="w-100 border rounded preview-frame"
                  />
                  <img
                    v-else-if="previewKind === 'image'"
                    :src="previewObjectUrl"
                    alt="Document preview"
                    class="img-fluid border rounded"
                  />
                </template>
                <div v-if="previewContextLines.length" class="mt-3 pt-3 border-top small">
                  <div class="fw-semibold mb-2">Review context</div>
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
                  {{ document.is_valid ? 'Validated' : 'Pending Validation' }}
                </span>
              </div>
              <div class="card-body">
                <div class="row mb-3">
                  <div class="col-md-6">
                    <label class="text-muted small">Document Type</label>
                    <p class="fw-bold">{{ document.type?.name || document.type }}</p>
                  </div>
                  <div class="col-md-6">
                    <label class="text-muted small">Application</label>
                    <p>
                      <router-link :to="{ name: 'ApplicationDetail', params: { id: document.application } }">
                        {{ getApplicationName(document.application) }}
                      </router-link>
                    </p>
                  </div>
                </div>
                <div class="row mb-3">
                  <div class="col-md-6">
                    <label class="text-muted small">Uploaded By</label>
                    <p class="fw-bold">{{ document.uploaded_by || 'N/A' }}</p>
                  </div>
                  <div class="col-md-6">
                    <label class="text-muted small">Uploaded At</label>
                    <p class="fw-bold">{{ formatDateTime(document.created_at) }}</p>
                  </div>
                </div>
                <div v-if="document.validated_at" class="row mb-3">
                  <div class="col-md-6">
                    <label class="text-muted small">Validated At</label>
                    <p class="fw-bold">{{ formatDateTime(document.validated_at) }}</p>
                  </div>
                </div>

                <div class="mt-4 pt-3 border-top">
                  <a
                    v-if="document.file"
                    :href="resolveFileUrl(document.file)"
                    target="_blank"
                    rel="noopener"
                    class="btn btn-primary"
                  >
                    <i class="bi bi-download me-2"></i>Download Document
                  </a>
                </div>

                <div v-if="isStudent" class="mt-4 pt-3 border-top">
                  <h6 class="mb-2">Replace file</h6>
                  <p class="small text-muted mb-2">
                    Upload a new file when staff asked for a resubmission or your application is still in draft.
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
                    Upload replacement
                  </button>
                </div>
              </div>
            </div>

            <div class="card mb-4">
              <div class="card-header">
                <h6 class="mb-0">Review history</h6>
              </div>
              <div class="card-body">
                <p v-if="!orderedValidations.length" class="text-muted small mb-0">No validation records yet.</p>
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
                    <div v-if="v.validator_name" class="small text-muted mt-1">By {{ v.validator_name }}</div>
                    <div v-if="v.details" class="small mt-1">{{ v.details }}</div>
                  </li>
                </ul>
              </div>
            </div>

            <div class="card mb-4">
              <div class="card-header">
                <h6 class="mb-0">Comments</h6>
              </div>
              <div class="card-body">
                <div v-if="!document.comments?.length" class="text-muted small mb-3">No comments yet.</div>
                <div v-for="c in document.comments" :key="c.id" class="border-bottom pb-2 mb-2">
                  <div class="d-flex justify-content-between">
                    <strong class="small">{{ c.author }}</strong>
                    <span class="small text-muted">{{ formatDateTime(c.created_at) }}</span>
                  </div>
                  <span v-if="c.is_private" class="badge bg-secondary small">Staff only</span>
                  <p class="small mb-0 mt-1">{{ c.text }}</p>
                </div>
                <div class="mt-3">
                  <label class="form-label small">Add a comment</label>
                  <textarea
                    v-model="newComment"
                    class="form-control form-control-sm mb-2"
                    rows="3"
                    placeholder="Reply or leave a note…"
                  />
                  <div v-if="isStaff" class="form-check mb-2">
                    <input id="privComment" v-model="commentPrivate" class="form-check-input" type="checkbox" />
                    <label class="form-check-label small" for="privComment">Private (staff only)</label>
                  </div>
                  <button
                    type="button"
                    class="btn btn-primary btn-sm"
                    :disabled="actionBusy || !newComment.trim()"
                    @click="postComment"
                  >
                    Post comment
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div class="col-lg-4">
            <div v-if="isStaff" class="card mb-4">
              <div class="card-header">
                <h6 class="mb-0">Coordinator actions</h6>
              </div>
              <div class="card-body">
                <label class="form-label small">Request resubmission</label>
                <textarea
                  v-model="resubmitReason"
                  class="form-control form-control-sm mb-2"
                  rows="2"
                  placeholder="Reason shown to the student"
                />
                <button
                  type="button"
                  class="btn btn-warning btn-sm w-100 mb-3"
                  :disabled="actionBusy || !resubmitReason.trim()"
                  @click="requestResubmission"
                >
                  Request resubmission
                </button>

                <label class="form-label small">Validation</label>
                <textarea
                  v-model="validationNote"
                  class="form-control form-control-sm mb-2"
                  rows="2"
                  placeholder="Optional note (recommended if marking invalid)"
                />
                <div class="d-grid gap-2">
                  <button
                    type="button"
                    class="btn btn-success btn-sm"
                    :disabled="actionBusy"
                    @click="validateDoc('valid')"
                  >
                    Mark valid
                  </button>
                  <button
                    type="button"
                    class="btn btn-outline-danger btn-sm"
                    :disabled="actionBusy"
                    @click="validateDoc('invalid')"
                  >
                    Mark invalid / needs update
                  </button>
                </div>
              </div>
            </div>

            <div class="card mb-4">
              <div class="card-header">
                <h6 class="mb-0">Quick Actions</h6>
              </div>
              <div class="card-body">
                <div class="d-grid gap-2">
                  <a
                    v-if="document.file"
                    :href="resolveFileUrl(document.file)"
                    target="_blank"
                    rel="noopener"
                    class="btn btn-outline-primary"
                  >
                    <i class="bi bi-download me-2"></i>Download
                  </a>
                  <router-link
                    :to="{ name: 'ApplicationDetail', params: { id: document.application } }"
                    class="btn btn-outline-secondary"
                  >
                    <i class="bi bi-file-earmark-text me-2"></i>View Application
                  </router-link>
                  <router-link :to="{ name: 'Documents' }" class="btn btn-outline-secondary">
                    <i class="bi bi-arrow-left me-2"></i>Back to Documents
                  </router-link>
                </div>
              </div>
            </div>

            <div class="card">
              <div class="card-header">
                <h6 class="mb-0">Document Info</h6>
              </div>
              <div class="card-body">
                <div class="mb-3">
                  <label class="text-muted small">Document ID</label>
                  <p class="small font-monospace">{{ document.id }}</p>
                </div>
                <div class="mb-3">
                  <label class="text-muted small">Status</label>
                  <p>
                    <span class="badge" :class="document.is_valid ? 'bg-success' : 'bg-warning'">
                      {{ document.is_valid ? 'Validated' : 'Pending' }}
                    </span>
                  </p>
                </div>
                <div class="mb-3">
                  <label class="text-muted small">Last Updated</label>
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
import { useToast } from '@/composables/useToast'
import { resolveFileUrl } from '@/utils/apiUrl'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
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
    lines.push(`Resubmission requested: ${req.reason}`)
  }
  const inv = latestInvalidValidation.value
  if (inv?.details) {
    lines.push(`Latest review note: ${inv.details}`)
  } else if (inv && String(inv.result || '').toLowerCase() !== 'valid') {
    lines.push(`Latest validation: ${inv.result}`)
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
    previewError.value = 'Preview could not be loaded. Use Download instead.'
  } finally {
    previewLoading.value = false
  }
}

function fileName(fileUrl) {
  if (!fileUrl) return 'Unknown'
  const parts = fileUrl.split('/')
  return decodeURIComponent(parts[parts.length - 1] || 'document')
}

function getApplicationName(appId) {
  if (typeof appId === 'object' && appId?.program?.name) return appId.program.name
  const app = applications.value.find(a => a.id === appId)
  return app?.program?.name || appId || 'Unknown'
}

function formatDateTime(dateString) {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString('en-US', {
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
    error.value = 'Failed to load document. Please try again.'
    toast.error('Failed to load document')
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
    toast.success('Comment posted')
    await fetchDocument()
  } catch (err) {
    console.error(err)
    toast.error(err.response?.data?.detail || 'Could not post comment')
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
    toast.success('Resubmission requested')
    await fetchDocument()
  } catch (err) {
    console.error(err)
    const msg =
      err.response?.data?.detail ||
      (typeof err.response?.data === 'string' ? err.response.data : null) ||
      'Could not create resubmission request'
    toast.error(msg)
  } finally {
    actionBusy.value = false
  }
}

async function resolveResubmission(req) {
  actionBusy.value = true
  try {
    await api.patch(`/api/document-resubmissions/${req.id}/`, { resolved: true })
    toast.success('Marked as addressed')
    await fetchDocument()
  } catch (err) {
    console.error(err)
    toast.error(err.response?.data?.detail || 'Could not update request')
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
    toast.success(result === 'valid' ? 'Marked valid' : 'Marked invalid; student notified')
    await fetchDocument()
  } catch (err) {
    console.error(err)
    toast.error(err.response?.data?.detail || 'Validation failed')
  } finally {
    actionBusy.value = false
  }
}

async function submitReplaceFile() {
  if (!document.value || !replaceInput.value?.files?.length) {
    toast.error('Choose a file first')
    return
  }
  const fd = new FormData()
  fd.append('file', replaceInput.value.files[0])
  actionBusy.value = true
  try {
    await api.patch(`/api/documents/${document.value.id}/`, fd)
    replaceInput.value.value = ''
    toast.success('File updated')
    await fetchDocument()
  } catch (err) {
    console.error(err)
    const d = err.response?.data
    const msg =
      (typeof d === 'object' && d && (d.detail || d.file?.[0])) ||
      (typeof d === 'string' ? d : null) ||
      'Could not replace file'
    toast.error(msg)
  } finally {
    actionBusy.value = false
  }
}

onMounted(async () => {
  await authStore.checkAuth()
  await fetchApplications()
  await fetchDocument()
})

onUnmounted(() => {
  revokePreviewUrl()
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
