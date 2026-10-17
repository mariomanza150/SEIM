<template>
  <div class="container-fluid py-3" data-testid="qa-checklist-page">
    <div class="d-flex flex-wrap align-items-center justify-content-between gap-2 mb-1">
      <h1 class="h3 mb-0">{{ t('qa.checklist.title') }}</h1>
      <div v-if="qa.isTriager" class="btn-group btn-group-sm" role="group">
        <button type="button" class="btn" :class="tab === 'mine' ? 'btn-primary' : 'btn-outline-primary'" @click="setTab('mine')">
          {{ t('qa.checklist.myRun') }}
        </button>
        <button type="button" class="btn" :class="tab === 'matrix' ? 'btn-primary' : 'btn-outline-primary'" data-testid="qa-checklist-matrix-tab" @click="setTab('matrix')">
          {{ t('qa.checklist.matrix') }}
        </button>
      </div>
    </div>
    <p class="text-muted mb-3">{{ t('qa.checklist.intro', { build: shortCommit(build) || '—' }) }}</p>
    <TesterNotAvailable v-if="qa.loaded && !qa.isTester" />
    <template v-else>
      <div v-if="error" class="alert alert-danger">{{ error }}</div>
      <div v-if="loading" class="text-muted">{{ t('qa.common.loading') }}</div>

      <template v-else-if="tab === 'mine'">
        <div class="d-flex flex-wrap gap-2 mb-3 small" data-testid="qa-checklist-summary">
          <span v-for="k in SUMMARY_KEYS" :key="k" class="badge" :class="outcomeClass(k)">
            {{ t(`qa.checklist.outcome.${k}`) }}: {{ summary[k] || 0 }}
          </span>
        </div>
        <div class="mb-3" style="max-width: 16rem">
          <label for="qa-cl-area" class="form-label small">{{ t('qa.checklist.area') }}</label>
          <select id="qa-cl-area" v-model="area" class="form-select form-select-sm">
            <option value="">{{ t('qa.checklist.allAreas') }}</option>
            <option v-for="a in areas" :key="a" :value="a">{{ a }}</option>
          </select>
        </div>
        <div class="list-group">
          <div v-for="s in visible" :key="s.id" class="list-group-item" :data-testid="`qa-scenario-${s.code}`">
            <div class="d-flex flex-wrap justify-content-between gap-2">
              <div>
                <span class="badge text-bg-light border me-1">{{ s.code }}</span>
                <strong>{{ s.title }}</strong>
                <span v-if="s.role" class="badge text-bg-secondary ms-1">{{ roleLabel(s.role) }}</span>
              </div>
              <span v-if="s.result" class="badge" :class="outcomeClass(s.result.outcome)">
                {{ t(`qa.checklist.outcome.${s.result.outcome}`) }}
                <template v-if="s.result.issue_number"> · QA-{{ s.result.issue_number }}</template>
              </span>
            </div>
            <details class="small mt-1">
              <summary>{{ t('qa.checklist.howTo') }}</summary>
              <p class="mb-1 mt-1 seim-qa-text"><strong>{{ t('qa.fields.steps') }}:</strong> {{ s.steps }}</p>
              <p class="mb-0 seim-qa-text"><strong>{{ t('qa.checklist.expected') }}:</strong> {{ s.expected }}</p>
            </details>
            <div class="d-flex flex-wrap align-items-center gap-1 mt-2">
              <button
                v-for="o in OUTCOMES"
                :key="o"
                type="button"
                class="btn btn-sm"
                :class="s.result?.outcome === o ? outcomeBtn(o) : 'btn-outline-secondary'"
                :disabled="busy === s.id"
                :data-testid="`qa-scenario-${s.code}-${o}`"
                @click="record(s, o)"
              >
                {{ t(`qa.checklist.outcome.${o}`) }}
              </button>
              <button v-if="s.result" type="button" class="btn btn-sm btn-link" :disabled="busy === s.id" @click="clear(s)">
                {{ t('qa.checklist.clear') }}
              </button>
              <button
                v-if="s.result?.outcome === 'fail' && !s.result.issue_number"
                type="button"
                class="btn btn-sm btn-warning ms-auto"
                @click="reportFor(s)"
              >
                <i class="bi bi-bug me-1" aria-hidden="true" />{{ t('qa.checklist.reportFailure') }}
              </button>
            </div>
            <div v-if="s.result?.outcome === 'fail' || s.result?.outcome === 'blocked'" class="row g-2 mt-1">
              <div class="col-8 col-md-6">
                <input
                  v-model="notes[s.id]"
                  class="form-control form-control-sm"
                  :placeholder="t('qa.checklist.note')"
                  :aria-label="t('qa.checklist.note')"
                />
              </div>
              <div class="col-4 col-md-2">
                <input
                  v-model="issueNumbers[s.id]"
                  type="number"
                  min="1"
                  class="form-control form-control-sm"
                  :placeholder="t('qa.checklist.reportNumber')"
                  :aria-label="t('qa.checklist.reportNumber')"
                />
              </div>
              <div class="col-12 col-md-2">
                <button type="button" class="btn btn-sm btn-outline-primary" @click="record(s, s.result.outcome)">{{ t('qa.triage.save') }}</button>
              </div>
            </div>
          </div>
        </div>
      </template>

      <template v-else>
        <div class="table-responsive" data-testid="qa-checklist-matrix">
          <table class="table table-sm align-middle">
            <thead>
              <tr>
                <th scope="col">{{ t('qa.checklist.scenario') }}</th>
                <th v-for="b in matrix.builds" :key="b" scope="col" class="text-nowrap">
                  {{ shortCommit(b) || '—' }}<span v-if="b === matrix.current" class="badge text-bg-info ms-1">{{ t('qa.checklist.current') }}</span>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in matrix.results" :key="row.id">
                <td><span class="badge text-bg-light border me-1">{{ row.code }}</span>{{ row.title }}</td>
                <td v-for="b in matrix.builds" :key="b">
                  <span v-if="row.builds[b]" class="badge" :class="outcomeClass(row.builds[b].outcome)" :title="countsTitle(row.builds[b].counts)">
                    {{ t(`qa.checklist.outcome.${row.builds[b].outcome}`) }}
                  </span>
                  <span v-else class="text-muted small">—</span>
                  <span v-for="n in row.builds[b]?.issues || []" :key="n" class="small ms-1">QA-{{ n }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useQaStore } from '@/stores/qa'
import { clearScenarioResult, getScenarioMatrix, listScenarios, saveScenarioResult } from '@/qa/api'
import { shortCommit } from '@/qa/buildInfo'
import TesterNotAvailable from './TesterNotAvailable.vue'

const { t, te, locale } = useI18n()
const qa = useQaStore()
const OUTCOMES = ['pass', 'fail', 'blocked', 'skipped']
const SUMMARY_KEYS = ['todo', ...OUTCOMES]
const tab = ref('mine')
const rows = ref([])
const summary = ref({})
const build = ref('')
const matrix = ref({ builds: [], results: [], current: '' })
const loading = ref(false)
const error = ref('')
const busy = ref(null)
const area = ref('')
const notes = reactive({})
const issueNumbers = reactive({})

const areas = computed(() => [...new Set(rows.value.map((r) => r.area))])
const visible = computed(() => (area.value ? rows.value.filter((r) => r.area === area.value) : rows.value))

function roleLabel(role) {
  return te(`qa.roles.${role}`) ? t(`qa.roles.${role}`) : role
}
function outcomeClass(o) {
  return { pass: 'text-bg-success', fail: 'text-bg-danger', blocked: 'text-bg-warning', skipped: 'text-bg-secondary', todo: 'text-bg-light border' }[o] || 'text-bg-light'
}
function outcomeBtn(o) {
  return { pass: 'btn-success', fail: 'btn-danger', blocked: 'btn-warning', skipped: 'btn-secondary' }[o]
}
function countsTitle(counts) {
  return Object.entries(counts || {})
    .map(([k, v]) => `${t(`qa.checklist.outcome.${k}`)}: ${v}`)
    .join(', ')
}
function lang() {
  return String(locale.value || 'en').slice(0, 2)
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    if (tab.value === 'matrix') {
      const { data } = await getScenarioMatrix({ lang: lang() })
      matrix.value = data
      build.value = data.current
    } else {
      const { data } = await listScenarios({ lang: lang() })
      rows.value = data.results || []
      summary.value = data.summary || {}
      build.value = data.build
      for (const r of rows.value) {
        notes[r.id] = r.result?.note || ''
        issueNumbers[r.id] = r.result?.issue_number || ''
      }
    }
  } catch {
    error.value = t('qa.common.loadFailed')
  } finally {
    loading.value = false
  }
}

function recount() {
  const s = {}
  for (const r of rows.value) {
    const k = r.result?.outcome || 'todo'
    s[k] = (s[k] || 0) + 1
  }
  summary.value = s
}

async function record(s, outcome) {
  busy.value = s.id
  error.value = ''
  try {
    const payload = { outcome, note: notes[s.id] || '' }
    if (issueNumbers[s.id]) payload.issue_number = issueNumbers[s.id]
    const { data } = await saveScenarioResult(s.id, payload)
    s.result = data
    recount()
  } catch (e) {
    const body = e?.response?.data
    error.value = body && typeof body === 'object' ? Object.values(body).flat().join(' ') : t('qa.triage.saveFailed')
  } finally {
    busy.value = null
  }
}

async function clear(s) {
  busy.value = s.id
  try {
    await clearScenarioResult(s.id)
    s.result = null
    notes[s.id] = ''
    issueNumbers[s.id] = ''
    recount()
  } finally {
    busy.value = null
  }
}

function reportFor(s) {
  window.dispatchEvent(
    new CustomEvent('seim:qa-report', {
      detail: { title: `${s.code}: ${s.title}`, steps: `${s.steps}\n\nExpected: ${s.expected}\nActual: ` },
    }),
  )
}

function setTab(v) {
  tab.value = v
  load()
}

onMounted(async () => {
  await qa.load()
  if (qa.isTester) await load()
})
</script>

<style scoped>
.seim-qa-text {
  white-space: pre-wrap;
}
</style>
