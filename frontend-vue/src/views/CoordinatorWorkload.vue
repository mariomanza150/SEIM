<template>
  <div class="coordinator-workload-page">
    <div class="container-fluid mt-4">
      <nav :aria-label="t('workloadPage.breadcrumbAria')">
        <ol class="breadcrumb">
          <li class="breadcrumb-item">
            <router-link :to="{ name: 'Dashboard' }">{{ t('route.names.Dashboard') }}</router-link>
          </li>
          <li class="breadcrumb-item active">{{ t('route.names.CoordinatorWorkload') }}</li>
        </ol>
      </nav>

      <div class="row mb-4">
        <div class="col-md-8">
          <h2>
            <i class="bi bi-graph-up-arrow me-2"></i>{{ t('route.names.CoordinatorWorkload') }}
          </h2>
          <p class="text-muted mb-0">
            {{ t('workloadPage.pageSubtitleBefore') }}<strong>{{ t('workloadPage.pageSubtitleStatusSubmitted') }}</strong
            >{{ t('workloadPage.pageSubtitleOr') }}<strong>{{ t('workloadPage.pageSubtitleStatusUnderReview') }}</strong
            >{{ t('workloadPage.pageSubtitleAfter') }}
          </p>
        </div>
        <div class="col-md-4 text-md-end mt-2 mt-md-0">
          <router-link :to="{ name: 'CoordinatorReviewQueue' }" class="btn btn-outline-primary">
            <i class="bi bi-clipboard-check me-1"></i>{{ t('route.names.CoordinatorReviewQueue') }}
          </router-link>
        </div>
      </div>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">{{ t('workloadPage.loading') }}</span>
        </div>
      </div>
      <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
      <template v-else-if="data">
        <h3 class="h5 mb-3">{{ t('workloadPage.yourWorkload') }}</h3>
        <div class="row g-3 mb-4">
          <div class="col-md-6 col-xl-3">
            <div class="card h-100 border-0 shadow-sm">
              <div class="card-body">
                <div class="text-muted small">{{ t('workloadPage.assignedToYou') }}</div>
                <div class="display-6 fw-semibold">{{ data.you.assigned_pending_review }}</div>
              </div>
            </div>
          </div>
          <div class="col-md-6 col-xl-3">
            <div class="card h-100 border-0 shadow-sm">
              <div class="card-body">
                <div class="text-muted small">{{ t('workloadPage.yourProgramsAnyCoordinator') }}</div>
                <div class="display-6 fw-semibold">{{ data.you.coordinated_programs_pending }}</div>
              </div>
            </div>
          </div>
          <div class="col-md-6 col-xl-3">
            <div class="card h-100 border-0 shadow-sm">
              <div class="card-body">
                <div class="text-muted small">{{ t('workloadPage.assignedOpenResubmit') }}</div>
                <div class="display-6 fw-semibold">{{ data.you.assigned_with_open_resubmit }}</div>
              </div>
            </div>
          </div>
          <div class="col-md-6 col-xl-3">
            <div class="card h-100 border-0 shadow-sm">
              <div class="card-body">
                <div class="text-muted small">{{ t('workloadPage.avgDaysInQueue') }}</div>
                <div class="display-6 fw-semibold">
                  {{ data.you.avg_days_in_queue_assigned ?? t('workloadPage.emDash') }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <template v-if="data.global">
          <h3 class="h5 mb-3">{{ t('workloadPage.institutionOverview') }}</h3>
          <div class="row g-3 mb-4">
            <div class="col-md-4">
              <div class="card border-0 shadow-sm">
                <div class="card-body">
                  <div class="text-muted small">{{ t('workloadPage.totalPendingReview') }}</div>
                  <div class="fs-3 fw-semibold">{{ data.global.pending_review_total }}</div>
                </div>
              </div>
            </div>
            <div class="col-md-4">
              <div class="card border-0 shadow-sm">
                <div class="card-body">
                  <div class="text-muted small">{{ t('workloadPage.unassignedCoordinator') }}</div>
                  <div class="fs-3 fw-semibold">{{ data.global.unassigned_pending_review }}</div>
                </div>
              </div>
            </div>
            <div class="col-md-4">
              <div class="card border-0 shadow-sm">
                <div class="card-body">
                  <div class="text-muted small">{{ t('workloadPage.staleUnderReview14d') }}</div>
                  <div class="fs-3 fw-semibold text-warning">{{ data.global.stale_under_review_14d }}</div>
                </div>
              </div>
            </div>
          </div>

          <div class="card border-0 shadow-sm mb-4">
            <div class="card-header bg-light">
              <span class="fw-semibold">{{ t('workloadPage.pendingByCoordinator') }}</span>
            </div>
            <div class="table-responsive">
              <table class="table table-hover mb-0">
                <thead class="table-light">
                  <tr>
                    <th>{{ t('workloadPage.colCoordinator') }}</th>
                    <th class="text-end">{{ t('workloadPage.colAssignedPending') }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="!data.distribution.length">
                    <td colspan="2" class="text-muted small">{{ t('workloadPage.distributionEmpty') }}</td>
                  </tr>
                  <template v-else>
                    <tr v-for="row in data.distribution" :key="row.coordinator_id">
                      <td>{{ row.display_name }}</td>
                      <td class="text-end">{{ row.assigned_pending_review }}</td>
                    </tr>
                  </template>
                </tbody>
              </table>
            </div>
          </div>
        </template>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useToast } from '@/composables/useToast'

const { t } = useI18n()
const { error: errorToast } = useToast()
const loading = ref(true)
const error = ref('')
const data = ref(null)

onMounted(async () => {
  try {
    const { data: body } = await api.get('/api/accounts/dashboard/coordinator-workload/')
    data.value = body
  } catch (e) {
    console.error(e)
    error.value = t('workloadPage.loadError')
    errorToast(error.value)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.coordinator-workload-page {
  min-height: 100vh;
  background-color: var(--seim-app-bg, #f8f9fa);
}
</style>
