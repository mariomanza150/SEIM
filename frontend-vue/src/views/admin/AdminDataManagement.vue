<template>
  <div class="admin-data-management-page">
    <PageHeader :title="t('adminData.title')" :subtitle="t('adminData.subtitle')">
      <template #breadcrumb>
        <PageBreadcrumb
          :aria-label="t('adminCommon.breadcrumbAria')"
          :items="[
            { to: { name: 'Dashboard' }, label: t('route.names.Dashboard') },
            { label: t('route.names.AdminDataManagement') },
          ]"
        />
      </template>
      <template #actions>
        <button type="button" class="btn btn-outline-secondary" :disabled="loading" @click="load">
          <i class="bi bi-arrow-clockwise me-1" aria-hidden="true"></i>{{ t('adminCommon.refresh') }}
        </button>
      </template>
    </PageHeader>

    <PageStateShell
      :loading="loading"
      :error="error || ''"
      skeleton="none"
      :loading-label="t('adminCommon.loading')"
    >
      <div class="row g-3 mb-4">
        <div v-for="section in sections" :key="section.key" class="col-md-6 col-xl-4">
          <button
            type="button"
            class="card h-100 w-100 text-start"
            :class="{ 'border-primary': selectedSection === section.key }"
            data-testid="data-management-tool"
            @click="selectSection(section.key)"
          >
            <div class="card-body">
              <h2 class="h5">{{ section.title }}</h2>
              <p class="text-muted mb-0">{{ section.description }}</p>
            </div>
          </button>
        </div>
        <div v-if="!sections.length" class="col-12">
          <p class="text-muted">{{ t('adminData.empty') }}</p>
        </div>
      </div>

      <div v-if="selectedSection" class="card mb-4" data-testid="data-management-console">
        <div class="card-header d-flex justify-content-between align-items-center">
          <span>{{ currentSection?.title || selectedSection }}</span>
          <span v-if="actionMessage" class="small text-success">{{ actionMessage }}</span>
        </div>
        <div class="card-body">
          <div v-if="actionError" class="alert alert-danger">{{ actionError }}</div>

          <div v-if="selectedSection === 'database'">
            <p>{{ t('adminData.resetHelp') }}</p>
            <label class="form-label">{{ t('adminData.resetConfirmLabel') }}</label>
            <input v-model="resetConfirm" class="form-control mb-3" type="text" data-testid="data-reset-confirm" />
            <button type="button" class="btn btn-danger" :disabled="running" data-testid="data-reset-run" @click="runReset">
              {{ t('adminData.runReset') }}
            </button>
          </div>

          <div v-else-if="selectedSection === 'data_cleanup'">
            <div class="form-check">
              <input id="cleanOrphaned" v-model="cleanup.clean_orphaned" class="form-check-input" type="checkbox" />
              <label class="form-check-label" for="cleanOrphaned">{{ t('adminData.cleanOrphaned') }}</label>
            </div>
            <div class="form-check">
              <input id="cleanDuplicates" v-model="cleanup.clean_duplicates" class="form-check-input" type="checkbox" />
              <label class="form-check-label" for="cleanDuplicates">{{ t('adminData.cleanDuplicates') }}</label>
            </div>
            <div class="form-check mb-3">
              <input id="cleanInvalid" v-model="cleanup.clean_invalid" class="form-check-input" type="checkbox" />
              <label class="form-check-label" for="cleanInvalid">{{ t('adminData.cleanInvalid') }}</label>
            </div>
            <button type="button" class="btn btn-primary" :disabled="running" data-testid="data-cleanup-run" @click="runCleanup">
              {{ t('adminData.runCleanup') }}
            </button>
          </div>

          <div v-else>
            <div v-if="resourcesLoading" class="text-muted">{{ t('adminCommon.loading') }}</div>
            <div v-else-if="!items.length" class="text-muted">{{ t('adminData.noItems') }}</div>
            <div v-else class="table-responsive">
              <ResponsiveList :items="items" :columns="itemMobileColumns" mobile-test-id="data-management-items-mobile">
              <table class="table align-middle mb-0" data-testid="data-management-items">
                <thead>
                  <tr>
                    <th>{{ t('adminData.itemName') }}</th>
                    <th>{{ t('adminData.itemDetail') }}</th>
                    <th v-if="selectedSection === 'data_import'">{{ t('adminData.file') }}</th>
                    <th class="text-end">{{ t('adminCommon.actions') }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in items" :key="item.id">
                    <td>
                      <div class="fw-medium">{{ item.name }}</div>
                      <div class="small text-muted">{{ item.description }}</div>
                    </td>
                    <td class="small">{{ item.format || item.operation_type || item.model_name || '—' }}</td>
                    <td v-if="selectedSection === 'data_import'">
                      <input
                        class="form-control form-control-sm"
                        type="file"
                        :data-testid="`data-import-file-${item.id}`"
                        @change="onFileChange(item.id, $event)"
                      />
                    </td>
                    <td class="text-end">
                      <button
                        type="button"
                        class="btn btn-sm btn-primary"
                        :disabled="running"
                        data-testid="data-execute"
                        @click="runItem(item)"
                      >
                        {{ t('adminData.execute') }}
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
              <template #col-name="{ item }">
                <div class="fw-medium">{{ item.name }}</div>
                <div class="small text-muted">{{ item.description }}</div>
              </template>
              <template #col-detail="{ item }">{{ item.format || item.operation_type || item.model_name || '—' }}</template>
              <template v-if="selectedSection === 'data_import'" #col-file="{ item }">
                <input
                  class="form-control form-control-sm"
                  type="file"
                  :data-testid="`data-import-file-${item.id}`"
                  @change="onFileChange(item.id, $event)"
                />
              </template>
              <template #actions="{ item }">
                <button
                  type="button"
                  class="btn btn-sm btn-primary"
                  :disabled="running"
                  data-testid="data-execute"
                  @click="runItem(item)"
                >
                  {{ t('adminData.execute') }}
                </button>
              </template>
              </ResponsiveList>
            </div>
          </div>
        </div>
      </div>

    <div class="card">
      <div class="card-header">{{ t('adminData.recentLogs') }}</div>
      <ResponsiveList :items="logs" :columns="logMobileColumns" mobile-test-id="data-management-logs-mobile">
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
          </tbody>
        </table>
      </div>
      <template #col-operation_type="{ item }">{{ item.operation_type }}</template>
      <template #col-model_name="{ item }">{{ item.model_name }}</template>
      <template #col-status="{ item }">{{ item.status }}</template>
      <template #col-user="{ item }">{{ item.user || '—' }}</template>
      </ResponsiveList>
    </div>
    </PageStateShell>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import PageHeader from '@/components/PageHeader.vue'
import PageBreadcrumb from '@/components/PageBreadcrumb.vue'
import PageStateShell from '@/components/State/PageStateShell.vue'
import ResponsiveList from '@/components/ResponsiveList.vue'
import api from '@/services/api'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const loading = ref(true)
const resourcesLoading = ref(false)
const running = ref(false)
const error = ref(null)
const actionError = ref(null)
const actionMessage = ref('')
const sections = ref([])
const logs = ref([])
const items = ref([])
const files = ref({})
const resetConfirm = ref('')
const cleanup = ref({
  clean_orphaned: false,
  clean_duplicates: false,
  clean_invalid: false,
})

const selectedSection = computed(() => String(route.query.section || ''))
const currentSection = computed(() => sections.value.find((row) => row.key === selectedSection.value))

const itemMobileColumns = computed(() => {
  const cols = [
    { key: 'name', label: t('adminData.itemName') },
    { key: 'detail', label: t('adminData.itemDetail') },
  ]
  if (selectedSection.value === 'data_import') {
    cols.push({ key: 'file', label: t('adminData.file') })
  }
  return cols
})

const logMobileColumns = computed(() => [
  { key: 'operation_type', label: t('adminData.logType') },
  { key: 'model_name', label: t('adminData.logModel') },
  { key: 'status', label: t('adminData.logStatus') },
  { key: 'user', label: t('adminData.logUser') },
])

function selectSection(key) {
  router.replace({ query: { ...route.query, section: key } })
}

function onFileChange(id, event) {
  files.value = { ...files.value, [id]: event.target.files?.[0] || null }
}

async function loadLogs() {
  const logsRes = await api.get('/api/data-management/logs/')
  logs.value = logsRes.data.results || []
}

async function loadResources(section) {
  if (!section || section === 'database' || section === 'data_cleanup') {
    items.value = []
    return
  }
  resourcesLoading.value = true
  try {
    const response = await api.get('/api/data-management/resources/', { params: { section } })
    items.value = response.data.results || []
  } catch {
    items.value = []
    actionError.value = t('adminData.resourcesError')
  } finally {
    resourcesLoading.value = false
  }
}

async function load() {
  loading.value = true
  error.value = null
  try {
    const catalogRes = await api.get('/api/data-management/catalog/')
    sections.value = catalogRes.data.sections || []
    await loadLogs()
    if (!selectedSection.value && sections.value[0]) {
      selectSection(sections.value[0].key)
    } else if (selectedSection.value) {
      await loadResources(selectedSection.value)
    }
  } catch {
    error.value = t('adminData.loadError')
  } finally {
    loading.value = false
  }
}

async function runExecute(payload, { multipart = false } = {}) {
  running.value = true
  actionError.value = null
  actionMessage.value = ''
  try {
    const response = multipart
      ? await api.post('/api/data-management/execute/', payload, {
          headers: { 'Content-Type': 'multipart/form-data' },
        })
      : await api.post('/api/data-management/execute/', payload)
    actionMessage.value = response.data.message || t('adminData.queued')
    await loadLogs()
  } catch (err) {
    actionError.value = err.response?.data?.detail || t('adminData.executeError')
  } finally {
    running.value = false
  }
}

async function runItem(item) {
  if (selectedSection.value === 'data_import') {
    const file = files.value[item.id]
    if (!file) {
      actionError.value = t('adminData.fileRequired')
      return
    }
    const formData = new FormData()
    formData.append('section', 'data_import')
    formData.append('item_id', item.id)
    formData.append('file', file)
    await runExecute(formData, { multipart: true })
    return
  }
  await runExecute({ section: selectedSection.value, item_id: item.id })
}

async function runReset() {
  await runExecute({ section: 'database', confirm: resetConfirm.value })
}

async function runCleanup() {
  await runExecute({ section: 'data_cleanup', cleanup_options: cleanup.value })
}

watch(
  () => route.query.section,
  (section) => {
    actionError.value = null
    actionMessage.value = ''
    if (section) loadResources(String(section))
  },
)

onMounted(load)
</script>

<style scoped>
button.card {
  background: var(--bs-body-bg);
}
</style>
