<template>
  <div class="scholarship-scoring-rulesets-page">
    <PageHeader
      :title="t('scholarshipScoringRulesetsPage.title')"
      :subtitle="t('scholarshipScoringRulesetsPage.subtitle')"
    >
      <template #breadcrumb>
        <PageBreadcrumb
          :aria-label="t('scholarshipScoringRulesetsPage.breadcrumbAria')"
          :items="[
            { to: { name: 'Dashboard' }, label: t('route.names.Dashboard') },
            { label: t('route.names.ScholarshipScoringRulesets') },
          ]"
        />
      </template>
      <template #actions>
        <button type="button" class="btn btn-outline-secondary" :disabled="loading" @click="fetchList">
          {{ t('adminCommon.refresh') }}
        </button>
        <button
          type="button"
          class="btn btn-primary"
          data-testid="scholarship-ruleset-create"
          @click="openCreate"
        >
          {{ t('scholarshipScoringRulesetsPage.create') }}
        </button>
      </template>
    </PageHeader>

    <RulesetListShell
      :loading="loading"
      :error="error"
      :empty="!loading && !error && rows.length === 0"
      :empty-body="t('scholarshipScoringRulesetsPage.empty')"
      :loading-label="t('adminCommon.loading')"
      :skeleton-columns="5"
      :items="rows"
      :columns="rulesetColumns"
      mobile-test-id="scholarship-ruleset"
    >
      <template #table>
        <div class="card" data-testid="scholarship-scoring-rulesets-page">
          <div class="table-responsive">
            <table class="table table-hover mb-0">
              <thead>
                <tr>
                  <th>{{ t('scholarshipScoringRulesetsPage.colLabel') }}</th>
                  <th>{{ t('scholarshipScoringRulesetsPage.colSlug') }}</th>
                  <th>{{ t('scholarshipScoringRulesetsPage.colActive') }}</th>
                  <th>{{ t('scholarshipScoringRulesetsPage.colUpdated') }}</th>
                  <th class="text-end">{{ t('adminCommon.actions') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in rows" :key="row.id">
                  <td>{{ row.label }}</td>
                  <td><code data-testid="scholarship-ruleset-slug">{{ row.slug }}</code></td>
                  <td>{{ row.is_active ? t('adminCommon.yes') : t('adminCommon.no') }}</td>
                  <td>{{ formatDate(row.updated_at) }}</td>
                  <td class="text-end">
                    <button
                      type="button"
                      class="btn btn-sm btn-outline-primary"
                      data-testid="scholarship-ruleset-edit"
                      @click="openEdit(row)"
                    >
                      {{ t('adminCommon.edit') }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </template>
      <template #col-slug="{ item }"><code data-testid="scholarship-ruleset-slug">{{ item.slug }}</code></template>
      <template #col-is_active="{ item }">{{ item.is_active ? t('adminCommon.yes') : t('adminCommon.no') }}</template>
      <template #col-updated_at="{ item }">{{ formatDate(item.updated_at) }}</template>
      <template #actions="{ item }">
        <button
          type="button"
          class="btn btn-sm btn-outline-primary"
          data-testid="scholarship-ruleset-edit"
          @click="openEdit(item)"
        >
          {{ t('adminCommon.edit') }}
        </button>
      </template>
    </RulesetListShell>

    <FormModal
      :open="editor.open"
      :title="editor.id ? t('scholarshipScoringRulesetsPage.editTitle') : t('scholarshipScoringRulesetsPage.create')"
      :error="editor.error"
      :saving="editor.saving"
      data-testid="scholarship-ruleset-editor"
      @close="editor.open = false"
      @submit="saveEditor"
    >
              <p class="small text-muted" data-testid="scholarship-ruleset-mvp-note">
                {{ t('scholarshipScoringRulesetsPage.mvpNote') }}
              </p>
              <div class="mb-3">
                <label class="form-label" for="ssr-label">{{
                  t('scholarshipScoringRulesetsPage.fieldLabel')
                }}</label>
                <input
                  id="ssr-label"
                  v-model.trim="editor.form.label"
                  class="form-control"
                  required
                  data-testid="scholarship-ruleset-label"
                />
              </div>
              <div class="mb-3">
                <label class="form-label" for="ssr-slug">{{
                  t('scholarshipScoringRulesetsPage.fieldSlug')
                }}</label>
                <input
                  id="ssr-slug"
                  v-model.trim="editor.form.slug"
                  class="form-control"
                  required
                  :disabled="!!editor.id"
                  data-testid="scholarship-ruleset-slug-input"
                />
              </div>
              <div class="mb-3">
                <label class="form-label" for="ssr-desc">{{
                  t('scholarshipScoringRulesetsPage.fieldDescription')
                }}</label>
                <textarea
                  id="ssr-desc"
                  v-model="editor.form.description"
                  class="form-control"
                  rows="2"
                ></textarea>
              </div>
              <div class="form-check mb-3">
                <input
                  id="ssr-active"
                  v-model="editor.form.is_active"
                  class="form-check-input"
                  type="checkbox"
                  data-testid="scholarship-ruleset-active"
                />
                <label class="form-check-label" for="ssr-active">{{
                  t('scholarshipScoringRulesetsPage.fieldActive')
                }}</label>
              </div>
              <h6 class="text-muted">{{ t('scholarshipScoringRulesetsPage.weightsHeading') }}</h6>
              <p class="small text-muted mb-2">
                {{ t('scholarshipScoringRulesetsPage.weightsHint', { total: weightsTotal }) }}
              </p>
              <div class="row g-3">
                <div v-for="fid in factorIds" :key="fid" class="col-md-6">
                  <label class="form-label" :for="`ssr-w-${fid}`">{{
                    t(`scholarshipScoringRulesetsPage.factors.${fid}`)
                  }}</label>
                  <input
                    :id="`ssr-w-${fid}`"
                    v-model.number="editor.form.factor_weights[fid]"
                    class="form-control"
                    type="number"
                    min="0.01"
                    max="200"
                    step="0.01"
                    required
                    :data-testid="`scholarship-weight-${fid}`"
                  />
                </div>
              </div>
    </FormModal>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import PageHeader from '@/components/PageHeader.vue'
import PageBreadcrumb from '@/components/PageBreadcrumb.vue'
import RulesetListShell from '@/components/RulesetListShell.vue'
import FormModal from '@/components/FormModal.vue'
import api from '@/services/api'
import { useToast } from '@/composables/useToast'

const { t, locale } = useI18n()
const toast = useToast()

const FACTOR_IDS = [
  'academic',
  'language',
  'program_fit',
  'application_quality',
  'timeliness',
]

const DEFAULT_WEIGHTS = {
  academic: 25,
  language: 20,
  program_fit: 15,
  application_quality: 25,
  timeliness: 15,
}

const loading = ref(true)
const error = ref('')
const rows = ref([])
const factorIds = FACTOR_IDS

const rulesetColumns = computed(() => [
  { key: 'label', label: t('scholarshipScoringRulesetsPage.colLabel') },
  { key: 'slug', label: t('scholarshipScoringRulesetsPage.colSlug') },
  { key: 'is_active', label: t('scholarshipScoringRulesetsPage.colActive') },
  { key: 'updated_at', label: t('scholarshipScoringRulesetsPage.colUpdated') },
])

const editor = reactive({
  open: false,
  id: null,
  saving: false,
  error: '',
  form: emptyForm(),
})

const weightsTotal = computed(() =>
  FACTOR_IDS.reduce((sum, fid) => sum + (Number(editor.form.factor_weights[fid]) || 0), 0),
)

function emptyForm() {
  return {
    label: '',
    slug: '',
    description: '',
    is_active: true,
    factor_weights: { ...DEFAULT_WEIGHTS },
  }
}

function formFromRow(row) {
  const weights = { ...DEFAULT_WEIGHTS, ...(row.factor_weights || {}) }
  return {
    label: row.label || '',
    slug: row.slug || '',
    description: row.description || '',
    is_active: row.is_active !== false,
    factor_weights: Object.fromEntries(
      FACTOR_IDS.map((fid) => [fid, Number(weights[fid]) || DEFAULT_WEIGHTS[fid]]),
    ),
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
    const { data } = await api.get('/api/scholarship-scoring-rulesets/', {
      params: { ordering: 'label' },
    })
    rows.value = data.results || data || []
  } catch {
    error.value = t('scholarshipScoringRulesetsPage.loadError')
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editor.open = true
  editor.id = null
  editor.error = ''
  editor.form = emptyForm()
}

function openEdit(row) {
  editor.open = true
  editor.id = row.id
  editor.error = ''
  editor.form = formFromRow(row)
}

async function saveEditor() {
  editor.saving = true
  editor.error = ''
  const payload = {
    label: editor.form.label,
    description: editor.form.description,
    is_active: editor.form.is_active,
    factor_weights: { ...editor.form.factor_weights },
  }
  if (!editor.id) {
    payload.slug = editor.form.slug
  }
  try {
    if (editor.id) {
      await api.patch(`/api/scholarship-scoring-rulesets/${editor.id}/`, payload)
      toast.success(t('scholarshipScoringRulesetsPage.toastSaved'))
    } else {
      await api.post('/api/scholarship-scoring-rulesets/', payload)
      toast.success(t('scholarshipScoringRulesetsPage.toastCreated'))
    }
    editor.open = false
    await fetchList()
  } catch (err) {
    const data = err?.response?.data
    editor.error =
      (typeof data === 'object' && data && (data.detail || data.slug?.[0] || data.factor_weights)) ||
      t('scholarshipScoringRulesetsPage.saveError')
    if (typeof editor.error !== 'string') {
      editor.error = t('scholarshipScoringRulesetsPage.saveError')
    }
  } finally {
    editor.saving = false
  }
}

onMounted(fetchList)
</script>
