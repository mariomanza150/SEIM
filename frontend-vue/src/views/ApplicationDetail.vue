<template>
  <div class="application-detail">
    <div class="container-fluid mt-4">
      <!-- Breadcrumb -->
      <nav aria-label="breadcrumb">
        <ol class="breadcrumb">
          <li class="breadcrumb-item">
            <router-link :to="{ name: 'Dashboard' }">Dashboard</router-link>
          </li>
          <li class="breadcrumb-item">
            <router-link :to="{ name: 'Applications' }">Applications</router-link>
          </li>
          <li class="breadcrumb-item active">{{ application?.program?.name || 'Loading...' }}</li>
        </ol>
      </nav>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-3 text-muted">Loading application details...</p>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="alert alert-danger">
        <i class="bi bi-exclamation-triangle me-2"></i>
        {{ error }}
        <router-link :to="{ name: 'Applications' }" class="btn btn-sm btn-outline-danger ms-3">
          Back to Applications
        </router-link>
      </div>

      <!-- Application Details -->
      <div v-else-if="application" data-testid="application-detail-page">
        <!-- Header -->
        <div class="row mb-4">
          <div class="col-md-8">
            <h2>
              <i class="bi bi-file-earmark-text me-2"></i>
              {{ application.program?.name }}
            </h2>
            <p class="text-muted">
              <i class="bi bi-building me-1"></i>
              {{ application.program?.institution || 'N/A' }}
            </p>
          </div>
          <div class="col-md-4 text-end">
            <span class="badge fs-6 me-2" :class="statusClass(application.status)">
              {{ formatStatus(application.status) }}
            </span>
            <router-link
              v-if="application.status === 'draft'"
              :to="{ name: 'ApplicationEdit', params: { id: application.id } }"
              class="btn btn-primary"
            >
              <i class="bi bi-pencil me-1"></i>Edit
            </router-link>
          </div>
        </div>

        <div class="row">
          <!-- Main Content -->
          <div class="col-lg-8">
            <!-- Program Information -->
            <div class="card mb-4">
              <div class="card-header">
                <h5 class="mb-0"><i class="bi bi-info-circle me-2"></i>Program Information</h5>
              </div>
              <div class="card-body">
                <div class="row mb-3">
                  <div class="col-md-6">
                    <label class="text-muted small">Program Name</label>
                    <p class="fw-bold">{{ application.program?.name }}</p>
                  </div>
                  <div class="col-md-6">
                    <label class="text-muted small">Institution</label>
                    <p class="fw-bold">{{ application.program?.institution }}</p>
                  </div>
                </div>
                <div class="row mb-3">
                  <div class="col-md-6">
                    <label class="text-muted small">Country</label>
                    <p class="fw-bold">{{ application.program?.country || 'N/A' }}</p>
                  </div>
                  <div class="col-md-6">
                    <label class="text-muted small">Duration</label>
                    <p class="fw-bold">{{ application.program?.duration || 'N/A' }}</p>
                  </div>
                </div>
                <div v-if="application.program?.description">
                  <label class="text-muted small">Description</label>
                  <p>{{ application.program.description }}</p>
                </div>
              </div>
            </div>

            <!-- Required documents checklist -->
            <div
              v-if="application.document_checklist && application.document_checklist.required_count > 0"
              class="card mb-4"
              data-testid="document-checklist-card"
            >
              <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0">
                  <i class="bi bi-clipboard-check me-2"></i>Required documents
                </h5>
                <span
                  class="badge"
                  :class="application.document_checklist.complete ? 'bg-success' : 'bg-warning text-dark'"
                >
                  {{ application.document_checklist.approved_count }} /
                  {{ application.document_checklist.required_count }} approved
                </span>
              </div>
              <div class="card-body">
                <p v-if="application.status === 'draft' && !application.document_checklist.complete" class="text-muted small">
                  All listed documents must be uploaded and marked valid by staff before you can submit.
                </p>
                <ul class="list-group list-group-flush">
                  <li
                    v-for="item in application.document_checklist.items"
                    :key="item.document_type_id"
                    class="list-group-item px-0 d-flex justify-content-between align-items-start flex-wrap gap-2"
                  >
                    <div>
                      <span class="fw-semibold">{{ item.name }}</span>
                      <p v-if="item.description" class="small text-muted mb-0">{{ item.description }}</p>
                      <p
                        v-if="item.status === 'resubmit_requested' && item.resubmission_reason"
                        class="small text-danger mb-0 mt-1"
                      >
                        {{ item.resubmission_reason }}
                      </p>
                    </div>
                    <div class="d-flex align-items-center gap-2">
                      <span class="badge" :class="checklistBadgeClass(item.status)">
                        {{ checklistStatusLabel(item.status) }}
                      </span>
                      <router-link
                        v-if="item.document_id"
                        :to="{ name: 'DocumentDetail', params: { id: item.document_id } }"
                        class="btn btn-sm btn-outline-primary"
                      >
                        View
                      </router-link>
                    </div>
                  </li>
                </ul>
              </div>
            </div>

            <!-- Activity timeline (server TimelineEvent rows + record start) -->
            <div class="card mb-4" data-testid="activity-timeline-card">
              <div class="card-header">
                <h5 class="mb-0"><i class="bi bi-clock-history me-2"></i>Activity timeline</h5>
              </div>
              <div class="card-body">
                <div v-if="timelineLoading" class="text-center py-3">
                  <div class="spinner-border spinner-border-sm text-primary" role="status">
                    <span class="visually-hidden">Loading timeline...</span>
                  </div>
                </div>
                <div v-else-if="timelineError" class="alert alert-warning small mb-0">
                  {{ timelineError }}
                </div>
                <div v-else class="timeline">
                  <div class="timeline-item">
                    <div class="timeline-icon bg-primary">
                      <i class="bi bi-file-earmark-plus"></i>
                    </div>
                    <div class="timeline-content">
                      <h6>Application record created</h6>
                      <p class="text-muted small mb-0">{{ formatDateTime(application.created_at) }}</p>
                    </div>
                  </div>
                  <div
                    v-for="event in timelineEvents"
                    :key="event.id"
                    class="timeline-item"
                  >
                    <div class="timeline-icon" :class="timelineIconBg(event.event_type)">
                      <i :class="['bi', timelineIconName(event.event_type)]"></i>
                    </div>
                    <div class="timeline-content">
                      <h6>{{ timelineEventHeading(event) }}</h6>
                      <p class="mb-1">{{ event.description }}</p>
                      <p class="text-muted small mb-0">
                        {{ formatDateTime(event.created_at) }}
                        <span v-if="event.created_by_name"> · {{ event.created_by_name }}</span>
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Comments Section -->
            <div class="card mb-4">
              <div class="card-header">
                <h5 class="mb-0"><i class="bi bi-chat-dots me-2"></i>Comments</h5>
              </div>
              <div class="card-body">
                <div v-if="commentsLoading" class="text-center py-3">
                  <div class="spinner-border spinner-border-sm text-primary" role="status">
                    <span class="visually-hidden">Loading comments...</span>
                  </div>
                </div>
                <div v-else-if="commentsError" class="alert alert-warning mb-3">
                  <i class="bi bi-exclamation-circle me-2"></i>
                  {{ commentsError }}
                </div>
                <div v-else-if="comments.length > 0" class="mb-3">
                  <div
                    v-for="comment in comments"
                    :key="comment.id"
                    class="comment-item border rounded p-3 mb-3"
                  >
                    <div class="d-flex justify-content-between align-items-start gap-2 mb-2">
                      <div>
                        <div class="fw-semibold d-flex align-items-center flex-wrap gap-2">
                          <span>{{ formatCommentAuthor(comment) }}</span>
                          <span class="badge text-bg-light">{{ formatRole(comment.author_role) }}</span>
                          <span v-if="comment.is_private" class="badge text-bg-warning">Private</span>
                        </div>
                        <p class="text-muted small mb-0">{{ formatDateTime(comment.created_at) }}</p>
                      </div>
                    </div>
                    <p class="mb-0 comment-text">{{ comment.text }}</p>
                  </div>
                </div>
                <p v-else class="text-muted text-center py-3">
                  <i class="bi bi-info-circle me-1"></i>
                  No comments yet
                </p>

                <form class="border-top pt-3" @submit.prevent="submitComment">
                  <div class="mb-3">
                    <label class="form-label" for="commentText">Add comment</label>
                    <textarea
                      id="commentText"
                      v-model="newCommentText"
                      class="form-control"
                      rows="3"
                      maxlength="2000"
                      placeholder="Write a comment about this application"
                    ></textarea>
                  </div>
                  <div
                    v-if="canPostPrivateComment"
                    class="form-check mb-3"
                  >
                    <input
                      id="privateComment"
                      v-model="newCommentPrivate"
                      class="form-check-input"
                      type="checkbox"
                    >
                    <label class="form-check-label" for="privateComment">
                      Private comment (visible to coordinators/admins only)
                    </label>
                  </div>
                  <div class="d-flex justify-content-end">
                    <button
                      type="submit"
                      class="btn btn-primary"
                      :disabled="submittingComment || !newCommentText.trim()"
                    >
                      <span v-if="submittingComment" class="spinner-border spinner-border-sm me-2"></span>
                      Post Comment
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>

          <!-- Sidebar -->
          <div class="col-lg-4">
            <!-- Coordinator: Review / Status update -->
            <div
              v-if="isCoordinator && application.status !== 'draft' && application.status !== 'cancelled'"
              class="card mb-4"
            >
              <div class="card-header">
                <h6 class="mb-0"><i class="bi bi-pencil-square me-2"></i>Review Application</h6>
              </div>
              <div class="card-body">
                <div class="mb-3">
                  <label class="form-label small">Change status</label>
                  <select v-model="reviewStatus" class="form-select form-select-sm">
                    <option value="">Select new status</option>
                    <option value="under_review">Under review</option>
                    <option value="approved">Approved</option>
                    <option value="rejected">Rejected</option>
                    <option value="completed">Completed</option>
                  </select>
                </div>
                <button
                  class="btn btn-primary btn-sm w-100"
                  :disabled="!reviewStatus || updatingStatus"
                  @click="updateApplicationStatus"
                >
                  <span v-if="updatingStatus" class="spinner-border spinner-border-sm me-1"></span>
                  Update status
                </button>
              </div>
            </div>

            <!-- Quick Actions -->
            <div class="card mb-4">
              <div class="card-header">
                <h6 class="mb-0">Quick Actions</h6>
              </div>
              <div class="card-body">
                <div class="d-grid gap-2">
                  <router-link
                    v-if="application.status === 'draft'"
                    :to="{ name: 'ApplicationEdit', params: { id: application.id } }"
                    class="btn btn-primary"
                    data-testid="edit-application-link"
                  >
                    <i class="bi bi-pencil me-2"></i>Edit Application
                  </router-link>
                  <button
                    v-if="application.status === 'draft'"
                    class="btn btn-success"
                    :disabled="submitBlockedByDocuments"
                    :title="submitBlockedByDocuments ? 'Required documents must be approved first' : ''"
                    @click="submitApplication"
                    data-testid="submit-application-btn"
                  >
                    <i class="bi bi-send me-2"></i>Submit Application
                  </button>
                  <button
                    v-if="application.status === 'draft'"
                    class="btn btn-danger"
                    @click="confirmDelete"
                  >
                    <i class="bi bi-trash me-2"></i>Delete Application
                  </button>
                  <router-link :to="{ name: 'Applications' }" class="btn btn-outline-secondary">
                    <i class="bi bi-arrow-left me-2"></i>Back to List
                  </router-link>
                </div>
              </div>
            </div>

            <!-- Application Details -->
            <div class="card mb-4">
              <div class="card-header">
                <h6 class="mb-0">Application Details</h6>
              </div>
              <div class="card-body">
                <div class="mb-3">
                  <label class="text-muted small">Application ID</label>
                  <p class="small font-monospace">{{ application.id }}</p>
                </div>
                <div class="mb-3">
                  <label class="text-muted small">Status</label>
                  <p>
                    <span class="badge" :class="statusClass(application.status)">
                      {{ formatStatus(application.status) }}
                    </span>
                  </p>
                </div>
                <div class="mb-3">
                  <label class="text-muted small">Created</label>
                  <p>{{ formatDateTime(application.created_at) }}</p>
                </div>
                <div v-if="application.submitted_at" class="mb-3">
                  <label class="text-muted small">Submitted</label>
                  <p>{{ formatDateTime(application.submitted_at) }}</p>
                </div>
                <div class="mb-3">
                  <label class="text-muted small">Last Updated</label>
                  <p>{{ formatDateTime(application.updated_at) }}</p>
                </div>
              </div>
            </div>

            <!-- Upload Document -->
            <div v-if="application.status === 'draft' || application.status === 'submitted'" class="card mb-4">
              <DocumentUpload
                :application-id="application.id"
                @uploaded="fetchApplication"
              />
            </div>

            <!-- Documents List -->
            <div class="card">
              <div class="card-header d-flex justify-content-between align-items-center">
                <h6 class="mb-0">Documents</h6>
                <router-link :to="{ name: 'Documents' }" class="btn btn-sm btn-outline-primary">
                  View All
                </router-link>
              </div>
              <div class="card-body">
                <div v-if="documentsLoading" class="text-center py-3">
                  <div class="spinner-border spinner-border-sm text-primary"></div>
                </div>
                <div v-else-if="applicationDocuments.length > 0">
                  <ul class="list-group list-group-flush">
                    <li
                      v-for="doc in applicationDocuments"
                      :key="doc.id"
                      class="list-group-item px-0 d-flex justify-content-between align-items-center flex-wrap gap-1"
                    >
                      <router-link :to="{ name: 'DocumentDetail', params: { id: doc.id } }" class="text-decoration-none">
                        <i class="bi bi-file-earmark me-2"></i>
                        {{ doc.type?.name || doc.type }}
                      </router-link>
                      <span class="d-flex align-items-center gap-1">
                        <span class="badge" :class="doc.is_valid === true ? 'bg-success' : doc.is_valid === false ? 'bg-danger' : 'bg-warning'">
                          {{ doc.is_valid === true ? 'Valid' : doc.is_valid === false ? 'Invalid' : 'Pending' }}
                        </span>
                        <template v-if="isCoordinator">
                          <template v-if="docValidatingId !== doc.id">
                            <button
                              type="button"
                              class="btn btn-sm btn-outline-success"
                              title="Mark valid"
                              @click="validateDocument(doc.id, 'valid')"
                            >
                              <i class="bi bi-check-lg"></i>
                            </button>
                            <button
                              type="button"
                              class="btn btn-sm btn-outline-danger"
                              title="Mark invalid"
                              @click="validateDocument(doc.id, 'invalid')"
                            >
                              <i class="bi bi-x-lg"></i>
                            </button>
                          </template>
                          <span v-else class="spinner-border spinner-border-sm text-primary"></span>
                        </template>
                      </span>
                    </li>
                  </ul>
                </div>
                <p v-else class="text-muted text-center small mb-0">
                  <i class="bi bi-info-circle me-1"></i>
                  No documents uploaded
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import DocumentUpload from '@/components/DocumentUpload.vue'
import api from '@/services/api'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const { success, error: errorToast } = useToast()

const isCoordinator = computed(() =>
  authStore.userRole === 'coordinator' || authStore.userRole === 'admin'
)

const submitBlockedByDocuments = computed(() => {
  const c = application.value?.document_checklist
  if (!c?.required_count) return false
  return !c.complete
})

const currentUserId = computed(() => authStore.user?.id || null)
const canPostPrivateComment = computed(() => isCoordinator.value)

const application = ref(null)
const comments = ref([])
const commentsLoading = ref(false)
const commentsError = ref(null)
const newCommentText = ref('')
const newCommentPrivate = ref(false)
const submittingComment = ref(false)
const reviewStatus = ref('')
const updatingStatus = ref(false)
const docValidatingId = ref(null)
const applicationDocuments = ref([])
const documentsLoading = ref(false)
const timelineEvents = ref([])
const timelineLoading = ref(false)
const timelineError = ref(null)
const loading = ref(true)
const error = ref(null)

async function fetchApplication() {
  try {
    loading.value = true
    error.value = null

    const response = await api.get(`/api/applications/${route.params.id}/`)
    application.value = response.data
    await Promise.all([fetchApplicationDocuments(), fetchComments(), fetchTimelineEvents()])
  } catch (err) {
    console.error('Failed to fetch application:', err)
    error.value = 'Failed to load application details. Please try again.'
    errorToast('Failed to load application')
  } finally {
    loading.value = false
  }
}

/** Refetch without full-page loading spinner (WebSocket application.sync). */
async function softRefreshFromSync() {
  if (!application.value?.id) return
  try {
    const response = await api.get(`/api/applications/${route.params.id}/`)
    application.value = response.data
    await Promise.all([fetchApplicationDocuments(), fetchComments(), fetchTimelineEvents()])
  } catch (err) {
    console.warn('Live sync refresh failed:', err)
  }
}

function onApplicationSyncEvent(ev) {
  const id = ev.detail?.applicationId
  if (!id || String(id) !== String(route.params.id)) return
  softRefreshFromSync()
}

async function fetchTimelineEvents() {
  if (!application.value?.id) return
  try {
    timelineLoading.value = true
    timelineError.value = null
    const response = await api.get('/api/timeline-events/', {
      params: {
        application: application.value.id,
        ordering: 'created_at',
      },
    })
    timelineEvents.value = response.data.results || response.data || []
  } catch (err) {
    console.warn('Failed to fetch timeline events:', err)
    timelineEvents.value = []
    timelineError.value = 'Could not load activity timeline.'
  } finally {
    timelineLoading.value = false
  }
}

async function fetchApplicationDocuments() {
  if (!application.value?.id) return
  try {
    documentsLoading.value = true
    const response = await api.get('/api/documents/', {
      params: { application: application.value.id },
    })
    applicationDocuments.value = response.data.results || response.data
  } catch (err) {
    console.warn('Failed to fetch documents:', err)
    applicationDocuments.value = []
  } finally {
    documentsLoading.value = false
  }
}

async function fetchComments() {
  if (!application.value?.id) return
  try {
    commentsLoading.value = true
    commentsError.value = null
    const response = await api.get('/api/comments/', {
      params: { application: application.value.id },
    })
    const results = response.data.results || response.data || []
    comments.value = [...results].sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  } catch (err) {
    console.error('Failed to fetch comments:', err)
    comments.value = []
    commentsError.value = 'Failed to load comments.'
  } finally {
    commentsLoading.value = false
  }
}

function statusClass(status) {
  const classes = {
    draft: 'bg-secondary',
    submitted: 'bg-info',
    under_review: 'bg-warning',
    approved: 'bg-success',
    rejected: 'bg-danger',
    completed: 'bg-primary',
  }
  return classes[status] || 'bg-secondary'
}

function formatStatus(status) {
  return status ? status.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase()) : 'Unknown'
}

function formatDateTime(dateString) {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function formatRole(role) {
  if (!role) return 'User'
  return role.replace(/_/g, ' ').replace(/\b\w/g, (letter) => letter.toUpperCase())
}

function formatCommentAuthor(comment) {
  if (comment.author && currentUserId.value && comment.author === currentUserId.value) {
    return 'You'
  }
  return comment.author_name || 'Unknown user'
}

function checklistStatusLabel(status) {
  const labels = {
    missing: 'Missing',
    pending_review: 'Pending review',
    resubmit_requested: 'Resubmission needed',
    approved: 'Approved',
  }
  return labels[status] || status
}

function checklistBadgeClass(status) {
  const classes = {
    missing: 'bg-secondary',
    pending_review: 'bg-warning text-dark',
    resubmit_requested: 'bg-danger',
    approved: 'bg-success',
  }
  return classes[status] || 'bg-secondary'
}

function timelineEventHeading(event) {
  const t = event.event_type || ''
  if (t === 'submitted') return 'Application submitted'
  if (t.startsWith('status_')) {
    const rest = t.slice(7).replace(/_/g, ' ')
    return `Status: ${rest.replace(/\b\w/g, (c) => c.toUpperCase())}`
  }
  if (t === 'form_submitted') return 'Program form activity'
  if (t === 'withdrawn') return 'Application withdrawn'
  if (t === 'comment') return 'Comment recorded'
  return t.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()) || 'Event'
}

function timelineIconName(eventType) {
  const t = eventType || ''
  if (t === 'submitted') return 'bi-send'
  if (t.startsWith('status_')) {
    if (t.includes('approved')) return 'bi-check-circle'
    if (t.includes('rejected')) return 'bi-x-circle'
    if (t.includes('review')) return 'bi-eye'
    return 'bi-flag'
  }
  if (t === 'form_submitted') return 'bi-file-earmark-text'
  if (t === 'withdrawn') return 'bi-door-open'
  if (t === 'comment') return 'bi-chat-dots'
  return 'bi-circle'
}

function timelineIconBg(eventType) {
  const t = eventType || ''
  if (t === 'submitted') return 'bg-info'
  if (t.startsWith('status_')) {
    if (t.includes('approved')) return 'bg-success'
    if (t.includes('rejected')) return 'bg-danger'
    if (t.includes('completed')) return 'bg-primary'
    return 'bg-warning text-dark'
  }
  if (t === 'form_submitted') return 'bg-secondary'
  if (t === 'withdrawn') return 'bg-dark'
  if (t === 'comment') return 'bg-primary'
  return 'bg-secondary'
}

async function submitApplication() {
  if (!confirm('Are you sure you want to submit this application? You will not be able to edit it after submission.')) {
    return
  }

  try {
    await api.post(`/api/applications/${route.params.id}/submit/`)
    success('Application submitted successfully!')
    await fetchApplication()
  } catch (err) {
    console.error('Failed to submit application:', err)
    const msg = err.response?.data?.error || 'Failed to submit application'
    errorToast(msg)
  }
}

async function confirmDelete() {
  if (confirm('Are you sure you want to delete this application? This action cannot be undone.')) {
    await deleteApplication()
  }
}

async function deleteApplication() {
  try {
    await api.delete(`/api/applications/${route.params.id}/`)
    success('Application deleted successfully')
    router.push({ name: 'Applications' })
  } catch (err) {
    console.error('Failed to delete application:', err)
    errorToast('Failed to delete application')
  }
}

async function updateApplicationStatus() {
  if (!reviewStatus.value) return
  try {
    updatingStatus.value = true
    await api.patch(`/api/applications/${route.params.id}/`, { status: reviewStatus.value })
    success('Status updated')
    reviewStatus.value = ''
    await fetchApplication()
  } catch (err) {
    console.error('Failed to update status:', err)
    const msg = err.response?.data?.status?.[0] || err.response?.data?.detail || 'Failed to update status'
    errorToast(msg)
  } finally {
    updatingStatus.value = false
  }
}

async function submitComment() {
  const text = newCommentText.value.trim()
  if (!text || !application.value?.id) return

  try {
    submittingComment.value = true
    await api.post('/api/comments/', {
      application: application.value.id,
      text,
      is_private: canPostPrivateComment.value ? newCommentPrivate.value : false,
    })
    newCommentText.value = ''
    newCommentPrivate.value = false
    success('Comment posted successfully')
    await fetchComments()
  } catch (err) {
    console.error('Failed to submit comment:', err)
    const message =
      err.response?.data?.text?.[0] ||
      err.response?.data?.detail ||
      'Failed to post comment'
    errorToast(message)
  } finally {
    submittingComment.value = false
  }
}

async function validateDocument(docId, result) {
  try {
    docValidatingId.value = docId
    await api.post(`/api/documents/${docId}/validate_document/`, { result, details: '' })
    success(result === 'valid' ? 'Document marked valid' : 'Document marked invalid')
    await fetchApplication()
  } catch (err) {
    console.error('Failed to validate document:', err)
    errorToast(err.response?.data?.detail || 'Failed to validate document')
  } finally {
    docValidatingId.value = null
  }
}

onMounted(() => {
  fetchApplication()
  if (typeof window !== 'undefined') {
    window.addEventListener('seim-application-sync', onApplicationSyncEvent)
  }
})

onBeforeUnmount(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('seim-application-sync', onApplicationSyncEvent)
  }
})
</script>

<style scoped>
.application-detail {
  min-height: 100vh;
  background-color: #f8f9fa;
}

.timeline {
  position: relative;
  padding-left: 30px;
}

.timeline-item {
  position: relative;
  padding-bottom: 20px;
}

.timeline-item:not(:last-child)::before {
  content: '';
  position: absolute;
  left: -19px;
  top: 30px;
  width: 2px;
  height: calc(100% - 10px);
  background: #dee2e6;
}

.timeline-icon {
  position: absolute;
  left: -30px;
  top: 0;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
}

.timeline-content h6 {
  margin-bottom: 0.25rem;
}

.badge {
  font-size: 0.875rem;
  padding: 0.5rem 1rem;
}

.comment-item:last-child {
  margin-bottom: 0;
}

.comment-text {
  white-space: pre-wrap;
}
</style>
