<template>
  <div class="admin-sessions-page">
    <PageHeader :title="t('adminSessions.title')" :subtitle="t('adminSessions.subtitle')">
      <template #breadcrumb>
        <PageBreadcrumb
          :aria-label="t('adminCommon.breadcrumbAria')"
          :items="[
            { to: { name: 'Dashboard' }, label: t('route.names.Dashboard') },
            { label: t('route.names.AdminSessions') },
          ]"
        />
      </template>
      <template #actions>
        <button type="button" class="btn btn-outline-secondary" :disabled="loading" @click="load">
          <i class="bi bi-arrow-clockwise me-1" aria-hidden="true"></i>{{ t('adminCommon.refresh') }}
        </button>
      </template>
    </PageHeader>

    <ul class="nav nav-tabs mb-3" data-testid="admin-sessions-tabs" role="tablist">
      <li v-for="tab in tabKeys" :key="tab" class="nav-item" role="presentation">
        <button
          type="button"
          class="nav-link"
          :class="{ active: activeTab === tab }"
          role="tab"
          :aria-selected="activeTab === tab"
          :data-tab="tab"
          @click="selectTab(tab)"
        >
          {{ t(`adminSessions.tabs.${tab}`) }}
        </button>
      </li>
    </ul>

    <PageStateShell
      :loading="loading"
      :error="error || ''"
      :empty="activeTab === 'sessions' ? !sessions.length : !reminders.length"
      :empty-title="activeTab === 'sessions' ? t('adminSessions.emptySessions') : t('adminSessions.emptyReminders')"
      skeleton="table"
      :loading-label="t('adminCommon.loading')"
      :skeleton-columns="6"
    >
    <template v-if="activeTab === 'sessions'">
      <CompactFilterBar test-id="admin-sessions-filters" @clear="clearSessionFilters">
        <template #primary>
          <div class="col-md-8">
            <label class="form-label">{{ t('adminCommon.searchLabel') }}</label>
            <input
              v-model="sessionSearch"
              class="form-control"
              type="text"
              :placeholder="t('adminSessions.sessionSearch')"
              @input="debouncedSessionSearch"
            >
          </div>
          <div class="col-md-4">
            <label class="form-label">{{ t('adminSessions.fields.active') }}</label>
            <select v-model="sessionActive" class="form-select" @change="load">
              <option value="">{{ t('adminCommon.filterAll') }}</option>
              <option value="true">{{ t('adminCommon.yes') }}</option>
              <option value="false">{{ t('adminCommon.no') }}</option>
            </select>
          </div>
        </template>
      </CompactFilterBar>
      <div class="card">
        <ResponsiveList :items="sessions" :columns="sessionMobileColumns" mobile-test-id="admin-sessions-mobile">
        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0" data-testid="admin-sessions-table">
            <thead>
              <tr>
                <th scope="col">{{ t('adminSessions.fields.user') }}</th>
                <th scope="col">{{ t('adminSessions.fields.device') }}</th>
                <th scope="col">{{ t('adminSessions.fields.location') }}</th>
                <th scope="col">{{ t('adminSessions.fields.lastActivity') }}</th>
                <th scope="col">{{ t('adminSessions.fields.active') }}</th>
                <th scope="col" class="text-end">{{ t('adminCommon.actions') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in sessions" :key="row.id">
                <td>
                  <div class="fw-medium">{{ row.user_email }}</div>
                  <div class="text-muted small">{{ row.user_username }}</div>
                </td>
                <td>{{ row.device || t('adminCommon.notSet') }}</td>
                <td>
                  <div>{{ row.location || t('adminCommon.notSet') }}</div>
                  <div v-if="row.ip_address" class="text-muted small">{{ row.ip_address }}</div>
                </td>
                <td>{{ formatWhen(row.last_activity) }}</td>
                <td>
                  <span class="badge" :class="row.is_active ? 'bg-success' : 'bg-secondary'">
                    {{ row.is_active ? t('adminCommon.yes') : t('adminCommon.no') }}
                  </span>
                </td>
                <td class="text-end">
                  <button
                    v-if="row.is_active"
                    type="button"
                    class="btn btn-sm btn-outline-danger"
                    :disabled="saving"
                    @click="revokeSession(row)"
                  >
                    {{ t('adminSessions.revoke') }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <template #col-user="{ item }">
          <div class="fw-medium">{{ item.user_email }}</div>
          <div class="text-muted small">{{ item.user_username }}</div>
        </template>
        <template #col-device="{ item }">{{ item.device || t('adminCommon.notSet') }}</template>
        <template #col-location="{ item }">
          <div>{{ item.location || t('adminCommon.notSet') }}</div>
          <div v-if="item.ip_address" class="text-muted small">{{ item.ip_address }}</div>
        </template>
        <template #col-lastActivity="{ item }">{{ formatWhen(item.last_activity) }}</template>
        <template #col-active="{ item }">
          <span class="badge" :class="item.is_active ? 'bg-success' : 'bg-secondary'">
            {{ item.is_active ? t('adminCommon.yes') : t('adminCommon.no') }}
          </span>
        </template>
        <template #actions="{ item }">
          <button
            v-if="item.is_active"
            type="button"
            class="btn btn-sm btn-outline-danger"
            :disabled="saving"
            @click="revokeSession(item)"
          >
            {{ t('adminSessions.revoke') }}
          </button>
        </template>
        </ResponsiveList>
      </div>
    </template>

    <template v-else>
      <form class="card mb-3" data-testid="admin-reminders-create" @submit.prevent="createReminder">
        <div class="card-body">
          <div v-if="formError" class="alert alert-danger" role="alert">{{ formError }}</div>
          <div class="row g-2 align-items-end">
            <div class="col-md-3">
              <label class="form-label">{{ t('adminSessions.fields.user') }}</label>
              <select v-model="draft.user" class="form-select" required>
                <option value="">{{ t('adminCommon.notSet') }}</option>
                <option v-for="user in users" :key="user.id" :value="user.id">{{ user.email }}</option>
              </select>
            </div>
            <div class="col-md-2">
              <label class="form-label">{{ t('adminSessions.fields.eventType') }}</label>
              <select v-model="draft.event_type" class="form-select">
                <option v-for="type in eventTypes" :key="type" :value="type">
                  {{ t(`adminSessions.eventTypes.${type}`) }}
                </option>
              </select>
            </div>
            <div class="col-md-3">
              <label class="form-label">{{ t('adminSessions.fields.title') }}</label>
              <input v-model="draft.event_title" class="form-control" type="text" required>
            </div>
            <div class="col-md-2">
              <label class="form-label">{{ t('adminSessions.fields.remindAt') }}</label>
              <input v-model="draft.remind_at" class="form-control" type="datetime-local" required>
            </div>
            <div class="col-md-2">
              <button type="submit" class="btn btn-primary w-100" :disabled="saving">
                {{ t('adminSessions.createReminder') }}
              </button>
            </div>
          </div>
        </div>
      </form>
      <div class="card">
        <ResponsiveList :items="reminders" :columns="reminderMobileColumns" mobile-test-id="admin-reminders-mobile">
        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0" data-testid="admin-reminders-table">
            <thead>
              <tr>
                <th scope="col">{{ t('adminSessions.fields.user') }}</th>
                <th scope="col">{{ t('adminSessions.fields.title') }}</th>
                <th scope="col">{{ t('adminSessions.fields.eventType') }}</th>
                <th scope="col">{{ t('adminSessions.fields.remindAt') }}</th>
                <th scope="col">{{ t('adminSessions.fields.sent') }}</th>
                <th scope="col" class="text-end">{{ t('adminCommon.actions') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in reminders" :key="row.id">
                <td>{{ row.user_email }}</td>
                <td>{{ row.event_title }}</td>
                <td>{{ t(`adminSessions.eventTypes.${row.event_type}`) }}</td>
                <td>{{ formatWhen(row.remind_at) }}</td>
                <td>
                  <span class="badge" :class="row.sent ? 'bg-success' : 'bg-secondary'">
                    {{ row.sent ? t('adminCommon.yes') : t('adminCommon.no') }}
                  </span>
                </td>
                <td class="text-end">
                  <button
                    type="button"
                    class="btn btn-sm btn-outline-danger"
                    :disabled="saving"
                    @click="confirmDeleteReminder(row)"
                  >
                    <i class="bi bi-trash me-1" aria-hidden="true"></i>{{ t('adminCommon.delete') }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <template #col-user="{ item }">{{ item.user_email }}</template>
        <template #col-title="{ item }">{{ item.event_title }}</template>
        <template #col-eventType="{ item }">{{ t(`adminSessions.eventTypes.${item.event_type}`) }}</template>
        <template #col-remindAt="{ item }">{{ formatWhen(item.remind_at) }}</template>
        <template #col-sent="{ item }">
          <span class="badge" :class="item.sent ? 'bg-success' : 'bg-secondary'">
            {{ item.sent ? t('adminCommon.yes') : t('adminCommon.no') }}
          </span>
        </template>
        <template #actions="{ item }">
          <button
            type="button"
            class="btn btn-sm btn-outline-danger"
            :disabled="saving"
            @click="confirmDeleteReminder(item)"
          >
            <i class="bi bi-trash me-1" aria-hidden="true"></i>{{ t('adminCommon.delete') }}
          </button>
        </template>
        </ResponsiveList>
      </div>
    </template>
    </PageStateShell>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useToast } from '@/composables/useToast'
import { useConfirm } from '@/composables/useConfirm'
import CompactFilterBar from '@/components/CompactFilterBar.vue'
import ResponsiveList from '@/components/ResponsiveList.vue'
import PageHeader from '@/components/PageHeader.vue'
import PageBreadcrumb from '@/components/PageBreadcrumb.vue'
import PageStateShell from '@/components/State/PageStateShell.vue'
import { formatDateTime } from '@/utils/formatters'

const eventTypes = [
  'application_deadline',
  'document_deadline',
  'program_start',
  'program_end',
  'custom',
]

const { t, locale } = useI18n()
const { success, error: errorToast } = useToast()
const { confirm } = useConfirm()

const tabKeys = ['sessions', 'reminders']
const activeTab = ref('sessions')
const loading = ref(false)
const saving = ref(false)
const error = ref(null)
const formError = ref(null)
const sessions = ref([])
const reminders = ref([])
const users = ref([])
const sessionSearch = ref('')
const sessionActive = ref('')

const sessionMobileColumns = computed(() => [
  { key: 'user', label: t('adminSessions.fields.user') },
  { key: 'device', label: t('adminSessions.fields.device') },
  { key: 'location', label: t('adminSessions.fields.location') },
  { key: 'lastActivity', label: t('adminSessions.fields.lastActivity') },
  { key: 'active', label: t('adminSessions.fields.active') },
])

const reminderMobileColumns = computed(() => [
  { key: 'user', label: t('adminSessions.fields.user') },
  { key: 'title', label: t('adminSessions.fields.title') },
  { key: 'eventType', label: t('adminSessions.fields.eventType') },
  { key: 'remindAt', label: t('adminSessions.fields.remindAt') },
  { key: 'sent', label: t('adminSessions.fields.sent') },
])

let sessionSearchTimeout = null
function debouncedSessionSearch() {
  clearTimeout(sessionSearchTimeout)
  sessionSearchTimeout = setTimeout(() => load(), 400)
}

function clearSessionFilters() {
  sessionSearch.value = ''
  sessionActive.value = ''
  load()
}

const draft = reactive({
  user: '',
  event_type: 'custom',
  event_title: '',
  remind_at: '',
})

function normalizeApiList(data) {
  if (data && typeof data === 'object' && Array.isArray(data.results)) return data.results
  return Array.isArray(data) ? data : []
}

function formatWhen(value) {
  return formatDateTime({ dateString: value, locale: locale.value })
}

function selectTab(tab) {
  activeTab.value = tab
  formError.value = null
  load()
}

async function load() {
  loading.value = true
  error.value = null
  try {
    if (activeTab.value === 'sessions') {
      const params = { ordering: '-last_activity' }
      if (sessionSearch.value.trim()) params.search = sessionSearch.value.trim()
      if (sessionActive.value !== '') params.is_active = sessionActive.value
      const res = await api.get('/api/user-sessions/', { params })
      sessions.value = normalizeApiList(res.data)
      return
    }
    const [remRes, userRes] = await Promise.all([
      api.get('/api/reminders/', { params: { ordering: 'remind_at' } }),
      api.get('/api/users/', { params: { ordering: 'email' } }),
    ])
    reminders.value = normalizeApiList(remRes.data)
    users.value = normalizeApiList(userRes.data)
  } catch (err) {
    console.error('Failed to load sessions console:', err)
    error.value = t('adminSessions.loadError')
  } finally {
    loading.value = false
  }
}

async function revokeSession(row) {
  const ok = await confirm({
    title: t('adminSessions.revoke'),
    message: t('adminSessions.revokeConfirm', { email: row.user_email || '' }),
    confirmText: t('adminCommon.yes'),
    cancelText: t('adminCommon.no'),
    variant: 'danger',
  })
  if (!ok) return
  saving.value = true
  try {
    await api.post(`/api/user-sessions/${row.id}/revoke/`)
    success(t('adminSessions.toastRevoked'))
    await load()
  } catch (err) {
    console.error('Failed to revoke session:', err)
    errorToast(t('adminSessions.saveError'))
  } finally {
    saving.value = false
  }
}

async function createReminder() {
  formError.value = null
  saving.value = true
  try {
    await api.post('/api/reminders/', {
      user: draft.user,
      event_type: draft.event_type,
      event_title: (draft.event_title || '').trim(),
      event_id: crypto.randomUUID(),
      remind_at: new Date(draft.remind_at).toISOString(),
    })
    success(t('adminSessions.toastCreated'))
    draft.event_title = ''
    draft.remind_at = ''
    await load()
  } catch (err) {
    console.error('Failed to create reminder:', err)
    formError.value = t('adminSessions.saveError')
    errorToast(t('adminSessions.saveError'))
  } finally {
    saving.value = false
  }
}

async function confirmDeleteReminder(row) {
  const ok = await confirm({
    title: t('adminCommon.delete'),
    message: t('adminSessions.deleteConfirm', { name: row.event_title || '' }),
    confirmText: t('adminCommon.yes'),
    cancelText: t('adminCommon.no'),
    variant: 'danger',
  })
  if (!ok) return
  saving.value = true
  try {
    await api.delete(`/api/reminders/${row.id}/`)
    success(t('adminSessions.toastDeleted'))
    await load()
  } catch (err) {
    console.error('Failed to delete reminder:', err)
    errorToast(t('adminSessions.saveError'))
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  load()
})
</script>

<style scoped>
.admin-sessions-page {
  min-height: 60vh;
}
</style>
