<template>
  <div class="staff-agreement-docs-page">
    <div class="container-fluid mt-4">
      <nav aria-label="breadcrumb">
        <ol class="breadcrumb">
          <li class="breadcrumb-item">
            <router-link :to="{ name: 'Dashboard' }">Dashboard</router-link>
          </li>
          <li class="breadcrumb-item active">Agreement documents</li>
        </ol>
      </nav>

      <div class="row mb-4">
        <div class="col">
          <h2><i class="bi bi-archive me-2"></i>Agreement document repository</h2>
          <p class="text-muted">Files linked to exchange agreements (staff)</p>
        </div>
      </div>

      <div class="card mb-4">
        <div class="card-body">
          <div class="row g-3 align-items-end">
            <div class="col-md-4">
              <label class="form-label">Search</label>
              <input
                v-model="filters.search"
                type="text"
                class="form-control"
                placeholder="Title, notes, agreement…"
                @input="debouncedFetch"
              />
            </div>
            <div class="col-md-4">
              <label class="form-label">Agreement</label>
              <select v-model="filters.agreement" class="form-select" @change="fetchRows(1)">
                <option value="">Any</option>
                <option v-for="a in agreements" :key="a.id" :value="a.id">{{ a.title }} — {{ a.partner_institution_name }}</option>
              </select>
            </div>
            <div class="col-md-2">
              <label class="form-label">Category</label>
              <select v-model="filters.category" class="form-select" @change="fetchRows(1)">
                <option value="">All</option>
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
                <label class="form-check-label" for="cur-only">Current only</label>
              </div>
            </div>
            <div class="col-md-3">
              <label class="form-label">Sort</label>
              <select v-model="filters.ordering" class="form-select" @change="fetchRows(1)">
                <option value="-created_at">Newest</option>
                <option value="created_at">Oldest</option>
                <option value="category">Category</option>
              </select>
            </div>
            <div class="col-md-2">
              <button type="button" class="btn btn-outline-secondary w-100" @click="clearFilters">Clear</button>
            </div>
            <div class="col-12 border-top pt-3 mt-2">
              <div class="d-flex flex-wrap align-items-end gap-2 mb-2">
                <div class="flex-grow-1" style="min-width: 200px">
                  <label class="form-label small text-muted mb-1">Save filters as preset</label>
                  <div class="input-group input-group-sm">
                    <input v-model="newPresetName" type="text" class="form-control" placeholder="Preset name" />
                    <button
                      type="button"
                      class="btn btn-outline-primary"
                      :disabled="!newPresetName.trim() || presetsLoading"
                      @click="savePreset(() => serializeAgreementDocumentFilters(filters))"
                    >
                      Save
                    </button>
                  </div>
                </div>
                <div class="form-check mb-1">
                  <input id="adoc-preset-def" v-model="saveAsDefault" class="form-check-input" type="checkbox" />
                  <label class="form-check-label small" for="adoc-preset-def">Default when opening this page</label>
                </div>
              </div>
              <div v-if="savedPresets.length" class="small">
                <span class="text-muted me-2">Saved:</span>
                <span
                  v-for="p in savedPresets"
                  :key="p.id"
                  class="d-inline-flex align-items-center gap-1 me-3 mb-1"
                >
                  <button type="button" class="btn btn-link btn-sm p-0" @click="applyPreset(p)">{{ p.name }}</button>
                  <i
                    v-if="p.is_default"
                    class="bi bi-star-fill text-warning"
                    title="Default preset"
                    aria-label="Default preset"
                  ></i>
                  <button
                    v-else
                    type="button"
                    class="btn btn-link btn-sm p-0 text-secondary"
                    title="Set as default"
                    aria-label="Set as default"
                    @click="setDefaultPreset(p)"
                  >
                    <i class="bi bi-star"></i>
                  </button>
                  <button
                    type="button"
                    class="btn btn-link btn-sm p-0 text-danger"
                    title="Remove preset"
                    aria-label="Remove preset"
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
          <span class="visually-hidden">Loading…</span>
        </div>
      </div>
      <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
      <div v-else-if="rows.length === 0" class="card">
        <div class="card-body text-center text-muted py-5">No repository documents match these filters.</div>
      </div>
      <div v-else class="table-responsive card">
        <table class="table table-hover mb-0">
          <thead class="table-light">
            <tr>
              <th>Title</th>
              <th>Category</th>
              <th>Agreement</th>
              <th>Uploaded</th>
              <th class="text-end">File</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="d in rows" :key="d.id">
              <td class="fw-medium">{{ d.title || fileLabel(d.file) }}</td>
              <td><span class="badge bg-secondary">{{ formatEnum(d.category) }}</span></td>
              <td class="small text-muted">{{ agreementLabel(d.agreement) }}</td>
              <td class="small text-muted">{{ formatDate(d.created_at) }}</td>
              <td class="text-end">
                <a
                  v-if="d.file"
                  :href="resolveFileUrl(d.file)"
                  class="btn btn-sm btn-outline-secondary"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <i class="bi bi-download"></i>
                </a>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <nav v-if="!loading && pagination.count > pagination.pageSize" class="mt-3" aria-label="Pagination">
        <ul class="pagination justify-content-center">
          <li class="page-item" :class="{ disabled: !pagination.previous }">
            <button type="button" class="page-link" @click="goToPage(pagination.currentPage - 1)">Previous</button>
          </li>
          <li
            v-for="page in totalPages"
            :key="page"
            class="page-item"
            :class="{ active: page === pagination.currentPage }"
          >
            <button type="button" class="page-link" @click="goToPage(page)">{{ page }}</button>
          </li>
          <li class="page-item" :class="{ disabled: !pagination.next }">
            <button type="button" class="page-link" @click="goToPage(pagination.currentPage + 1)">Next</button>
          </li>
        </ul>
      </nav>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import { useStaffSavedPresets } from '@/composables/useStaffSavedPresets'
import api from '@/services/api'
import { resolveFileUrl } from '@/utils/apiUrl'
import {
  STAFF_SAVED_SEARCH_TYPE,
  deserializeAgreementDocumentFilters,
  serializeAgreementDocumentFilters,
} from '@/utils/staffListSearchPresets'

const { error: errorToast } = useToast()

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

const categoryChoices = [
  { value: 'signed_copy', label: 'Signed copy' },
  { value: 'amendment', label: 'Amendment / addendum' },
  { value: 'mou', label: 'Memorandum of understanding' },
  { value: 'annex', label: 'Annex / schedule' },
  { value: 'correspondence', label: 'Correspondence' },
  { value: 'other', label: 'Other' },
]

const agreements = ref([])
const agreementMap = ref({})
const rows = ref([])
const loading = ref(true)
const error = ref(null)

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

async function loadAgreements() {
  try {
    const { data } = await api.get('/api/exchange-agreements/', { params: { page_size: 200, ordering: 'title' } })
    const list = data.results ?? data ?? []
    agreements.value = list
    const m = {}
    for (const a of list) {
      m[a.id] = a
    }
    agreementMap.value = m
  } catch {
    agreements.value = []
    agreementMap.value = {}
  }
}

function agreementLabel(id) {
  const a = agreementMap.value[id]
  if (a) return `${a.title} — ${a.partner_institution_name}`
  return id || '—'
}

async function fetchRows(page = 1) {
  try {
    loading.value = true
    error.value = null
    const params = { page, ordering: filters.value.ordering }
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.agreement) params.agreement = filters.value.agreement
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
    error.value = 'Failed to load agreement documents.'
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
    agreement: '',
    category: '',
    current_only: false,
    ordering: '-created_at',
  }
  fetchRows(1)
}

function applyPreset(p) {
  filters.value = deserializeAgreementDocumentFilters(p.filters)
  pagination.value.currentPage = 1
  fetchRows(1)
}

function fileLabel(url) {
  if (!url) return '—'
  const parts = String(url).split('/')
  return decodeURIComponent(parts[parts.length - 1] || 'file')
}

function formatEnum(s) {
  if (!s) return '—'
  return s.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

function formatDate(dateString) {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

onMounted(async () => {
  await loadAgreements()
  await loadPresets()
  const def = savedPresets.value.find((p) => p.is_default)
  if (def) {
    filters.value = deserializeAgreementDocumentFilters(def.filters)
  }
  await fetchRows(1)
})
</script>

<style scoped>
.staff-agreement-docs-page {
  min-height: 100vh;
  background-color: #f8f9fa;
}
</style>
