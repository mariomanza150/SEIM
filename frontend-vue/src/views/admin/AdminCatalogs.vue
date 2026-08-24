<template>
  <div class="admin-catalogs-page">
    <PageHeader :title="t('adminCatalogs.title')" :subtitle="t('adminCatalogs.subtitle')">
      <template #breadcrumb>
        <nav aria-label="Breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item">
              <router-link :to="{ name: 'Dashboard' }">{{ t('route.names.Dashboard') }}</router-link>
            </li>
            <li class="breadcrumb-item active">{{ t('route.names.AdminCatalogs') }}</li>
          </ol>
        </nav>
      </template>
      <template #actions>
        <button type="button" class="btn btn-outline-secondary" :disabled="loading" @click="load">
          <i class="bi bi-arrow-clockwise me-1" aria-hidden="true"></i>{{ t('adminCommon.refresh') }}
        </button>
      </template>
    </PageHeader>

    <ul class="nav nav-tabs mb-3" data-testid="admin-catalogs-tabs" role="tablist">
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
          {{ t(`adminCatalogs.tabs.${tab}`) }}
        </button>
      </li>
    </ul>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">{{ t('adminCommon.loading') }}</span>
      </div>
    </div>
    <div v-else-if="error" class="alert alert-danger" role="alert">
      <i class="bi bi-exclamation-triangle me-2" aria-hidden="true"></i>{{ error }}
    </div>

    <template v-else-if="activeTab === 'destinations'">
      <p class="text-muted">{{ t('adminCatalogs.destinationsHelp') }}</p>
      <div class="card">
        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0" data-testid="admin-catalogs-destinations">
            <thead>
              <tr>
                <th scope="col">{{ t('adminCatalogs.fields.name') }}</th>
                <th scope="col" class="text-end">{{ t('adminCommon.actions') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!programs.length">
                <td colspan="2" class="text-muted text-center py-4">{{ t('adminCatalogs.destinationsEmpty') }}</td>
              </tr>
              <tr v-for="program in programs" :key="program.id">
                <td class="fw-medium">{{ program.name }}</td>
                <td class="text-end text-nowrap">
                  <router-link
                    class="btn btn-sm btn-outline-secondary"
                    :to="{ name: 'AdminProgramDestinations', params: { id: program.id } }"
                  >
                    <i class="bi bi-geo-alt me-1" aria-hidden="true"></i>{{ t('adminCatalogs.openDestinations') }}
                  </router-link>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>

    <template v-else>
      <p v-if="activeTab === 'domains'" class="text-muted">{{ t('adminCatalogs.domainHelp') }}</p>

      <form class="card mb-3" data-testid="admin-catalogs-create" @submit.prevent="createItem">
        <div class="card-body">
          <div v-if="formError" class="alert alert-danger" role="alert">{{ formError }}</div>
          <div class="row g-2 align-items-end">
            <div class="col-md-3">
              <label class="form-label" for="catalog-create-name">{{ t('adminCatalogs.fields.name') }}</label>
              <input id="catalog-create-name" v-model="draft.name" class="form-control" type="text" required>
            </div>
            <div class="col-md-2">
              <label class="form-label" for="catalog-create-code">{{ t('adminCatalogs.fields.code') }}</label>
              <input id="catalog-create-code" v-model="draft.code" class="form-control" type="text">
            </div>
            <div class="col-md-2">
              <label class="form-label" for="catalog-create-ordering">{{ t('adminCatalogs.fields.ordering') }}</label>
              <input id="catalog-create-ordering" v-model.number="draft.ordering" class="form-control" type="number" min="0" step="1">
            </div>
            <div v-if="activeTab === 'programs'" class="col-md-3">
              <label class="form-label" for="catalog-create-school">{{ t('adminCatalogs.fields.school') }}</label>
              <select id="catalog-create-school" v-model="draft.school" class="form-select" required>
                <option value="">{{ t('adminCommon.notSet') }}</option>
                <option v-for="school in schools" :key="school.id" :value="school.id">{{ school.name }}</option>
              </select>
            </div>
            <div v-if="activeTab === 'languages'" class="col-md-4">
              <label class="form-label" for="catalog-create-aliases">{{ t('adminCatalogs.fields.aliases') }}</label>
              <input
                id="catalog-create-aliases"
                v-model="draft.aliasesText"
                class="form-control"
                type="text"
                :placeholder="t('adminCatalogs.fields.aliasesPlaceholder')"
              >
            </div>
            <div class="col-md-2">
              <div class="form-check mt-2">
                <input id="catalog-create-active" v-model="draft.is_active" class="form-check-input" type="checkbox">
                <label class="form-check-label" for="catalog-create-active">{{ t('adminCatalogs.fields.active') }}</label>
              </div>
            </div>
            <div class="col-md-2">
              <button type="submit" class="btn btn-primary w-100" :disabled="saving || !canCreate">
                {{ t('adminCatalogs.create') }}
              </button>
            </div>
          </div>
        </div>
      </form>

      <div class="card">
        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0" data-testid="admin-catalogs-table">
            <thead>
              <tr>
                <th scope="col">{{ t('adminCatalogs.fields.name') }}</th>
                <th scope="col">{{ t('adminCatalogs.fields.code') }}</th>
                <th scope="col">{{ t('adminCatalogs.fields.ordering') }}</th>
                <th v-if="activeTab === 'programs'" scope="col">{{ t('adminCatalogs.fields.school') }}</th>
                <th v-if="activeTab === 'languages'" scope="col">{{ t('adminCatalogs.fields.aliases') }}</th>
                <th scope="col">{{ t('adminCatalogs.fields.active') }}</th>
                <th scope="col" class="text-end">{{ t('adminCommon.actions') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!items.length">
                <td :colspan="activeTab === 'programs' ? 6 : activeTab === 'languages' ? 6 : 5" class="text-muted text-center py-4">
                  {{ t('adminCatalogs.empty') }}
                </td>
              </tr>
              <tr v-for="item in items" :key="item.id">
                <td>
                  <div class="fw-medium">{{ item.name }}</div>
                  <input v-model="item.name" class="form-control form-control-sm mt-1" type="text" @change="saveRow(item)">
                </td>
                <td>
                  <input v-model="item.code" class="form-control form-control-sm" type="text" @change="saveRow(item)">
                </td>
                <td style="max-width: 6rem">
                  <input
                    v-model.number="item.ordering"
                    class="form-control form-control-sm"
                    type="number"
                    min="0"
                    step="1"
                    @change="saveRow(item)"
                  >
                </td>
                <td v-if="activeTab === 'programs'">
                  <select v-model="item.school" class="form-select form-select-sm" @change="saveRow(item)">
                    <option value="">{{ t('adminCommon.notSet') }}</option>
                    <option v-for="school in schools" :key="school.id" :value="school.id">{{ school.name }}</option>
                  </select>
                </td>
                <td v-if="activeTab === 'languages'">
                  <input
                    v-model="item.aliasesText"
                    class="form-control form-control-sm"
                    type="text"
                    :placeholder="t('adminCatalogs.fields.aliasesPlaceholder')"
                    @change="saveRow(item)"
                  >
                </td>
                <td>
                  <div class="form-check mb-0">
                    <input
                      :id="`catalog-active-${item.id}`"
                      v-model="item.is_active"
                      class="form-check-input"
                      type="checkbox"
                      @change="toggleActive(item)"
                    >
                    <label class="form-check-label" :for="`catalog-active-${item.id}`">
                      {{ item.is_active ? t('adminCommon.yes') : t('adminCommon.no') }}
                    </label>
                  </div>
                </td>
                <td class="text-end text-nowrap">
                  <button
                    type="button"
                    class="btn btn-sm btn-outline-secondary me-2"
                    data-testid="admin-catalogs-save-row"
                    :disabled="saving || !(item.name || '').trim()"
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
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useToast } from '@/composables/useToast'
import { useConfirm } from '@/composables/useConfirm'
import PageHeader from '@/components/PageHeader.vue'

const CATALOG_ENDPOINTS = {
  levels: '/api/accounts/catalogs/academic-levels/',
  schools: '/api/accounts/catalogs/schools/',
  programs: '/api/accounts/catalogs/programs/',
  unidades: '/api/accounts/catalogs/unidades/',
  banks: '/api/accounts/catalogs/banks/',
  domains: '/api/accounts/catalogs/allowed-email-domains/',
  languages: '/api/accounts/catalogs/spoken-languages/',
}

const tabKeys = ['levels', 'schools', 'programs', 'unidades', 'banks', 'languages', 'domains', 'destinations']

const { t } = useI18n()
const { success, error: errorToast } = useToast()
const { confirm } = useConfirm()

const activeTab = ref('levels')
const loading = ref(true)
const saving = ref(false)
const error = ref(null)
const formError = ref(null)
const items = ref([])
const programs = ref([])
const schools = ref([])
const draft = reactive(emptyDraft())

const catalogUrl = computed(() => CATALOG_ENDPOINTS[activeTab.value] || '')
const canCreate = computed(() => {
  if (!draft.name.trim()) return false
  if (activeTab.value === 'programs' && !draft.school) return false
  return true
})

function emptyDraft() {
  return { name: '', code: '', ordering: 0, is_active: true, school: '', aliasesText: '' }
}

function parseAliasesText(text) {
  return String(text || '')
    .split(',')
    .map((part) => part.trim())
    .filter(Boolean)
}

function aliasesToText(value) {
  return Array.isArray(value) ? value.join(', ') : ''
}

function resetDraft() {
  Object.assign(draft, emptyDraft())
}

function normalizeApiList(data) {
  if (data && typeof data === 'object' && Array.isArray(data.results)) return data.results
  return Array.isArray(data) ? data : []
}

function normalizeItem(row) {
  return {
    ...row,
    name: row.name || '',
    code: row.code || '',
    ordering: row.ordering ?? 0,
    is_active: row.is_active !== false,
    school: row.school || '',
    aliasesText: aliasesToText(row.aliases),
  }
}

function itemUrl(id) {
  return `${catalogUrl.value}${id}/`
}

function payloadFrom(source) {
  const payload = {
    name: (source.name || '').trim(),
    code: (source.code || '').trim(),
    ordering: Number(source.ordering) || 0,
    is_active: Boolean(source.is_active),
  }
  if (activeTab.value === 'programs') payload.school = source.school
  if (activeTab.value === 'languages') payload.aliases = parseAliasesText(source.aliasesText)
  return payload
}

async function selectTab(tab) {
  activeTab.value = tab
  formError.value = null
  resetDraft()
  await load()
  await nextTick()
  if (activeTab.value === 'destinations') return
  document.getElementById('catalog-create-name')?.focus?.()
}

async function load() {
  loading.value = true
  error.value = null
  try {
    if (activeTab.value === 'destinations') {
      const res = await api.get('/api/programs/')
      programs.value = normalizeApiList(res.data)
      return
    }
    const res = await api.get(catalogUrl.value)
    items.value = normalizeApiList(res.data).map(normalizeItem)
    if (activeTab.value === 'programs') {
      const schoolsRes = await api.get(CATALOG_ENDPOINTS.schools)
      schools.value = normalizeApiList(schoolsRes.data)
    }
  } catch (err) {
    console.error('Failed to load catalogs:', err)
    error.value = t('adminCatalogs.loadError')
  } finally {
    loading.value = false
  }
}

async function createItem() {
  formError.value = null
  saving.value = true
  try {
    await api.post(catalogUrl.value, payloadFrom(draft))
    success(t('adminCatalogs.toastCreated'))
    resetDraft()
    await load()
  } catch (err) {
    console.error('Failed to create catalog entry:', err)
    formError.value = t('adminCatalogs.saveError')
    errorToast(t('adminCatalogs.saveError'))
  } finally {
    saving.value = false
  }
}

async function saveRow(item) {
  if (!(item.name || '').trim()) return
  saving.value = true
  try {
    await api.patch(itemUrl(item.id), payloadFrom(item))
    success(t('adminCatalogs.toastSaved'))
  } catch (err) {
    console.error('Failed to save catalog entry:', err)
    errorToast(t('adminCatalogs.saveError'))
  } finally {
    saving.value = false
  }
}

async function toggleActive(item) {
  saving.value = true
  try {
    await api.patch(itemUrl(item.id), { is_active: Boolean(item.is_active) })
    success(t('adminCatalogs.toastSaved'))
  } catch (err) {
    console.error('Failed to toggle catalog entry:', err)
    item.is_active = !item.is_active
    errorToast(t('adminCatalogs.saveError'))
  } finally {
    saving.value = false
  }
}

async function confirmDelete(item) {
  const ok = await confirm({
    title: t('adminCommon.delete'),
    message: t('adminCatalogs.deleteConfirm', { name: item.name || '' }),
    confirmText: t('adminCommon.yes'),
    cancelText: t('adminCommon.no'),
    variant: 'danger',
  })
  if (!ok) return
  saving.value = true
  try {
    await api.delete(itemUrl(item.id))
    success(t('adminCatalogs.toastDeleted'))
    await load()
  } catch (err) {
    console.error('Failed to delete catalog entry:', err)
    errorToast(t('adminCatalogs.saveError'))
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  load()
})
</script>

<style scoped>
.admin-catalogs-page {
  min-height: 60vh;
}

.admin-catalogs-page :deep(header.seim-page-header) {
  position: relative;
  z-index: 5;
}
</style>
