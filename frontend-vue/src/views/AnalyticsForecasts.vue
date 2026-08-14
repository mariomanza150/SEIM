<template>
  <div class="analytics-forecasts-page">
    <PageHeader :title="t('route.names.AnalyticsForecasts')" :subtitle="t('analyticsForecastsPage.subtitle')">
      <template #breadcrumb>
        <nav :aria-label="t('exchangeAgreementsPage.breadcrumbAria')">
          <ol class="breadcrumb">
            <li class="breadcrumb-item">
              <router-link :to="{ name: 'Dashboard' }">{{ t('route.names.Dashboard') }}</router-link>
            </li>
            <li class="breadcrumb-item active">{{ t('route.names.AnalyticsForecasts') }}</li>
          </ol>
        </nav>
      </template>
    </PageHeader>

    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3 align-items-end">
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
        </div>
        <div class="border-top pt-3 mt-3">
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
        </div>
      </div>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"></div>
    </div>
    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-else-if="data" data-testid="analytics-forecasts-page">
      <div class="card mb-4">
        <div class="card-header">
          <h5 class="mb-0">{{ t('analyticsForecastsPage.demandHeading') }}</h5>
        </div>
        <div class="card-body">
          <p class="text-muted">{{ t('analyticsForecastsPage.trend', { n: data.demand?.trend_per_week ?? 0 }) }}</p>
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
          <table v-else class="table table-sm mb-0">
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
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import PageHeader from '@/components/PageHeader.vue'
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
  const { data: payload } = await api.get('/api/programs/', { params: { page_size: 200, ordering: 'name' } })
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
