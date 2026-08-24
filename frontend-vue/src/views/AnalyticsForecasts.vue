<template>
  <div class="analytics-forecasts-page">
    <PageHeader :title="t('route.names.AnalyticsForecasts')" :subtitle="t('analyticsForecastsPage.subtitle')">
      <template #breadcrumb>
        <PageBreadcrumb
          :aria-label="t('analyticsForecastsPage.breadcrumbAria')"
          :items="[
            { to: { name: 'Dashboard' }, label: t('route.names.Dashboard') },
            { label: t('route.names.AnalyticsForecasts') },
          ]"
        />
      </template>
    </PageHeader>

    <CompactFilterBar test-id="forecasts-filters" @clear="clearFilters">
      <template #primary>
        <div class="col-md-6">
          <label class="form-label" for="af-program">{{ t('analyticsForecastsPage.programLabel') }}</label>
          <select
            id="af-program"
            v-model="programId"
            class="form-select"
            data-testid="forecasts-program"
            @change="loadForecasts"
          >
            <option value="">{{ t('analyticsForecastsPage.programAny') }}</option>
            <option v-for="p in programs" :key="p.id" :value="p.id">{{ p.name }}</option>
          </select>
        </div>
      </template>
      <template #presets>
        <span class="form-label small text-muted d-block mb-2">{{ t('analyticsForecastsPage.savedViewsLabel') }}</span>
        <div class="d-flex flex-wrap align-items-end gap-2 mb-2">
          <div class="flex-grow-1" style="min-width: 200px">
            <input
              v-model="newPresetName"
              type="text"
              class="form-control form-control-sm"
              :placeholder="t('analyticsForecastsPage.presetNamePlaceholder')"
              data-testid="forecasts-preset-name"
            />
          </div>
          <button
            type="button"
            class="btn btn-sm btn-outline-primary"
            :disabled="!newPresetName.trim() || presetsLoading"
            data-testid="forecasts-preset-save"
            @click="savePreset(() => serializeAnalyticsForecastFilters({ program: programId }))"
          >
            {{ t('analyticsForecastsPage.saveView') }}
          </button>
          <div class="form-check mb-0">
            <input id="af-preset-def" v-model="saveAsDefault" class="form-check-input" type="checkbox" />
            <label class="form-check-label small" for="af-preset-def">{{
              t('analyticsForecastsPage.presetDefaultCheckbox')
            }}</label>
          </div>
        </div>
        <div v-if="savedPresets.length" class="small">
          <span class="text-muted me-2">{{ t('analyticsForecastsPage.presetSavedPrefix') }}</span>
          <span v-for="p in savedPresets" :key="p.id" class="d-inline-flex align-items-center gap-1 me-3 mb-1">
            <button
              type="button"
              class="btn btn-link btn-sm p-0"
              data-testid="forecasts-preset-apply"
              @click="applyPreset(p)"
            >{{ p.name }}</button>
            <i
              v-if="p.is_default"
              class="bi bi-star-fill text-warning"
              :title="t('analyticsForecastsPage.presetDefaultTitle')"
              :aria-label="t('analyticsForecastsPage.presetDefaultAria')"
            ></i>
            <button
              v-else
              type="button"
              class="btn btn-link btn-sm p-0 text-secondary"
              :title="t('analyticsForecastsPage.presetSetDefaultTitle')"
              :aria-label="t('analyticsForecastsPage.presetSetDefaultAria')"
              @click="setDefaultPreset(p)"
            >
              <i class="bi bi-star"></i>
            </button>
            <button
              type="button"
              class="btn btn-link btn-sm p-0 text-danger"
              :title="t('analyticsForecastsPage.presetRemoveTitle')"
              :aria-label="t('analyticsForecastsPage.presetRemoveAria')"
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
      :error="error"
      :loading-label="t('analyticsForecastsPage.loading')"
      skeleton="stats"
      :skeleton-count="3"
    >
    <div v-if="data" data-testid="analytics-forecasts-page">
      <div class="card mb-4">
        <div class="card-header">
          <h5 class="mb-0">{{ t('analyticsForecastsPage.demandHeading') }}</h5>
        </div>
        <div class="card-body">
          <p class="text-muted">{{ t('analyticsForecastsPage.trend', { n: data.demand?.trend_per_week ?? 0 }) }}</p>
          <ResponsiveList :items="demandRows" :columns="demandMobileColumns" mobile-test-id="forecasts-demand-mobile">
          <div class="table-responsive">
            <table class="table table-sm mb-0">
              <thead>
                <tr>
                  <th>{{ t('analyticsForecastsPage.colWeek') }}</th>
                  <th>{{ t('analyticsForecastsPage.colActual') }}</th>
                  <th>{{ t('analyticsForecastsPage.colPredicted') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in data.demand?.history || []" :key="'h-' + row.week_start">
                  <td>{{ row.week_start }}</td>
                  <td>{{ row.applications }}</td>
                  <td class="text-muted">—</td>
                </tr>
                <tr v-for="row in data.demand?.forecast || []" :key="'f-' + row.week_start">
                  <td>{{ row.week_start }}</td>
                  <td class="text-muted">—</td>
                  <td>{{ row.predicted_applications }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <template #col-week="{ item }">{{ item.week_start }}</template>
          <template #col-actual="{ item }">{{ item.applications ?? '—' }}</template>
          <template #col-predicted="{ item }">{{ item.predicted_applications ?? '—' }}</template>
          </ResponsiveList>
        </div>
      </div>

      <div class="card mb-4">
        <div class="card-header">
          <h5 class="mb-0">{{ t('analyticsForecastsPage.bottlenecksHeading') }}</h5>
        </div>
        <div class="card-body">
          <p>
            {{ t('analyticsForecastsPage.pendingReview', { n: data.bottlenecks?.pending_review ?? 0 }) }}
            · {{ t('analyticsForecastsPage.aging', { n: data.bottlenecks?.aging_over_7_days ?? 0 }) }}
            · {{ t('analyticsForecastsPage.waitlisted', { n: data.bottlenecks?.waitlisted ?? 0 }) }}
          </p>
          <ResponsiveList
            :items="data.bottlenecks?.by_program || []"
            :columns="bottleneckMobileColumns"
            mobile-test-id="forecasts-bottlenecks-mobile"
          >
          <table class="table table-sm mb-0">
            <thead>
              <tr>
                <th>{{ t('analyticsForecastsPage.colProgram') }}</th>
                <th>{{ t('analyticsForecastsPage.colPending') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in data.bottlenecks?.by_program || []" :key="row.program_id">
                <td>{{ row.program_name }}</td>
                <td>{{ row.pending_count }}</td>
              </tr>
            </tbody>
          </table>
          <template #col-program="{ item }">{{ item.program_name }}</template>
          <template #col-pending="{ item }">{{ item.pending_count }}</template>
          </ResponsiveList>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h5 class="mb-0">{{ t('analyticsForecastsPage.deadlinesHeading') }}</h5>
        </div>
        <div class="card-body">
          <p v-if="!(data.deadline_risk || []).length" class="text-muted mb-0">
            {{ t('analyticsForecastsPage.noDeadlines') }}
          </p>
          <ResponsiveList
            v-else
            :items="data.deadline_risk"
            :columns="deadlineMobileColumns"
            mobile-test-id="forecasts-deadlines-mobile"
          >
          <table class="table table-sm mb-0">
            <thead>
              <tr>
                <th>{{ t('analyticsForecastsPage.colProgram') }}</th>
                <th>{{ t('analyticsForecastsPage.colDeadline') }}</th>
                <th>{{ t('analyticsForecastsPage.colDaysLeft') }}</th>
                <th>{{ t('analyticsForecastsPage.colDrafts') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in data.deadline_risk" :key="row.program_id">
                <td>{{ row.program_name }}</td>
                <td>{{ row.deadline }}</td>
                <td>{{ row.days_left }}</td>
                <td>{{ row.draft_applications }}</td>
              </tr>
            </tbody>
          </table>
          <template #col-program="{ item }">{{ item.program_name }}</template>
          <template #col-deadline="{ item }">{{ item.deadline }}</template>
          <template #col-daysLeft="{ item }">{{ item.days_left }}</template>
          <template #col-drafts="{ item }">{{ item.draft_applications }}</template>
          </ResponsiveList>
        </div>
      </div>
    </div>
    </PageStateShell>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import CompactFilterBar from '@/components/CompactFilterBar.vue'
import ResponsiveList from '@/components/ResponsiveList.vue'
import PageHeader from '@/components/PageHeader.vue'
import PageBreadcrumb from '@/components/PageBreadcrumb.vue'
import PageStateShell from '@/components/State/PageStateShell.vue'
import { useStaffSavedPresets } from '@/composables/useStaffSavedPresets'
import {
  STAFF_SAVED_SEARCH_TYPE,
  deserializeAnalyticsForecastFilters,
  serializeAnalyticsForecastFilters,
} from '@/utils/staffListSearchPresets'

const { t } = useI18n()
const loading = ref(true)
const error = ref('')
const data = ref(null)
const programs = ref([])
const programId = ref('')

const demandMobileColumns = computed(() => [
  { key: 'week', label: t('analyticsForecastsPage.colWeek') },
  { key: 'actual', label: t('analyticsForecastsPage.colActual') },
  { key: 'predicted', label: t('analyticsForecastsPage.colPredicted') },
])

const bottleneckMobileColumns = computed(() => [
  { key: 'program', label: t('analyticsForecastsPage.colProgram') },
  { key: 'pending', label: t('analyticsForecastsPage.colPending') },
])

const deadlineMobileColumns = computed(() => [
  { key: 'program', label: t('analyticsForecastsPage.colProgram') },
  { key: 'deadline', label: t('analyticsForecastsPage.colDeadline') },
  { key: 'daysLeft', label: t('analyticsForecastsPage.colDaysLeft') },
  { key: 'drafts', label: t('analyticsForecastsPage.colDrafts') },
])

const demandRows = computed(() => {
  if (!data.value?.demand) return []
  const history = (data.value.demand.history || []).map((row) => ({
    week_start: row.week_start,
    applications: row.applications,
    predicted_applications: null,
  }))
  const forecast = (data.value.demand.forecast || []).map((row) => ({
    week_start: row.week_start,
    applications: null,
    predicted_applications: row.predicted_applications,
  }))
  return [...history, ...forecast]
})

function clearFilters() {
  programId.value = ''
  loadForecasts()
}

const {
  savedPresets,
  newPresetName,
  saveAsDefault,
  presetsLoading,
  loadPresets,
  savePreset,
  deletePreset,
  setDefaultPreset,
} = useStaffSavedPresets(STAFF_SAVED_SEARCH_TYPE.ANALYTICS_FORECAST)

async function loadPrograms() {
  const { data: payload } = await api.get('/api/programs/', { params: { page_size: 100, ordering: 'name' } })
  programs.value = payload.results ?? payload ?? []
}

async function loadForecasts() {
  loading.value = true
  error.value = ''
  try {
    const params = {}
    if (programId.value) params.program = programId.value
    const { data: payload } = await api.get('/api/admin/dashboard/forecasts/', { params })
    data.value = payload
  } catch {
    error.value = t('analyticsForecastsPage.loadError')
  } finally {
    loading.value = false
  }
}

function applyPreset(p) {
  const f = deserializeAnalyticsForecastFilters(p.filters)
  programId.value = f.program || ''
  loadForecasts()
}

onMounted(async () => {
  await loadPrograms()
  await loadPresets()
  const def = savedPresets.value.find((p) => p.is_default)
  if (def) applyPreset(def)
  else await loadForecasts()
})
</script>
