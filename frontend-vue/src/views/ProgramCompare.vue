<template>
  <div class="program-compare-page" data-testid="program-compare-page">
    <nav :aria-label="t('programComparePage.breadcrumbAria')">
      <ol class="breadcrumb">
        <li class="breadcrumb-item">
          <router-link :to="{ name: 'Dashboard' }">{{ t('route.names.Dashboard') }}</router-link>
        </li>
        <li class="breadcrumb-item active">{{ t('route.names.ProgramCompare') }}</li>
      </ol>
    </nav>

      <div class="row mb-4">
        <div class="col-lg-8">
          <h2><i class="bi bi-columns-gap me-2"></i>{{ t('route.names.ProgramCompare') }}</h2>
          <p class="text-muted mb-0">
            {{ t('programComparePage.pageSubtitle') }}
          </p>
        </div>
        <div class="col-lg-4 text-lg-end mt-2 mt-lg-0">
          <router-link :to="{ name: 'ApplicationNew' }" class="btn btn-primary">
            <i class="bi bi-plus-circle me-1"></i>{{ t('programComparePage.newApplication') }}
          </router-link>
        </div>
      </div>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">{{ t('programComparePage.loadingSpinner') }}</span>
        </div>
        <p class="mt-3 text-muted">{{ t('programComparePage.loadingPrograms') }}</p>
      </div>

      <div v-else-if="loadError" class="alert alert-danger">{{ loadError }}</div>

      <template v-else>
        <div class="card mb-4">
          <div class="card-body">
            <label class="form-label fw-semibold">{{
              t('programComparePage.pickerLabel', { current: selectedIds.length, max: maxCompare })
            }}</label>
            <div class="row g-2 program-picker-scroll">
              <div
                v-for="p in programs"
                :key="p.id"
                class="col-md-6 col-xl-4"
              >
                <div class="form-check">
                  <input
                    :id="`cmp-${p.id}`"
                    class="form-check-input"
                    type="checkbox"
                    :checked="selectedIds.includes(p.id)"
                    :disabled="!selectedIds.includes(p.id) && selectedIds.length >= maxCompare"
                    @change="toggleId(p.id, $event.target.checked)"
                  >
                  <label class="form-check-label" :for="`cmp-${p.id}`">{{ p.name }}</label>
                </div>
              </div>
            </div>
            <div class="mt-3 d-flex flex-wrap gap-2">
              <button type="button" class="btn btn-outline-secondary btn-sm" @click="clearSelection">
                {{ t('programComparePage.clearSelection') }}
              </button>
            </div>
          </div>
        </div>

        <div
          v-if="selectedIds.length < 2"
          class="alert alert-info"
          data-testid="program-compare-hint"
        >
          {{ t('programComparePage.hintChooseTwo') }}
        </div>

        <div v-else class="card">
          <div class="card-body p-0">
            <div class="table-responsive">
              <table class="table table-bordered table-hover mb-0 align-middle" data-testid="program-compare-table">
                <thead class="table-light">
                  <tr>
                    <th scope="col" class="text-muted small" style="min-width: 9rem">{{ t('programComparePage.colCriterion') }}</th>
                    <th v-for="p in selectedPrograms" :key="p.id" scope="col">
                      <div class="fw-semibold">{{ p.name }}</div>
                      <router-link
                        class="btn btn-sm btn-outline-primary mt-1"
                        :to="{ name: 'ApplicationNew', query: { program: p.id } }"
                      >
                        {{ t('programComparePage.apply') }}
                      </router-link>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <th scope="row" class="small text-muted">{{ t('programComparePage.rowProgramDates') }}</th>
                    <td v-for="p in selectedPrograms" :key="`${p.id}-dates`" class="small">
                      {{ formatDate(p.start_date) }}{{ t('programComparePage.dateRangeSeparator') }}{{ formatDate(p.end_date) }}
                    </td>
                  </tr>
                  <tr>
                    <th scope="row" class="small text-muted">{{ t('programComparePage.rowApplicationWindow') }}</th>
                    <td v-for="p in selectedPrograms" :key="`${p.id}-win`" class="small">
                      <div v-if="p.application_open_date || p.application_deadline">
                        <div v-if="p.application_open_date">
                          {{ t('programComparePage.windowOpens', { date: formatDate(p.application_open_date) }) }}
                        </div>
                        <div v-if="p.application_deadline">
                          {{ t('programComparePage.windowDeadline', { date: formatDate(p.application_deadline) }) }}
                        </div>
                      </div>
                      <span v-else class="text-muted">{{ t('programComparePage.windowNotSet') }}</span>
                      <div class="mt-1">
                        <span
                          class="badge"
                          :class="p.application_window_open ? 'bg-success' : 'bg-secondary'"
                        >
                          {{
                            p.application_window_open
                              ? t('programComparePage.acceptingApplications')
                              : t('programComparePage.notOpen')
                          }}
                        </span>
                      </div>
                    </td>
                  </tr>
                  <tr>
                    <th scope="row" class="small text-muted">{{ t('programComparePage.rowMinGpa') }}</th>
                    <td v-for="p in selectedPrograms" :key="`${p.id}-gpa`">
                      {{ p.min_gpa != null ? p.min_gpa : t('programComparePage.emDash') }}
                    </td>
                  </tr>
                  <tr>
                    <th scope="row" class="small text-muted">{{ t('programComparePage.rowLanguage') }}</th>
                    <td v-for="p in selectedPrograms" :key="`${p.id}-lang`" class="small">
                      <template v-if="p.required_language">
                        {{ p.required_language }}
                        <span v-if="p.min_language_level" class="badge bg-secondary">{{ p.min_language_level }}</span>
                      </template>
                      <span v-else class="text-muted">{{ t('programComparePage.emDash') }}</span>
                    </td>
                  </tr>
                  <tr>
                    <th scope="row" class="small text-muted">{{ t('programComparePage.rowAgeRange') }}</th>
                    <td v-for="p in selectedPrograms" :key="`${p.id}-age`" class="small">
                      <template v-if="p.min_age != null || p.max_age != null">
                        {{ p.min_age != null ? p.min_age : t('programComparePage.emDash') }}
                        {{ t('programComparePage.dateRangeSeparator') }}
                        {{ p.max_age != null ? p.max_age : t('programComparePage.emDash') }}
                      </template>
                      <span v-else class="text-muted">{{ t('programComparePage.emDash') }}</span>
                    </td>
                  </tr>
                  <tr>
                    <th scope="row" class="small text-muted">{{ t('programComparePage.rowRecurring') }}</th>
                    <td v-for="p in selectedPrograms" :key="`${p.id}-rec`">
                      {{ p.recurring ? t('programComparePage.recurringYes') : t('programComparePage.recurringNo') }}
                    </td>
                  </tr>
                  <tr>
                    <th scope="row" class="small text-muted align-top">{{ t('programComparePage.rowDescription') }}</th>
                    <td v-for="p in selectedPrograms" :key="`${p.id}-desc`" class="small text-muted">
                      {{ truncate(p.description, 280) }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </template>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useToast } from '@/composables/useToast'
import {
  parseCompareIdsFromQuery,
  compareIdsToQueryParam,
  MAX_COMPARE_PROGRAMS,
} from '@/utils/programCompareQuery'

const route = useRoute()
const router = useRouter()
const { t, locale } = useI18n()
const { error: errorToast } = useToast()

const maxCompare = MAX_COMPARE_PROGRAMS
const programs = ref([])
const loading = ref(true)
const loadError = ref('')
const selectedIds = ref([])

let querySyncTimer = null

const selectedPrograms = computed(() => {
  const order = selectedIds.value
  const map = new Map(programs.value.map((p) => [p.id, p]))
  return order.map((id) => map.get(id)).filter(Boolean)
})

function formatDate(d) {
  if (!d) return t('programComparePage.emDash')
  const loc = locale.value === 'es' ? 'es' : 'en-US'
  return new Date(d).toLocaleDateString(loc, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

function truncate(text, len) {
  if (!text) return t('programComparePage.emDash')
  const s = String(text).trim()
  if (s.length <= len) return s
  return `${s.slice(0, len)}…`
}

function toggleId(id, checked) {
  if (checked) {
    if (selectedIds.value.includes(id)) return
    if (selectedIds.value.length >= maxCompare) return
    selectedIds.value = [...selectedIds.value, id]
  } else {
    selectedIds.value = selectedIds.value.filter((x) => x !== id)
  }
}

function clearSelection() {
  selectedIds.value = []
}

async function fetchAllActivePrograms() {
  const acc = []
  let page = 1
  const pageSize = 50
  for (;;) {
    const { data } = await api.get('/api/programs/', {
      params: {
        is_active: true,
        ordering: 'name',
        page,
        page_size: pageSize,
      },
    })
    const chunk = data.results ?? data ?? []
    acc.push(...chunk)
    if (!data.next) break
    page += 1
    if (page > 100) break
  }
  return acc
}

onMounted(async () => {
  loading.value = true
  loadError.value = ''
  try {
    programs.value = await fetchAllActivePrograms()
    const fromQuery = parseCompareIdsFromQuery(route.query)
    const valid = new Set(programs.value.map((p) => p.id))
    selectedIds.value = fromQuery.filter((id) => valid.has(id))
  } catch (e) {
    console.error(e)
    loadError.value = t('programComparePage.loadError')
    errorToast(loadError.value)
  } finally {
    loading.value = false
  }
})

watch(
  selectedIds,
  (ids) => {
    if (querySyncTimer != null) clearTimeout(querySyncTimer)
    querySyncTimer = setTimeout(() => {
      querySyncTimer = null
      const next = { ...route.query }
      const param = compareIdsToQueryParam(ids)
      if (param) next.ids = param
      else delete next.ids
      router.replace({ query: next })
    }, 250)
  },
  { deep: true },
)
</script>

<style scoped>
.program-compare-page {
  min-height: 100vh;
  background-color: var(--seim-app-bg, #f8f9fa);
}

.program-picker-scroll {
  max-height: 16rem;
  overflow-y: auto;
}
</style>
