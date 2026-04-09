<template>
  <div class="coordinator-workload-page">
    <div class="container-fluid mt-4">
      <nav aria-label="breadcrumb">
        <ol class="breadcrumb">
          <li class="breadcrumb-item">
            <router-link :to="{ name: 'Dashboard' }">Dashboard</router-link>
          </li>
          <li class="breadcrumb-item active">Coordinator workload</li>
        </ol>
      </nav>

      <div class="row mb-4">
        <div class="col-md-8">
          <h2><i class="bi bi-graph-up-arrow me-2"></i>Coordinator workload</h2>
          <p class="text-muted mb-0">
            Queue depth for applications in <strong>submitted</strong> or <strong>under review</strong>, plus simple bottleneck signals.
          </p>
        </div>
        <div class="col-md-4 text-md-end mt-2 mt-md-0">
          <router-link :to="{ name: 'CoordinatorReviewQueue' }" class="btn btn-outline-primary">
            <i class="bi bi-clipboard-check me-1"></i>Review queue
          </router-link>
        </div>
      </div>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading…</span>
        </div>
      </div>
      <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
      <template v-else-if="data">
        <h3 class="h5 mb-3">Your workload</h3>
        <div class="row g-3 mb-4">
          <div class="col-md-6 col-xl-3">
            <div class="card h-100 border-0 shadow-sm">
              <div class="card-body">
                <div class="text-muted small">Assigned to you</div>
                <div class="display-6 fw-semibold">{{ data.you.assigned_pending_review }}</div>
              </div>
            </div>
          </div>
          <div class="col-md-6 col-xl-3">
            <div class="card h-100 border-0 shadow-sm">
              <div class="card-body">
                <div class="text-muted small">Your programs (any coordinator)</div>
                <div class="display-6 fw-semibold">{{ data.you.coordinated_programs_pending }}</div>
              </div>
            </div>
          </div>
          <div class="col-md-6 col-xl-3">
            <div class="card h-100 border-0 shadow-sm">
              <div class="card-body">
                <div class="text-muted small">Assigned + open resubmit</div>
                <div class="display-6 fw-semibold">{{ data.you.assigned_with_open_resubmit }}</div>
              </div>
            </div>
          </div>
          <div class="col-md-6 col-xl-3">
            <div class="card h-100 border-0 shadow-sm">
              <div class="card-body">
                <div class="text-muted small">Avg. days in queue (assigned)</div>
                <div class="display-6 fw-semibold">
                  {{ data.you.avg_days_in_queue_assigned ?? '—' }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <template v-if="data.global">
          <h3 class="h5 mb-3">Institution overview (admin)</h3>
          <div class="row g-3 mb-4">
            <div class="col-md-4">
              <div class="card border-0 shadow-sm">
                <div class="card-body">
                  <div class="text-muted small">Total pending review</div>
                  <div class="fs-3 fw-semibold">{{ data.global.pending_review_total }}</div>
                </div>
              </div>
            </div>
            <div class="col-md-4">
              <div class="card border-0 shadow-sm">
                <div class="card-body">
                  <div class="text-muted small">Unassigned coordinator</div>
                  <div class="fs-3 fw-semibold">{{ data.global.unassigned_pending_review }}</div>
                </div>
              </div>
            </div>
            <div class="col-md-4">
              <div class="card border-0 shadow-sm">
                <div class="card-body">
                  <div class="text-muted small">Stale under review (&gt;14 days)</div>
                  <div class="fs-3 fw-semibold text-warning">{{ data.global.stale_under_review_14d }}</div>
                </div>
              </div>
            </div>
          </div>

          <div class="card border-0 shadow-sm mb-4">
            <div class="card-header bg-light">
              <span class="fw-semibold">Pending by assigned coordinator</span>
            </div>
            <div class="table-responsive">
              <table class="table table-hover mb-0">
                <thead class="table-light">
                  <tr>
                    <th>Coordinator</th>
                    <th class="text-end">Assigned pending</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="row in data.distribution" :key="row.coordinator_id">
                    <td>{{ row.display_name }}</td>
                    <td class="text-end">{{ row.assigned_pending_review }}</td>
                  </tr>
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
import api from '@/services/api'
import { useToast } from '@/composables/useToast'

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
    error.value = 'Could not load workload data.'
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
