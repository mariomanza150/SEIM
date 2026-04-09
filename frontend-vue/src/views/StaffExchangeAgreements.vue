<template>
  <div class="staff-agreements-page">
    <div class="container-fluid mt-4">
      <nav aria-label="breadcrumb">
        <ol class="breadcrumb">
          <li class="breadcrumb-item">
            <router-link :to="{ name: 'Dashboard' }">Dashboard</router-link>
          </li>
          <li class="breadcrumb-item active">Exchange agreements</li>
        </ol>
      </nav>

      <div class="row mb-4">
        <div class="col">
          <h2><i class="bi bi-file-earmark-richtext me-2"></i>Exchange agreements</h2>
          <p class="text-muted">Operational agreement registry (staff)</p>
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
                placeholder="Title, partner, reference…"
                @input="debouncedFetch"
              />
            </div>
            <div class="col-md-2">
              <label class="form-label">Status</label>
              <select v-model="filters.status" class="form-select" @change="fetchAgreements(1)">
                <option value="">All</option>
                <option v-for="s in statusChoices" :key="s.value" :value="s.value">{{ s.label }}</option>
              </select>
            </div>
            <div class="col-md-2">
              <label class="form-label">Type</label>
              <select v-model="filters.agreement_type" class="form-select" @change="fetchAgreements(1)">
                <option value="">All</option>
                <option v-for="t in typeChoices" :key="t.value" :value="t.value">{{ t.label }}</option>
              </select>
            </div>
            <div class="col-md-4">
              <label class="form-label">Linked program</label>
              <select v-model="filters.program" class="form-select" @change="fetchAgreements(1)">
                <option value="">Any</option>
                <option v-for="p in programs" :key="p.id" :value="p.id">{{ p.name }}</option>
              </select>
            </div>
            <div class="col-md-3">
              <label class="form-label">Partner contains</label>
              <input
                v-model="filters.partner"
                type="text"
                class="form-control"
                @change="fetchAgreements(1)"
              />
            </div>
            <div class="col-md-2">
              <label class="form-label">End after</label>
              <input v-model="filters.end_date_after" type="date" class="form-control" @change="fetchAgreements(1)" />
            </div>
            <div class="col-md-2">
              <label class="form-label">End before</label>
              <input v-model="filters.end_date_before" type="date" class="form-control" @change="fetchAgreements(1)" />
            </div>
            <div class="col-md-2">
              <label class="form-label">Expiring (days)</label>
              <input
                v-model.number="filters.expiring_within_days"
                type="number"
                min="0"
                class="form-control"
                placeholder="—"
                @change="fetchAgreements(1)"
              />
            </div>
            <div class="col-md-3">
              <label class="form-label">Sort</label>
              <select v-model="filters.ordering" class="form-select" @change="fetchAgreements(1)">
                <option value="-end_date">End date (soonest first)</option>
                <option value="end_date">End date (latest first)</option>
                <option value="-created_at">Newest</option>
                <option value="partner_institution_name">Partner A–Z</option>
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
                      @click="savePreset(() => serializeExchangeAgreementFilters(filters))"
                    >
                      Save
                    </button>
                  </div>
                </div>
                <div class="form-check mb-1">
                  <input id="ag-preset-def" v-model="saveAsDefault" class="form-check-input" type="checkbox" />
                  <label class="form-check-label small" for="ag-preset-def">Default when opening this page</label>
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
        <div class="card-body text-center text-muted py-5">No agreements match these filters.</div>
      </div>
      <div v-else class="table-responsive card">
        <table class="table table-hover mb-0">
          <thead class="table-light">
            <tr>
              <th>Title</th>
              <th>Partner</th>
              <th>Status</th>
              <th>Type</th>
              <th>End</th>
              <th>Programs</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in rows" :key="a.id">
              <td class="fw-medium">{{ a.title }}</td>
              <td>{{ a.partner_institution_name }}</td>
              <td>
                <span class="badge" :class="statusBadge(a.status)">{{ formatEnum(a.status) }}</span>
              </td>
              <td class="small">{{ formatEnum(a.agreement_type) }}</td>
              <td class="small text-muted">{{ a.end_date || '—' }}</td>
              <td class="small">{{ (a.programs && a.programs.length) || 0 }}</td>
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
import {
  STAFF_SAVED_SEARCH_TYPE,
  deserializeExchangeAgreementFilters,
  serializeExchangeAgreementFilters,
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
} = useStaffSavedPresets(STAFF_SAVED_SEARCH_TYPE.EXCHANGE_AGREEMENT)

const statusChoices = [
  { value: 'draft', label: 'Draft' },
  { value: 'active', label: 'Active' },
  { value: 'suspended', label: 'Suspended' },
  { value: 'expired', label: 'Expired' },
  { value: 'terminated', label: 'Terminated' },
  { value: 'renewal_pending', label: 'Renewal pending' },
]

const typeChoices = [
  { value: 'bilateral', label: 'Bilateral' },
  { value: 'multilateral', label: 'Multilateral' },
  { value: 'erasmus', label: 'Erasmus+' },
  { value: 'specific', label: 'Specific program' },
  { value: 'other', label: 'Other' },
]

const programs = ref([])
const rows = ref([])
const loading = ref(true)
const error = ref(null)

const filters = ref({
  search: '',
  status: '',
  agreement_type: '',
  program: '',
  partner: '',
  end_date_before: '',
  end_date_after: '',
  expiring_within_days: '',
  ordering: '-end_date',
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
  debounceTimer = setTimeout(() => fetchAgreements(1), 400)
}

async function loadPrograms() {
  try {
    const { data } = await api.get('/api/programs/', { params: { page_size: 200, ordering: 'name' } })
    programs.value = data.results ?? data ?? []
  } catch {
    programs.value = []
  }
}

async function fetchAgreements(page = 1) {
  try {
    loading.value = true
    error.value = null
    const params = { page, ordering: filters.value.ordering }
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.status) params.status = filters.value.status
    if (filters.value.agreement_type) params.agreement_type = filters.value.agreement_type
    if (filters.value.program) params.program = filters.value.program
    if (filters.value.partner) params.partner = filters.value.partner
    if (filters.value.end_date_before) params.end_date_before = filters.value.end_date_before
    if (filters.value.end_date_after) params.end_date_after = filters.value.end_date_after
    if (filters.value.expiring_within_days !== '' && filters.value.expiring_within_days != null) {
      params.expiring_within_days = filters.value.expiring_within_days
    }

    const { data } = await api.get('/api/exchange-agreements/', { params })
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
    error.value = 'Failed to load agreements.'
    errorToast(error.value)
  } finally {
    loading.value = false
  }
}

function goToPage(page) {
  if (page >= 1 && page <= totalPages.value) {
    fetchAgreements(page)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

function clearFilters() {
  filters.value = {
    search: '',
    status: '',
    agreement_type: '',
    program: '',
    partner: '',
    end_date_before: '',
    end_date_after: '',
    expiring_within_days: '',
    ordering: '-end_date',
  }
  fetchAgreements(1)
}

function applyPreset(p) {
  filters.value = deserializeExchangeAgreementFilters(p.filters)
  pagination.value.currentPage = 1
  fetchAgreements(1)
}

function statusBadge(status) {
  const m = {
    active: 'bg-success',
    draft: 'bg-secondary',
    suspended: 'bg-warning text-dark',
    expired: 'bg-dark',
    terminated: 'bg-danger',
    renewal_pending: 'bg-info text-dark',
  }
  return m[status] || 'bg-secondary'
}

function formatEnum(s) {
  if (!s) return '—'
  return s.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

onMounted(async () => {
  await loadPrograms()
  await loadPresets()
  const def = savedPresets.value.find((p) => p.is_default)
  if (def) {
    filters.value = deserializeExchangeAgreementFilters(def.filters)
  }
  await fetchAgreements(1)
})
</script>

<style scoped>
.staff-agreements-page {
  min-height: 100vh;
  background-color: #f8f9fa;
}
</style>
