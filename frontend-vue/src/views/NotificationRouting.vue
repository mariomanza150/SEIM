<template>
  <div class="notification-routing-page">
    <div class="container-fluid mt-4">
      <nav :aria-label="t('notificationRoutingPage.breadcrumbAria')">
        <ol class="breadcrumb">
          <li class="breadcrumb-item">
            <router-link :to="{ name: 'Dashboard' }">{{ t('route.names.Dashboard') }}</router-link>
          </li>
          <li class="breadcrumb-item active">{{ t('route.names.NotificationRouting') }}</li>
        </ol>
      </nav>

      <div class="row mb-4">
        <div class="col-md-8">
          <h2>
            <i class="bi bi-diagram-3 me-2"></i>{{ t('route.names.NotificationRouting') }}
          </h2>
          <p class="text-muted mb-0">{{ t('notificationRoutingPage.subtitle') }}</p>
        </div>
        <div class="col-md-4 text-md-end mt-2 mt-md-0">
          <router-link :to="{ name: 'Settings' }" class="btn btn-outline-primary">
            <i class="bi bi-gear me-1"></i>{{ t('route.names.Settings') }}
          </router-link>
        </div>
      </div>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">{{ t('notificationRoutingPage.loading') }}</span>
        </div>
      </div>
      <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
      <template v-else-if="payload">
        <p class="small text-muted mb-3">
          {{ t('notificationRoutingPage.schemaVersion') }}:
          <span class="badge bg-secondary">{{ payload.schema_version }}</span>
        </p>

        <div class="card border-0 shadow-sm mb-4">
          <div class="card-header bg-light">
            <span class="fw-semibold">{{ t('notificationRoutingPage.categoriesTitle') }}</span>
          </div>
          <div class="table-responsive">
            <table class="table table-hover mb-0">
              <thead class="table-light">
                <tr>
                  <th scope="col">{{ t('notificationRoutingPage.colCategory') }}</th>
                  <th scope="col">{{ t('notificationRoutingPage.colEmailField') }}</th>
                  <th scope="col">{{ t('notificationRoutingPage.colInappField') }}</th>
                  <th scope="col">{{ t('notificationRoutingPage.colTypicalTriggers') }}</th>
                  <th scope="col">{{ t('notificationRoutingPage.colPrimaryRecipients') }}</th>
                  <th scope="col">{{ t('notificationRoutingPage.colNotes') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in categoryRows" :key="row.key">
                  <td><code>{{ row.key }}</code></td>
                  <td><code>{{ row.email_user_settings_field }}</code></td>
                  <td><code>{{ row.inapp_user_settings_field }}</code></td>
                  <td class="small text-muted">{{ row.typicalTriggers || t('notificationRoutingPage.emDash') }}</td>
                  <td class="small text-muted">{{ row.primaryRecipients || t('notificationRoutingPage.emDash') }}</td>
                  <td class="small text-muted">{{ row.notes || t('notificationRoutingPage.emDash') }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div
          v-if="payload.transactional_routes?.length"
          class="card border-0 shadow-sm mb-4"
        >
          <div class="card-header bg-light">
            <span class="fw-semibold">{{ t('notificationRoutingPage.transactionalRoutesTitle') }}</span>
          </div>
          <div class="card-body small text-muted border-bottom">
            {{ t('notificationRoutingPage.transactionalRoutesIntro') }}
          </div>
          <div class="table-responsive">
            <table class="table table-hover mb-0">
              <thead class="table-light">
                <tr>
                  <th scope="col">{{ t('notificationRoutingPage.colRouteKey') }}</th>
                  <th scope="col">{{ t('notificationRoutingPage.colSettingsCategory') }}</th>
                  <th scope="col">{{ t('notificationRoutingPage.colRouteSummary') }}</th>
                  <th scope="col">{{ t('notificationRoutingPage.colRouteSource') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in transactionalRows" :key="row.route_key">
                  <td><code>{{ row.route_key }}</code></td>
                  <td>
                    <code v-if="row.settings_category != null">{{ row.settings_category }}</code>
                    <span v-else class="text-muted">{{ t('notificationRoutingPage.emDash') }}</span>
                  </td>
                  <td class="small text-muted">{{ row.summary }}</td>
                  <td class="small text-muted font-monospace">{{ row.source }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="card border-0 shadow-sm mb-4">
          <div class="card-header bg-light">
            <span class="fw-semibold">{{ t('notificationRoutingPage.remindersTitle') }}</span>
          </div>
          <div class="table-responsive">
            <table class="table table-hover mb-0">
              <thead class="table-light">
                <tr>
                  <th scope="col">{{ t('notificationRoutingPage.colReminderEventType') }}</th>
                  <th scope="col">{{ t('notificationRoutingPage.colSettingsCategory') }}</th>
                  <th scope="col">{{ t('notificationRoutingPage.colReminderDescription') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in reminderRows" :key="row.eventType">
                  <td><code>{{ row.eventType }}</code></td>
                  <td><code>{{ row.category }}</code></td>
                  <td class="small text-muted">{{ row.description || t('notificationRoutingPage.emDash') }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="card-footer small text-muted bg-white">
            {{ t('notificationRoutingPage.reminderDefault') }}:
            <code>{{ payload.reminder_default_settings_category }}</code>
          </div>
        </div>

        <div v-if="payload.digest" class="card border-0 shadow-sm mb-4">
          <div class="card-header bg-light">
            <span class="fw-semibold">{{ t('notificationRoutingPage.digestTitle') }}</span>
          </div>
          <div class="card-body">
            <dl class="row mb-0 small">
              <dt class="col-sm-3">{{ t('notificationRoutingPage.digestCategory') }}</dt>
              <dd class="col-sm-9"><code>{{ payload.digest.settings_category }}</code></dd>
              <dt class="col-sm-3">{{ t('notificationRoutingPage.digestEmailGates') }}</dt>
              <dd class="col-sm-9">
                <code v-for="g in payload.digest.email_gates" :key="g" class="me-2 d-inline-block">{{ g }}</code>
              </dd>
              <dt class="col-sm-3">{{ t('notificationRoutingPage.digestInappField') }}</dt>
              <dd class="col-sm-9"><code>{{ payload.digest.inapp_user_settings_field }}</code></dd>
              <template v-if="payload.digest.typical_triggers">
                <dt class="col-sm-3">{{ t('notificationRoutingPage.digestTypicalTriggers') }}</dt>
                <dd class="col-sm-9 text-muted">{{ payload.digest.typical_triggers }}</dd>
              </template>
            </dl>
          </div>
        </div>

        <div v-if="payload.reference_api_access" class="card border-0 shadow-sm mb-4">
          <div class="card-header bg-light">
            <span class="fw-semibold">{{ t('notificationRoutingPage.apiAccessTitle') }}</span>
          </div>
          <div class="card-body small">
            <p class="text-muted mb-2">{{ payload.reference_api_access.description }}</p>
            <div v-if="payload.reference_api_access.roles_any?.length" class="mb-1">
              <span class="text-muted me-2">{{ t('notificationRoutingPage.apiAccessRoles') }}</span>
              <code v-for="r in payload.reference_api_access.roles_any" :key="r" class="me-1">{{ r }}</code>
            </div>
            <p v-if="payload.reference_api_access.superuser" class="mb-0 text-muted">
              {{ t('notificationRoutingPage.apiAccessSuperuser') }}
            </p>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useToast } from '@/composables/useToast'

const { t } = useI18n()
const { error: errorToast } = useToast()
const loading = ref(true)
const error = ref('')
const payload = ref(null)

const categoryRows = computed(() => {
  const cats = payload.value?.settings_categories
  if (!cats || typeof cats !== 'object') return []
  return Object.keys(cats)
    .sort((a, b) => a.localeCompare(b))
    .map((key) => ({
      key,
      email_user_settings_field: cats[key].email_user_settings_field,
      inapp_user_settings_field: cats[key].inapp_user_settings_field,
      typicalTriggers: cats[key].typical_triggers || '',
      primaryRecipients: cats[key].primary_recipients || '',
      notes: cats[key].notes || '',
    }))
})

const transactionalRows = computed(() => {
  const rows = payload.value?.transactional_routes
  if (!Array.isArray(rows)) return []
  return [...rows].sort((a, b) =>
    String(a.route_key).localeCompare(String(b.route_key)),
  )
})

const reminderRows = computed(() => {
  const m = payload.value?.reminder_event_type_to_settings_category
  if (!m || typeof m !== 'object') return []
  const desc = payload.value?.reminder_event_type_descriptions || {}
  return Object.keys(m)
    .sort((a, b) => a.localeCompare(b))
    .map((eventType) => ({
      eventType,
      category: m[eventType],
      description: desc[eventType] || '',
    }))
})

onMounted(async () => {
  try {
    const { data } = await api.get('/api/notifications/routing-reference/')
    payload.value = data
  } catch (e) {
    const status = e?.response?.status
    if (status === 403) {
      error.value = t('notificationRoutingPage.forbidden')
    } else {
      console.error(e)
      error.value = t('notificationRoutingPage.loadError')
    }
    errorToast(error.value)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.notification-routing-page {
  min-height: 100vh;
  background-color: var(--seim-app-bg, #f8f9fa);
}
</style>
