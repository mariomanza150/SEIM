<template>
  <div class="container-fluid py-3" data-testid="qa-triage-page">
    <h1 class="h3 mb-1">{{ t('qa.triage.title') }}</h1>
    <p class="text-muted mb-3">{{ t('qa.triage.intro') }}</p>
    <TesterNotAvailable v-if="qa.loaded && !qa.isTriager" />
    <template v-else>
      <form class="row g-2 align-items-end mb-3" @submit.prevent="load">
        <div class="col-12 col-md-3">
          <label for="qa-tg-q" class="form-label small">{{ t('qa.triage.search') }}</label>
          <input id="qa-tg-q" v-model.trim="filters.search" type="search" class="form-control form-control-sm" />
        </div>
        <div class="col-6 col-md-2">
          <label for="qa-tg-status" class="form-label small">{{ t('qa.fields.status') }}</label>
          <select id="qa-tg-status" v-model="filters.status" class="form-select form-select-sm" @change="load">
            <option value="">{{ t('qa.triage.openStatuses') }}</option>
            <option value="all">{{ t('qa.triage.anyStatus') }}</option>
            <option v-for="s in STATUSES" :key="s" :value="s">{{ t(`qa.status.${s}`) }}</option>
          </select>
        </div>
        <div class="col-6 col-md-2">
          <label for="qa-tg-sev" class="form-label small">{{ t('qa.fields.severity') }}</label>
          <select id="qa-tg-sev" v-model="filters.severity" class="form-select form-select-sm" @change="load">
            <option value="">{{ t('qa.triage.anySeverity') }}</option>
            <option v-for="s in SEVERITIES" :key="s" :value="s">{{ t(`qa.severity.${s}`) }}</option>
          </select>
        </div>
        <div class="col-6 col-md-2">
          <label for="qa-tg-assigned" class="form-label small">{{ t('qa.triage.assignee') }}</label>
          <select id="qa-tg-assigned" v-model="filters.assigned" class="form-select form-select-sm" @change="load">
            <option value="">{{ t('qa.triage.anyone') }}</option>
            <option value="me">{{ t('qa.triage.assignedToMe') }}</option>
            <option value="none">{{ t('qa.triage.unassigned') }}</option>
          </select>
        </div>
        <div class="col-6 col-md-1">
          <button type="submit" class="btn btn-outline-primary btn-sm w-100">{{ t('qa.triage.apply') }}</button>
        </div>
      </form>
      <div v-if="error" class="alert alert-danger">{{ error }}</div>
      <div v-if="loading" class="text-muted">{{ t('qa.common.loading') }}</div>
      <p v-else-if="!items.length" class="text-muted" data-testid="qa-triage-empty">{{ t('qa.triage.empty') }}</p>
      <div v-else class="table-responsive">
        <table class="table table-sm table-hover align-middle" data-testid="qa-triage-table">
          <thead>
            <tr>
              <th scope="col">#</th>
              <th scope="col">{{ t('qa.fields.title') }}</th>
              <th scope="col">{{ t('qa.fields.severity') }}</th>
              <th scope="col">{{ t('qa.fields.status') }}</th>
              <th scope="col">{{ t('qa.triage.assignee') }}</th>
              <th scope="col">{{ t('qa.fields.reporter') }}</th>
              <th scope="col">{{ t('qa.reports.version') }}</th>
              <th scope="col">{{ t('qa.fields.created') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="it in items" :key="it.id">
              <td class="text-nowrap">{{ it.reference }}</td>
              <td>
                <router-link :to="{ name: 'TesterReportDetail', params: { id: it.id } }">{{ it.title }}</router-link>
                <i v-if="it.attachment_count" class="bi bi-paperclip ms-1 text-muted" :aria-label="t('qa.widget.attachments')" />
              </td>
              <td><span class="badge" :class="severityClass(it.severity)">{{ t(`qa.severity.${it.severity}`) }}</span></td>
              <td style="min-width: 9rem">
                <select
                  class="form-select form-select-sm"
                  :value="it.status"
                  :aria-label="t('qa.fields.status')"
                  :data-testid="`qa-triage-status-${it.number}`"
                  @change="setStatus(it, $event.target.value)"
                >
                  <option v-for="s in STATUSES" :key="s" :value="s">{{ t(`qa.status.${s}`) }}</option>
                </select>
              </td>
              <td class="small">{{ it.assignee?.email || '—' }}</td>
              <td class="small">{{ it.reporter?.email }}<span v-if="it.reporter_role" class="text-muted"> ({{ it.reporter_role }})</span></td>
              <td class="small text-nowrap">{{ shortCommit(it.build_commit) || it.app_version }}</td>
              <td class="small text-nowrap">{{ formatDate(it.created_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useQaStore } from '@/stores/qa'
import { listIssues, updateIssue } from '@/qa/api'
import { severityClass } from '@/qa/format'
import { shortCommit } from '@/qa/buildInfo'
import { useToast } from '@/composables/useToast'
import TesterNotAvailable from './TesterNotAvailable.vue'

const { t, locale } = useI18n()
const qa = useQaStore()
const toast = useToast()
const STATUSES = ['new', 'triaged', 'in_progress', 'needs_info', 'fixed', 'verified', 'closed', 'wont_fix', 'duplicate']
const SEVERITIES = ['blocker', 'major', 'minor', 'cosmetic']
const items = ref([])
const loading = ref(false)
const error = ref('')
const filters = reactive({ search: '', status: '', severity: '', assigned: '' })

function formatDate(v) {
  return v ? new Date(v).toLocaleString(locale.value) : ''
}

function params() {
  const p = { page_size: 100 }
  if (filters.search) p.search = filters.search
  if (filters.status === '') p.open = 1
  else if (filters.status !== 'all') p.status = filters.status
  if (filters.severity) p.severity = filters.severity
  if (filters.assigned) p.assigned = filters.assigned
  return p
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await listIssues(params())
    items.value = Array.isArray(data) ? data : data.results || []
  } catch {
    error.value = t('qa.common.loadFailed')
  } finally {
    loading.value = false
  }
}

async function setStatus(it, status) {
  const previous = it.status
  it.status = status
  try {
    await updateIssue(it.id, { status })
    toast.success(t('qa.triage.saved'))
  } catch {
    it.status = previous
    toast.error(t('qa.triage.saveFailed'))
  }
}

onMounted(async () => {
  await qa.load()
  if (qa.isTriager) await load()
})
</script>
