<template>
  <div class="review-queue-page">
    <PageHeader
      :title="t('reviewQueuePage.pageHeading')"
      :subtitle="t('reviewQueuePage.pageSubtitle')"
      icon-class="bi bi-clipboard-check"
      test-id="review-queue-heading"
    >
      <template #breadcrumb>
        <PageBreadcrumb
          :aria-label="t('reviewQueuePage.breadcrumbAria')"
          :items="[
            { to: { name: 'Dashboard' }, label: t('route.names.Dashboard') },
            { label: t('route.names.CoordinatorReviewQueue') },
          ]"
        />
      </template>
      <template #actions>
        <router-link :to="{ name: 'Applications' }" class="btn btn-outline-secondary">
          <i class="bi bi-person-lines-fill me-1" aria-hidden="true"></i>{{ t('reviewQueuePage.myApplications') }}
        </router-link>
      </template>
    </PageHeader>

      <CompactFilterBar
        test-id="review-queue-filters"
        :clear-label="t('reviewQueuePage.clearFilters')"
        :toggle-label="t('reviewQueuePage.advancedFiltersToggle')"
        @clear="clearFilters"
      >
        <template #primary>
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
            <div class="col-md-4">
              <label class="form-label d-block">{{ t('reviewQueuePage.quickFilters') }}</label>
              <div class="d-flex flex-wrap gap-2">
                <div class="form-check form-check-inline">
                  <input
                    id="fq-pending"
                    v-model="filters.pending_review"
                    class="form-check-input"
                    type="checkbox"
                    @change="() => fetchApplications(1)"
                  />
                  <label class="form-check-label" for="fq-pending">{{ t('reviewQueuePage.filterPendingReview') }}</label>
                </div>
                <div class="form-check form-check-inline">
                  <input
                    id="fq-resubmit"
                    v-model="filters.needs_document_resubmit"
                    class="form-check-input"
                    type="checkbox"
                    @change="() => fetchApplications(1)"
                  />
                  <label class="form-check-label" for="fq-resubmit">{{ t('reviewQueuePage.filterDocumentResubmit') }}</label>
                </div>
                <div class="form-check form-check-inline">
                  <input
                    id="fq-assigned"
                    v-model="filters.assigned_to_me"
                    class="form-check-input"
                    type="checkbox"
                    @change="() => fetchApplications(1)"
                  />
                  <label class="form-check-label" for="fq-assigned">{{ t('reviewQueuePage.filterAssignedToMe') }}</label>
                </div>
              </div>
            </div>
            <div class="col-md-3">
              <label class="form-label">{{ t('reviewQueuePage.statusLabel') }}</label>
              <select
                v-model="filters.status"
                class="form-select"
                data-testid="review-queue-filter-status"
                @change="() => fetchApplications(1)"
              >
                <option value="">{{ t('reviewQueuePage.statusAll') }}</option>
                <option value="draft">{{ t('reviewQueuePage.status.draft') }}</option>
                <option value="submitted">{{ t('reviewQueuePage.status.submitted') }}</option>
                <option value="under_review">{{ t('reviewQueuePage.status.under_review') }}</option>
                <option value="nominated">{{ t('reviewQueuePage.status.nominated') }}</option>
                <option value="waitlist">{{ t('reviewQueuePage.status.waitlist') }}</option>
                <option value="approved">{{ t('reviewQueuePage.status.approved') }}</option>
                <option value="rejected">{{ t('reviewQueuePage.status.rejected') }}</option>
                <option value="completed">{{ t('reviewQueuePage.status.completed') }}</option>
                <option value="cancelled">{{ t('reviewQueuePage.status.cancelled') }}</option>
                <option value="withdrawn">{{ t('reviewQueuePage.status.withdrawn') }}</option>
              </select>
            </div>
        </template>
        <template #advanced>
            <div class="row g-2">
            <div class="col-md-3">
              <label class="form-label">{{ t('reviewQueuePage.sortLabel') }}</label>
              <select v-model="filters.ordering" class="form-select" @change="() => fetchApplications(1)">
                <option value="-submitted_at">{{ t('reviewQueuePage.sortRecentlySubmitted') }}</option>
                <option value="-created_at">{{ t('reviewQueuePage.sortNewest') }}</option>
                <option value="created_at">{{ t('reviewQueuePage.sortOldest') }}</option>
              </select>
            </div>
            </div>
        </template>
        <template #presets>
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
        </template>
      </CompactFilterBar>

      <LoadingState v-if="loading" :spinner-label="t('reviewQueuePage.loading')" />
      <ErrorAlert v-else-if="error" :message="error" />
      <EmptyState
        v-else-if="applications.length === 0"
        test-id="review-queue-empty"
        :body="t('reviewQueuePage.empty')"
      />
      <div v-else class="table-responsive card" data-testid="review-queue-table">
        <table class="table table-hover mb-0" role="grid" :aria-label="t('reviewQueuePage.tableAria')">
          <thead class="table-light">
            <tr>
              <th scope="col" class="review-queue-select-col">
                <input
                  type="checkbox"
                  class="form-check-input"
                  :checked="allPageSelected"
                  :indeterminate.prop="somePageSelected && !allPageSelected"
                  :aria-label="t('reviewQueuePage.selectAllAria')"
                  data-testid="review-queue-select-all"
                  @change="toggleSelectAllPage"
                />
              </th>
              <th scope="col">{{ t('reviewQueuePage.colStudent') }}</th>
              <th scope="col">{{ t('reviewQueuePage.colProgram') }}</th>
              <th scope="col">{{ t('reviewQueuePage.colStatus') }}</th>
              <th scope="col">{{ t('reviewQueuePage.colCoordinator') }}</th>
              <th scope="col">{{ t('reviewQueuePage.colSubmitted') }}</th>
              <th scope="col"></th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(app, index) in applications"
              :key="app.id"
              :class="{ 'table-active': focusedIndex === index, 'review-queue-row--selected': isSelected(app.id) }"
              :aria-selected="focusedIndex === index ? 'true' : 'false'"
              data-testid="review-queue-row"
              @click="focusRow(index)"
            >
              <td class="review-queue-select-col" @click.stop>
                <input
                  type="checkbox"
                  class="form-check-input"
                  :checked="isSelected(app.id)"
                  :aria-label="t('reviewQueuePage.selectRowAria', { name: app.student_display_name || app.id })"
                  data-testid="review-queue-row-select"
                  @change="toggleSelect(app.id)"
                />
              </td>
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
                  @click.stop
                >
                  {{ t('reviewQueuePage.openDetail') }}
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
        <p class="small text-muted mb-0 px-3 py-2 border-top" data-testid="review-queue-keyboard-hint">
          {{ t('reviewQueuePage.keyboardHint') }}
        </p>
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

      <div
        v-if="selectedCount > 0"
        class="review-queue-selection-bar"
        role="region"
        :aria-label="t('reviewQueuePage.selectionBarAria')"
        data-testid="review-queue-selection-bar"
      >
        <span class="fw-medium" data-testid="review-queue-selection-count">
          {{ t('reviewQueuePage.selectedCount', { count: selectedCount }) }}
        </span>
        <div class="d-flex flex-wrap gap-2">
          <button
            type="button"
            class="btn btn-sm btn-primary"
            data-testid="review-queue-open-selected"
            @click="openSelected"
          >
            {{ t('reviewQueuePage.openSelected') }}
          </button>
          <button
            type="button"
            class="btn btn-sm btn-outline-secondary"
            data-testid="review-queue-clear-selection"
            @click="clearSelection"
          >
            {{ t('reviewQueuePage.clearSelection') }}
          </button>
        </div>
      </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useToast } from '@/composables/useToast'
import { useConfirm } from '@/composables/useConfirm'
import api from '@/services/api'
import PageHeader from '@/components/PageHeader.vue'
import PageBreadcrumb from '@/components/PageBreadcrumb.vue'
import CompactFilterBar from '@/components/CompactFilterBar.vue'
import Pagination from '@/components/Pagination.vue'
import LoadingState from '@/components/State/LoadingState.vue'
import ErrorAlert from '@/components/State/ErrorAlert.vue'
import EmptyState from '@/components/State/EmptyState.vue'
import {
  REVIEW_QUEUE_SEARCH_TYPE,
  deserializeReviewQueueFilters,
  serializeReviewQueueFilters,
} from '@/utils/reviewQueuePresets'
import { resolveListPage } from '@/utils/listPage'
import { applicationStatusBadgeClass, applicationStatusFromRouteQuery } from '@/utils/formatters'

const route = useRoute()
const router = useRouter()

const { t, te, locale } = useI18n()
const { success, error: errorToast } = useToast()
const { confirm } = useConfirm()

const applications = ref([])
const loading = ref(true)
const error = ref(null)
const savedPresets = ref([])
const presetsLoading = ref(false)
const newPresetName = ref('')
const saveAsDefault = ref(false)
const selectedIds = ref([])
const focusedIndex = ref(-1)

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

const selectedCount = computed(() => selectedIds.value.length)
const pageIds = computed(() => applications.value.map((app) => app.id))
const allPageSelected = computed(
  () => pageIds.value.length > 0 && pageIds.value.every((id) => selectedIds.value.includes(id)),
)
const somePageSelected = computed(() => pageIds.value.some((id) => selectedIds.value.includes(id)))

let searchTimeout = null
function debouncedSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => fetchApplications(), 400)
}

function isSelected(id) {
  return selectedIds.value.includes(id)
}

function toggleSelect(id) {
  if (selectedIds.value.includes(id)) {
    selectedIds.value = selectedIds.value.filter((x) => x !== id)
  } else {
    selectedIds.value = [...selectedIds.value, id]
  }
}

function toggleSelectAllPage() {
  if (allPageSelected.value) {
    const pageSet = new Set(pageIds.value)
    selectedIds.value = selectedIds.value.filter((id) => !pageSet.has(id))
  } else {
    const merged = new Set([...selectedIds.value, ...pageIds.value])
    selectedIds.value = [...merged]
  }
}

function clearSelection() {
  selectedIds.value = []
}

function focusRow(index) {
  if (index < 0 || index >= applications.value.length) return
  focusedIndex.value = index
}

function moveFocus(delta) {
  if (!applications.value.length) return
  const next =
    focusedIndex.value < 0
      ? delta > 0
        ? 0
        : applications.value.length - 1
      : Math.min(applications.value.length - 1, Math.max(0, focusedIndex.value + delta))
  focusedIndex.value = next
}

function openApplication(id) {
  if (id == null) return
  router.push({ name: 'ApplicationDetail', params: { id } })
}

function openFocused() {
  const app = applications.value[focusedIndex.value]
  if (app) openApplication(app.id)
}

function openSelected() {
  const ordered = applications.value.filter((app) => selectedIds.value.includes(app.id))
  const first = ordered[0] || applications.value.find((app) => selectedIds.value.includes(app.id))
  if (first) openApplication(first.id)
}

function toggleFocusedSelect() {
  const app = applications.value[focusedIndex.value]
  if (app) toggleSelect(app.id)
}

function isTypingTarget(el) {
  if (!el || typeof el.closest !== 'function') return false
  const tag = el.tagName
  if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || tag === 'BUTTON' || tag === 'A') {
    return true
  }
  if (el.isContentEditable) return true
  return Boolean(el.closest('input, textarea, select, button, a, [contenteditable="true"]'))
}

function onQueueKeydown(event) {
  if (loading.value || !applications.value.length) return
  if (isTypingTarget(event.target)) return
  const key = event.key
  if (key === 'ArrowDown' || key === 'j' || key === 'J') {
    event.preventDefault()
    moveFocus(1)
    return
  }
  if (key === 'ArrowUp' || key === 'k' || key === 'K') {
    event.preventDefault()
    moveFocus(-1)
    return
  }
  if (key === 'Enter' || key === 'o' || key === 'O') {
    if (focusedIndex.value < 0) return
    event.preventDefault()
    openFocused()
    return
  }
  if (key === 'x' || key === 'X') {
    if (focusedIndex.value < 0) return
    event.preventDefault()
    toggleFocusedSelect()
  }
}

async function fetchApplications(page = 1) {
  const pageNumber = resolveListPage(page)
  try {
    loading.value = true
    error.value = null
    const params = {
      page: pageNumber,
      ordering: filters.value.ordering,
    }
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.status) params.status = filters.value.status
    if (filters.value.pending_review) params.pending_review = 'true'
    if (filters.value.needs_document_resubmit) params.needs_document_resubmit = 'true'
    if (filters.value.assigned_to_me) params.assigned_to_me = 'true'

    const response = await api.get('/api/applications/', { params })
    applications.value = response.data.results || response.data
    selectedIds.value = []
    focusedIndex.value = applications.value.length ? 0 : -1
    if (response.data.count !== undefined) {
      pagination.value = {
        count: response.data.count,
        next: response.data.next,
        previous: response.data.previous,
        currentPage: pageNumber,
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
  return applicationStatusBadgeClass(status)
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
  window.addEventListener('keydown', onQueueKeydown)
  await loadPresets()
  const defaultPreset = savedPresets.value.find((p) => p.is_default)
  if (defaultPreset) {
    filters.value = deserializeReviewQueueFilters(defaultPreset.filters)
  }
  const statusFromQuery = applicationStatusFromRouteQuery(route.query)
  if (statusFromQuery) {
    filters.value.status = statusFromQuery
  }
  await fetchApplications(1)
})

onUnmounted(() => {
  window.removeEventListener('keydown', onQueueKeydown)
})
</script>

<style scoped>
.review-queue-page {
  min-height: 100vh;
  background-color: var(--seim-app-bg);
  padding-bottom: 4.5rem;
}

.review-queue-select-col {
  width: 2.5rem;
  vertical-align: middle;
}

.review-queue-row--selected {
  background-color: color-mix(in srgb, var(--bs-primary, #0d6efd) 8%, transparent);
}

.review-queue-selection-bar {
  position: sticky;
  bottom: 0.75rem;
  z-index: 20;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  border: 1px solid var(--seim-border, #dee2e6);
  border-radius: 0.5rem;
  background: var(--seim-surface, #fff);
  box-shadow: 0 0.25rem 1rem rgba(0, 0, 0, 0.08);
}
</style>
