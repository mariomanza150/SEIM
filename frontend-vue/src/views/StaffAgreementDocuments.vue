<template>
  <div class="staff-agreement-docs-page">
    <nav :aria-label="t('staffAgreementDocumentsPage.breadcrumbAria')">
      <ol class="breadcrumb">
        <li class="breadcrumb-item">
          <router-link :to="{ name: 'Dashboard' }">{{ t('route.names.Dashboard') }}</router-link>
        </li>
        <li class="breadcrumb-item">
          <router-link :to="{ name: 'StaffExchangeAgreements' }">{{
            t('route.names.StaffExchangeAgreements')
          }}</router-link>
        </li>
        <li class="breadcrumb-item active" aria-current="page">
          {{ agreement?.title || t('route.names.StaffAgreementDocuments') }}
        </li>
      </ol>
    </nav>

    <div v-if="routeInvalid" class="alert alert-warning">
      {{ t('staffAgreementDocumentsPage.invalidRoute') }}
      <router-link :to="{ name: 'StaffExchangeAgreements' }">{{ t('route.names.StaffExchangeAgreements') }}</router-link>
    </div>

    <template v-else>
      <div class="row mb-4">
        <div class="col">
          <h2>
            <i class="bi bi-archive me-2"></i>{{ t('route.names.StaffAgreementDocuments') }}
          </h2>
          <p v-if="agreement" class="text-muted mb-0">
            <span class="fw-medium">{{ agreement.title }}</span>
            <span class="mx-1">·</span>
            <span>{{ agreement.partner_institution_name }}</span>
          </p>
          <p v-else-if="!agreementLoading" class="text-muted">{{ t('staffAgreementDocumentsPage.pageSubtitle') }}</p>
        </div>
      </div>

      <div v-if="agreementError" class="alert alert-danger">{{ agreementError }}</div>

      <div class="card mb-4">
        <div class="card-header d-flex justify-content-between align-items-center">
          <span class="fw-medium">{{ t('staffAgreementDocumentsPage.addSectionTitle') }}</span>
        </div>
        <div class="card-body">
          <div class="row g-3">
            <div class="col-md-3">
              <label class="form-label">{{ t('staffAgreementDocumentsPage.categoryLabel') }}</label>
              <select v-model="createForm.category" class="form-select" @change="onCreateCategoryChange">
                <option v-for="c in categoryChoices" :key="c.value" :value="c.value">{{ c.label }}</option>
              </select>
            </div>
            <div class="col-md-4">
              <label class="form-label">{{ t('staffAgreementDocumentsPage.colTitle') }}</label>
              <input v-model="createForm.title" type="text" class="form-control" />
            </div>
            <div class="col-md-5">
              <label class="form-label">{{ t('staffAgreementDocumentsPage.fileLabel') }}</label>
              <input
                ref="createFileInput"
                type="file"
                class="form-control"
                @change="onCreateFile"
              />
            </div>
            <div class="col-12">
              <label class="form-label">{{ t('staffAgreementDocumentsPage.notesLabel') }}</label>
              <textarea v-model="createForm.notes" class="form-control" rows="2"></textarea>
            </div>
            <div v-if="supersedesChoices.length" class="col-md-6">
              <label class="form-label">{{ t('staffAgreementDocumentsPage.supersedesLabel') }}</label>
              <select v-model="createForm.supersedes" class="form-select">
                <option value="">{{ t('staffAgreementDocumentsPage.supersedesNone') }}</option>
                <option v-for="o in supersedesChoices" :key="o.id" :value="o.id">{{ o.label }}</option>
              </select>
            </div>
            <div class="col-12">
              <button
                type="button"
                class="btn btn-primary"
                :disabled="createSubmitting || !createForm.file || agreementLoading"
                @click="submitCreate"
              >
                {{ t('staffAgreementDocumentsPage.addSubmit') }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="card mb-4">
        <div class="card-body">
          <div class="row g-3 align-items-end">
            <div class="col-md-4">
              <label class="form-label">{{ t('exchangeAgreementsPage.searchLabel') }}</label>
              <input
                v-model="filters.search"
                type="text"
                class="form-control"
                :placeholder="t('staffAgreementDocumentsPage.searchPlaceholder')"
                @input="debouncedFetch"
              />
            </div>
            <div class="col-md-2">
              <label class="form-label">{{ t('staffAgreementDocumentsPage.categoryLabel') }}</label>
              <select v-model="filters.category" class="form-select" @change="fetchRows(1)">
                <option value="">{{ t('staffAgreementDocumentsPage.filterOptionAll') }}</option>
                <option v-for="c in categoryChoices" :key="c.value" :value="c.value">{{ c.label }}</option>
              </select>
            </div>
            <div class="col-md-2">
              <div class="form-check mt-4">
                <input
                  id="cur-only"
                  v-model="filters.current_only"
                  class="form-check-input"
                  type="checkbox"
                  @change="fetchRows(1)"
                />
                <label class="form-check-label" for="cur-only">{{ t('staffAgreementDocumentsPage.currentOnly') }}</label>
              </div>
            </div>
            <div class="col-md-3">
              <label class="form-label">{{ t('exchangeAgreementsPage.sortLabel') }}</label>
              <select v-model="filters.ordering" class="form-select" @change="fetchRows(1)">
                <option value="-created_at">{{ t('staffAgreementDocumentsPage.sortNewest') }}</option>
                <option value="created_at">{{ t('staffAgreementDocumentsPage.sortOldest') }}</option>
                <option value="category">{{ t('staffAgreementDocumentsPage.sortCategory') }}</option>
              </select>
            </div>
            <div class="col-md-2">
              <button type="button" class="btn btn-outline-secondary w-100" @click="clearFilters">
                {{ t('staffAgreementDocumentsPage.clearFilters') }}
              </button>
            </div>
            <div class="col-12 border-top pt-3 mt-2">
              <div class="d-flex flex-wrap align-items-end gap-2 mb-2">
                <div class="flex-grow-1" style="min-width: 200px">
                  <label class="form-label small text-muted mb-1">{{ t('staffAgreementDocumentsPage.presetSaveLabel') }}</label>
                  <div class="input-group input-group-sm">
                    <input
                      v-model="newPresetName"
                      type="text"
                      class="form-control"
                      data-testid="agreement-docs-preset-name"
                      :placeholder="t('staffAgreementDocumentsPage.presetNamePlaceholder')"
                    />
                    <button
                      type="button"
                      class="btn btn-outline-primary"
                      :disabled="!newPresetName.trim() || presetsLoading"
                      @click="savePreset(() => serializeAgreementDocumentFilters(filters))"
                    >
                      {{ t('staffAgreementDocumentsPage.presetSave') }}
                    </button>
                  </div>
                </div>
                <div class="form-check mb-1">
                  <input id="adoc-preset-def" v-model="saveAsDefault" class="form-check-input" type="checkbox" />
                  <label class="form-check-label small" for="adoc-preset-def">{{
                    t('staffAgreementDocumentsPage.presetDefaultCheckbox')
                  }}</label>
                </div>
              </div>
              <div v-if="savedPresets.length" class="small">
                <span class="text-muted me-2">{{ t('staffAgreementDocumentsPage.presetSavedPrefix') }}</span>
                <span
                  v-for="p in savedPresets"
                  :key="p.id"
                  class="d-inline-flex align-items-center gap-1 me-3 mb-1"
                >
                  <button type="button" class="btn btn-link btn-sm p-0" @click="applyPreset(p)">{{ p.name }}</button>
                  <i
                    v-if="p.is_default"
                    class="bi bi-star-fill text-warning"
                    :title="t('staffAgreementDocumentsPage.presetDefaultTitle')"
                    :aria-label="t('staffAgreementDocumentsPage.presetDefaultAria')"
                  ></i>
                  <button
                    v-else
                    type="button"
                    class="btn btn-link btn-sm p-0 text-secondary"
                    :title="t('staffAgreementDocumentsPage.presetSetDefaultTitle')"
                    :aria-label="t('staffAgreementDocumentsPage.presetSetDefaultAria')"
                    @click="setDefaultPreset(p)"
                  >
                    <i class="bi bi-star"></i>
                  </button>
                  <button
                    type="button"
                    class="btn btn-link btn-sm p-0 text-danger"
                    :title="t('staffAgreementDocumentsPage.presetRemoveTitle')"
                    :aria-label="t('staffAgreementDocumentsPage.presetRemoveAria')"
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

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">{{ t('staffAgreementDocumentsPage.loadingSpinner') }}</span>
        </div>
      </div>
      <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
      <div v-else-if="rows.length === 0" class="card" data-testid="agreement-docs-empty">
        <div class="card-body text-center text-muted py-5">{{ t('staffAgreementDocumentsPage.emptyFiltered') }}</div>
      </div>
      <div v-else class="table-responsive card">
        <table class="table table-hover mb-0">
          <thead class="table-light">
            <tr>
              <th>{{ t('staffAgreementDocumentsPage.colTitle') }}</th>
              <th>{{ t('staffAgreementDocumentsPage.colCategory') }}</th>
              <th>{{ t('staffAgreementDocumentsPage.colUploaded') }}</th>
              <th class="text-end">{{ t('staffAgreementDocumentsPage.colActions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="d in rows" :key="d.id">
              <td class="fw-medium">{{ d.title || fileLabel(d.file) }}</td>
              <td><span class="badge bg-secondary">{{ formatCategory(d.category) }}</span></td>
              <td class="small text-muted">{{ formatDate(d.created_at) }}</td>
              <td class="text-end text-nowrap">
                <div class="btn-group btn-group-sm" role="group">
                  <button
                    v-if="d.file"
                    type="button"
                    class="btn btn-outline-secondary"
                    :title="t('staffAgreementDocumentsPage.previewTitle')"
                    :aria-label="t('staffAgreementDocumentsPage.previewTitle')"
                    @click="openPreview(d)"
                  >
                    <i class="bi bi-eye"></i>
                  </button>
                  <button
                    type="button"
                    class="btn btn-outline-secondary"
                    :title="t('staffAgreementDocumentsPage.editTitle')"
                    :aria-label="t('staffAgreementDocumentsPage.editTitle')"
                    @click="openEdit(d)"
                  >
                    <i class="bi bi-pencil"></i>
                  </button>
                  <a
                    v-if="d.file"
                    :href="resolveFileUrl(d.file)"
                    class="btn btn-outline-secondary"
                    target="_blank"
                    rel="noopener noreferrer"
                    :aria-label="t('staffAgreementDocumentsPage.downloadTitle')"
                  >
                    <i class="bi bi-download"></i>
                  </a>
                  <button
                    type="button"
                    class="btn btn-outline-danger"
                    :title="t('staffAgreementDocumentsPage.deleteTitle')"
                    :aria-label="t('staffAgreementDocumentsPage.deleteTitle')"
                    @click="onDelete(d)"
                  >
                    <i class="bi bi-trash"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <nav
        v-if="!loading && pagination.count > pagination.pageSize"
        class="mt-3"
        :aria-label="t('staffAgreementDocumentsPage.paginationAria')"
      >
        <ul class="pagination justify-content-center">
          <li class="page-item" :class="{ disabled: !pagination.previous }">
            <button
              type="button"
              class="page-link"
              :disabled="!pagination.previous"
              :aria-label="t('pagination.previous')"
              @click="goToPage(pagination.currentPage - 1)"
            >
              {{ t('pagination.previous') }}
            </button>
          </li>
          <li
            v-for="page in totalPages"
            :key="page"
            class="page-item"
            :class="{ active: page === pagination.currentPage }"
          >
            <button
              type="button"
              class="page-link"
              :aria-label="t('pagination.pageNumberAria', { n: page })"
              :aria-current="page === pagination.currentPage ? 'page' : undefined"
              @click="goToPage(page)"
            >
              {{ page }}
            </button>
          </li>
          <li class="page-item" :class="{ disabled: !pagination.next }">
            <button
              type="button"
              class="page-link"
              :disabled="!pagination.next"
              :aria-label="t('pagination.next')"
              @click="goToPage(pagination.currentPage + 1)"
            >
              {{ t('pagination.next') }}
            </button>
          </li>
        </ul>
      </nav>
    </template>

    <div
      v-if="previewDoc"
      class="modal fade show d-block"
      tabindex="-1"
      style="background: rgba(0, 0, 0, 0.45)"
      role="dialog"
      aria-modal="true"
      @click.self="previewDoc = null"
    >
      <div class="modal-dialog modal-xl modal-dialog-scrollable" @click.stop>
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ previewDoc.title || fileLabel(previewDoc.file) }}</h5>
            <button type="button" class="btn-close" :aria-label="t('settings.cancel')" @click="previewDoc = null"></button>
          </div>
          <div class="modal-body p-0" style="min-height: 60vh">
            <iframe
              v-if="previewKind === 'pdf'"
              class="w-100 border-0"
              style="min-height: 70vh"
              :title="t('staffAgreementDocumentsPage.previewTitle')"
              :src="resolveFileUrl(previewDoc.file)"
            />
            <div v-else-if="previewKind === 'image'" class="p-3 text-center">
              <img
                class="img-fluid"
                :src="resolveFileUrl(previewDoc.file)"
                :alt="previewDoc.title || ''"
              />
            </div>
            <div v-else class="p-4 text-center text-muted">
              <p>{{ t('staffAgreementDocumentsPage.previewUnavailable') }}</p>
              <a
                v-if="previewDoc.file"
                :href="resolveFileUrl(previewDoc.file)"
                class="btn btn-primary"
                target="_blank"
                rel="noopener noreferrer"
              >
                {{ t('staffAgreementDocumentsPage.downloadTitle') }}
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div
      v-if="editDoc"
      class="modal fade show d-block"
      tabindex="-1"
      style="background: rgba(0, 0, 0, 0.45)"
      role="dialog"
      aria-modal="true"
      @click.self="editDoc = null"
    >
      <div class="modal-dialog" @click.stop>
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ t('staffAgreementDocumentsPage.editTitle') }}</h5>
            <button type="button" class="btn-close" :aria-label="t('settings.cancel')" @click="editDoc = null"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">{{ t('staffAgreementDocumentsPage.colTitle') }}</label>
              <input v-model="editForm.title" type="text" class="form-control" />
            </div>
            <div class="mb-3">
              <label class="form-label">{{ t('staffAgreementDocumentsPage.categoryLabel') }}</label>
              <select v-model="editForm.category" class="form-select">
                <option v-for="c in categoryChoices" :key="c.value" :value="c.value">{{ c.label }}</option>
              </select>
            </div>
            <div class="mb-3">
              <label class="form-label">{{ t('staffAgreementDocumentsPage.notesLabel') }}</label>
              <textarea v-model="editForm.notes" class="form-control" rows="3"></textarea>
            </div>
            <div class="mb-3">
              <label class="form-label">{{ t('staffAgreementDocumentsPage.replaceFileLabel') }}</label>
              <input type="file" class="form-control" @change="onEditFile" />
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="editDoc = null">{{ t('settings.cancel') }}</button>
            <button type="button" class="btn btn-primary" :disabled="editSubmitting" @click="submitEdit">
              {{ t('staffAgreementDocumentsPage.saveEdit') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useToast } from '@/composables/useToast'
import { useStaffSavedPresets } from '@/composables/useStaffSavedPresets'
import { useConfirm } from '@/composables/useConfirm'
import api from '@/services/api'
import { resolveFileUrl } from '@/utils/apiUrl'
import {
  STAFF_SAVED_SEARCH_TYPE,
  deserializeAgreementDocumentFilters,
  serializeAgreementDocumentFilters,
} from '@/utils/staffListSearchPresets'

const route = useRoute()
const { t, te, locale } = useI18n()
const { error: errorToast, success: successToast } = useToast()
const { confirm } = useConfirm()

const {
  savedPresets,
  newPresetName,
  saveAsDefault,
  presetsLoading,
  loadPresets,
  savePreset,
  deletePreset,
  setDefaultPreset,
} = useStaffSavedPresets(STAFF_SAVED_SEARCH_TYPE.AGREEMENT_REPOSITORY_DOC)

const CATEGORY_VALUES = ['signed_copy', 'amendment', 'mou', 'annex', 'correspondence', 'other']

const categoryChoices = computed(() =>
  CATEGORY_VALUES.map((value) => ({
    value,
    label: t(`staffAgreementDocumentsPage.category.${value}`),
  })),
)

const agreementId = computed(() => {
  const raw = route.params.agreementId
  return raw != null && String(raw).trim() !== '' ? String(raw) : ''
})

const routeInvalid = computed(() => !agreementId.value)

const agreement = ref(null)
const agreementLoading = ref(false)
const agreementError = ref(null)

const rows = ref([])
const loading = ref(true)
const error = ref(null)

const createFileInput = ref(null)
const createForm = ref({
  category: 'other',
  title: '',
  notes: '',
  file: null,
  supersedes: '',
})
const supersedesChoices = ref([])
const createSubmitting = ref(false)

const previewDoc = ref(null)
const editDoc = ref(null)
const editForm = ref({ title: '', notes: '', category: 'other' })
const editFile = ref(null)
const editSubmitting = ref(false)

const previewKind = computed(() => {
  const f = previewDoc.value?.file
  if (!f) return 'other'
  const s = String(f).toLowerCase()
  if (s.includes('.pdf') || s.endsWith('pdf')) return 'pdf'
  if (/\.(png|jpe?g|gif|webp|svg)(\?|$)/i.test(s)) return 'image'
  return 'other'
})

const filters = ref({
  search: '',
  agreement: '',
  category: '',
  current_only: false,
  ordering: '-created_at',
})

const pagination = ref({
  count: 0,
  next: null,
  previous: null,
  currentPage: 1,
  pageSize: 20,
})

const totalPages = computed(() => Math.ceil(pagination.value.count / pagination.value.pageSize) || 1)

let debounceTimer = null
function debouncedFetch() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => fetchRows(1), 400)
}

function syncAgreementFilter() {
  if (agreementId.value) {
    filters.value.agreement = agreementId.value
  }
}

async function loadAgreement() {
  if (!agreementId.value) {
    agreement.value = null
    return
  }
  agreementLoading.value = true
  agreementError.value = null
  try {
    const { data } = await api.get(`/api/exchange-agreements/${agreementId.value}/`)
    agreement.value = data
  } catch {
    agreement.value = null
    agreementError.value = t('staffAgreementDocumentsPage.agreementLoadError')
    errorToast(agreementError.value)
  } finally {
    agreementLoading.value = false
  }
}

async function loadSupersedesOptions() {
  if (!agreementId.value || !createForm.value.category) {
    supersedesChoices.value = []
    return
  }
  try {
    const { data } = await api.get('/api/agreement-documents/', {
      params: {
        agreement: agreementId.value,
        category: createForm.value.category,
        current_only: 'true',
        page_size: 200,
      },
    })
    const list = data.results ?? data ?? []
    supersedesChoices.value = list.map((row) => ({
      id: row.id,
      label: row.title?.trim() ? row.title : fileLabel(row.file),
    }))
  } catch {
    supersedesChoices.value = []
  }
}

function onCreateCategoryChange() {
  createForm.value.supersedes = ''
  loadSupersedesOptions()
}

function onCreateFile(e) {
  const f = e.target.files?.[0]
  createForm.value.file = f || null
}

function onEditFile(e) {
  editFile.value = e.target.files?.[0] || null
}

async function submitCreate() {
  if (!agreementId.value || !createForm.value.file) return
  createSubmitting.value = true
  try {
    const fd = new FormData()
    fd.append('agreement', agreementId.value)
    fd.append('category', createForm.value.category)
    if (createForm.value.title?.trim()) fd.append('title', createForm.value.title.trim())
    fd.append('file', createForm.value.file)
    if (createForm.value.notes?.trim()) fd.append('notes', createForm.value.notes.trim())
    if (createForm.value.supersedes) fd.append('supersedes', createForm.value.supersedes)

    await api.post('/api/agreement-documents/', fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    successToast(t('staffAgreementDocumentsPage.createSuccess'))
    createForm.value = {
      category: createForm.value.category,
      title: '',
      notes: '',
      file: null,
      supersedes: '',
    }
    if (createFileInput.value) createFileInput.value.value = ''
    await loadSupersedesOptions()
    await fetchRows(1)
  } catch (e) {
    const msg =
      e.response?.data?.file?.[0] ||
      e.response?.data?.detail ||
      e.response?.data?.non_field_errors?.[0] ||
      t('staffAgreementDocumentsPage.createError')
    errorToast(msg)
  } finally {
    createSubmitting.value = false
  }
}

function openPreview(d) {
  previewDoc.value = d
}

function openEdit(d) {
  editDoc.value = d
  editForm.value = {
    title: d.title || '',
    notes: d.notes || '',
    category: d.category || 'other',
  }
  editFile.value = null
}

async function submitEdit() {
  if (!editDoc.value) return
  editSubmitting.value = true
  const id = editDoc.value.id
  try {
    if (editFile.value) {
      const fd = new FormData()
      fd.append('title', editForm.value.title || '')
      fd.append('notes', editForm.value.notes || '')
      fd.append('category', editForm.value.category)
      fd.append('file', editFile.value)
      await api.patch(`/api/agreement-documents/${id}/`, fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
    } else {
      await api.patch(`/api/agreement-documents/${id}/`, {
        title: editForm.value.title || '',
        notes: editForm.value.notes || '',
        category: editForm.value.category,
      })
    }
    successToast(t('staffAgreementDocumentsPage.editSuccess'))
    editDoc.value = null
    await loadSupersedesOptions()
    await fetchRows(pagination.value.currentPage)
  } catch (e) {
    const msg = e.response?.data?.detail || e.response?.data?.file?.[0] || t('staffAgreementDocumentsPage.editError')
    errorToast(msg)
  } finally {
    editSubmitting.value = false
  }
}

async function onDelete(d) {
  const ok = await confirm({
    title: t('staffAgreementDocumentsPage.deleteTitle'),
    message: t('staffAgreementDocumentsPage.deleteConfirm'),
    confirmText: t('staffAgreementDocumentsPage.deleteTitle'),
    cancelText: t('settings.cancel'),
    variant: 'danger',
  })
  if (!ok) return
  try {
    await api.delete(`/api/agreement-documents/${d.id}/`)
    successToast(t('staffAgreementDocumentsPage.deleteSuccess'))
    await loadSupersedesOptions()
    await fetchRows(pagination.value.currentPage)
  } catch {
    errorToast(t('staffAgreementDocumentsPage.deleteError'))
  }
}

async function fetchRows(page = 1) {
  if (!agreementId.value) {
    loading.value = false
    rows.value = []
    return
  }
  try {
    loading.value = true
    error.value = null
    syncAgreementFilter()
    const params = { page, ordering: filters.value.ordering, agreement: filters.value.agreement }
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.category) params.category = filters.value.category
    if (filters.value.current_only) params.current_only = 'true'

    const { data } = await api.get('/api/agreement-documents/', { params })
    rows.value = data.results ?? data ?? []
    if (data.count !== undefined) {
      pagination.value = {
        count: data.count,
        next: data.next,
        previous: data.previous,
        currentPage: page,
        pageSize: pagination.value.pageSize,
      }
    }
  } catch {
    error.value = t('staffAgreementDocumentsPage.loadError')
    errorToast(error.value)
  } finally {
    loading.value = false
  }
}

function goToPage(page) {
  if (page >= 1 && page <= totalPages.value) {
    fetchRows(page)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

function clearFilters() {
  filters.value = {
    search: '',
    agreement: agreementId.value || '',
    category: '',
    current_only: false,
    ordering: '-created_at',
  }
  fetchRows(1)
}

function applyPreset(p) {
  filters.value = deserializeAgreementDocumentFilters(p.filters)
  syncAgreementFilter()
  pagination.value.currentPage = 1
  fetchRows(1)
}

function fileLabel(url) {
  if (!url) return t('staffAgreementDocumentsPage.emDash')
  const parts = String(url).split('/')
  return decodeURIComponent(parts[parts.length - 1] || 'file')
}

function formatCategory(s) {
  if (!s) return t('staffAgreementDocumentsPage.emDash')
  const key = `staffAgreementDocumentsPage.category.${s}`
  if (te(key)) return t(key)
  return s.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

function formatDate(dateString) {
  if (!dateString) return t('staffAgreementDocumentsPage.emDash')
  const date = new Date(dateString)
  const localeTag = locale.value === 'es' ? 'es' : 'en-US'
  return date.toLocaleDateString(localeTag, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

watch(agreementId, async () => {
  syncAgreementFilter()
  if (!agreementId.value) {
    loading.value = false
    rows.value = []
    agreement.value = null
    agreementError.value = null
    return
  }
  await loadAgreement()
  await loadSupersedesOptions()
  await fetchRows(1)
})

onMounted(async () => {
  syncAgreementFilter()
  if (!agreementId.value) {
    loading.value = false
    return
  }
  await loadAgreement()
  await loadPresets()
  const def = savedPresets.value.find((p) => p.is_default)
  if (def) {
    filters.value = deserializeAgreementDocumentFilters(def.filters)
    syncAgreementFilter()
  }
  await loadSupersedesOptions()
  await fetchRows(1)
})
</script>

<style scoped>
.staff-agreement-docs-page {
  min-height: 100vh;
  background-color: var(--seim-app-bg);
}
</style>
