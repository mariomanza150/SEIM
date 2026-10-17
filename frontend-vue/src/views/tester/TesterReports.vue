<template>
  <div class="container-fluid py-3" data-testid="qa-reports-page">
    <div class="d-flex flex-wrap align-items-center justify-content-between gap-2 mb-3">
      <h1 class="h3 mb-0">{{ t('qa.reports.title') }}</h1>
      <button v-if="qa.isTester" type="button" class="btn btn-warning btn-sm" @click="openWidget">
        <i class="bi bi-bug me-1" aria-hidden="true" />{{ t('qa.widget.open') }}
      </button>
    </div>
    <TesterNotAvailable v-if="qa.loaded && !qa.isTester" />
    <template v-else>
      <div class="d-flex flex-wrap gap-3 align-items-center mb-3">
        <div class="form-check form-switch">
          <input id="qa-open-only" v-model="openOnly" class="form-check-input" type="checkbox" @change="load" />
          <label class="form-check-label" for="qa-open-only">{{ t('qa.reports.openOnly') }}</label>
        </div>
        <div v-if="qa.isTriager" class="btn-group btn-group-sm" role="group">
          <button type="button" class="btn" :class="scope === 'all' ? 'btn-primary' : 'btn-outline-primary'" @click="setScope('all')">
            {{ t('qa.reports.scopeAll') }}
          </button>
          <button type="button" class="btn" :class="scope === 'mine' ? 'btn-primary' : 'btn-outline-primary'" @click="setScope('mine')">
            {{ t('qa.reports.scopeMine') }}
          </button>
        </div>
      </div>
      <div v-if="loading" class="text-muted">{{ t('qa.common.loading') }}</div>
      <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
      <p v-else-if="!items.length" class="text-muted" data-testid="qa-reports-empty">{{ t('qa.reports.empty') }}</p>
      <div v-else class="table-responsive">
        <table class="table table-hover align-middle" data-testid="qa-reports-table">
          <thead>
            <tr>
              <th scope="col">#</th>
              <th scope="col">{{ t('qa.fields.title') }}</th>
              <th scope="col">{{ t('qa.fields.severity') }}</th>
              <th scope="col">{{ t('qa.fields.status') }}</th>
              <th v-if="qa.isTriager" scope="col">{{ t('qa.fields.reporter') }}</th>
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
              <td>{{ t(`qa.status.${it.status}`) }}</td>
              <td v-if="qa.isTriager">{{ it.reporter?.email }}</td>
              <td class="text-nowrap small">{{ formatDate(it.created_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { useQaStore } from '@/stores/qa'
import { listIssues } from '@/qa/api'
import { severityClass } from '@/qa/format'
import TesterNotAvailable from './TesterNotAvailable.vue'

const { t, locale } = useI18n()
const qa = useQaStore()
const route = useRoute()
const items = ref([])
const loading = ref(false)
const error = ref('')
const openOnly = ref(false)
const scope = ref('all')

function formatDate(v) {
  return v ? new Date(v).toLocaleString(locale.value) : ''
}

function openWidget() {
  window.dispatchEvent(new CustomEvent('seim:qa-report'))
}

function setScope(s) {
  scope.value = s
  load()
}

async function load() {
  await qa.load()
  if (!qa.isTester) return
  loading.value = true
  error.value = ''
  try {
    const params = { page_size: 100 }
    if (openOnly.value) params.open = 1
    if (!qa.isTriager || scope.value === 'mine') params.mine = 1
    const { data } = await listIssues(params)
    items.value = Array.isArray(data) ? data : data.results || []
  } catch {
    error.value = t('qa.common.loadFailed')
  } finally {
    loading.value = false
  }
}

onMounted(load)
watch(() => route.query.r, load)
</script>
