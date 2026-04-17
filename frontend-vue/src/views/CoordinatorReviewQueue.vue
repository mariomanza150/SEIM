<template>
  <div class="review-queue-page">
    <PageHeader
      :title="t('reviewQueuePage.pageHeading')"
      :subtitle="t('reviewQueuePage.pageSubtitle')"
      icon-class="bi bi-clipboard-check"
      test-id="review-queue-heading"
    >
      <template #breadcrumb>
        <nav :aria-label="t('reviewQueuePage.breadcrumbAria')">
          <ol class="breadcrumb">
            <li class="breadcrumb-item">
              <router-link :to="{ name: 'Dashboard' }">{{ t('route.names.Dashboard') }}</router-link>
            </li>
            <li class="breadcrumb-item active">{{ t('route.names.CoordinatorReviewQueue') }}</li>
          </ol>
        </nav>
      </template>
      <template #actions>
        <router-link :to="{ name: 'Applications' }" class="btn btn-outline-secondary">
          <i class="bi bi-person-lines-fill me-1" aria-hidden="true"></i>{{ t('reviewQueuePage.myApplications') }}
        </router-link>
      </template>
    </PageHeader>

      <div class="card mb-4" data-testid="review-queue-filters">
        <div class="card-body">
          <div class="row g-3 align-items-end">
            <div class="col-md-4">
              <label class="form-label">{{ t('reviewQueuePage.searchLabel') }}</label>
              <input
                v-model="filters.search"
                type="text"
                class="form-control"
                :placeholder="t('reviewQueuePage.searchPlaceholder')"
                @input="debouncedSearch"
                data-testid="review-queue-search"
              />
            </div>
            <div class="col-md-8">
              <label class="form-label d-block">{{ t('reviewQueuePage.quickFilters') }}</label>
              <div class="d-flex flex-wrap gap-2">
                <div class="form-check form-check-inline">
                  <input
                    id="fq-pending"
                    v-model="filters.pending_review"
                    class="form-check-input"
                    type="checkbox"
                    @change="fetchApplications"
                  />
                  <label class="form-check-label" for="fq-pending">{{ t('reviewQueuePage.filterPendingReview') }}</label>
                </div>
                <div class="form-check form-check-inline">
                  <input
                    id="fq-resubmit"
                    v-model="filters.needs_document_resubmit"
                    class="form-check-input"
                    type="checkbox"
                    @change="fetchApplications"
                  />
                  <label class="form-check-label" for="fq-resubmit">{{ t('reviewQueuePage.filterDocumentResubmit') }}</label>
                </div>
                <div class="form-check form-check-inline">
                  <input
                    id="fq-assigned"
                    v-model="filters.assigned_to_me"
                    class="form-check-input"
                    type="checkbox"
                    @change="fetchApplications"
                  />
                  <label class="form-check-label" for="fq-assigned">{{ t('reviewQueuePage.filterAssignedToMe') }}</label>
                </div>
              </div>
            </div>
            <div class="col-md-3">
              <label class="form-label">{{ t('reviewQueuePage.statusLabel') }}</label>
              <select v-model="filters.status" class="form-select" @change="fetchApplications">
                <option value="">{{ t('reviewQueuePage.statusAll') }}</option>
                <option value="draft">{{ t('reviewQueuePage.status.draft') }}</option>
                <option value="submitted">{{ t('reviewQueuePage.status.submitted') }}</option>
                <option value="under_review">{{ t('reviewQueuePage.status.under_review') }}</option>
                <option value="approved">{{ t('reviewQueuePage.status.approved') }}</option>
                <option value="rejected">{{ t('reviewQueuePage.status.rejected') }}</option>
                <option value="completed">{{ t('reviewQueuePage.status.completed') }}</option>
              </select>
            </div>
            <div class="col-md-3">
              <label class="form-label">{{ t('reviewQueuePage.sortLabel') }}</label>
              <select v-model="filters.ordering" class="form-select" @change="fetchApplications">
                <option value="-submitted_at">{{ t('reviewQueuePage.sortRecentlySubmitted') }}</option>
                <option value="-created_at">{{ t('reviewQueuePage.sortNewest') }}</option>
                <option value="created_at">{{ t('reviewQueuePage.sortOldest') }}</option>
              </select>
            </div>
            <div class="col-md-2">
              <button type="button" class="btn btn-outline-secondary w-100" @click="clearFilters">
                {{ t('reviewQueuePage.clearFilters') }}
              </button>
            </div>
            <div class="col-12 d-flex justify-content-end pt-1">
              <button
                type="button"
                class="btn btn-link btn-sm px-0"
                :aria-expanded="advancedFiltersOpen ? 'true' : 'false'"
                @click="advancedFiltersOpen = !advancedFiltersOpen"
              >
                <i class="bi" :class="advancedFiltersOpen ? 'bi-chevron-up' : 'bi-chevron-down'" aria-hidden="true"></i>
                <span class="ms-1">{{ t('reviewQueuePage.advancedFiltersToggle') }}</span>
              </button>
            </div>
            <div v-if="advancedFiltersOpen" class="col-12 border-top pt-3 mt-2">
              <div class="d-flex flex-wrap align-items-end gap-2 mb-2">
                <div class="flex-grow-1" style="min-width: 200px">
                  <label class="form-label small text-muted mb-1">{{ t('reviewQueuePage.presetSaveLabel') }}</label>
                  <div class="input-group input-group-sm">
                    <input
                      v-model="newPresetName"
                      type="text"
                      class="form-control"
                      :placeholder="t('reviewQueuePage.presetNamePlaceholder')"
                      data-testid="review-queue-preset-name"
                    />
                    <button
                      type="button"
                      class="btn btn-outline-primary"
                      :disabled="!newPresetName.trim() || presetsLoading"
                      data-testid="review-queue-preset-save"
                      @click="savePreset"
                    >
                      {{ t('reviewQueuePage.presetSave') }}
                    </button>
                  </div>
                </div>
                <div class="form-check mb-1">
                  <input
                    id="preset-default"
                    v-model="saveAsDefault"
                    class="form-check-input"
                    type="checkbox"
                  />
                  <label class="form-check-label small" for="preset-default">{{ t('reviewQueuePage.presetDefaultQueue') }}</label>
                </div>
              </div>
              <div v-if="savedPresets.length" class="small">
                <span class="text-muted me-2">{{ t('reviewQueuePage.presetSavedPrefix') }}</span>
                <span
                  v-for="p in savedPresets"
                  :key="p.id"
                  class="d-inline-flex align-items-center gap-1 me-3 mb-1"
                >
                  <button
                    type="button"
                    class="btn btn-link btn-sm p-0"
                    data-testid="review-queue-preset-apply"
                    @click="applyPreset(p)"
                  >
                    {{ p.name }}
                  </button>
                  <i
                    v-if="p.is_default"
                    class="bi bi-star-fill text-warning"
                    :title="t('reviewQueuePage.presetDefaultTitle')"
                    :aria-label="t('reviewQueuePage.presetDefaultAria')"
                  />
                  <button
                    v-else
                    type="button"
                    class="btn btn-link btn-sm p-0 text-secondary"
                    :title="t('reviewQueuePage.presetSetDefaultTitle')"
                    :aria-label="t('reviewQueuePage.presetSetDefaultAria')"
                    @click="setDefaultPreset(p)"
                  >
                    <i class="bi bi-star"></i>
                  </button>
                  <button
                    type="button"
                    class="btn btn-link btn-sm p-0 text-danger"
                    :title="t('reviewQueuePage.presetRemoveTitle')"
                    :aria-label="t('reviewQueuePage.presetRemoveAria')"
                    @click="deletePreset(p)"
                  >
                    <i class="bi bi-trash"></i>
                  </button>
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <LoadingState v-if="loading" :spinner-label="t('reviewQueuePage.loading')" />
      <ErrorAlert v-else-if="error" :message="error" />
      <EmptyState
        v-else-if="applications.length === 0"
        test-id="review-queue-empty"
        :body="t('reviewQueuePage.empty')"
      />
      <div v-else class="table-responsive card">
        <table class="table table-hover mb-0">
          <thead class="table-light">
            <tr>
              <th>{{ t('reviewQueuePage.colStudent') }}</th>
              <th>{{ t('reviewQueuePage.colProgram') }}</th>
              <th>{{ t('reviewQueuePage.colStatus') }}</th>
              <th>{{ t('reviewQueuePage.colCoordinator') }}</th>
              <th>{{ t('reviewQueuePage.colSubmitted') }}</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="app in applications" :key="app.id">
              <td>
                <div class="fw-medium">{{ app.student_display_name || t('reviewQueuePage.emDash') }}</div>
                <div class="small text-muted">{{ app.student_email }}</div>
              </td>
              <td>{{ app.program_name || app.program?.name || t('reviewQueuePage.emDash') }}</td>
              <td>
                <span class="badge" :class="statusClass(app.status)">{{ formatStatus(app.status) }}</span>
              </td>
              <td class="small">
                {{ app.assigned_coordinator_name || (app.effective_coordinator?.full_name) || t('reviewQueuePage.emDash') }}
              </td>
              <td class="small text-muted">{{ formatDate(app.submitted_at) }}</td>
              <td class="text-end">
                <router-link
                  :to="{ name: 'ApplicationDetail', params: { id: app.id } }"
                  class="btn btn-sm btn-outline-primary"
                  data-testid="review-queue-open-detail"
                >
                  {{ t('reviewQueuePage.openDetail') }}
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <Pagination
        v-if="!loading"
        :count="pagination.count"
        :page-size="pagination.pageSize"
        :current-page="pagination.currentPage"
        :can-go-previous="!!pagination.previous"
        :can-go-next="!!pagination.next"
        :aria-label="t('reviewQueuePage.paginationAria')"
        ul-class="mt-3"
        @page-change="goToPage"
      />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useToast } from '@/composables/useToast'
import { useConfirm } from '@/composables/useConfirm'
import api from '@/services/api'
import PageHeader from '@/components/PageHeader.vue'
import Pagination from '@/components/Pagination.vue'
import LoadingState from '@/components/State/LoadingState.vue'
import ErrorAlert from '@/components/State/ErrorAlert.vue'
import EmptyState from '@/components/State/EmptyState.vue'
import {
  REVIEW_QUEUE_SEARCH_TYPE,
  deserializeReviewQueueFilters,
  serializeReviewQueueFilters,
} from '@/utils/reviewQueuePresets'

const { t, te, locale } = useI18n()
const { success, error: errorToast } = useToast()
const { confirm } = useConfirm()

const applications = ref([])
const loading = ref(true)
const error = ref(null)
const advancedFiltersOpen = ref(false)
const savedPresets = ref([])
const presetsLoading = ref(false)
const newPresetName = ref('')
const saveAsDefault = ref(false)

const filters = ref({
  search: '',
  status: '',
  ordering: '-submitted_at',
  pending_review: false,
  needs_document_resubmit: false,
  assigned_to_me: false,
})

const pagination = ref({
  count: 0,
  next: null,
  previous: null,
  currentPage: 1,
  pageSize: 20,
})

let searchTimeout = null
function debouncedSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => fetchApplications(), 400)
}

async function fetchApplications(page = 1) {
  try {
    loading.value = true
    error.value = null
    const params = {
      page,
      ordering: filters.value.ordering,
    }
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.status) params.status = filters.value.status
    if (filters.value.pending_review) params.pending_review = 'true'
    if (filters.value.needs_document_resubmit) params.needs_document_resubmit = 'true'
    if (filters.value.assigned_to_me) params.assigned_to_me = 'true'

    const response = await api.get('/api/applications/', { params })
    applications.value = response.data.results || response.data
    if (response.data.count !== undefined) {
      pagination.value = {
        count: response.data.count,
        next: response.data.next,
        previous: response.data.previous,
        currentPage: page,
        pageSize: pagination.value.pageSize,
      }
    }
  } catch (err) {
    const msg = t('reviewQueuePage.loadError')
    error.value = msg
    errorToast(msg)
  } finally {
    loading.value = false
  }
}

function goToPage(page) {
  fetchApplications(page)
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function clearFilters() {
  filters.value = {
    search: '',
    status: '',
    ordering: '-submitted_at',
    pending_review: false,
    needs_document_resubmit: false,
    assigned_to_me: false,
  }
  fetchApplications()
}

async function loadPresets() {
  try {
    presetsLoading.value = true
    const { data } = await api.get('/api/saved-searches/', {
      params: { search_type: REVIEW_QUEUE_SEARCH_TYPE, ordering: 'name', page_size: 100 },
    })
    savedPresets.value = data.results ?? data ?? []
  } catch {
    savedPresets.value = []
  } finally {
    presetsLoading.value = false
  }
}

function applyPreset(p) {
  filters.value = deserializeReviewQueueFilters(p.filters)
  pagination.value.currentPage = 1
  fetchApplications(1)
}

async function savePreset() {
  const name = newPresetName.value.trim()
  if (!name) return
  try {
    presetsLoading.value = true
    await api.post('/api/saved-searches/', {
      name,
      search_type: REVIEW_QUEUE_SEARCH_TYPE,
      filters: serializeReviewQueueFilters(filters.value),
      is_default: saveAsDefault.value,
    })
    newPresetName.value = ''
    saveAsDefault.value = false
    await loadPresets()
    success(t('savedPresets.toastSaved'))
  } catch {
    errorToast(t('savedPresets.toastSaveError'))
  } finally {
    presetsLoading.value = false
  }
}

async function deletePreset(p) {
  const ok = await confirm({
    title: t('savedPresets.removeTitle'),
    message: t('savedPresets.confirmRemove', { name: p.name }),
    confirmText: t('savedPresets.removeConfirm'),
    cancelText: t('settings.cancel'),
    variant: 'danger',
  })
  if (!ok) return
  try {
    presetsLoading.value = true
    await api.delete(`/api/saved-searches/${p.id}/`)
    await loadPresets()
    success(t('savedPresets.toastRemoved'))
  } catch {
    errorToast(t('savedPresets.toastRemoveError'))
  } finally {
    presetsLoading.value = false
  }
}

async function setDefaultPreset(p) {
  try {
    presetsLoading.value = true
    await api.post(`/api/saved-searches/${p.id}/set_default/`)
    await loadPresets()
    success(t('savedPresets.toastDefaultUpdated'))
  } catch {
    errorToast(t('savedPresets.toastDefaultError'))
  } finally {
    presetsLoading.value = false
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
  if (!status) return t('reviewQueuePage.emDash')
  const key = `reviewQueuePage.status.${status}`
  if (te(key)) return t(key)
  return String(status).replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())
}

function formatDate(dateString) {
  if (!dateString) return t('reviewQueuePage.emDash')
  const loc = locale.value === 'es' ? 'es' : 'en-US'
  return new Date(dateString).toLocaleDateString(loc, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

onMounted(async () => {
  await loadPresets()
  const defaultPreset = savedPresets.value.find((p) => p.is_default)
  if (defaultPreset) {
    filters.value = deserializeReviewQueueFilters(defaultPreset.filters)
  }
  await fetchApplications(1)
})
</script>

<style scoped>
.review-queue-page {
  min-height: 100vh;
  background-color: var(--seim-app-bg);
}
</style>
