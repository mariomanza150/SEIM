<template>
  <div class="toefl-practice-page" data-testid="toefl-practice-page">
    <PageHeader
      :title="t('route.names.ToeflPractice')"
      :subtitle="t('toeflPracticePage.subtitle')"
      icon-class="bi bi-journal-text"
      test-id="toefl-practice-heading"
    >
      <template #breadcrumb>
        <PageBreadcrumb
          :aria-label="t('toeflPracticePage.breadcrumbAria')"
          :items="[
            { to: { name: 'Dashboard' }, label: t('route.names.Dashboard') },
            { label: t('route.names.ToeflPractice') },
          ]"
        />
      </template>
      <template #actions>
        <button
          type="button"
          class="btn btn-primary"
          data-testid="toefl-start-practice"
          :disabled="launching || syncing"
          @click="startPractice"
        >
          <span
            v-if="launching"
            class="spinner-border spinner-border-sm me-1"
            role="status"
            aria-hidden="true"
          />
          {{ t('toeflPracticePage.startButton') }}
        </button>
      </template>
    </PageHeader>

    <p class="text-muted small mb-3" data-testid="toefl-disclaimer">
      {{ t('toeflPracticePage.disclaimer') }}
    </p>

    <div
      v-if="returnNotice"
      class="alert"
      :class="syncTimedOut ? 'alert-warning' : 'alert-info'"
      data-testid="toefl-return-notice"
      role="status"
    >
      <div class="d-flex flex-wrap align-items-center gap-2 justify-content-between">
        <span>{{ returnNotice }}</span>
        <button
          v-if="syncTimedOut"
          type="button"
          class="btn btn-sm btn-outline-secondary"
          data-testid="toefl-sync-retry"
          @click="retrySync"
        >
          {{ t('toeflPracticePage.retrySync') }}
        </button>
      </div>
    </div>
    <div v-if="launchError" class="alert alert-danger" role="alert" data-testid="toefl-error">
      {{ launchError }}
    </div>

    <div class="card border-0 shadow-sm">
      <div class="card-body">
        <h3 class="h5 mb-3">{{ t('toeflPracticePage.historyHeading') }}</h3>
        <PageStateShell
          :loading="loading && !attempts.length"
          :error="error"
          :empty="!loading && !error && !attempts.length"
          :empty-body="t('toeflPracticePage.empty')"
          empty-test-id="toefl-empty"
          :loading-label="t('toeflPracticePage.loading')"
          skeleton="table"
          :skeleton-columns="5"
          :skeleton-rows="4"
        >
          <template #emptyActions>
            <button
              type="button"
              class="btn btn-primary"
              data-testid="toefl-empty-cta"
              :disabled="launching || syncing"
              @click="startPractice"
            >
              {{ t('toeflPracticePage.emptyCtaStart') }}
            </button>
          </template>
          <div class="table-responsive">
            <table class="table table-sm align-middle mb-0" data-testid="toefl-attempts-table">
              <thead>
                <tr>
                  <th scope="col" class="w-1" />
                  <th scope="col">{{ t('toeflPracticePage.colDate') }}</th>
                  <th scope="col">{{ t('toeflPracticePage.colExam') }}</th>
                  <th scope="col">{{ t('toeflPracticePage.colScore') }}</th>
                  <th scope="col">{{ t('toeflPracticePage.colWeak') }}</th>
                </tr>
              </thead>
              <tbody>
                <template v-for="row in attempts" :key="row.id">
                  <tr
                    :data-session-id="row.external_session_id"
                    :class="{ 'table-success': row.external_session_id === highlightedSession }"
                    data-testid="toefl-attempt-row"
                  >
                    <td>
                      <button
                        type="button"
                        class="btn btn-sm btn-link p-0"
                        :aria-expanded="expandedId === row.id"
                        :aria-label="t('toeflPracticePage.toggleDetails')"
                        data-testid="toefl-expand-row"
                        @click="toggleDetail(row)"
                      >
                        <i
                          class="bi"
                          :class="expandedId === row.id ? 'bi-chevron-down' : 'bi-chevron-right'"
                          aria-hidden="true"
                        />
                      </button>
                    </td>
                    <td>{{ formatDate(row.completed_at || row.created_at) }}</td>
                    <td>{{ row.exam_code || '—' }}</td>
                    <td>{{ formatScore(row) }}</td>
                    <td>{{ formatWeak(row.weakest) }}</td>
                  </tr>
                  <tr v-if="expandedId === row.id" :data-testid="`toefl-detail-${row.id}`">
                    <td colspan="5" class="bg-body-tertiary">
                      <div v-if="detailLoadingId === row.id" class="text-muted small py-2">
                        {{ t('toeflPracticePage.detailLoading') }}
                      </div>
                      <div v-else-if="detailErrorId === row.id" class="text-danger small py-2">
                        {{ t('toeflPracticePage.detailError') }}
                      </div>
                      <div v-else-if="detailsById[row.id]" class="py-2 small">
                        <p class="fw-semibold mb-2">{{ t('toeflPracticePage.categoriesHeading') }}</p>
                        <ul
                          v-if="categoryRows(detailsById[row.id]).length"
                          class="mb-3"
                          data-testid="toefl-detail-categories"
                        >
                          <li v-for="(cat, idx) in categoryRows(detailsById[row.id])" :key="idx">
                            {{ cat }}
                          </li>
                        </ul>
                        <p v-else class="text-muted mb-3">{{ t('toeflPracticePage.noCategories') }}</p>

                        <p class="fw-semibold mb-2">{{ t('toeflPracticePage.itemsHeading') }}</p>
                        <ul
                          v-if="itemRows(detailsById[row.id]).length"
                          class="mb-0"
                          data-testid="toefl-detail-items"
                        >
                          <li v-for="(item, idx) in itemRows(detailsById[row.id])" :key="idx">
                            {{ item }}
                          </li>
                        </ul>
                        <p v-else class="text-muted mb-0">{{ t('toeflPracticePage.noItems') }}</p>
                      </div>
                    </td>
                  </tr>
                </template>
              </tbody>
            </table>
          </div>
        </PageStateShell>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import PageHeader from '@/components/PageHeader.vue'
import PageBreadcrumb from '@/components/PageBreadcrumb.vue'
import PageStateShell from '@/components/State/PageStateShell.vue'
import api from '@/services/api'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const attempts = ref([])
const loading = ref(true)
const launching = ref(false)
const syncing = ref(false)
const syncTimedOut = ref(false)
const error = ref('')
const launchError = ref('')
const returnNotice = ref('')
const highlightedSession = ref('')
const expandedId = ref('')
const detailLoadingId = ref('')
const detailErrorId = ref('')
const detailsById = ref({})
let pollTimer = null
let pendingSessionId = ''

const MAX_POLL_TRIES = 8
const POLL_MS = 1500

function formatDate(value) {
  if (!value) return '—'
  try {
    return new Date(value).toLocaleString()
  } catch {
    return String(value)
  }
}

function formatScore(row) {
  const pct = row.percent != null ? Number(row.percent).toFixed(1) : '—'
  return `${row.earned ?? 0}/${row.total ?? 0} (${pct}%)`
}

function formatWeak(weakest) {
  if (!Array.isArray(weakest) || !weakest.length) return '—'
  return weakest
    .map((w) => (typeof w === 'string' ? w : w?.name || w?.category || ''))
    .filter(Boolean)
    .slice(0, 3)
    .join(', ')
}

function categoryRows(detail) {
  const cats = detail?.categories
  if (!Array.isArray(cats)) return []
  return cats.map((c) => {
    if (typeof c === 'string') return c
    const name = c?.name || c?.category || '—'
    const earned = c?.earned
    const total = c?.total
    const pct = c?.percent ?? c?.acc
    const score =
      earned != null && total != null
        ? `${earned}/${total}`
        : pct != null
          ? `${Number(pct).toFixed(1)}%`
          : ''
    return score ? `${name}: ${score}` : name
  })
}

function itemRows(detail) {
  const items = detail?.items
  if (!Array.isArray(items)) return []
  return items.slice(0, 20).map((item, idx) => {
    if (typeof item === 'string') return item
    const q = item?.question_id || item?.id || `#${idx + 1}`
    const correct = item?.is_correct
    const label =
      correct === true ? t('toeflPracticePage.itemCorrect') : correct === false ? t('toeflPracticePage.itemIncorrect') : ''
    const cat = item?.category || ''
    return [q, cat, label].filter(Boolean).join(' — ')
  })
}

function mapApiError(err, fallbackKey) {
  const status = err?.response?.status
  const detail = err?.response?.data?.detail
  if (status === 503) return t('toeflPracticePage.configError')
  if (typeof detail === 'string' && detail.trim()) return detail
  return t(fallbackKey)
}

async function fetchAttempts({ quiet = false } = {}) {
  if (!quiet) loading.value = true
  if (!quiet) error.value = ''
  try {
    const { data } = await api.get('/api/toefl/attempts/')
    attempts.value = data.results || data || []
  } catch (err) {
    error.value = mapApiError(err, 'toeflPracticePage.loadError')
    attempts.value = []
  } finally {
    if (!quiet) loading.value = false
  }
}

async function toggleDetail(row) {
  if (expandedId.value === row.id) {
    expandedId.value = ''
    return
  }
  expandedId.value = row.id
  if (detailsById.value[row.id]) return
  detailLoadingId.value = row.id
  detailErrorId.value = ''
  try {
    const { data } = await api.get(`/api/toefl/attempts/${row.id}/`)
    detailsById.value = { ...detailsById.value, [row.id]: data }
  } catch {
    detailErrorId.value = row.id
  } finally {
    detailLoadingId.value = ''
  }
}

async function startPractice() {
  launching.value = true
  launchError.value = ''
  try {
    const { data } = await api.post('/api/toefl/launch/', { n: 20 })
    if (!data?.launch_url) {
      throw new Error('missing launch_url')
    }
    window.location.assign(data.launch_url)
  } catch (err) {
    launchError.value = mapApiError(err, 'toeflPracticePage.launchError')
    launching.value = false
  }
}

function clearReturnQuery() {
  if (!route.query.session_id && !route.query.client_ref) return
  const nextQuery = { ...route.query }
  delete nextQuery.session_id
  delete nextQuery.client_ref
  router.replace({ name: 'ToeflPractice', query: nextQuery })
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

function onSyncSuccess(sessionId) {
  stopPolling()
  syncing.value = false
  syncTimedOut.value = false
  returnNotice.value = t('toeflPracticePage.syncSuccess')
  highlightedSession.value = sessionId
  window.setTimeout(() => {
    if (returnNotice.value === t('toeflPracticePage.syncSuccess')) {
      returnNotice.value = ''
    }
  }, 4000)
}

function onSyncTimeout() {
  stopPolling()
  syncing.value = false
  syncTimedOut.value = true
  returnNotice.value = t('toeflPracticePage.syncTimeout')
}

async function pollForSession(sessionId) {
  let tries = 0
  const poll = async () => {
    tries += 1
    await fetchAttempts({ quiet: true })
    const found = attempts.value.some((a) => a.external_session_id === sessionId)
    if (found) {
      onSyncSuccess(sessionId)
      return
    }
    if (tries >= MAX_POLL_TRIES) {
      onSyncTimeout()
    }
  }
  await poll()
  if (syncing.value) {
    pollTimer = setInterval(poll, POLL_MS)
  }
}

async function handleReturnLanding() {
  const sessionId = typeof route.query.session_id === 'string' ? route.query.session_id : ''
  if (!sessionId) return
  pendingSessionId = sessionId
  highlightedSession.value = sessionId
  syncing.value = true
  syncTimedOut.value = false
  returnNotice.value = t('toeflPracticePage.returnNotice')
  clearReturnQuery()
  await pollForSession(sessionId)
}

async function retrySync() {
  if (!pendingSessionId && !highlightedSession.value) return
  const sessionId = pendingSessionId || highlightedSession.value
  syncTimedOut.value = false
  syncing.value = true
  returnNotice.value = t('toeflPracticePage.returnNotice')
  await pollForSession(sessionId)
}

onMounted(async () => {
  await fetchAttempts()
  await handleReturnLanding()
})

onUnmounted(() => {
  stopPolling()
})
</script>
