<template>
  <div class="container-fluid py-3" data-testid="qa-outbox-page">
    <h1 class="h3 mb-1">{{ t('qa.outbox.title') }}</h1>
    <p class="text-muted mb-3">{{ t('qa.outbox.intro') }}</p>
    <TesterNotAvailable v-if="qa.loaded && !qa.isTester" />
    <template v-else>
      <div v-if="loaded && !capturing" class="alert alert-warning" data-testid="qa-outbox-not-capturing">
        {{ t('qa.outbox.notCapturing') }}
      </div>
      <div class="d-flex gap-2 mb-3">
        <input
          v-model="q"
          type="search"
          class="form-control form-control-sm"
          style="max-width: 22rem"
          :placeholder="t('qa.outbox.search')"
          :aria-label="t('qa.outbox.search')"
          @keyup.enter="load"
        />
        <button type="button" class="btn btn-outline-secondary btn-sm" @click="load">
          <i class="bi bi-arrow-clockwise me-1" aria-hidden="true" />{{ t('qa.outbox.refresh') }}
        </button>
      </div>
      <div v-if="error" class="alert alert-danger">{{ error }}</div>
      <div class="row g-3">
        <div class="col-12 col-lg-5">
          <div v-if="loading" class="text-muted">{{ t('qa.common.loading') }}</div>
          <p v-else-if="!items.length" class="text-muted" data-testid="qa-outbox-empty">{{ t('qa.outbox.empty') }}</p>
          <div v-else class="list-group" data-testid="qa-outbox-list">
            <button
              v-for="m in items"
              :key="m.id"
              type="button"
              class="list-group-item list-group-item-action"
              :class="{ active: selected?.id === m.id }"
              @click="open(m.id)"
            >
              <div class="fw-semibold text-break">{{ m.subject || t('qa.outbox.noSubject') }}</div>
              <div class="small text-break">{{ t('qa.outbox.to') }}: {{ (m.to || []).join(', ') }}</div>
              <div class="small opacity-75">{{ formatDate(m.created_at) }}</div>
            </button>
          </div>
        </div>
        <div class="col-12 col-lg-7">
          <div v-if="selected" class="card" data-testid="qa-outbox-detail">
            <div class="card-body">
              <h2 class="h5 text-break">{{ selected.subject || t('qa.outbox.noSubject') }}</h2>
              <dl class="row small mb-2">
                <dt class="col-3">{{ t('qa.outbox.from') }}</dt><dd class="col-9 text-break">{{ selected.from_email }}</dd>
                <dt class="col-3">{{ t('qa.outbox.to') }}</dt><dd class="col-9 text-break">{{ (selected.to || []).join(', ') }}</dd>
                <template v-if="selected.cc?.length">
                  <dt class="col-3">Cc</dt><dd class="col-9 text-break">{{ selected.cc.join(', ') }}</dd>
                </template>
              </dl>
              <div v-if="selected.body_html" class="btn-group btn-group-sm mb-2" role="group">
                <button type="button" class="btn" :class="view === 'html' ? 'btn-primary' : 'btn-outline-primary'" @click="view = 'html'">HTML</button>
                <button type="button" class="btn" :class="view === 'text' ? 'btn-primary' : 'btn-outline-primary'" @click="view = 'text'">{{ t('qa.outbox.text') }}</button>
              </div>
              <!-- Sandboxed: no scripts, no same-origin access. -->
              <iframe
                v-if="selected.body_html && view === 'html'"
                :srcdoc="selected.body_html"
                sandbox=""
                referrerpolicy="no-referrer"
                class="w-100 border rounded bg-white"
                style="min-height: 28rem"
                :title="t('qa.outbox.preview')"
                data-testid="qa-outbox-iframe"
              />
              <pre v-else class="small bg-body-tertiary p-2 rounded text-wrap" data-testid="qa-outbox-text">{{ selected.body_text }}</pre>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useQaStore } from '@/stores/qa'
import { getOutboxMessage, listOutbox } from '@/qa/api'
import TesterNotAvailable from './TesterNotAvailable.vue'

const { t, locale } = useI18n()
const qa = useQaStore()
const items = ref([])
const selected = ref(null)
const capturing = ref(true)
const loaded = ref(false)
const loading = ref(false)
const error = ref('')
const q = ref('')
const view = ref('html')

function formatDate(v) {
  return v ? new Date(v).toLocaleString(locale.value) : ''
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await listOutbox(q.value ? { q: q.value } : {})
    items.value = data.results || []
    capturing.value = Boolean(data.capturing)
    loaded.value = true
  } catch {
    error.value = t('qa.common.loadFailed')
  } finally {
    loading.value = false
  }
}

async function open(id) {
  try {
    const { data } = await getOutboxMessage(id)
    selected.value = data
    view.value = data.body_html ? 'html' : 'text'
  } catch {
    error.value = t('qa.common.loadFailed')
  }
}

onMounted(async () => {
  await qa.load()
  if (qa.isTester) await load()
})
</script>
