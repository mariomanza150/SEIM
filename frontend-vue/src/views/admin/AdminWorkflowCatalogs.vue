<template>
  <div class="admin-workflow-catalogs-page">
    <PageHeader :title="t('adminWorkflowCatalogs.title')" :subtitle="t('adminWorkflowCatalogs.subtitle')">
      <template #breadcrumb>
        <nav aria-label="Breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item">
              <router-link :to="{ name: 'Dashboard' }">{{ t('route.names.Dashboard') }}</router-link>
            </li>
            <li class="breadcrumb-item active">{{ t('route.names.AdminWorkflowCatalogs') }}</li>
          </ol>
        </nav>
      </template>
      <template #actions>
        <button type="button" class="btn btn-outline-secondary" :disabled="loading" @click="load">
          <i class="bi bi-arrow-clockwise me-1" aria-hidden="true"></i>{{ t('adminCommon.refresh') }}
        </button>
      </template>
    </PageHeader>

    <ul class="nav nav-tabs mb-3" data-testid="admin-workflow-catalogs-tabs" role="tablist">
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
          {{ t(`adminWorkflowCatalogs.tabs.${tab}`) }}
        </button>
      </li>
    </ul>

    <p class="text-muted">{{ t(`adminWorkflowCatalogs.help.${activeTab}`) }}</p>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">{{ t('adminCommon.loading') }}</span>
      </div>
    </div>
    <div v-else-if="error" class="alert alert-danger" role="alert">
      <i class="bi bi-exclamation-triangle me-2" aria-hidden="true"></i>{{ error }}
    </div>

    <template v-else>
      <form class="card mb-3" data-testid="admin-workflow-catalogs-create" @submit.prevent="createItem">
        <div class="card-body">
          <div v-if="formError" class="alert alert-danger" role="alert">{{ formError }}</div>
          <div class="row g-2 align-items-end">
            <div :class="activeTab === 'statuses' ? 'col-md-6' : 'col-md-8'">
              <label class="form-label">{{ t('adminWorkflowCatalogs.fields.name') }}</label>
              <input
                v-model="draft.name"
                class="form-control"
                type="text"
                required
                :placeholder="t('adminWorkflowCatalogs.namePlaceholder')"
              >
            </div>
            <div v-if="activeTab === 'statuses'" class="col-md-3">
              <label class="form-label">{{ t('adminWorkflowCatalogs.fields.order') }}</label>
              <input v-model.number="draft.order" class="form-control" type="number" min="0" step="1">
            </div>
            <div class="col-md-3">
              <button type="submit" class="btn btn-primary w-100" :disabled="saving || !canCreate">
                {{ t('adminWorkflowCatalogs.create') }}
              </button>
            </div>
          </div>
        </div>
      </form>

      <div class="card">
        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0" data-testid="admin-workflow-catalogs-table">
            <thead>
              <tr>
                <th scope="col">{{ t('adminWorkflowCatalogs.fields.name') }}</th>
                <th v-if="activeTab === 'statuses'" scope="col">{{ t('adminWorkflowCatalogs.fields.order') }}</th>
                <th scope="col" class="text-end">{{ t('adminCommon.actions') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!items.length">
                <td :colspan="activeTab === 'statuses' ? 3 : 2" class="text-muted text-center py-4">
                  {{ t('adminWorkflowCatalogs.empty') }}
                </td>
              </tr>
              <tr v-for="item in items" :key="item.id">
                <td>
                  <div class="fw-medium">{{ item.name }}</div>
                  <input
                    v-model="item.name"
                    class="form-control form-control-sm mt-1"
                    type="text"
                    @change="saveRow(item)"
                  >
                </td>
                <td v-if="activeTab === 'statuses'" style="max-width: 8rem">
                  <input
                    v-model.number="item.order"
                    class="form-control form-control-sm"
                    type="number"
                    min="0"
                    step="1"
                    @change="saveRow(item)"
                  >
                </td>
                <td class="text-end text-nowrap">
                  <button
                    type="button"
                    class="btn btn-sm btn-outline-secondary me-1"
                    :disabled="saving"
                    @click="saveRow(item)"
                  >
                    {{ t('adminCommon.save') }}
                  </button>
                  <button
                    type="button"
                    class="btn btn-sm btn-outline-danger"
                    :disabled="saving"
                    @click="confirmDelete(item)"
                  >
                    <i class="bi bi-trash me-1" aria-hidden="true"></i>{{ t('adminCommon.delete') }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useToast } from '@/composables/useToast'
import { useConfirm } from '@/composables/useConfirm'
import PageHeader from '@/components/PageHeader.vue'

const ENDPOINTS = {
  statuses: '/api/application-statuses/',
  types: '/api/notification-types/',
}

const { t } = useI18n()
const { success, error: errorToast } = useToast()
const { confirm } = useConfirm()

const tabKeys = ['statuses', 'types']
const activeTab = ref('statuses')
const loading = ref(false)
const saving = ref(false)
const error = ref(null)
const formError = ref(null)
const items = ref([])
const draft = reactive({ name: '', order: 0 })

const catalogUrl = computed(() => ENDPOINTS[activeTab.value])
const canCreate = computed(() => Boolean((draft.name || '').trim()))

function normalizeApiList(data) {
  if (data && typeof data === 'object' && Array.isArray(data.results)) return data.results
  return Array.isArray(data) ? data : []
}

function resetDraft() {
  draft.name = ''
  draft.order = items.value.reduce((max, row) => Math.max(max, Number(row.order) || 0), 0) + 1
}

function itemUrl(id) {
  return `${catalogUrl.value}${id}/`
}

function payloadFrom(source) {
  const payload = { name: (source.name || '').trim() }
  if (activeTab.value === 'statuses') payload.order = Number(source.order) || 0
  return payload
}

function selectTab(tab) {
  activeTab.value = tab
  formError.value = null
  resetDraft()
  load()
}

async function load() {
  loading.value = true
  error.value = null
  try {
    const res = await api.get(catalogUrl.value)
    items.value = normalizeApiList(res.data)
    resetDraft()
  } catch (err) {
    console.error('Failed to load workflow catalogs:', err)
    error.value = t('adminWorkflowCatalogs.loadError')
  } finally {
    loading.value = false
  }
}

async function createItem() {
  formError.value = null
  saving.value = true
  try {
    await api.post(catalogUrl.value, payloadFrom(draft))
    success(t('adminWorkflowCatalogs.toastCreated'))
    await load()
  } catch (err) {
    console.error('Failed to create catalog entry:', err)
    formError.value = t('adminWorkflowCatalogs.saveError')
    errorToast(t('adminWorkflowCatalogs.saveError'))
  } finally {
    saving.value = false
  }
}

async function saveRow(item) {
  saving.value = true
  try {
    await api.patch(itemUrl(item.id), payloadFrom(item))
    success(t('adminWorkflowCatalogs.toastSaved'))
  } catch (err) {
    console.error('Failed to save catalog entry:', err)
    errorToast(t('adminWorkflowCatalogs.saveError'))
  } finally {
    saving.value = false
  }
}

async function confirmDelete(item) {
  const ok = await confirm({
    title: t('adminCommon.delete'),
    message: t('adminWorkflowCatalogs.deleteConfirm', { name: item.name || '' }),
    confirmText: t('adminCommon.yes'),
    cancelText: t('adminCommon.no'),
    variant: 'danger',
  })
  if (!ok) return
  saving.value = true
  try {
    await api.delete(itemUrl(item.id))
    success(t('adminWorkflowCatalogs.toastDeleted'))
    await load()
  } catch (err) {
    console.error('Failed to delete catalog entry:', err)
    errorToast(t('adminWorkflowCatalogs.saveError'))
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  load()
})
</script>

<style scoped>
.admin-workflow-catalogs-page {
  min-height: 60vh;
}
</style>
