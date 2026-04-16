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
          <div class="card-header bg-light d-flex flex-wrap justify-content-between align-items-center gap-2">
            <span class="fw-semibold">{{ t('notificationRoutingPage.overridesTitle') }}</span>
            <span v-if="overridesLoading" class="spinner-border spinner-border-sm text-primary" role="status">
              <span class="visually-hidden">{{ t('notificationRoutingPage.overridesLoading') }}</span>
            </span>
          </div>
          <div class="card-body border-bottom">
            <p class="small text-muted mb-3">{{ t('notificationRoutingPage.overridesIntro') }}</p>
            <div v-if="overridesError" class="alert alert-warning">{{ overridesError }}</div>
            <form class="row g-3 align-items-end" @submit.prevent="submitOverrideForm">
              <div class="col-md-3">
                <label class="form-label" for="nr-override-kind">{{ t('notificationRoutingPage.formKind') }}</label>
                <select id="nr-override-kind" v-model="overrideForm.kind" class="form-select" required>
                  <option value="reminder_event_type">{{ t('notificationRoutingPage.kindReminderEventType') }}</option>
                  <option value="transactional_route_key">{{ t('notificationRoutingPage.kindTransactionalRouteKey') }}</option>
                </select>
              </div>
              <div class="col-md-3">
                <label class="form-label" for="nr-override-key">{{ t('notificationRoutingPage.formKey') }}</label>
                <input
                  id="nr-override-key"
                  v-model.trim="overrideForm.key"
                  type="text"
                  class="form-control"
                  required
                  maxlength="128"
                  :disabled="!!editingOverrideId"
                  autocomplete="off"
                />
              </div>
              <div class="col-md-3">
                <label class="form-label" for="nr-override-cat">{{ t('notificationRoutingPage.formCategory') }}</label>
                <select id="nr-override-cat" v-model="overrideForm.settings_category" class="form-select" required>
                  <option value="applications">{{ t('notificationRoutingPage.categoryApplications') }}</option>
                  <option value="documents">{{ t('notificationRoutingPage.categoryDocuments') }}</option>
                  <option value="comments">{{ t('notificationRoutingPage.categoryComments') }}</option>
                  <option value="programs">{{ t('notificationRoutingPage.categoryPrograms') }}</option>
                  <option value="system">{{ t('notificationRoutingPage.categorySystem') }}</option>
                  <option value="ungated">{{ t('notificationRoutingPage.categoryUngated') }}</option>
                </select>
              </div>
              <div class="col-md-2">
                <div class="form-check mt-4">
                  <input id="nr-override-active" v-model="overrideForm.is_active" class="form-check-input" type="checkbox" />
                  <label class="form-check-label" for="nr-override-active">{{ t('notificationRoutingPage.formActive') }}</label>
                </div>
              </div>
              <div class="col-md-12 d-flex flex-wrap gap-2">
                <button type="submit" class="btn btn-primary" :disabled="overrideSaving">
                  <span
                    v-if="overrideSaving"
                    class="spinner-border spinner-border-sm me-1"
                    role="status"
                    aria-hidden="true"
                  ></span>
                  {{
                    editingOverrideId
                      ? t('notificationRoutingPage.saveOverride')
                      : t('notificationRoutingPage.createOverride')
                  }}
                </button>
                <button
                  v-if="editingOverrideId"
                  type="button"
                  class="btn btn-outline-secondary"
                  :disabled="overrideSaving"
                  @click="cancelOverrideEdit"
                >
                  {{ t('notificationRoutingPage.cancelEdit') }}
                </button>
              </div>
            </form>
          </div>
          <div class="table-responsive">
            <table class="table table-hover mb-0">
              <thead class="table-light">
                <tr>
                  <th scope="col">{{ t('notificationRoutingPage.colOverrideKind') }}</th>
                  <th scope="col">{{ t('notificationRoutingPage.colOverrideKey') }}</th>
                  <th scope="col">{{ t('notificationRoutingPage.colOverrideCategory') }}</th>
                  <th scope="col">{{ t('notificationRoutingPage.colOverrideActive') }}</th>
                  <th scope="col" class="text-end">{{ t('notificationRoutingPage.colOverrideActions') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="!overridesLoading && !routingOverrides.length">
                  <td colspan="5" class="text-muted small px-3 py-3">{{ t('notificationRoutingPage.overridesEmpty') }}</td>
                </tr>
                <tr v-for="row in routingOverrides" :key="row.id">
                  <td class="small"><code>{{ row.kind }}</code></td>
                  <td class="small"><code>{{ row.key }}</code></td>
                  <td class="small"><code>{{ row.settings_category }}</code></td>
                  <td>
                    <span v-if="row.is_active" class="badge bg-success">{{ t('notificationRoutingPage.statusActive') }}</span>
                    <span v-else class="badge bg-secondary">{{ t('notificationRoutingPage.statusInactive') }}</span>
                  </td>
                  <td class="text-end text-nowrap">
                    <button
                      type="button"
                      class="btn btn-link btn-sm py-0"
                      :aria-label="t('notificationRoutingPage.editOverrideAria', { key: row.key })"
                      @click="startEditOverride(row)"
                    >
                      {{ t('notificationRoutingPage.editOverride') }}
                    </button>
                    <button
                      type="button"
                      class="btn btn-link btn-sm py-0"
                      :disabled="overrideSaving"
                      :aria-label="
                        row.is_active
                          ? t('notificationRoutingPage.deactivateOverrideAria', { key: row.key })
                          : t('notificationRoutingPage.activateOverrideAria', { key: row.key })
                      "
                      @click="toggleOverrideActive(row)"
                    >
                      {{
                        row.is_active
                          ? t('notificationRoutingPage.deactivateOverride')
                          : t('notificationRoutingPage.activateOverride')
                      }}
                    </button>
                    <button
                      type="button"
                      class="btn btn-link btn-sm py-0 text-danger"
                      :disabled="overrideSaving"
                      :aria-label="t('notificationRoutingPage.deleteOverrideAria', { key: row.key })"
                      @click="deleteOverride(row)"
                    >
                      {{ t('notificationRoutingPage.deleteOverride') }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

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
                  <th scope="col">{{ t('notificationRoutingPage.colRecipientSummary') }}</th>
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
                  <td class="small text-muted">{{ row.recipient_summary || t('notificationRoutingPage.emDash') }}</td>
                  <td class="small text-muted">{{ row.summary }}</td>
                  <td class="small text-muted font-monospace">{{ row.source }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div
          v-if="transactionalRouteKeysByCategory.length"
          class="card border-0 shadow-sm mb-4"
        >
          <div class="card-header bg-light">
            <span class="fw-semibold">{{ t('notificationRoutingPage.transactionalByCategoryTitle') }}</span>
          </div>
          <div class="card-body small text-muted border-bottom">
            {{ t('notificationRoutingPage.transactionalByCategoryIntro') }}
          </div>
          <div class="table-responsive">
            <table class="table table-hover mb-0">
              <thead class="table-light">
                <tr>
                  <th scope="col">{{ t('notificationRoutingPage.colCategoryBucket') }}</th>
                  <th scope="col">{{ t('notificationRoutingPage.colRouteKeys') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in transactionalRouteKeysByCategory" :key="row.bucket">
                  <td><code>{{ row.bucket }}</code></td>
                  <td class="small">
                    <code v-for="k in row.keys" :key="k" class="me-2 d-inline-block">{{ k }}</code>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div
          v-if="reminderTypesByCategory.length"
          class="card border-0 shadow-sm mb-4"
        >
          <div class="card-header bg-light">
            <span class="fw-semibold">{{ t('notificationRoutingPage.reminderByCategoryTitle') }}</span>
          </div>
          <div class="card-body small text-muted border-bottom">
            {{ t('notificationRoutingPage.reminderByCategoryIntro') }}
          </div>
          <div class="table-responsive">
            <table class="table table-hover mb-0">
              <thead class="table-light">
                <tr>
                  <th scope="col">{{ t('notificationRoutingPage.colCategoryBucket') }}</th>
                  <th scope="col">{{ t('notificationRoutingPage.colEventTypeKeys') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in reminderTypesByCategory" :key="row.bucket">
                  <td><code>{{ row.bucket }}</code></td>
                  <td class="small">
                    <code v-for="k in row.keys" :key="k" class="me-2 d-inline-block">{{ k }}</code>
                  </td>
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
                  <th scope="col">{{ t('notificationRoutingPage.colReminderRecipientSummary') }}</th>
                  <th scope="col">{{ t('notificationRoutingPage.colReminderDescription') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in reminderRows" :key="row.eventType">
                  <td><code>{{ row.eventType }}</code></td>
                  <td><code>{{ row.category }}</code></td>
                  <td class="small text-muted">{{ row.recipientSummary || t('notificationRoutingPage.emDash') }}</td>
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
              <template v-if="payload.digest.recipient_summary">
                <dt class="col-sm-3">{{ t('notificationRoutingPage.digestRecipientSummary') }}</dt>
                <dd class="col-sm-9 text-muted">{{ payload.digest.recipient_summary }}</dd>
              </template>
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
const { error: errorToast, success: successToast } = useToast()
const loading = ref(true)
const error = ref('')
const payload = ref(null)

const routingOverrides = ref([])
const overridesLoading = ref(false)
const overridesError = ref('')
const overrideSaving = ref(false)
const editingOverrideId = ref(null)
const overrideForm = ref({
  kind: 'reminder_event_type',
  key: '',
  settings_category: 'applications',
  is_active: true,
})

function defaultOverrideForm() {
  return {
    kind: 'reminder_event_type',
    key: '',
    settings_category: 'applications',
    is_active: true,
  }
}

async function fetchAllRoutingOverrides() {
  const all = []
  let url = '/api/notification-routing-overrides/'
  while (url) {
    const { data } = await api.get(url)
    const chunk = data.results ?? data
    if (Array.isArray(chunk)) {
      all.push(...chunk)
    }
    url = data.next || null
  }
  return all.sort((a, b) => {
    const k = String(a.kind).localeCompare(String(b.kind))
    if (k !== 0) return k
    return String(a.key).localeCompare(String(b.key))
  })
}

async function refreshRoutingReference() {
  const { data } = await api.get('/api/notifications/routing-reference/')
  payload.value = data
}

async function loadRoutingOverrides() {
  overridesLoading.value = true
  overridesError.value = ''
  try {
    routingOverrides.value = await fetchAllRoutingOverrides()
  } catch (e) {
    console.error(e)
    overridesError.value = t('notificationRoutingPage.overridesLoadError')
    errorToast(overridesError.value)
  } finally {
    overridesLoading.value = false
  }
}

function startEditOverride(row) {
  editingOverrideId.value = row.id
  overrideForm.value = {
    kind: row.kind,
    key: row.key,
    settings_category: row.settings_category,
    is_active: row.is_active,
  }
}

function cancelOverrideEdit() {
  editingOverrideId.value = null
  overrideForm.value = defaultOverrideForm()
}

function formatOverrideApiError(err) {
  const d = err?.response?.data
  if (!d || typeof d !== 'object') return t('notificationRoutingPage.overrideSaveError')
  const first = Object.values(d).find((v) => v != null)
  if (Array.isArray(first) && first.length) return String(first[0])
  if (typeof first === 'string') return first
  return t('notificationRoutingPage.overrideSaveError')
}

async function submitOverrideForm() {
  overrideSaving.value = true
  try {
    const body = {
      kind: overrideForm.value.kind,
      key: overrideForm.value.key,
      settings_category: overrideForm.value.settings_category,
      is_active: overrideForm.value.is_active,
    }
    if (editingOverrideId.value) {
      await api.patch(`/api/notification-routing-overrides/${editingOverrideId.value}/`, body)
      successToast(t('notificationRoutingPage.overrideUpdatedToast'))
    } else {
      await api.post('/api/notification-routing-overrides/', body)
      successToast(t('notificationRoutingPage.overrideCreatedToast'))
    }
    cancelOverrideEdit()
    await loadRoutingOverrides()
    await refreshRoutingReference()
  } catch (e) {
    console.error(e)
    errorToast(formatOverrideApiError(e))
  } finally {
    overrideSaving.value = false
  }
}

async function toggleOverrideActive(row) {
  overrideSaving.value = true
  try {
    await api.patch(`/api/notification-routing-overrides/${row.id}/`, {
      is_active: !row.is_active,
    })
    successToast(t('notificationRoutingPage.overrideUpdatedToast'))
    await loadRoutingOverrides()
    await refreshRoutingReference()
  } catch (e) {
    console.error(e)
    errorToast(formatOverrideApiError(e))
  } finally {
    overrideSaving.value = false
  }
}

async function deleteOverride(row) {
  if (
    !window.confirm(
      t('notificationRoutingPage.deleteOverrideConfirm', {
        key: row.key,
      }),
    )
  ) {
    return
  }
  overrideSaving.value = true
  try {
    await api.delete(`/api/notification-routing-overrides/${row.id}/`)
    successToast(t('notificationRoutingPage.overrideDeletedToast'))
    if (editingOverrideId.value === row.id) {
      cancelOverrideEdit()
    }
    await loadRoutingOverrides()
    await refreshRoutingReference()
  } catch (e) {
    console.error(e)
    errorToast(formatOverrideApiError(e))
  } finally {
    overrideSaving.value = false
  }
}

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

const transactionalRouteKeysByCategory = computed(() => {
  const idx = payload.value?.transactional_route_keys_by_settings_category
  if (!idx || typeof idx !== 'object') return []
  return Object.keys(idx)
    .sort((a, b) => a.localeCompare(b))
    .map((bucket) => ({
      bucket,
      keys: Array.isArray(idx[bucket]) ? idx[bucket] : [],
    }))
})

const reminderTypesByCategory = computed(() => {
  const idx = payload.value?.reminder_event_types_by_settings_category
  if (!idx || typeof idx !== 'object') return []
  return Object.keys(idx)
    .sort((a, b) => a.localeCompare(b))
    .map((bucket) => ({
      bucket,
      keys: Array.isArray(idx[bucket]) ? idx[bucket] : [],
    }))
})

const reminderRows = computed(() => {
  const m = payload.value?.reminder_event_type_to_settings_category
  if (!m || typeof m !== 'object') return []
  const desc = payload.value?.reminder_event_type_descriptions || {}
  const rsum = payload.value?.reminder_event_type_recipient_summaries || {}
  return Object.keys(m)
    .sort((a, b) => a.localeCompare(b))
    .map((eventType) => ({
      eventType,
      category: m[eventType],
      recipientSummary: rsum[eventType] || '',
      description: desc[eventType] || '',
    }))
})

onMounted(async () => {
  try {
    const { data } = await api.get('/api/notifications/routing-reference/')
    payload.value = data
    await loadRoutingOverrides()
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
