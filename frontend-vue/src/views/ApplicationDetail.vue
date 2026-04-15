<template>
  <div class="application-detail">
    <div class="container-fluid mt-4">
      <!-- Breadcrumb -->
      <nav :aria-label="t('applicationDetailPage.breadcrumbAria')">
        <ol class="breadcrumb">
          <li class="breadcrumb-item">
            <router-link :to="{ name: 'Dashboard' }">{{ t('route.names.Dashboard') }}</router-link>
          </li>
          <li class="breadcrumb-item">
            <router-link :to="{ name: 'Applications' }">{{ t('route.names.Applications') }}</router-link>
          </li>
          <li class="breadcrumb-item active">{{
            programDisplayName(application) || t('applicationDetailPage.loadingProgram')
          }}</li>
        </ol>
      </nav>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">{{ t('applicationDetailPage.loadingSpinner') }}</span>
        </div>
        <p class="mt-3 text-muted">{{ t('applicationDetailPage.loadingDetails') }}</p>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="alert alert-danger">
        <i class="bi bi-exclamation-triangle me-2"></i>
        {{ error }}
        <router-link :to="{ name: 'Applications' }" class="btn btn-sm btn-outline-danger ms-3">
          {{ t('applicationDetailPage.backToApplications') }}
        </router-link>
      </div>

      <!-- Application Details -->
      <div v-else-if="application" data-testid="application-detail-page">
        <!-- Header -->
        <div class="row mb-4">
          <div class="col-md-8">
            <h2>
              <i class="bi bi-file-earmark-text me-2"></i>
              {{ programDisplayName(application) }}
            </h2>
            <p class="text-muted">
              <i class="bi bi-building me-1"></i>
              {{ application.program?.institution || t('applicationDetailPage.notAvailable') }}
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
              <i class="bi bi-pencil me-1"></i>{{ t('applicationDetailPage.edit') }}
            </router-link>
          </div>
        </div>

        <div v-if="application.readiness" class="row mb-3" data-testid="readiness-banner">
          <div class="col-12">
            <div class="card border-0 shadow-sm">
              <div class="card-body py-3 d-flex flex-wrap align-items-center gap-3">
                <div>
                  <span class="text-muted small d-block">{{ t('applicationDetailPage.readinessLabel') }}</span>
                  <span class="badge fs-6" :class="readinessLevelBadgeClass(application.readiness.level)">
                    {{ application.readiness.score }}%
                  </span>
                </div>
                <div class="flex-grow-1" style="min-width: 220px">
                  <p class="small mb-2">{{ application.readiness.headline }}</p>
                  <div v-if="application.status === 'draft'" class="progress" style="height: 6px">
                    <div
                      class="progress-bar"
                      :class="readinessScoreBarClass(application.readiness.score)"
                      role="progressbar"
                      :style="{ width: Math.min(100, application.readiness.score) + '%' }"
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div
          v-if="isCoordinator && application.scholarship_allocation_score"
          class="row mb-3"
          data-testid="scholarship-score-panel"
        >
          <div class="col-12">
            <div class="card border-secondary shadow-sm">
              <div class="card-header d-flex flex-wrap justify-content-between align-items-center gap-2">
                <h5 class="mb-0">
                  <i class="bi bi-calculator me-2"></i>{{ t('applicationDetailPage.scholarshipScoring.title') }}
                </h5>
                <div
                  class="btn-group btn-group-sm"
                  role="group"
                  :aria-label="t('applicationDetailPage.scholarshipScoring.exportGroupAria')"
                >
                  <button
                    type="button"
                    class="btn btn-outline-secondary"
                    :disabled="scholarshipExportLoading"
                    @click="downloadScholarshipCohortExport('csv')"
                  >
                    <span
                      v-if="scholarshipExportLoading"
                      class="spinner-border spinner-border-sm"
                      role="status"
                      aria-hidden="true"
                    ></span>
                    <template v-else>{{ t('applicationDetailPage.scholarshipScoring.exportCohortCsv') }}</template>
                  </button>
                  <button
                    type="button"
                    class="btn btn-outline-secondary"
                    :disabled="scholarshipExportLoading"
                    @click="downloadScholarshipCohortExport('xlsx')"
                  >
                    {{ t('applicationDetailPage.scholarshipScoring.exportCohortXlsx') }}
                  </button>
                  <button
                    type="button"
                    class="btn btn-outline-secondary"
                    :disabled="scholarshipExportLoading"
                    @click="downloadScholarshipCohortExport('pdf')"
                  >
                    {{ t('applicationDetailPage.scholarshipScoring.exportCohortPdf') }}
                  </button>
                </div>
              </div>
              <div class="card-body">
                <p class="small text-muted mb-2">
                  {{ application.scholarship_allocation_score.ruleset_label }} ({{ application.scholarship_allocation_score.ruleset_id }})
                </p>
                <div class="d-flex flex-wrap align-items-baseline gap-3 mb-3">
                  <div>
                    <span class="text-muted small d-block">{{ t('applicationDetailPage.scholarshipScoring.totalLabel') }}</span>
                    <span class="fs-4 fw-semibold">
                      {{ application.scholarship_allocation_score.total_points }}
                      <span class="text-muted fs-6">/ {{ application.scholarship_allocation_score.max_points }}</span>
                    </span>
                  </div>
                  <p v-if="application.scholarship_allocation_score.flags?.withdrawn" class="small text-warning mb-0">
                    <i class="bi bi-exclamation-triangle me-1"></i>{{ t('applicationDetailPage.scholarshipScoring.withdrawnNote') }}
                  </p>
                </div>
                <div class="table-responsive">
                  <table class="table table-sm table-bordered mb-0">
                    <thead class="table-light">
                      <tr>
                        <th scope="col">{{ t('applicationDetailPage.scholarshipScoring.colFactor') }}</th>
                        <th scope="col" class="text-end">{{ t('applicationDetailPage.scholarshipScoring.colPoints') }}</th>
                        <th scope="col">{{ t('applicationDetailPage.scholarshipScoring.colDetail') }}</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="row in application.scholarship_allocation_score.factors" :key="row.id">
                        <td>{{ row.label }}</td>
                        <td class="text-end text-nowrap">{{ row.points }} / {{ row.max_points }}</td>
                        <td class="small">{{ row.detail }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <p class="small text-muted mt-3 mb-1">
                  <strong>{{ t('applicationDetailPage.scholarshipScoring.tieBreakers') }}</strong>
                  {{ (application.scholarship_allocation_score.tie_breakers || []).join(', ') }}
                </p>
                <p class="small text-muted mb-0 fst-italic">
                  {{ application.scholarship_allocation_score.disclaimer }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div class="row">
          <!-- Main Content -->
          <div class="col-lg-8">
            <!-- Program Information -->
            <div class="card mb-4">
              <div class="card-header">
                <h5 class="mb-0"><i class="bi bi-info-circle me-2"></i>{{ t('applicationDetailPage.programInfo') }}</h5>
              </div>
              <div class="card-body">
                <div class="row mb-3">
                  <div class="col-md-6">
                    <label class="text-muted small">{{ t('applicationDetailPage.labelProgramName') }}</label>
                    <p class="fw-bold">{{ programDisplayName(application) }}</p>
                  </div>
                  <div class="col-md-6">
                    <label class="text-muted small">{{ t('applicationDetailPage.labelInstitution') }}</label>
                    <p class="fw-bold">{{ application.program?.institution }}</p>
                  </div>
                </div>
                <div class="row mb-3">
                  <div class="col-md-6">
                    <label class="text-muted small">{{ t('applicationDetailPage.labelCountry') }}</label>
                    <p class="fw-bold">{{ application.program?.country || t('applicationDetailPage.notAvailable') }}</p>
                  </div>
                  <div class="col-md-6">
                    <label class="text-muted small">{{ t('applicationDetailPage.labelDuration') }}</label>
                    <p class="fw-bold">{{ application.program?.duration || t('applicationDetailPage.notAvailable') }}</p>
                  </div>
                </div>
                <div v-if="application.program?.description">
                  <label class="text-muted small">{{ t('applicationDetailPage.labelDescription') }}</label>
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
                  <i class="bi bi-clipboard-check me-2"></i>{{ t('applicationDetailPage.requiredDocuments') }}
                </h5>
                <span
                  class="badge"
                  :class="application.document_checklist.complete ? 'bg-success' : 'bg-warning text-dark'"
                >
                  {{
                    t('applicationDetailPage.approvedFraction', {
                      approved: application.document_checklist.approved_count,
                      required: application.document_checklist.required_count,
                    })
                  }}
                </span>
              </div>
              <div class="card-body">
                <p v-if="application.status === 'draft' && !application.document_checklist.complete" class="text-muted small">
                  {{ t('applicationDetailPage.checklistDraftHint') }}
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
                        {{ t('applicationDetailPage.view') }}
                      </router-link>
                    </div>
                  </li>
                </ul>
              </div>
            </div>

            <!-- Activity timeline (server TimelineEvent rows + record start) -->
            <div class="card mb-4" data-testid="activity-timeline-card">
              <div class="card-header">
                <h5 class="mb-0"><i class="bi bi-clock-history me-2"></i>{{ t('applicationDetailPage.activityTimeline') }}</h5>
              </div>
              <div class="card-body">
                <div v-if="timelineLoading" class="text-center py-3">
                  <div class="spinner-border spinner-border-sm text-primary" role="status">
                    <span class="visually-hidden">{{ t('applicationDetailPage.loadingTimeline') }}</span>
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
                      <h6>{{ t('applicationDetailPage.timelineCreated') }}</h6>
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
                <h5 class="mb-0"><i class="bi bi-chat-dots me-2"></i>{{ t('applicationDetailPage.comments') }}</h5>
              </div>
              <div class="card-body">
                <div v-if="commentsLoading" class="text-center py-3">
                  <div class="spinner-border spinner-border-sm text-primary" role="status">
                    <span class="visually-hidden">{{ t('applicationDetailPage.loadingComments') }}</span>
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
                          <span v-if="comment.is_private" class="badge text-bg-warning">{{
                            t('applicationDetailPage.privateBadge')
                          }}</span>
                        </div>
                        <p class="text-muted small mb-0">{{ formatDateTime(comment.created_at) }}</p>
                      </div>
                    </div>
                    <p class="mb-0 comment-text">{{ comment.text }}</p>
                  </div>
                </div>
                <p v-else class="text-muted text-center py-3">
                  <i class="bi bi-info-circle me-1"></i>
                  {{ t('applicationDetailPage.noCommentsYet') }}
                </p>

                <form class="border-top pt-3" @submit.prevent="submitComment">
                  <div class="mb-3">
                    <label class="form-label" for="commentText">{{ t('applicationDetailPage.addCommentLabel') }}</label>
                    <textarea
                      id="commentText"
                      v-model="newCommentText"
                      class="form-control"
                      rows="3"
                      maxlength="2000"
                      :placeholder="t('applicationDetailPage.commentPlaceholder')"
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
                      {{ t('applicationDetailPage.privateCommentCheckbox') }}
                    </label>
                  </div>
                  <div class="d-flex justify-content-end">
                    <button
                      type="submit"
                      class="btn btn-primary"
                      :disabled="submittingComment || !newCommentText.trim()"
                    >
                      <span v-if="submittingComment" class="spinner-border spinner-border-sm me-2"></span>
                      {{ t('applicationDetailPage.postComment') }}
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
                <h6 class="mb-0"><i class="bi bi-pencil-square me-2"></i>{{ t('applicationDetailPage.reviewApplication') }}</h6>
              </div>
              <div class="card-body">
                <div class="mb-3">
                  <label class="form-label small">{{ t('applicationDetailPage.changeStatus') }}</label>
                  <select v-model="reviewStatus" class="form-select form-select-sm">
                    <option value="">{{ t('applicationDetailPage.selectNewStatus') }}</option>
                    <option value="under_review">{{ t('applicationDetailPage.status.under_review') }}</option>
                    <option value="approved">{{ t('applicationDetailPage.status.approved') }}</option>
                    <option value="rejected">{{ t('applicationDetailPage.status.rejected') }}</option>
                    <option value="completed">{{ t('applicationDetailPage.status.completed') }}</option>
                  </select>
                </div>
                <button
                  class="btn btn-primary btn-sm w-100"
                  :disabled="!reviewStatus || updatingStatus"
                  @click="updateApplicationStatus"
                >
                  <span v-if="updatingStatus" class="spinner-border spinner-border-sm me-1"></span>
                  {{ t('applicationDetailPage.updateStatus') }}
                </button>
              </div>
            </div>

            <!-- Quick Actions -->
            <div class="card mb-4">
              <div class="card-header">
                <h6 class="mb-0">{{ t('applicationDetailPage.quickActions') }}</h6>
              </div>
              <div class="card-body">
                <div class="d-grid gap-2">
                  <router-link
                    v-if="application.status === 'draft'"
                    :to="{ name: 'ApplicationEdit', params: { id: application.id } }"
                    class="btn btn-primary"
                    data-testid="edit-application-link"
                  >
                    <i class="bi bi-pencil me-2"></i>{{ t('applicationDetailPage.editApplication') }}
                  </router-link>
                  <button
                    v-if="application.status === 'draft'"
                    class="btn btn-success"
                    :disabled="submitBlockedByDocuments"
                    :title="submitBlockedByDocuments ? t('applicationDetailPage.submitBlockedTitle') : ''"
                    @click="submitApplication"
                    data-testid="submit-application-btn"
                  >
                    <i class="bi bi-send me-2"></i>{{ t('applicationDetailPage.submitApplication') }}
                  </button>
                  <button
                    v-if="application.status === 'draft'"
                    class="btn btn-danger"
                    @click="confirmDelete"
                  >
                    <i class="bi bi-trash me-2"></i>{{ t('applicationDetailPage.deleteApplication') }}
                  </button>
                  <router-link :to="{ name: 'Applications' }" class="btn btn-outline-secondary">
                    <i class="bi bi-arrow-left me-2"></i>{{ t('applicationDetailPage.backToList') }}
                  </router-link>
                </div>
              </div>
            </div>

            <!-- Application Details -->
            <div class="card mb-4">
              <div class="card-header">
                <h6 class="mb-0">{{ t('applicationDetailPage.sidebarApplicationDetails') }}</h6>
              </div>
              <div class="card-body">
                <div class="mb-3">
                  <label class="text-muted small">{{ t('applicationDetailPage.applicationId') }}</label>
                  <p class="small font-monospace">{{ application.id }}</p>
                </div>
                <div class="mb-3">
                  <label class="text-muted small">{{ t('applicationDetailPage.statusLabel') }}</label>
                  <p>
                    <span class="badge" :class="statusClass(application.status)">
                      {{ formatStatus(application.status) }}
                    </span>
                  </p>
                </div>
                <div class="mb-3">
                  <label class="text-muted small">{{ t('applicationDetailPage.created') }}</label>
                  <p>{{ formatDateTime(application.created_at) }}</p>
                </div>
                <div v-if="application.submitted_at" class="mb-3">
                  <label class="text-muted small">{{ t('applicationDetailPage.submitted') }}</label>
                  <p>{{ formatDateTime(application.submitted_at) }}</p>
                </div>
                <div class="mb-3">
                  <label class="text-muted small">{{ t('applicationDetailPage.lastUpdated') }}</label>
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
                <h6 class="mb-0">{{ t('applicationDetailPage.documentsHeading') }}</h6>
                <router-link :to="{ name: 'Documents' }" class="btn btn-sm btn-outline-primary">
                  {{ t('applicationDetailPage.viewAll') }}
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
                        {{ documentTypeLabel(doc.type, t('documentDetailPage.notAvailable')) }}
                      </router-link>
                      <span class="d-flex align-items-center gap-1">
                        <span class="badge" :class="doc.is_valid === true ? 'bg-success' : doc.is_valid === false ? 'bg-danger' : 'bg-warning'">
                          {{
                            doc.is_valid === true
                              ? t('applicationDetailPage.docValid')
                              : doc.is_valid === false
                                ? t('applicationDetailPage.docInvalid')
                                : t('applicationDetailPage.docPending')
                          }}
                        </span>
                        <template v-if="isCoordinator">
                          <template v-if="docValidatingId !== doc.id">
                            <button
                              type="button"
                              class="btn btn-sm btn-outline-success"
                              :title="t('applicationDetailPage.markValidTitle')"
                              @click="validateDocument(doc.id, 'valid')"
                            >
                              <i class="bi bi-check-lg"></i>
                            </button>
                            <button
                              type="button"
                              class="btn btn-sm btn-outline-danger"
                              :title="t('applicationDetailPage.markInvalidTitle')"
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
                  {{ t('applicationDetailPage.noDocumentsUploaded') }}
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
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import DocumentUpload from '@/components/DocumentUpload.vue'
import api from '@/services/api'
import { readinessLevelBadgeClass, readinessScoreBarClass } from '@/utils/applicationReadiness'
import { documentTypeLabel } from '@/utils/documentApi'

const route = useRoute()
const router = useRouter()
const { t, te, locale } = useI18n()
const authStore = useAuthStore()
const { success, error: errorToast } = useToast()

function programDisplayName(app) {
  if (!app) return ''
  return (app.program_name || app.program?.name || '').trim()
}

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
const scholarshipExportLoading = ref(false)

const SCHOLARSHIP_EXPORT_MIME = {
  csv: 'text/csv;charset=utf-8',
  xlsx: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  pdf: 'application/pdf',
}

async function downloadScholarshipCohortExport(format = 'csv') {
  const programId = application.value?.program
  if (!programId) {
    errorToast(t('applicationDetailPage.scholarshipScoring.exportMissingProgram'))
    return
  }
  const fmt = format === 'xlsx' || format === 'pdf' ? format : 'csv'
  scholarshipExportLoading.value = true
  try {
    const response = await api.get('/api/applications/scholarship-scores-export/', {
      params: { program: programId, export_format: fmt },
      responseType: 'blob',
    })
    const blob = new Blob([response.data], { type: SCHOLARSHIP_EXPORT_MIME[fmt] })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `scholarship-scores-${programId}.${fmt}`
    a.rel = 'noopener noreferrer'
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
    success(t('applicationDetailPage.scholarshipScoring.exportSuccess'))
  } catch (err) {
    console.error('Scholarship export failed:', err)
    errorToast(t('applicationDetailPage.scholarshipScoring.exportError'))
  } finally {
    scholarshipExportLoading.value = false
  }
}

async function fetchApplication() {
  try {
    loading.value = true
    error.value = null

    const response = await api.get(`/api/applications/${route.params.id}/`)
    application.value = response.data
    await Promise.all([fetchApplicationDocuments(), fetchComments(), fetchTimelineEvents()])
  } catch (err) {
    console.error('Failed to fetch application:', err)
    error.value = t('applicationDetailPage.loadError')
    errorToast(t('applicationDetailPage.loadToastError'))
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
    timelineError.value = t('applicationDetailPage.timelineLoadError')
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
    commentsError.value = t('applicationDetailPage.commentsLoadError')
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
  if (!status) return t('applicationDetailPage.status.unknown')
  const key = `applicationDetailPage.status.${status}`
  if (te(key)) return t(key)
  return String(status).replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())
}

function formatDateTime(dateString) {
  if (!dateString) return t('applicationDetailPage.notAvailable')
  const loc = locale.value === 'es' ? 'es' : 'en-US'
  const date = new Date(dateString)
  return date.toLocaleString(loc, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function formatRole(role) {
  if (!role) return t('applicationDetailPage.roles.user')
  const key = `applicationDetailPage.roles.${role}`
  if (te(key)) return t(key)
  return String(role).replace(/_/g, ' ').replace(/\b\w/g, (letter) => letter.toUpperCase())
}

function formatCommentAuthor(comment) {
  if (comment.author && currentUserId.value && comment.author === currentUserId.value) {
    return t('applicationDetailPage.commentAuthorYou')
  }
  return comment.author_name || t('applicationDetailPage.unknownUser')
}

function checklistStatusLabel(status) {
  const key = `applicationDetailPage.checklist.${status}`
  if (te(key)) return t(key)
  return status
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
  const evtType = event.event_type || ''
  if (evtType === 'submitted') return t('applicationDetailPage.timeline.applicationSubmitted')
  if (evtType.startsWith('status_')) {
    const code = evtType.slice(7)
    const statusKey = `applicationDetailPage.status.${code}`
    const label = te(statusKey)
      ? t(statusKey)
      : code.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
    return t('applicationDetailPage.timeline.statusChanged', { status: label })
  }
  if (evtType === 'form_submitted') return t('applicationDetailPage.timeline.programFormActivity')
  if (evtType === 'withdrawn') return t('applicationDetailPage.timeline.applicationWithdrawn')
  if (evtType === 'comment') return t('applicationDetailPage.timeline.commentRecorded')
  return (
    evtType.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()) || t('applicationDetailPage.status.unknown')
  )
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
  if (!confirm(t('applicationDetailPage.confirmSubmit'))) {
    return
  }

  try {
    await api.post(`/api/applications/${route.params.id}/submit/`)
    success(t('applicationDetailPage.toastSubmitted'))
    await fetchApplication()
  } catch (err) {
    console.error('Failed to submit application:', err)
    const msg = err.response?.data?.error || t('applicationDetailPage.toastSubmitFailed')
    errorToast(msg)
  }
}

async function confirmDelete() {
  if (confirm(t('applicationDetailPage.confirmDelete'))) {
    await deleteApplication()
  }
}

async function deleteApplication() {
  try {
    await api.delete(`/api/applications/${route.params.id}/`)
    success(t('applicationDetailPage.toastDeleted'))
    router.push({ name: 'Applications' })
  } catch (err) {
    console.error('Failed to delete application:', err)
    errorToast(t('applicationDetailPage.toastDeleteFailed'))
  }
}

async function updateApplicationStatus() {
  if (!reviewStatus.value) return
  try {
    updatingStatus.value = true
    await api.patch(`/api/applications/${route.params.id}/`, { status: reviewStatus.value })
    success(t('applicationDetailPage.toastStatusUpdated'))
    reviewStatus.value = ''
    await fetchApplication()
  } catch (err) {
    console.error('Failed to update status:', err)
    const msg =
      err.response?.data?.status?.[0] ||
      err.response?.data?.detail ||
      t('applicationDetailPage.toastUpdateStatusFailed')
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
    success(t('applicationDetailPage.toastCommentPosted'))
    await fetchComments()
  } catch (err) {
    console.error('Failed to submit comment:', err)
    const message =
      err.response?.data?.text?.[0] ||
      err.response?.data?.detail ||
      t('applicationDetailPage.toastPostCommentFailed')
    errorToast(message)
  } finally {
    submittingComment.value = false
  }
}

async function validateDocument(docId, result) {
  try {
    docValidatingId.value = docId
    await api.post(`/api/documents/${docId}/validate_document/`, { result, details: '' })
    success(
      result === 'valid'
        ? t('applicationDetailPage.toastValidateValid')
        : t('applicationDetailPage.toastValidateInvalid')
    )
    await fetchApplication()
  } catch (err) {
    console.error('Failed to validate document:', err)
    errorToast(err.response?.data?.detail || t('applicationDetailPage.toastValidateFailed'))
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
  background-color: var(--seim-app-bg);
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
