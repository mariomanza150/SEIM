<template>
  <div v-if="qa.isTester" class="seim-qa-widget" data-qa-ignore data-testid="qa-widget">
    <button
      v-show="!qa.widgetOpen && !hidden"
      type="button"
      class="btn btn-warning shadow seim-qa-fab d-inline-flex align-items-center gap-2"
      data-testid="qa-report-fab"
      :aria-label="t('qa.widget.open')"
      :title="`${t('qa.widget.open')} (Ctrl+Shift+B)`"
      @click="open"
    >
      <i class="bi bi-bug-fill" aria-hidden="true" />
      <span class="d-none d-sm-inline">{{ t('qa.widget.fab') }}</span>
    </button>

    <Teleport to="body">
      <div v-if="qa.widgetOpen" class="seim-qa-backdrop" data-qa-ignore @click.self="close">
        <div
          class="seim-qa-dialog card shadow-lg"
          role="dialog"
          aria-modal="true"
          :aria-label="t('qa.widget.title')"
          data-testid="qa-report-dialog"
          @keydown.esc.prevent="close"
          @paste="onPaste"
        >
          <div class="card-header d-flex align-items-center justify-content-between">
            <h2 class="h5 mb-0"><i class="bi bi-bug me-2" aria-hidden="true" />{{ t('qa.widget.title') }}</h2>
            <button type="button" class="btn-close" :aria-label="t('qa.common.close')" @click="close" />
          </div>
          <form class="card-body seim-qa-dialog__body" novalidate @submit.prevent="submit">
            <div v-if="qa.actingAs" class="alert alert-info py-2 small">
              {{ t('qa.widget.actingAs', { email: qa.actingAs.email, role: qa.actingAs.role }) }}
            </div>
            <div class="mb-3">
              <label class="form-label" for="qa-title">{{ t('qa.fields.title') }} *</label>
              <input
                id="qa-title"
                ref="titleInput"
                v-model="form.title"
                class="form-control"
                :class="{ 'is-invalid': errors.title }"
                maxlength="200"
                required
                data-testid="qa-title"
              />
              <div v-if="errors.title" class="invalid-feedback">{{ errors.title }}</div>
            </div>
            <div class="row g-2 mb-3">
              <div class="col-6">
                <label class="form-label" for="qa-severity">{{ t('qa.fields.severity') }}</label>
                <select id="qa-severity" v-model="form.severity" class="form-select" data-testid="qa-severity">
                  <option v-for="s in severities" :key="s" :value="s">{{ t(`qa.severity.${s}`) }}</option>
                </select>
              </div>
              <div class="col-6">
                <label class="form-label" for="qa-kind">{{ t('qa.fields.kind') }}</label>
                <select id="qa-kind" v-model="form.kind" class="form-select">
                  <option v-for="k in kinds" :key="k" :value="k">{{ t(`qa.kind.${k}`) }}</option>
                </select>
              </div>
            </div>
            <div class="mb-3">
              <label class="form-label" for="qa-description">{{ t('qa.fields.description') }}</label>
              <textarea id="qa-description" v-model="form.description" class="form-control" rows="3" maxlength="10000" />
            </div>
            <div class="mb-3">
              <label class="form-label" for="qa-steps">{{ t('qa.fields.steps') }}</label>
              <textarea id="qa-steps" v-model="form.steps" class="form-control font-monospace small" rows="4" maxlength="10000" />
            </div>

            <fieldset class="mb-3">
              <legend class="form-label fs-6">{{ t('qa.widget.attachments') }}</legend>
              <div class="d-flex flex-wrap gap-2 mb-2">
                <button type="button" class="btn btn-outline-primary btn-sm" :disabled="busy" data-testid="qa-capture-page" @click="doCapturePage">
                  <i class="bi bi-camera me-1" aria-hidden="true" />{{ t('qa.widget.capturePage') }}
                </button>
                <button v-if="screenSupported" type="button" class="btn btn-outline-primary btn-sm" :disabled="busy" @click="doCaptureScreen">
                  <i class="bi bi-display me-1" aria-hidden="true" />{{ t('qa.widget.captureScreen') }}
                </button>
                <button
                  v-if="recordSupported && !recording"
                  type="button"
                  class="btn btn-outline-danger btn-sm"
                  :disabled="busy"
                  @click="doStartRecording"
                >
                  <i class="bi bi-record-circle me-1" aria-hidden="true" />{{ t('qa.widget.record') }}
                </button>
                <button v-if="recording" type="button" class="btn btn-danger btn-sm" @click="doStopRecording">
                  <i class="bi bi-stop-circle me-1" aria-hidden="true" />{{ t('qa.widget.stopRecording') }}
                </button>
                <label class="btn btn-outline-secondary btn-sm mb-0">
                  <i class="bi bi-paperclip me-1" aria-hidden="true" />{{ t('qa.widget.chooseFiles') }}
                  <input
                    type="file"
                    class="d-none"
                    multiple
                    :accept="accept"
                    data-testid="qa-file-input"
                    @change="onFiles"
                  />
                </label>
              </div>
              <p class="form-text mt-0">{{ t('qa.widget.attachHint', limitsText) }}</p>
              <div
                class="seim-qa-drop border rounded p-2 small text-muted text-center mb-2"
                :class="{ 'border-primary': dragging }"
                @dragover.prevent="dragging = true"
                @dragleave.prevent="dragging = false"
                @drop.prevent="onDrop"
              >
                {{ t('qa.widget.dropHint') }}
              </div>
              <ul v-if="files.length" class="list-unstyled d-flex flex-wrap gap-2 mb-0" data-testid="qa-file-list">
                <li v-for="(item, idx) in files" :key="item.key" class="seim-qa-thumb border rounded p-1 text-center">
                  <img v-if="item.preview" :src="item.preview" :alt="item.file.name" />
                  <i v-else class="bi bi-file-earmark fs-3 d-block" aria-hidden="true" />
                  <div class="small text-truncate">{{ item.file.name }}</div>
                  <button type="button" class="btn btn-link btn-sm text-danger p-0" @click="removeFile(idx)">
                    {{ t('qa.common.remove') }}
                  </button>
                </li>
              </ul>
              <div v-if="errors.files" class="text-danger small mt-1">{{ errors.files }}</div>
            </fieldset>

            <div class="form-check mb-2">
              <input id="qa-diag" v-model="includeDiagnostics" class="form-check-input" type="checkbox" />
              <label class="form-check-label" for="qa-diag">{{ t('qa.widget.includeDiagnostics') }}</label>
            </div>
            <details class="mb-3 small">
              <summary>{{ t('qa.widget.whatWeSend') }}</summary>
              <pre class="seim-qa-pre bg-body-tertiary p-2 rounded mt-2" data-testid="qa-context-preview">{{ previewText }}</pre>
            </details>
            <p class="small text-muted">{{ t('qa.widget.privacy') }}</p>
            <div v-if="errors.general" class="alert alert-danger py-2">{{ errors.general }}</div>
            <div class="d-flex justify-content-end gap-2">
              <button type="button" class="btn btn-outline-secondary" @click="close">{{ t('qa.common.cancel') }}</button>
              <button type="submit" class="btn btn-primary" :disabled="busy" data-testid="qa-submit">
                <span v-if="submitting" class="spinner-border spinner-border-sm me-1" aria-hidden="true" />
                {{ t('qa.widget.submit') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { useQaStore } from '@/stores/qa'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import { createIssue } from '@/qa/api'
import { environmentInfo, snapshotDiagnostics } from '@/qa/diagnostics'
import { canCaptureScreen, canRecordScreen, capturePage, captureScreen, startRecording } from '@/qa/capture'

const { t, locale } = useI18n()
const qa = useQaStore()
const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const toast = useToast()

const severities = ['blocker', 'major', 'minor', 'cosmetic']
const kinds = ['bug', 'ux', 'content', 'suggestion']
const accept = '.png,.jpg,.jpeg,.webp,.gif,.webm,.mp4,.txt,.log,.json'

const titleInput = ref(null)
const hidden = ref(false)
const busy = ref(false)
const submitting = ref(false)
const dragging = ref(false)
const recording = ref(null)
const includeDiagnostics = ref(true)
const files = ref([])
const errors = reactive({ title: '', files: '', general: '' })
const form = reactive({ title: '', description: '', steps: '', severity: 'minor', kind: 'bug' })

const screenSupported = canCaptureScreen()
const recordSupported = canRecordScreen()

const limitsText = computed(() => ({
  n: qa.limits.max_attachments,
  img: qa.limits.max_image_mb,
  video: qa.limits.max_video_mb,
}))

function resetForm() {
  Object.assign(form, { title: '', description: '', steps: t('qa.widget.stepsTemplate'), severity: 'minor', kind: 'bug' })
  files.value.forEach((f) => f.preview && URL.revokeObjectURL(f.preview))
  files.value = []
  Object.assign(errors, { title: '', files: '', general: '' })
  includeDiagnostics.value = true
}

function buildContext() {
  const env = environmentInfo()
  return {
    page_url: typeof window !== 'undefined' ? window.location.href : '',
    route_name: route?.name ? String(route.name) : '',
    route: { fullPath: route?.fullPath || '', params: route?.params || {} },
    user: auth.user ? { email: auth.user.email, role: auth.user.role } : null,
    locale: locale.value,
    viewport: env.viewport || '',
    user_agent: env.userAgent || '',
    app_version: qa.backendVersion,
    build_commit: qa.frontendCommit || qa.backendCommit,
    environment: env,
  }
}

const previewText = computed(() => {
  if (!qa.widgetOpen) return ''
  const ctx = buildContext()
  const out = { ...ctx }
  if (includeDiagnostics.value) out.diagnostics = snapshotDiagnostics()
  return JSON.stringify(out, null, 2)
})

async function open() {
  resetForm()
  qa.openWidget()
  await nextTick()
  titleInput.value?.focus()
}

function close() {
  if (recording.value) doStopRecording()
  qa.closeWidget()
}

function addFiles(list) {
  errors.files = ''
  for (const file of Array.from(list || [])) {
    if (files.value.length >= qa.limits.max_attachments) {
      errors.files = t('qa.widget.tooManyFiles', { n: qa.limits.max_attachments })
      break
    }
    const isVideo = file.type.startsWith('video/')
    const maxMb = isVideo ? qa.limits.max_video_mb : qa.limits.max_image_mb
    if (file.size > maxMb * 1024 * 1024) {
      errors.files = t('qa.widget.fileTooLarge', { name: file.name, mb: maxMb })
      continue
    }
    const preview = file.type.startsWith('image/') && typeof URL.createObjectURL === 'function' ? URL.createObjectURL(file) : ''
    files.value.push({ file, preview, key: `${file.name}-${file.size}-${Math.random()}` })
  }
}

function removeFile(idx) {
  const [item] = files.value.splice(idx, 1)
  if (item?.preview) URL.revokeObjectURL(item.preview)
}

function onFiles(e) {
  addFiles(e.target.files)
  e.target.value = ''
}

function onDrop(e) {
  dragging.value = false
  addFiles(e.dataTransfer?.files)
}

function onPaste(e) {
  const items = Array.from(e.clipboardData?.items || [])
  const images = items.filter((i) => i.kind === 'file' && i.type.startsWith('image/')).map((i) => i.getAsFile()).filter(Boolean)
  if (images.length) {
    e.preventDefault()
    addFiles(images.map((f, i) => new File([f], f.name && f.name !== 'image.png' ? f.name : `pasted-${Date.now()}-${i}.png`, { type: f.type })))
  }
}

async function withHiddenDialog(fn) {
  busy.value = true
  const wasOpen = qa.widgetOpen
  qa.closeWidget()
  hidden.value = true
  await nextTick()
  await new Promise((r) => setTimeout(r, 150))
  try {
    return await fn()
  } finally {
    hidden.value = false
    if (wasOpen) qa.widgetOpen = true
    busy.value = false
  }
}

async function doCapturePage() {
  try {
    const file = await withHiddenDialog(() => capturePage())
    addFiles([file])
  } catch (e) {
    errors.files = t('qa.widget.captureFailed')
  }
}

async function doCaptureScreen() {
  try {
    const file = await withHiddenDialog(() => captureScreen())
    addFiles([file])
  } catch (e) {
    if (e?.name !== 'NotAllowedError') errors.files = t('qa.widget.captureFailed')
  }
}

async function doStartRecording() {
  try {
    recording.value = await startRecording({ maxSeconds: 60 })
    toast.info(t('qa.widget.recordingStarted'), 4000)
    recording.value.done.then((file) => {
      if (recording.value) {
        recording.value = null
        addFiles([file])
      }
    })
  } catch (e) {
    recording.value = null
    if (e?.name !== 'NotAllowedError') errors.files = t('qa.widget.captureFailed')
  }
}

async function doStopRecording() {
  const rec = recording.value
  if (!rec) return
  recording.value = null
  addFiles([await rec.stop()])
}

async function submit() {
  errors.title = form.title.trim() ? '' : t('qa.widget.titleRequired')
  errors.general = ''
  if (errors.title) return
  submitting.value = true
  busy.value = true
  try {
    const ctx = buildContext()
    const fd = new FormData()
    for (const [k, v] of Object.entries(form)) fd.append(k, v)
    for (const k of ['page_url', 'route_name', 'locale', 'viewport', 'user_agent', 'app_version', 'build_commit']) {
      fd.append(k, ctx[k] || '')
    }
    const diagnostics = { environment: ctx.environment, route: ctx.route }
    if (includeDiagnostics.value) Object.assign(diagnostics, snapshotDiagnostics())
    fd.append('diagnostics', JSON.stringify(diagnostics))
    for (const item of files.value) fd.append('files', item.file)
    const { data } = await createIssue(fd)
    toast.success(t('qa.widget.submitted', { ref: data.reference }), 6000)
    qa.closeWidget()
    resetForm()
    if (route?.name === 'TesterReports') router.replace({ name: 'TesterReports', query: { r: Date.now() } })
  } catch (e) {
    const body = e?.response?.data
    if (body?.files) errors.files = [].concat(body.files).join(' ')
    if (body?.title) errors.title = [].concat(body.title).join(' ')
    if (e?.response?.status === 429) errors.general = t('qa.widget.rateLimited')
    else if (!errors.files && !errors.title) errors.general = t('qa.widget.submitFailed')
  } finally {
    submitting.value = false
    busy.value = false
  }
}

function onKeydown(e) {
  if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.key === 'B' || e.key === 'b')) {
    if (!qa.isTester) return
    e.preventDefault()
    if (qa.widgetOpen) close()
    else open()
  }
}

function onOpenEvent() {
  if (qa.isTester && !qa.widgetOpen) open()
}

onMounted(() => {
  window.addEventListener('keydown', onKeydown)
  window.addEventListener('seim:qa-report', onOpenEvent)
})
onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKeydown)
  window.removeEventListener('seim:qa-report', onOpenEvent)
})

defineExpose({ open, submit, addFiles, form, files, errors })
</script>

<style scoped>
.seim-qa-fab {
  position: fixed;
  right: 1rem;
  bottom: 1rem;
  z-index: 1040;
  border-radius: 2rem;
}
.seim-qa-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1080;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 2rem 0.75rem;
  overflow-y: auto;
}
.seim-qa-dialog {
  width: 100%;
  max-width: 640px;
}
.seim-qa-dialog__body {
  max-height: calc(100vh - 8rem);
  overflow-y: auto;
}
.seim-qa-thumb {
  width: 120px;
}
.seim-qa-thumb img {
  max-width: 100%;
  max-height: 70px;
  object-fit: contain;
}
.seim-qa-pre {
  max-height: 240px;
  overflow: auto;
  white-space: pre-wrap;
  font-size: 0.75rem;
}
</style>
