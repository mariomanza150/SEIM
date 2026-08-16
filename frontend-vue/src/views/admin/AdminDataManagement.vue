<template>
  <div class="admin-data-management-page">
    <PageHeader :title="t('adminData.title')" :subtitle="t('adminData.subtitle')">
      <template #breadcrumb>
        <nav aria-label="Breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item">
              <router-link :to="{ name: 'Dashboard' }">{{ t('route.names.Dashboard') }}</router-link>
            </li>
            <li class="breadcrumb-item active">{{ t('route.names.AdminDataManagement') }}</li>
          </ol>
        </nav>
      </template>
      <template #actions>
        <button type="button" class="btn btn-outline-secondary" :disabled="loading" @click="load">
          <i class="bi bi-arrow-clockwise me-1" aria-hidden="true"></i>{{ t('adminCommon.refresh') }}
        </button>
      </template>
    </PageHeader>

    <p class="text-muted">{{ t('adminData.sessionNote') }}</p>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">{{ t('adminCommon.loading') }}</span>
      </div>
    </div>
    <div v-else-if="error" class="alert alert-danger" role="alert">{{ error }}</div>
    <div v-else class="row g-3 mb-4">
      <div v-for="section in sections" :key="section.key" class="col-md-6 col-xl-4">
        <div class="card h-100">
          <div class="card-body d-flex flex-column">
            <h2 class="h5">{{ section.title }}</h2>
            <p class="text-muted flex-grow-1">{{ section.description }}</p>
            <a class="btn btn-primary" :href="section.url" data-testid="data-management-tool">
              {{ t('adminData.openTool') }}
            </a>
          </div>
        </div>
      </div>
      <div v-if="!sections.length" class="col-12">
        <p class="text-muted">{{ t('adminData.empty') }}</p>
      </div>
    </div>

    <div class="card">
      <div class="card-header">{{ t('adminData.recentLogs') }}</div>
      <div class="table-responsive">
        <table class="table table-sm mb-0" data-testid="data-management-logs">
          <thead>
            <tr>
              <th>{{ t('adminData.logType') }}</th>
              <th>{{ t('adminData.logModel') }}</th>
              <th>{{ t('adminData.logStatus') }}</th>
              <th>{{ t('adminData.logUser') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in logs" :key="log.id">
              <td>{{ log.operation_type }}</td>
              <td>{{ log.model_name }}</td>
              <td>{{ log.status }}</td>
              <td>{{ log.user || '—' }}</td>
            </tr>
            <tr v-if="!logs.length">
              <td colspan="4" class="text-muted">{{ t('adminData.noLogs') }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import PageHeader from '@/components/PageHeader.vue'
import api from '@/services/api'

const { t } = useI18n()
const loading = ref(true)
const error = ref(null)
const sections = ref([])
const logs = ref([])

async function load() {
  loading.value = true
  error.value = null
  try {
    const [catalogRes, logsRes] = await Promise.all([
      api.get('/api/data-management/catalog/'),
      api.get('/api/data-management/logs/'),
    ])
    sections.value = catalogRes.data.sections || []
    logs.value = logsRes.data.results || []
  } catch (err) {
    error.value = t('adminData.loadError')
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>
