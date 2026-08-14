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

const { t } = useI18n()
const loading = ref(true)
const error = ref('')
const data = ref(null)

onMounted(async () => {
  loading.value = true
  try {
    const { data: payload } = await api.get('/api/admin/dashboard/forecasts/')
    data.value = payload
  } catch {
    error.value = t('analyticsForecastsPage.loadError')
  } finally {
    loading.value = false
  }
})
</script>
