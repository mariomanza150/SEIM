<template>
  <div class="admin-dynforms-page">
    <PageHeader :title="t('adminDynforms.title')" :subtitle="t('adminDynforms.subtitle')">
      <template #breadcrumb>
        <nav aria-label="Breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item">
              <router-link :to="{ name: 'Dashboard' }">{{ t('route.names.Dashboard') }}</router-link>
            </li>
            <li class="breadcrumb-item active">{{ t('route.names.AdminDynforms') }}</li>
          </ol>
        </nav>
      </template>
      <template #actions>
        <button type="button" class="btn btn-outline-secondary" :disabled="loading" @click="fetchForms">
          <i class="bi bi-arrow-clockwise me-1" aria-hidden="true"></i>{{ t('adminCommon.refresh') }}
        </button>
        <button type="button" class="btn btn-primary" data-testid="dynforms-create" @click="openCreate">
          <i class="bi bi-plus-circle me-1" aria-hidden="true"></i>{{ t('adminDynforms.create') }}
        </button>
      </template>
    </PageHeader>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">{{ t('adminCommon.loading') }}</span>
      </div>
    </div>
    <div v-else-if="error" class="alert alert-danger" role="alert">{{ error }}</div>
    <div v-else class="card">
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0" data-testid="dynforms-table">
          <thead>
            <tr>
              <th>{{ t('adminForms.columns.name') }}</th>
              <th>{{ t('adminForms.columns.type') }}</th>
              <th>{{ t('adminForms.columns.fields') }}</th>
              <th class="text-end">{{ t('adminCommon.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!forms.length">
              <td colspan="4" class="text-muted text-center py-4">{{ t('adminDynforms.empty') }}</td>
            </tr>
            <tr v-for="ft in forms" :key="ft.id">
              <td>
                <div class="fw-medium">{{ ft.name }}</div>
                <div class="text-muted small">{{ ft.description }}</div>
              </td>
              <td><span class="badge bg-secondary">{{ ft.form_type }}</span></td>
              <td>{{ ft.field_count ?? 0 }}</td>
              <td class="text-end text-nowrap">
                <router-link
                  class="btn btn-sm btn-primary me-2"
                  :to="{ name: 'AdminDynformEditor', params: { id: String(ft.id) } }"
                  data-testid="dynforms-open-builder"
                >
                  {{ t('adminDynforms.openBuilder') }}
                </router-link>
                <button type="button" class="btn btn-sm btn-outline-danger" :disabled="mutating" @click="confirmDelete(ft)">
                  {{ t('adminCommon.delete') }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="creator.open" class="modal-backdrop show"></div>
    <div v-if="creator.open" class="modal d-block" tabindex="-1" role="dialog" aria-modal="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ t('adminDynforms.create') }}</h5>
            <button type="button" class="btn-close" :aria-label="t('adminCommon.close')" @click="creator.open = false" />
          </div>
          <div class="modal-body">
            <div v-if="creator.error" class="alert alert-danger">{{ creator.error }}</div>
            <label class="form-label">{{ t('adminForms.fields.name') }}</label>
            <input v-model="creator.form.name" class="form-control mb-3" type="text" data-testid="dynforms-create-name" />
            <label class="form-label">{{ t('adminForms.fields.type') }}</label>
            <select v-model="creator.form.form_type" class="form-select mb-3">
              <option v-for="opt in formTypeOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
            </select>
            <label class="form-label">{{ t('adminForms.fields.description') }}</label>
            <textarea v-model="creator.form.description" class="form-control" rows="2" />
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-outline-secondary" @click="creator.open = false">
              {{ t('adminCommon.cancel') }}
            </button>
            <button type="button" class="btn btn-primary" :disabled="creator.saving" data-testid="dynforms-create-save" @click="createForm">
              {{ t('adminDynforms.createAndBuild') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import PageHeader from '@/components/PageHeader.vue'
import api from '@/services/api'
import { useConfirm } from '@/composables/useConfirm'
import { useToast } from '@/composables/useToast'

const { t } = useI18n()
const router = useRouter()
const { confirm } = useConfirm()
const { success, error: errorToast } = useToast()

const loading = ref(true)
const error = ref(null)
const forms = ref([])
const mutating = ref(false)
const formTypeOptions = [
  { value: 'application', label: 'Application' },
  { value: 'survey', label: 'Survey' },
  { value: 'feedback', label: 'Feedback' },
  { value: 'custom', label: 'Custom' },
]
const creator = ref({
  open: false,
  saving: false,
  error: null,
  form: { name: '', form_type: 'application', description: '' },
})

function normalizeApiList(data) {
  if (data && typeof data === 'object' && Array.isArray(data.results)) return data.results
  return Array.isArray(data) ? data : []
}

async function fetchForms() {
  loading.value = true
  error.value = null
  try {
    const response = await api.get('/api/application-forms/form-types/', { params: { ordering: 'name' } })
    forms.value = normalizeApiList(response.data)
  } catch {
    error.value = t('adminDynforms.loadError')
  } finally {
    loading.value = false
  }
}

function openCreate() {
  creator.value = {
    open: true,
    saving: false,
    error: null,
    form: { name: '', form_type: 'application', description: '' },
  }
}

async function createForm() {
  creator.value.saving = true
  creator.value.error = null
  try {
    const response = await api.post('/api/application-forms/form-types/', {
      name: creator.value.form.name,
      form_type: creator.value.form.form_type,
      description: creator.value.form.description,
      is_active: true,
      schema: { type: 'object', properties: {}, required: [] },
      ui_schema: {},
      step_definitions: [],
    })
    success(t('adminDynforms.toastCreated'))
    await router.push({ name: 'AdminDynformEditor', params: { id: String(response.data.id) } })
  } catch {
    creator.value.error = t('adminDynforms.createError')
    errorToast(t('adminDynforms.createError'))
  } finally {
    creator.value.saving = false
  }
}

async function confirmDelete(row) {
  const ok = await confirm({
    title: t('adminCommon.delete'),
    message: t('adminForms.deleteConfirm', { name: row?.name || '' }),
    confirmText: t('adminCommon.delete'),
    cancelText: t('adminCommon.cancel'),
    variant: 'danger',
  })
  if (!ok) return
  mutating.value = true
  try {
    await api.delete(`/api/application-forms/form-types/${row.id}/`)
    success(t('adminForms.toastDeleted'))
    await fetchForms()
  } catch {
    errorToast(t('adminForms.deleteToastError'))
  } finally {
    mutating.value = false
  }
}

onMounted(fetchForms)
</script>
