<template>
  <div class="admin-users-page">
    <PageHeader :title="t('adminUsers.title')" :subtitle="t('adminUsers.subtitle')">
      <template #breadcrumb>
        <PageBreadcrumb
          :aria-label="t('adminCommon.breadcrumbAria')"
          :items="[
            { to: { name: 'Dashboard' }, label: t('route.names.Dashboard') },
            { label: t('route.names.AdminUsers') },
          ]"
        />
      </template>
      <template #actions>
        <button type="button" class="btn btn-outline-secondary" :disabled="loading" @click="fetchUsers">
          <i class="bi bi-arrow-clockwise me-1" aria-hidden="true"></i>{{ t('adminCommon.refresh') }}
        </button>
        <button type="button" class="btn btn-primary" data-testid="admin-users-create" @click="openCreate">
          <i class="bi bi-plus-circle me-1" aria-hidden="true"></i>{{ t('adminUsers.create') }}
        </button>
      </template>
    </PageHeader>

    <CompactFilterBar test-id="admin-users-filters" @clear="clearFilters">
      <template #primary>
        <div class="col-md-6">
          <label class="form-label">{{ t('adminCommon.searchLabel') }}</label>
          <input
            v-model="filters.search"
            class="form-control"
            type="text"
            :placeholder="t('adminUsers.searchPlaceholder')"
            @input="debouncedSearch"
          >
        </div>
        <div class="col-md-3">
          <label class="form-label">{{ t('adminUsers.filterActive') }}</label>
          <select v-model="filters.is_active" class="form-select" @change="fetchUsers">
            <option value="">{{ t('adminCommon.filterAll') }}</option>
            <option value="true">{{ t('adminCommon.yes') }}</option>
            <option value="false">{{ t('adminCommon.no') }}</option>
          </select>
        </div>
        <div class="col-md-3">
          <label class="form-label">{{ t('adminUsers.filterRole') }}</label>
          <select v-model="filters.role" class="form-select" @change="fetchUsers">
            <option value="">{{ t('adminCommon.filterAll') }}</option>
            <option
              v-for="role in catalogRoles"
              :key="`role-filter-${role.id || role.name}`"
              :value="role.name"
            >
              {{ role.name }}
            </option>
          </select>
        </div>
      </template>
      <template #advanced>
        <div class="col-md-4">
          <label class="form-label">{{ t('adminCommon.sortLabel') }}</label>
          <select v-model="filters.ordering" class="form-select" @change="fetchUsers">
            <option value="email">{{ t('adminUsers.sortEmail') }}</option>
            <option value="username">{{ t('adminUsers.sortUsername') }}</option>
            <option value="-date_joined">{{ t('adminUsers.sortNewest') }}</option>
          </select>
        </div>
      </template>
    </CompactFilterBar>

    <PageStateShell
      :loading="loading"
      :error="error || ''"
      :empty="!users.length"
      :empty-title="t('adminUsers.empty')"
      skeleton="table"
      :loading-label="t('adminCommon.loading')"
      :skeleton-columns="5"
    >
    <div class="card">
      <ResponsiveList :items="users" :columns="mobileColumns" mobile-test-id="admin-users-mobile">
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0" data-testid="admin-users-table">
          <thead>
            <tr>
              <th scope="col" class="text-nowrap">{{ t('adminCommon.actions') }}</th>
              <th scope="col">{{ t('adminUsers.columns.email') }}</th>
              <th scope="col">{{ t('adminUsers.columns.name') }}</th>
              <th scope="col">{{ t('adminUsers.columns.roles') }}</th>
              <th scope="col">{{ t('adminUsers.columns.active') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id">
              <td class="text-nowrap">
                <button type="button" class="btn btn-sm btn-outline-secondary" @click="openEdit(user)">
                  <i class="bi bi-pencil me-1" aria-hidden="true"></i>{{ t('adminCommon.edit') }}
                </button>
              </td>
              <td>
                <div class="fw-medium">{{ user.email }}</div>
                <div class="text-muted small">{{ user.username }}</div>
              </td>
              <td>{{ displayName(user) }}</td>
              <td>
                <span
                  v-for="role in user.roles || []"
                  :key="role"
                  class="badge text-bg-secondary me-1"
                >{{ role }}</span>
                <span v-if="!(user.roles || []).length" class="text-muted">{{ user.role }}</span>
              </td>
              <td>
                <span class="badge" :class="user.is_active ? 'bg-success' : 'bg-secondary'">
                  {{ user.is_active ? t('adminCommon.yes') : t('adminCommon.no') }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <template #col-email="{ item }">
        <div class="fw-medium">{{ item.email }}</div>
        <div class="text-muted small">{{ item.username }}</div>
      </template>
      <template #col-name="{ item }">{{ displayName(item) }}</template>
      <template #col-roles="{ item }">
        <span v-for="role in item.roles || []" :key="role" class="badge text-bg-secondary me-1">{{ role }}</span>
        <span v-if="!(item.roles || []).length" class="text-muted">{{ item.role }}</span>
      </template>
      <template #col-active="{ item }">
        <span class="badge" :class="item.is_active ? 'bg-success' : 'bg-secondary'">
          {{ item.is_active ? t('adminCommon.yes') : t('adminCommon.no') }}
        </span>
      </template>
      <template #actions="{ item }">
        <button type="button" class="btn btn-sm btn-outline-secondary" @click="openEdit(item)">
          <i class="bi bi-pencil me-1" aria-hidden="true"></i>{{ t('adminCommon.edit') }}
        </button>
      </template>
      </ResponsiveList>
    </div>
    </PageStateShell>

    <FormModal
      :open="editor.open"
      :title="editor.mode === 'create' ? t('adminUsers.create') : t('adminUsers.editTitle')"
      :error="editor.error || ''"
      :saving="editor.saving"
      @close="closeEditor"
      @submit="saveUser"
    >
      <div class="row g-3">
              <div class="col-md-6">
                <label class="form-label">{{ t('adminUsers.fields.email') }}</label>
                <input v-model="editor.form.email" class="form-control" type="email" required>
              </div>
              <div class="col-md-6">
                <label class="form-label">{{ t('adminUsers.fields.username') }}</label>
                <input v-model="editor.form.username" class="form-control" type="text" required>
              </div>
              <div class="col-md-6">
                <label class="form-label">{{ t('adminUsers.fields.firstName') }}</label>
                <input v-model="editor.form.first_name" class="form-control" type="text">
              </div>
              <div class="col-md-6">
                <label class="form-label">{{ t('adminUsers.fields.lastName') }}</label>
                <input v-model="editor.form.last_name" class="form-control" type="text">
              </div>
              <div class="col-md-6">
                <label class="form-label">{{ t('adminUsers.fields.password') }}</label>
                <input
                  v-model="editor.form.password"
                  class="form-control"
                  type="password"
                  autocomplete="new-password"
                  :required="editor.mode === 'create'"
                >
                <div class="form-text">{{ editor.mode === 'create' ? t('adminUsers.fields.passwordHelpCreate') : t('adminUsers.fields.passwordHelpEdit') }}</div>
              </div>
              <div class="col-md-6">
                <label class="form-label">{{ t('adminUsers.fields.roles') }}</label>
                <div class="border rounded p-2" data-testid="admin-users-roles">
                  <div v-for="role in catalogRoles" :key="role.id || role.name" class="form-check">
                    <input
                      :id="`user-role-${role.name}`"
                      v-model="editor.form.roles"
                      class="form-check-input"
                      type="checkbox"
                      :value="role.name"
                    >
                    <label class="form-check-label" :for="`user-role-${role.name}`">{{ role.name }}</label>
                  </div>
                </div>
              </div>
              <div class="col-md-6">
                <div class="form-check mt-2">
                  <input id="userActive" v-model="editor.form.is_active" class="form-check-input" type="checkbox">
                  <label class="form-check-label" for="userActive">{{ t('adminUsers.fields.active') }}</label>
                </div>
                <div class="form-check">
                  <input id="userVerified" v-model="editor.form.is_email_verified" class="form-check-input" type="checkbox">
                  <label class="form-check-label" for="userVerified">{{ t('adminUsers.fields.verified') }}</label>
                </div>
                <div class="form-check">
                  <input id="userStaff" v-model="editor.form.is_staff" class="form-check-input" type="checkbox">
                  <label class="form-check-label" for="userStaff">{{ t('adminUsers.fields.staff') }}</label>
                </div>
                <div class="form-text">{{ t('adminUsers.fields.staffHelp') }}</div>
              </div>
            </div>
    </FormModal>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useToast } from '@/composables/useToast'
import CompactFilterBar from '@/components/CompactFilterBar.vue'
import ResponsiveList from '@/components/ResponsiveList.vue'
import FormModal from '@/components/FormModal.vue'
import PageHeader from '@/components/PageHeader.vue'
import PageBreadcrumb from '@/components/PageBreadcrumb.vue'
import PageStateShell from '@/components/State/PageStateShell.vue'

defineOptions({ name: 'AdminUsers' })

const { t } = useI18n()
const { success, error: errorToast } = useToast()

const loading = ref(true)
const error = ref(null)
const users = ref([])
const catalogRoles = ref([])
const filters = ref({ search: '', is_active: '', role: '', ordering: 'email' })

const mobileColumns = computed(() => [
  { key: 'email', label: t('adminUsers.columns.email') },
  { key: 'name', label: t('adminUsers.columns.name') },
  { key: 'roles', label: t('adminUsers.columns.roles') },
  { key: 'active', label: t('adminUsers.columns.active') },
])

function clearFilters() {
  filters.value = { search: '', is_active: '', role: '', ordering: 'email' }
  fetchUsers()
}

const editor = ref({
  open: false,
  mode: 'create',
  id: null,
  saving: false,
  error: null,
  form: emptyUserForm(),
})

function emptyUserForm() {
  return {
    email: '',
    username: '',
    first_name: '',
    last_name: '',
    password: '',
    roles: ['student'],
    is_active: true,
    is_email_verified: true,
    is_staff: false,
  }
}

function normalizeApiList(data) {
  if (data && typeof data === 'object' && Array.isArray(data.results)) return data.results
  return Array.isArray(data) ? data : []
}

function displayName(user) {
  const name = `${user.first_name || ''} ${user.last_name || ''}`.trim()
  return name || user.username
}

let searchTimeout = null
function debouncedSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => fetchUsers(), 400)
}

async function fetchUsers() {
  loading.value = true
  error.value = null
  try {
    const params = { ordering: filters.value.ordering, page_size: 100 }
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.is_active) params.is_active = filters.value.is_active
    if (filters.value.role) params.role = filters.value.role
    const res = await api.get('/api/users/', { params })
    users.value = normalizeApiList(res.data)
  } catch (err) {
    console.error('Failed to load users:', err)
    error.value = t('adminUsers.loadError')
  } finally {
    loading.value = false
  }
}

async function fetchRoles() {
  try {
    const res = await api.get('/api/roles/')
    catalogRoles.value = normalizeApiList(res.data)
  } catch (err) {
    console.error('Failed to load roles:', err)
    catalogRoles.value = []
  }
}

function openCreate() {
  editor.value = {
    open: true,
    mode: 'create',
    id: null,
    saving: false,
    error: null,
    form: emptyUserForm(),
  }
}

function openEdit(user) {
  editor.value = {
    open: true,
    mode: 'edit',
    id: user.id,
    saving: false,
    error: null,
    form: {
      email: user.email || '',
      username: user.username || '',
      first_name: user.first_name || '',
      last_name: user.last_name || '',
      password: '',
      roles: Array.isArray(user.roles) ? [...user.roles] : [],
      is_active: Boolean(user.is_active),
      is_email_verified: Boolean(user.is_email_verified),
      is_staff: Boolean(user.is_staff),
    },
  }
}

function closeEditor() {
  editor.value.open = false
}

function formatApiError(err, fallback) {
  const data = err?.response?.data
  if (typeof data?.detail === 'string') return data.detail
  if (data && typeof data === 'object' && !Array.isArray(data)) {
    const parts = []
    for (const [key, value] of Object.entries(data)) {
      if (Array.isArray(value)) parts.push(`${key}: ${value.join(' ')}`)
      else if (typeof value === 'string') parts.push(`${key}: ${value}`)
    }
    if (parts.length) return parts.join(' ')
  }
  return fallback
}

async function saveUser() {
  editor.value.error = null
  editor.value.saving = true
  try {
    const payload = { ...editor.value.form }
    if (!payload.password) delete payload.password
    if (editor.value.mode === 'create') {
      await api.post('/api/users/', payload)
      success(t('adminUsers.toastCreated'))
    } else {
      await api.patch(`/api/users/${editor.value.id}/`, payload)
      success(t('adminUsers.toastSaved'))
    }
    closeEditor()
    await fetchUsers()
  } catch (err) {
    console.error('Failed to save user:', err)
    editor.value.error = formatApiError(err, t('adminUsers.saveError'))
    errorToast(t('adminUsers.saveError'))
  } finally {
    editor.value.saving = false
  }
}

onMounted(async () => {
  await Promise.all([fetchRoles(), fetchUsers()])
})
</script>
