<template>
  <div class="coordinator-workload-page">
    <PageHeader
      :title="t('route.names.CoordinatorWorkload')"
      icon-class="bi bi-graph-up-arrow"
    >
      <template #breadcrumb>
        <PageBreadcrumb
          :aria-label="t('workloadPage.breadcrumbAria')"
          :items="[
            { to: { name: 'Dashboard' }, label: t('route.names.Dashboard') },
            { label: t('route.names.CoordinatorWorkload') },
          ]"
        />
      </template>
      <template #subtitle>
        {{ t('workloadPage.pageSubtitleBefore') }}<strong>{{ t('workloadPage.pageSubtitleStatusSubmitted') }}</strong
        >{{ t('workloadPage.pageSubtitleOr') }}<strong>{{ t('workloadPage.pageSubtitleStatusUnderReview') }}</strong
        >{{ t('workloadPage.pageSubtitleAfter') }}
      </template>
      <template #actions>
        <router-link :to="{ name: 'CoordinatorReviewQueue' }" class="btn btn-outline-primary">
          <i class="bi bi-clipboard-check me-1" aria-hidden="true"></i>{{ t('route.names.CoordinatorReviewQueue') }}
        </router-link>
      </template>
    </PageHeader>

    <PageStateShell
      :loading="loading"
      :error="error"
      :loading-label="t('workloadPage.loading')"
      skeleton="stats"
      :skeleton-count="4"
    >
      <template v-if="data">
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
            <div class="card-header seim-surface-muted">
              <span class="fw-semibold">{{ t('workloadPage.pendingByCoordinator') }}</span>
            </div>
            <ResponsiveList
              :items="data.distribution"
              :columns="distributionColumns"
              item-key="coordinator_id"
              mobile-test-id="workload-distribution"
            >
              <div class="table-responsive">
                <table class="table table-hover mb-0">
                  <thead class="seim-table-head">
                    <tr>
                      <th>{{ t('workloadPage.colCoordinator') }}</th>
                      <th class="text-end">{{ t('workloadPage.colAssignedPending') }}</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-if="!data.distribution.length">
                      <td colspan="2" class="text-muted small">{{ t('workloadPage.distributionEmpty') }}</td>
                    </tr>
                    <tr v-for="row in data.distribution" :key="row.coordinator_id">
                      <td>{{ row.display_name }}</td>
                      <td class="text-end">{{ row.assigned_pending_review }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </ResponsiveList>
          </div>
        </template>
      </template>
    </PageStateShell>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useToast } from '@/composables/useToast'
import PageHeader from '@/components/PageHeader.vue'
import PageBreadcrumb from '@/components/PageBreadcrumb.vue'
import PageStateShell from '@/components/State/PageStateShell.vue'
import ResponsiveList from '@/components/ResponsiveList.vue'

const { t } = useI18n()
const { error: errorToast } = useToast()
const loading = ref(true)
const error = ref('')
const data = ref(null)

const distributionColumns = computed(() => [
  { key: 'display_name', label: t('workloadPage.colCoordinator') },
  { key: 'assigned_pending_review', label: t('workloadPage.colAssignedPending') },
])

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
