<template>
  <div class="eligibility-rulesets-page">
    <PageHeader :title="t('eligibilityRulesetsPage.title')" :subtitle="t('eligibilityRulesetsPage.subtitle')">
      <template #breadcrumb>
        <nav :aria-label="t('eligibilityRulesetsPage.breadcrumbAria')">
          <ol class="breadcrumb">
            <li class="breadcrumb-item">
              <router-link :to="{ name: 'Dashboard' }">{{ t('route.names.Dashboard') }}</router-link>
            </li>
            <li class="breadcrumb-item active">{{ t('route.names.EligibilityRulesets') }}</li>
          </ol>
        </nav>
      </template>
      <template #actions>
        <button type="button" class="btn btn-outline-secondary" :disabled="loading" @click="fetchList">
          {{ t('adminCommon.refresh') }}
        </button>
        <button type="button" class="btn btn-primary" data-testid="ruleset-create" @click="openCreate">
          {{ t('eligibilityRulesetsPage.create') }}
        </button>
      </template>
    </PageHeader>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">{{ t('adminCommon.loading') }}</span>
      </div>
    </div>
    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-else class="card" data-testid="eligibility-rulesets-page">
      <div class="table-responsive">
        <table class="table table-hover mb-0">
          <thead>
            <tr>
              <th>{{ t('eligibilityRulesetsPage.colName') }}</th>
              <th>{{ t('eligibilityRulesetsPage.colSchema') }}</th>
              <th>{{ t('eligibilityRulesetsPage.colRevision') }}</th>
              <th>{{ t('eligibilityRulesetsPage.colActive') }}</th>
              <th>{{ t('eligibilityRulesetsPage.colUpdated') }}</th>
              <th class="text-end">{{ t('adminCommon.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in rows" :key="row.id">
              <td>{{ row.name }}</td>
              <td data-testid="ruleset-schema-version">v{{ row.schema_version }}</td>
              <td data-testid="ruleset-content-revision">r{{ row.content_revision ?? 1 }}</td>
              <td>{{ row.is_active ? t('adminCommon.yes') : t('adminCommon.no') }}</td>
              <td>{{ formatDate(row.updated_at) }}</td>
              <td class="text-end">
                <button type="button" class="btn btn-sm btn-outline-primary" @click="openEdit(row)">
                  {{ t('adminCommon.edit') }}
                </button>
              </td>
            </tr>
            <tr v-if="!rows.length">
              <td colspan="6" class="text-muted text-center py-4">{{ t('eligibilityRulesetsPage.empty') }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="editor.open" class="modal d-block" tabindex="-1" role="dialog" data-testid="ruleset-editor">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              {{ editor.id ? t('eligibilityRulesetsPage.editTitle') : t('eligibilityRulesetsPage.create') }}
            </h5>
            <button type="button" class="btn-close" :aria-label="t('adminCommon.close')" @click="editor.open = false"></button>
          </div>
          <form @submit.prevent="saveEditor">
            <div class="modal-body">
              <div v-if="editor.error" class="alert alert-danger">{{ editor.error }}</div>
              <div class="mb-3">
                <label class="form-label" for="rs-name">{{ t('eligibilityRulesetsPage.fieldName') }}</label>
                <input id="rs-name" v-model.trim="editor.form.name" class="form-control" required data-testid="ruleset-name" />
              </div>
              <div class="mb-3">
                <label class="form-label" for="rs-desc">{{ t('eligibilityRulesetsPage.fieldDescription') }}</label>
                <textarea id="rs-desc" v-model="editor.form.description" class="form-control" rows="2"></textarea>
              </div>
              <div class="form-check mb-3">
                <input id="rs-active" v-model="editor.form.is_active" class="form-check-input" type="checkbox" />
                <label class="form-check-label" for="rs-active">{{ t('eligibilityRulesetsPage.fieldActive') }}</label>
              </div>
              <p v-if="editor.id" class="small text-muted" data-testid="ruleset-version-meta">
                {{ t('eligibilityRulesetsPage.versionMeta', { schema: editor.schema_version, revision: editor.content_revision }) }}
              </p>
              <h6 class="text-muted">{{ t('eligibilityRulesetsPage.overridesHeading') }}</h6>
              <div class="row g-3">
                <div class="col-md-4">
                  <label class="form-label" for="rs-gpa">{{ t('eligibilityRulesetsPage.fieldMinGpa') }}</label>
                  <input id="rs-gpa" v-model="editor.form.min_gpa" class="form-control" type="number" step="0.01" min="0" />
                </div>
                <div class="col-md-4">
                  <label class="form-label" for="rs-sem">{{ t('eligibilityRulesetsPage.fieldMinSemester') }}</label>
                  <input id="rs-sem" v-model="editor.form.min_semester" class="form-control" type="number" min="0" />
                </div>
                <div class="col-md-4">
                  <label class="form-label" for="rs-credits">{{ t('eligibilityRulesetsPage.fieldMinCredits') }}</label>
                  <input id="rs-credits" v-model="editor.form.min_credits_approved_percent" class="form-control" type="number" step="0.01" min="0" max="100" />
                </div>
                <div class="col-md-6">
                  <label class="form-label" for="rs-lang">{{ t('eligibilityRulesetsPage.fieldLanguage') }}</label>
                  <input id="rs-lang" v-model.trim="editor.form.required_language" class="form-control" />
                </div>
                <div class="col-md-6">
                  <label class="form-label" for="rs-cefr">{{ t('eligibilityRulesetsPage.fieldMinLevel') }}</label>
                  <select id="rs-cefr" v-model="editor.form.min_language_level" class="form-select">
                    <option value="">{{ t('adminCommon.notSet') }}</option>
                    <option v-for="lv in ['A1','A2','B1','B2','C1','C2']" :key="lv" :value="lv">{{ lv }}</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label" for="rs-minage">{{ t('eligibilityRulesetsPage.fieldMinAge') }}</label>
                  <input id="rs-minage" v-model="editor.form.min_age" class="form-control" type="number" min="0" />
                </div>
                <div class="col-md-6">
                  <label class="form-label" for="rs-maxage">{{ t('eligibilityRulesetsPage.fieldMaxAge') }}</label>
                  <input id="rs-maxage" v-model="editor.form.max_age" class="form-control" type="number" min="0" />
                </div>
                <div class="col-md-6">
                  <label class="form-label" for="rs-open">{{ t('eligibilityRulesetsPage.fieldOpenDate') }}</label>
                  <input id="rs-open" v-model="editor.form.application_open_date" class="form-control" type="date" />
                </div>
                <div class="col-md-6">
                  <label class="form-label" for="rs-deadline">{{ t('eligibilityRulesetsPage.fieldDeadline') }}</label>
                  <input id="rs-deadline" v-model="editor.form.application_deadline" class="form-control" type="date" />
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-outline-secondary" @click="editor.open = false">{{ t('adminCommon.cancel') }}</button>
              <button type="submit" class="btn btn-primary" :disabled="editor.saving" data-testid="ruleset-save">
                {{ t('adminCommon.save') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
    <div v-if="editor.open" class="modal-backdrop fade show"></div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useToast } from '@/composables/useToast'
import api from '@/services/api'
import PageHeader from '@/components/PageHeader.vue'

const { t, locale } = useI18n()
const toast = useToast()
const loading = ref(true)
const error = ref('')
const rows = ref([])
const editor = reactive({
  open: false,
  id: null,
  saving: false,
  error: '',
  schema_version: 2,
  content_revision: 1,
  form: emptyForm(),
})

const RULESET_SCHEMA_VERSION = 2

function emptyForm() {
  return {
    name: '',
    description: '',
    is_active: true,
    min_gpa: '',
    min_semester: '',
    min_credits_approved_percent: '',
    required_language: '',
    min_language_level: '',
    min_age: '',
    max_age: '',
    application_open_date: '',
    application_deadline: '',
  }
}

function numOrNull(v) {
  if (v === '' || v === null || v === undefined) return null
  const n = Number(v)
  return Number.isFinite(n) ? n : null
}

function overridesFromForm(form) {
  const ov = {}
  const map = {
    min_gpa: numOrNull(form.min_gpa),
    min_semester: numOrNull(form.min_semester),
    min_credits_approved_percent: numOrNull(form.min_credits_approved_percent),
    required_language: form.required_language || null,
    min_language_level: form.min_language_level || null,
    min_age: numOrNull(form.min_age),
    max_age: numOrNull(form.max_age),
    application_open_date: form.application_open_date || null,
    application_deadline: form.application_deadline || null,
  }
  for (const [k, v] of Object.entries(map)) {
    if (v !== null && v !== '') ov[k] = v
  }
  return ov
}

function formFromRow(row) {
  const ov = row?.rules_json?.program_overrides || {}
  return {
    name: row.name || '',
    description: row.description || '',
    is_active: row.is_active !== false,
    min_gpa: ov.min_gpa ?? '',
    min_semester: ov.min_semester ?? '',
    min_credits_approved_percent: ov.min_credits_approved_percent ?? '',
    required_language: ov.required_language || '',
    min_language_level: ov.min_language_level || '',
    min_age: ov.min_age ?? '',
    max_age: ov.max_age ?? '',
    application_open_date: ov.application_open_date || '',
    application_deadline: ov.application_deadline || '',
  }
}

function formatDate(value) {
  if (!value) return '—'
  const loc = locale.value === 'es' ? 'es' : 'en-US'
  return new Date(value).toLocaleString(loc, { dateStyle: 'medium' })
}

async function fetchList() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/api/eligibility-rulesets/', { params: { ordering: 'name' } })
    rows.value = data.results || data || []
  } catch {
    error.value = t('eligibilityRulesetsPage.loadError')
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editor.open = true
  editor.id = null
  editor.error = ''
  editor.schema_version = RULESET_SCHEMA_VERSION
  editor.content_revision = 1
  editor.form = emptyForm()
}

function openEdit(row) {
  editor.open = true
  editor.id = row.id
  editor.error = ''
  editor.schema_version = row.schema_version ?? RULESET_SCHEMA_VERSION
  editor.content_revision = row.content_revision ?? 1
  editor.form = formFromRow(row)
}

async function saveEditor() {
  editor.saving = true
  editor.error = ''
  const payload = {
    name: editor.form.name,
    description: editor.form.description,
    is_active: editor.form.is_active,
    schema_version: RULESET_SCHEMA_VERSION,
    rules_json: { program_overrides: overridesFromForm(editor.form) },
  }
  try {
    if (editor.id) {
      await api.patch(`/api/eligibility-rulesets/${editor.id}/`, payload)
      toast.success(t('eligibilityRulesetsPage.toastSaved'))
    } else {
      await api.post('/api/eligibility-rulesets/', payload)
      toast.success(t('eligibilityRulesetsPage.toastCreated'))
    }
    editor.open = false
    await fetchList()
  } catch (err) {
    const data = err.response?.data
    const detail =
      (typeof data?.detail === 'string' && data.detail) ||
      (Array.isArray(data?.non_field_errors) && data.non_field_errors.join(' ')) ||
      (data && typeof data === 'object'
        ? Object.values(data)
            .flat()
            .filter((v) => typeof v === 'string')
            .join(' ')
        : '')
    editor.error = detail || t('eligibilityRulesetsPage.saveError')
  } finally {
    editor.saving = false
  }
}

onMounted(fetchList)
</script>
