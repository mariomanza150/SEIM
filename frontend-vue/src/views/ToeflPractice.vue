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
          :disabled="launching"
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

    <div v-if="returnNotice" class="alert alert-info" data-testid="toefl-return-notice" role="status">
      {{ returnNotice }}
    </div>
    <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>

    <div class="card border-0 shadow-sm">
      <div class="card-body">
        <h3 class="h5 mb-3">{{ t('toeflPracticePage.historyHeading') }}</h3>
        <div v-if="loading" class="text-muted">{{ t('toeflPracticePage.loading') }}</div>
        <div v-else-if="!attempts.length" class="text-muted" data-testid="toefl-empty">
          {{ t('toeflPracticePage.empty') }}
        </div>
        <div v-else class="table-responsive">
          <table class="table table-sm align-middle mb-0" data-testid="toefl-attempts-table">
            <thead>
              <tr>
                <th scope="col">{{ t('toeflPracticePage.colDate') }}</th>
                <th scope="col">{{ t('toeflPracticePage.colExam') }}</th>
                <th scope="col">{{ t('toeflPracticePage.colScore') }}</th>
                <th scope="col">{{ t('toeflPracticePage.colWeak') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="row in attempts"
                :key="row.id"
                :data-session-id="row.external_session_id"
                :class="{ 'table-success': row.external_session_id === highlightedSession }"
              >
                <td>{{ formatDate(row.completed_at || row.created_at) }}</td>
                <td>{{ row.exam_code || '—' }}</td>
                <td>{{ formatScore(row) }}</td>
                <td>{{ formatWeak(row.weakest) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
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
import api from '@/services/api'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const attempts = ref([])
const loading = ref(true)
const launching = ref(false)
const error = ref('')
const returnNotice = ref('')
const highlightedSession = ref('')
let pollTimer = null

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

async function fetchAttempts() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/api/toefl/attempts/')
    attempts.value = data.results || data || []
  } catch (err) {
    error.value = err?.response?.data?.detail || t('toeflPracticePage.loadError')
    attempts.value = []
  } finally {
    loading.value = false
  }
}

async function startPractice() {
  launching.value = true
  error.value = ''
  try {
    const { data } = await api.post('/api/toefl/launch/', { n: 20 })
    if (!data?.launch_url) {
      throw new Error('missing launch_url')
    }
    window.location.assign(data.launch_url)
  } catch (err) {
    error.value = err?.response?.data?.detail || t('toeflPracticePage.launchError')
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

async function handleReturnLanding() {
  const sessionId = typeof route.query.session_id === 'string' ? route.query.session_id : ''
  if (!sessionId) return
  highlightedSession.value = sessionId
  returnNotice.value = t('toeflPracticePage.returnNotice')
  clearReturnQuery()

  let tries = 0
  const poll = async () => {
    tries += 1
    await fetchAttempts()
    const found = attempts.value.some((a) => a.external_session_id === sessionId)
    if (found || tries >= 8) {
      if (pollTimer) {
        clearInterval(pollTimer)
        pollTimer = null
      }
      return
    }
  }
  await poll()
  pollTimer = setInterval(poll, 1500)
}

onMounted(async () => {
  await fetchAttempts()
  await handleReturnLanding()
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>
