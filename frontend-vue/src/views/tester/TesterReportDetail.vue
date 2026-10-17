<template>
  <div class="container-fluid py-3" data-testid="qa-report-detail">
    <router-link :to="{ name: 'TesterReports' }" class="small d-inline-block mb-2">
      <i class="bi bi-arrow-left me-1" aria-hidden="true" />{{ t('qa.reports.back') }}
    </router-link>
    <TesterNotAvailable v-if="qa.loaded && !qa.isTester" />
    <div v-else-if="loading" class="text-muted">{{ t('qa.common.loading') }}</div>
    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
    <template v-else-if="issue">
      <div class="d-flex flex-wrap align-items-center gap-2 mb-2">
        <h1 class="h4 mb-0">{{ issue.reference }} · {{ issue.title }}</h1>
        <span class="badge" :class="severityClass(issue.severity)">{{ t(`qa.severity.${issue.severity}`) }}</span>
        <span class="badge text-bg-light border" data-testid="qa-issue-status">{{ t(`qa.status.${issue.status}`) }}</span>
      </div>
      <p class="small text-muted mb-3">
        {{ t('qa.reports.reportedBy', { email: issue.reporter?.email || '—', when: formatDate(issue.created_at) }) }}
        <span v-if="issue.acting_as"> · {{ t('qa.reports.actingAs', { email: issue.acting_as.email }) }}</span>
      </p>
      <IssueVerifyPanel v-if="canVerify" :issue="issue" @updated="load" />
      <IssueTriagePanel v-if="qa.isTriager" :issue="issue" @updated="load" />
      <div class="row g-3">
        <div class="col-lg-7">
          <div class="card mb-3">
            <div class="card-body">
              <h2 class="h6">{{ t('qa.fields.description') }}</h2>
              <p class="seim-qa-text">{{ issue.description || '—' }}</p>
              <h2 class="h6">{{ t('qa.fields.steps') }}</h2>
              <pre class="seim-qa-text small mb-0">{{ issue.steps || '—' }}</pre>
            </div>
          </div>
          <div class="card mb-3">
            <div class="card-body">
              <h2 class="h6">{{ t('qa.widget.attachments') }}</h2>
              <p v-if="!issue.attachments.length" class="text-muted small mb-2">{{ t('qa.reports.noAttachments') }}</p>
              <ul class="list-unstyled d-flex flex-wrap gap-3">
                <li v-for="a in issue.attachments" :key="a.id" class="seim-qa-att">
                  <a v-if="urls[a.id] && a.content_type.startsWith('image/')" :href="urls[a.id]" target="_blank" rel="noopener">
                    <img :src="urls[a.id]" :alt="a.original_name" class="img-thumbnail" />
                  </a>
                  <video v-else-if="urls[a.id] && a.content_type.startsWith('video/')" :src="urls[a.id]" controls class="w-100" />
                  <button v-else type="button" class="btn btn-outline-secondary btn-sm" @click="openAttachment(a)">
                    <i class="bi bi-download me-1" aria-hidden="true" />{{ a.original_name }}
                  </button>
                  <div class="small text-muted text-truncate">{{ a.original_name }} · {{ formatBytes(a.size) }}</div>
                </li>
              </ul>
              <label class="btn btn-outline-secondary btn-sm mb-0">
                <i class="bi bi-paperclip me-1" aria-hidden="true" />{{ t('qa.reports.addFiles') }}
                <input type="file" class="d-none" multiple accept=".png,.jpg,.jpeg,.webp,.gif,.webm,.mp4,.txt,.log,.json" @change="onAddFiles" />
              </label>
              <div v-if="fileError" class="text-danger small mt-1">{{ fileError }}</div>
            </div>
          </div>
          <div class="card">
            <div class="card-body">
              <h2 class="h6">{{ t('qa.reports.comments') }}</h2>
              <ul class="list-unstyled">
                <li v-for="c in issue.comments" :key="c.id" class="border-bottom py-2" :class="{ 'text-muted fst-italic small': c.is_system }">
                  <div class="small text-muted">
                    {{ c.author?.email || '—' }} · {{ formatDate(c.created_at) }}
                    <span v-if="c.is_internal" class="badge text-bg-dark ms-1">{{ t('qa.reports.internal') }}</span>
                  </div>
                  <div class="seim-qa-text">{{ c.body }}</div>
                </li>
              </ul>
              <form @submit.prevent="sendComment">
                <label class="visually-hidden" for="qa-comment">{{ t('qa.reports.addComment') }}</label>
                <textarea id="qa-comment" v-model="comment" class="form-control mb-2" rows="2" :placeholder="t('qa.reports.addComment')" />
                <div class="d-flex align-items-center gap-3">
                  <button type="submit" class="btn btn-primary btn-sm" :disabled="!comment.trim()">{{ t('qa.reports.send') }}</button>
                  <div v-if="qa.isTriager" class="form-check mb-0">
                    <input id="qa-internal" v-model="internal" type="checkbox" class="form-check-input" />
                    <label for="qa-internal" class="form-check-label small">{{ t('qa.reports.internalNote') }}</label>
                  </div>
                </div>
              </form>
            </div>
          </div>
        </div>
        <div class="col-lg-5">
          <div class="card">
            <div class="card-body small">
              <h2 class="h6">{{ t('qa.reports.context') }}</h2>
              <dl class="row mb-0">
                <dt class="col-4">{{ t('qa.reports.page') }}</dt><dd class="col-8 text-break">{{ issue.page_url || '—' }}</dd>
                <dt class="col-4">{{ t('qa.reports.route') }}</dt><dd class="col-8">{{ issue.route_name || '—' }}</dd>
                <dt class="col-4">{{ t('qa.reports.role') }}</dt><dd class="col-8">{{ issue.reporter_role || '—' }}</dd>
                <dt class="col-4">{{ t('qa.reports.browser') }}</dt><dd class="col-8 text-break">{{ issue.user_agent || '—' }}</dd>
                <dt class="col-4">{{ t('qa.reports.viewport') }}</dt><dd class="col-8">{{ issue.viewport || '—' }}</dd>
                <dt class="col-4">{{ t('qa.reports.version') }}</dt><dd class="col-8">{{ issue.app_version }} {{ issue.build_commit?.slice(0, 7) }}</dd>
              </dl>
              <details class="mt-2">
                <summary>{{ t('qa.reports.diagnostics') }}</summary>
                <pre class="bg-body-tertiary p-2 rounded mt-2 seim-qa-diag">{{ JSON.stringify(issue.diagnostics, null, 2) }}</pre>
              </details>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { useQaStore } from '@/stores/qa'
import { addAttachments, addComment, attachmentObjectUrl, getIssue } from '@/qa/api'
import { formatBytes, severityClass } from '@/qa/format'
import TesterNotAvailable from './TesterNotAvailable.vue'
import IssueTriagePanel from '@/components/qa/IssueTriagePanel.vue'
import IssueVerifyPanel from '@/components/qa/IssueVerifyPanel.vue'

const props = defineProps({ id: { type: String, default: '' } })
const { t, locale } = useI18n()
const qa = useQaStore()
const route = useRoute()
const issue = ref(null)
const loading = ref(false)
const error = ref('')
const comment = ref('')
const internal = ref(false)
const fileError = ref('')
const urls = reactive({})
const canVerify = computed(
  () =>
    issue.value?.status === 'fixed' &&
    (qa.isTriager || (issue.value?.reporter?.id && issue.value.reporter.id === qa.context?.tester?.id)),
)

function formatDate(v) {
  return v ? new Date(v).toLocaleString(locale.value) : ''
}

function revokeAll() {
  for (const k of Object.keys(urls)) {
    URL.revokeObjectURL(urls[k])
    delete urls[k]
  }
}

async function loadPreviews() {
  for (const a of issue.value?.attachments || []) {
    if (urls[a.id]) continue
    if (!a.content_type.startsWith('image/') && !a.content_type.startsWith('video/')) continue
    try {
      urls[a.id] = await attachmentObjectUrl(a.download_url)
    } catch {
      /* leave as download button */
    }
  }
}

async function load() {
  await qa.load()
  if (!qa.isTester) return
  loading.value = !issue.value
  error.value = ''
  try {
    const { data } = await getIssue(props.id || route.params.id)
    issue.value = data
    loadPreviews()
  } catch {
    error.value = t('qa.common.loadFailed')
  } finally {
    loading.value = false
  }
}

async function openAttachment(a) {
  const url = await attachmentObjectUrl(a.download_url)
  const link = document.createElement('a')
  link.href = url
  link.download = a.original_name || 'attachment'
  link.click()
  setTimeout(() => URL.revokeObjectURL(url), 10000)
}

async function sendComment() {
  if (!comment.value.trim()) return
  await addComment(issue.value.id, comment.value, internal.value)
  comment.value = ''
  internal.value = false
  await load()
}

async function onAddFiles(e) {
  fileError.value = ''
  const files = Array.from(e.target.files || [])
  e.target.value = ''
  if (!files.length) return
  try {
    await addAttachments(issue.value.id, files)
    await load()
  } catch (err) {
    const body = err?.response?.data
    fileError.value = body?.files ? [].concat(body.files).join(' ') : t('qa.widget.submitFailed')
  }
}

onMounted(load)
watch(() => route.params.id, () => {
  revokeAll()
  issue.value = null
  load()
})
onBeforeUnmount(revokeAll)
defineExpose({ load, issue })
</script>

<style scoped>
.seim-qa-text {
  white-space: pre-wrap;
  word-break: break-word;
}
.seim-qa-att {
  width: 180px;
}
.seim-qa-att img {
  max-height: 120px;
  object-fit: contain;
}
.seim-qa-diag {
  max-height: 360px;
  overflow: auto;
  font-size: 0.75rem;
}
</style>
