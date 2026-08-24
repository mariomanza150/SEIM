<template>
  <div class="staff-agreements-page">
    <PageHeader
      :title="t('route.names.StaffExchangeAgreements')"
      :subtitle="t('exchangeAgreementsPage.pageSubtitle')"
      icon-class="bi bi-file-earmark-richtext"
    >
      <template #breadcrumb>
        <PageBreadcrumb
          :aria-label="t('exchangeAgreementsPage.breadcrumbAria')"
          :items="[
            { to: { name: 'Dashboard' }, label: t('route.names.Dashboard') },
            { label: t('route.names.StaffExchangeAgreements') },
          ]"
        />
      </template>
    </PageHeader>

      <CompactFilterBar :clear-label="t('exchangeAgreementsPage.clearFilters')" @clear="clearFilters">
        <template #primary>
            <div class="col-md-4">
              <label class="form-label">{{ t('exchangeAgreementsPage.searchLabel') }}</label>
              <input
                v-model="filters.search"
                type="text"
                class="form-control"
                :placeholder="t('exchangeAgreementsPage.searchPlaceholder')"
                @input="debouncedFetch"
              />
            </div>
            <div class="col-md-2">
              <label class="form-label">{{ t('exchangeAgreementsPage.colStatus') }}</label>
              <select v-model="filters.status" class="form-select" @change="fetchAgreements(1)">
                <option value="">{{ t('exchangeAgreementsPage.filterOptionAll') }}</option>
                <option v-for="s in statusChoices" :key="s.value" :value="s.value">{{ s.label }}</option>
              </select>
            </div>
            <div class="col-md-2">
              <label class="form-label">{{ t('exchangeAgreementsPage.typeLabel') }}</label>
              <select v-model="filters.agreement_type" class="form-select" @change="fetchAgreements(1)">
                <option value="">{{ t('exchangeAgreementsPage.filterOptionAll') }}</option>
                <option v-for="ty in typeChoices" :key="ty.value" :value="ty.value">{{ ty.label }}</option>
              </select>
            </div>
        </template>
        <template #advanced>
            <div class="row g-2">
            <div class="col-md-4">
              <label class="form-label">{{ t('exchangeAgreementsPage.linkedProgramLabel') }}</label>
              <select v-model="filters.program" class="form-select" @change="fetchAgreements(1)">
                <option value="">{{ t('exchangeAgreementsPage.programAny') }}</option>
                <option v-for="p in programs" :key="p.id" :value="p.id">{{ p.name }}</option>
              </select>
            </div>
            <div class="col-md-3">
              <label class="form-label">{{ t('exchangeAgreementsPage.partnerContainsLabel') }}</label>
              <input
                v-model="filters.partner"
                type="text"
                class="form-control"
                @change="fetchAgreements(1)"
              />
            </div>
            <div class="col-md-2">
              <label class="form-label">{{ t('exchangeAgreementsPage.endAfterLabel') }}</label>
              <input v-model="filters.end_date_after" type="date" class="form-control" @change="fetchAgreements(1)" />
            </div>
            <div class="col-md-2">
              <label class="form-label">{{ t('exchangeAgreementsPage.endBeforeLabel') }}</label>
              <input v-model="filters.end_date_before" type="date" class="form-control" @change="fetchAgreements(1)" />
            </div>
            <div class="col-md-2">
              <label class="form-label">{{ t('exchangeAgreementsPage.expiringDaysLabel') }}</label>
              <input
                v-model.number="filters.expiring_within_days"
                type="number"
                min="0"
                class="form-control"
                :placeholder="t('exchangeAgreementsPage.expiringPlaceholder')"
                @change="fetchAgreements(1)"
              />
            </div>
            <div class="col-md-3">
              <label class="form-label">{{ t('exchangeAgreementsPage.sortLabel') }}</label>
              <select v-model="filters.ordering" class="form-select" @change="fetchAgreements(1)">
                <option value="-end_date">{{ t('exchangeAgreementsPage.sortEndSoonest') }}</option>
                <option value="end_date">{{ t('exchangeAgreementsPage.sortEndLatest') }}</option>
                <option value="-created_at">{{ t('exchangeAgreementsPage.sortNewest') }}</option>
                <option value="partner_institution_name">{{ t('exchangeAgreementsPage.sortPartnerAz') }}</option>
              </select>
            </div>
            </div>
        </template>
        <template #presets>
              <div class="d-flex flex-wrap align-items-end gap-2 mb-2">
                <div class="flex-grow-1" style="min-width: 200px">
                  <label class="form-label small text-muted mb-1">{{ t('exchangeAgreementsPage.presetSaveLabel') }}</label>
                  <div class="input-group input-group-sm">
                    <input
                      v-model="newPresetName"
                      type="text"
                      class="form-control"
                      data-testid="agreements-preset-name"
                      :placeholder="t('exchangeAgreementsPage.presetNamePlaceholder')"
                    />
                    <button
                      type="button"
                      class="btn btn-outline-primary"
                      :disabled="!newPresetName.trim() || presetsLoading"
                      @click="savePreset(() => serializeExchangeAgreementFilters(filters))"
                    >
                      {{ t('exchangeAgreementsPage.presetSave') }}
                    </button>
                  </div>
                </div>
                <div class="form-check mb-1">
                  <input id="ag-preset-def" v-model="saveAsDefault" class="form-check-input" type="checkbox" />
                  <label class="form-check-label small" for="ag-preset-def">{{
                    t('exchangeAgreementsPage.presetDefaultCheckbox')
                  }}</label>
                </div>
              </div>
              <div v-if="savedPresets.length" class="small">
                <span class="text-muted me-2">{{ t('exchangeAgreementsPage.presetSavedPrefix') }}</span>
                <span
                  v-for="p in savedPresets"
                  :key="p.id"
                  class="d-inline-flex align-items-center gap-1 me-3 mb-1"
                >
                  <button type="button" class="btn btn-link btn-sm p-0" @click="applyPreset(p)">{{ p.name }}</button>
                  <i
                    v-if="p.is_default"
                    class="bi bi-star-fill text-warning"
                    :title="t('exchangeAgreementsPage.presetDefaultTitle')"
                    :aria-label="t('exchangeAgreementsPage.presetDefaultAria')"
                  ></i>
                  <button
                    v-else
                    type="button"
                    class="btn btn-link btn-sm p-0 text-secondary"
                    :title="t('exchangeAgreementsPage.presetSetDefaultTitle')"
                    :aria-label="t('exchangeAgreementsPage.presetSetDefaultAria')"
                    @click="setDefaultPreset(p)"
                  >
                    <i class="bi bi-star"></i>
                  </button>
                  <button
                    type="button"
                    class="btn btn-link btn-sm p-0 text-danger"
                    :title="t('exchangeAgreementsPage.presetRemoveTitle')"
                    :aria-label="t('exchangeAgreementsPage.presetRemoveAria')"
                    @click="deletePreset(p)"
                  >
                    <i class="bi bi-trash"></i>
                  </button>
                </span>
              </div>
        </template>
      </CompactFilterBar>

      <PageStateShell
        :loading="loading"
        :error="error || ''"
        :empty="!loading && !error && rows.length === 0"
        :empty-body="t('exchangeAgreementsPage.emptyFiltered')"
        empty-test-id="agreements-empty"
        :loading-label="t('exchangeAgreementsPage.loading')"
        skeleton="table"
        :skeleton-columns="10"
      >
        <ResponsiveList
          :items="rows"
          :columns="agreementColumns"
          mobile-test-id="agreements-mobile"
        >
          <div class="table-responsive card">
            <table class="table table-hover mb-0">
              <thead class="seim-table-head">
                <tr>
                  <th>{{ t('exchangeAgreementsPage.colTitle') }}</th>
                  <th>{{ t('exchangeAgreementsPage.colPartner') }}</th>
                  <th>{{ t('exchangeAgreementsPage.colStatus') }}</th>
                  <th>{{ t('exchangeAgreementsPage.colType') }}</th>
                  <th>{{ t('exchangeAgreementsPage.colEnd') }}</th>
                  <th>{{ t('exchangeAgreementsPage.colPrograms') }}</th>
                  <th>{{ t('exchangeAgreementsPage.colRepository') }}</th>
                  <th>{{ t('exchangeAgreementsPage.colMessages') }}</th>
                  <th>{{ t('exchangeAgreementsPage.colPortal') }}</th>
                  <th class="text-end">{{ t('exchangeAgreementsPage.colRenewal') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="a in rows" :key="a.id">
                  <td class="fw-medium">{{ a.title }}</td>
                  <td>{{ a.partner_institution_name }}</td>
                  <td>
                    <span class="badge" :class="statusBadge(a.status)">{{ formatAgreementStatus(a.status) }}</span>
                  </td>
                  <td class="small">{{ formatAgreementType(a.agreement_type) }}</td>
                  <td class="small text-muted">{{ a.end_date || t('exchangeAgreementsPage.emDash') }}</td>
                  <td class="small">{{ (a.programs && a.programs.length) || 0 }}</td>
                  <td>
                    <router-link
                      class="btn btn-sm btn-outline-primary"
                      :to="{ name: 'StaffAgreementDocuments', params: { agreementId: String(a.id) } }"
                    >
                      {{ t('exchangeAgreementsPage.openRepository') }}
                    </router-link>
                  </td>
                  <td>
                    <button
                      type="button"
                      class="btn btn-sm btn-outline-primary"
                      data-testid="agreements-open-thread"
                      @click="openThread(a)"
                    >
                      {{ t('exchangeAgreementsPage.openThread') }}
                    </button>
                  </td>
                  <td class="small" style="min-width: 220px">
                    <div v-if="(a.partner_contacts || []).length" class="mb-1">
                      <div v-for="c in a.partner_contacts" :key="c.id" class="text-truncate">
                        {{ c.user_email || c.user_name }}
                      </div>
                    </div>
                    <div v-else class="text-muted mb-1">{{ t('exchangeAgreementsPage.addPartnerEmpty') }}</div>
                    <form class="d-flex gap-1" @submit.prevent="addPartnerByEmail(a)">
                      <input
                        v-model="partnerEmails[a.id]"
                        type="email"
                        class="form-control form-control-sm"
                        required
                        :placeholder="t('exchangeAgreementsPage.addPartnerEmailPlaceholder')"
                        :aria-label="t('exchangeAgreementsPage.addPartnerAria', { title: a.title })"
                        data-testid="add-partner-email"
                      />
                      <button
                        type="submit"
                        class="btn btn-sm btn-outline-primary"
                        :disabled="!!partnerBusy[a.id]"
                        data-testid="add-partner-submit"
                      >
                        {{ t('exchangeAgreementsPage.addPartnerSubmit') }}
                      </button>
                    </form>
                  </td>
                  <td class="text-end text-nowrap">
                    <button
                      type="button"
                      class="btn btn-sm btn-outline-primary"
                      :title="t('exchangeAgreementsPage.renewalPendingTitle')"
                      @click="onMarkRenewalPending(a)"
                    >
                      {{ t('exchangeAgreementsPage.renewalPendingShort') }}
                    </button>
                    <button
                      type="button"
                      class="btn btn-sm btn-outline-secondary ms-1"
                      :title="t('exchangeAgreementsPage.renewalDraftTitle')"
                      :disabled="!!a.renewal_draft_successor_id"
                      @click="onCreateRenewalSuccessor(a)"
                    >
                      {{ t('exchangeAgreementsPage.renewalDraftShort') }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <template #col-status="{ item }">
            <span class="badge" :class="statusBadge(item.status)">{{ formatAgreementStatus(item.status) }}</span>
          </template>
          <template #col-agreement_type="{ item }">
            {{ formatAgreementType(item.agreement_type) }}
          </template>
          <template #col-end_date="{ item }">
            {{ item.end_date || t('exchangeAgreementsPage.emDash') }}
          </template>
          <template #col-programs="{ item }">
            {{ (item.programs && item.programs.length) || 0 }}
          </template>
          <template #actions="{ item }">
            <router-link
              class="btn btn-sm btn-outline-primary"
              :to="{ name: 'StaffAgreementDocuments', params: { agreementId: String(item.id) } }"
            >
              {{ t('exchangeAgreementsPage.openRepository') }}
            </router-link>
            <button
              type="button"
              class="btn btn-sm btn-outline-primary"
              data-testid="agreements-open-thread"
              @click="openThread(item)"
            >
              {{ t('exchangeAgreementsPage.openThread') }}
            </button>
          </template>
        </ResponsiveList>
      </PageStateShell>

      <div v-if="threadAgreement" class="card mt-3" data-testid="agreements-thread">
        <div class="card-header">
          <h5 class="mb-0">{{ t('exchangeAgreementsPage.threadHeading', { title: threadAgreement.title }) }}</h5>
        </div>
        <div class="card-body">
          <div v-if="threadLoading" class="text-muted small">{{ t('exchangeAgreementsPage.threadLoading') }}</div>
          <ul v-else class="list-unstyled mb-3">
            <li v-for="c in threadComments" :key="c.id" class="mb-2">
              <div class="small text-muted">
                {{ c.author_display_name }}
                <span v-if="c.is_private" class="badge bg-secondary ms-1">{{
                  t('exchangeAgreementsPage.privateBadge')
                }}</span>
              </div>
              <div>{{ c.text }}</div>
            </li>
            <li v-if="!threadComments.length" class="text-muted">{{ t('exchangeAgreementsPage.threadEmpty') }}</li>
          </ul>
          <form @submit.prevent="postThread">
            <label class="form-label" for="agreements-thread-text">{{ t('exchangeAgreementsPage.threadLabel') }}</label>
            <textarea
              id="agreements-thread-text"
              v-model="threadText"
              class="form-control mb-2"
              rows="3"
              required
              data-testid="agreements-thread-text"
            ></textarea>
            <div class="form-check mb-2">
              <input id="agreements-thread-private" v-model="threadPrivate" class="form-check-input" type="checkbox" />
              <label class="form-check-label" for="agreements-thread-private">{{
                t('exchangeAgreementsPage.threadPrivateLabel')
              }}</label>
            </div>
            <button
              type="submit"
              class="btn btn-primary btn-sm"
              :disabled="threadBusy"
              data-testid="agreements-thread-submit"
            >
              {{ t('exchangeAgreementsPage.threadSubmit') }}
            </button>
          </form>
        </div>
      </div>

      <nav
        v-if="!loading && pagination.count > pagination.pageSize"
        class="mt-3"
        :aria-label="t('exchangeAgreementsPage.paginationAria')"
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useToast } from '@/composables/useToast'
import { useStaffSavedPresets } from '@/composables/useStaffSavedPresets'
import { useConfirm } from '@/composables/useConfirm'
import api from '@/services/api'
import PageHeader from '@/components/PageHeader.vue'
import PageBreadcrumb from '@/components/PageBreadcrumb.vue'
import PageStateShell from '@/components/State/PageStateShell.vue'
import ResponsiveList from '@/components/ResponsiveList.vue'
import CompactFilterBar from '@/components/CompactFilterBar.vue'
import {
  STAFF_SAVED_SEARCH_TYPE,
  deserializeExchangeAgreementFilters,
  serializeExchangeAgreementFilters,
} from '@/utils/staffListSearchPresets'

const { t, te } = useI18n()
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
} = useStaffSavedPresets(STAFF_SAVED_SEARCH_TYPE.EXCHANGE_AGREEMENT)

const STATUS_VALUES = ['draft', 'active', 'suspended', 'expired', 'terminated', 'renewal_pending']
const TYPE_VALUES = ['bilateral', 'multilateral', 'erasmus', 'specific', 'other']

const statusChoices = computed(() =>
  STATUS_VALUES.map((value) => ({
    value,
    label: t(`exchangeAgreementsPage.status.${value}`),
  })),
)

const typeChoices = computed(() =>
  TYPE_VALUES.map((value) => ({
    value,
    label: t(`exchangeAgreementsPage.agreementType.${value}`),
  })),
)

const agreementColumns = computed(() => [
  { key: 'title', label: t('exchangeAgreementsPage.colTitle') },
  { key: 'partner_institution_name', label: t('exchangeAgreementsPage.colPartner') },
  { key: 'status', label: t('exchangeAgreementsPage.colStatus') },
  { key: 'agreement_type', label: t('exchangeAgreementsPage.colType') },
  { key: 'end_date', label: t('exchangeAgreementsPage.colEnd') },
  { key: 'programs', label: t('exchangeAgreementsPage.colPrograms') },
])

const programs = ref([])
const rows = ref([])
const partnerEmails = ref({})
const partnerBusy = ref({})
const threadAgreement = ref(null)
const threadComments = ref([])
const threadText = ref('')
const threadPrivate = ref(false)
const threadLoading = ref(false)
const threadBusy = ref(false)
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

function formatAgreementField(s, kind) {
  if (!s) return t('exchangeAgreementsPage.emDash')
  const key =
    kind === 'status' ? `exchangeAgreementsPage.status.${s}` : `exchangeAgreementsPage.agreementType.${s}`
  return te(key) ? t(key) : s.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

function formatAgreementStatus(s) {
  return formatAgreementField(s, 'status')
}

function formatAgreementType(s) {
  return formatAgreementField(s, 'type')
}

async function loadPrograms() {
  try {
    const { data } = await api.get('/api/programs/', { params: { page_size: 100, ordering: 'name' } })
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
    error.value = t('exchangeAgreementsPage.loadError')
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

async function openThread(a) {
  threadAgreement.value = a
  threadText.value = ''
  threadPrivate.value = false
  threadLoading.value = true
  try {
    const { data } = await api.get(`/api/exchange-agreements/${a.id}/comments/`)
    threadComments.value = Array.isArray(data) ? data : data.results ?? []
  } catch {
    threadComments.value = []
  } finally {
    threadLoading.value = false
  }
}

async function postThread() {
  const text = threadText.value.trim()
  if (!text || !threadAgreement.value) return
  threadBusy.value = true
  try {
    const { data } = await api.post(`/api/exchange-agreements/${threadAgreement.value.id}/comments/`, {
      text,
      is_private: threadPrivate.value,
    })
    threadComments.value = [...threadComments.value, data]
    threadText.value = ''
    threadPrivate.value = false
  } catch (e) {
    errorToast(e.response?.data?.detail || t('exchangeAgreementsPage.threadErrorFallback'))
  } finally {
    threadBusy.value = false
  }
}

async function addPartnerByEmail(a) {
  const email = (partnerEmails.value[a.id] || '').trim()
  if (!email) return
  partnerBusy.value = { ...partnerBusy.value, [a.id]: true }
  try {
    await api.post(`/api/partner/agreements/${a.id}/partner-contacts/`, { email })
    partnerEmails.value = { ...partnerEmails.value, [a.id]: '' }
    successToast(t('exchangeAgreementsPage.addPartnerSuccessToast'))
    await fetchAgreements(pagination.value.currentPage)
  } catch (e) {
    const data = e.response?.data
    const msg =
      (Array.isArray(data?.email) && data.email[0]) ||
      data?.detail ||
      t('exchangeAgreementsPage.addPartnerErrorFallback')
    errorToast(msg)
  } finally {
    partnerBusy.value = { ...partnerBusy.value, [a.id]: false }
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

async function onMarkRenewalPending(a) {
  const raw = window.prompt(t('exchangeAgreementsPage.markRenewalPrompt'))
  if (raw === null) return
  const body = {}
  const trimmed = raw.trim()
  if (trimmed) body.renewal_follow_up_due = trimmed
  try {
    await api.post(`/api/exchange-agreements/${a.id}/mark-renewal-pending/`, body)
    successToast(t('exchangeAgreementsPage.markRenewalSuccessToast'))
    await fetchAgreements(pagination.value.currentPage)
  } catch (e) {
    const msg = e.response?.data?.error || t('exchangeAgreementsPage.markRenewalErrorFallback')
    errorToast(msg)
  }
}

async function onCreateRenewalSuccessor(a) {
  const ok = await confirm({
    title: t('exchangeAgreementsPage.renewalDraftShort'),
    message: t('exchangeAgreementsPage.createRenewalConfirm'),
    confirmText: t('exchangeAgreementsPage.renewalDraftShort'),
    cancelText: t('settings.cancel'),
    variant: 'primary',
  })
  if (!ok) return
  try {
    await api.post(`/api/exchange-agreements/${a.id}/create-renewal-successor/`, {
      copy_documents: true,
    })
    successToast(t('exchangeAgreementsPage.createRenewalSuccessToast'))
    await fetchAgreements(pagination.value.currentPage)
  } catch (e) {
    const msg = e.response?.data?.error || t('exchangeAgreementsPage.createRenewalErrorFallback')
    errorToast(msg)
  }
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

