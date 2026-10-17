<template>
  <div class="card border-warning mb-3" data-testid="qa-triage-panel">
    <div class="card-body">
      <h2 class="h6">{{ t('qa.triage.panel') }}</h2>
      <form class="row g-2 align-items-end" @submit.prevent="save">
        <div class="col-6 col-md-3">
          <label class="form-label small" for="qa-tr-status">{{ t('qa.fields.status') }}</label>
          <select id="qa-tr-status" v-model="form.status" class="form-select form-select-sm">
            <option v-for="s in STATUSES" :key="s" :value="s">{{ t(`qa.status.${s}`) }}</option>
          </select>
        </div>
        <div class="col-6 col-md-2">
          <label class="form-label small" for="qa-tr-sev">{{ t('qa.fields.severity') }}</label>
          <select id="qa-tr-sev" v-model="form.severity" class="form-select form-select-sm">
            <option v-for="s in SEVERITIES" :key="s" :value="s">{{ t(`qa.severity.${s}`) }}</option>
          </select>
        </div>
        <div class="col-12 col-md-3">
          <label class="form-label small" for="qa-tr-assignee">{{ t('qa.triage.assignee') }}</label>
          <select id="qa-tr-assignee" v-model="form.assignee_id" class="form-select form-select-sm">
            <option :value="null">{{ t('qa.triage.unassigned') }}</option>
            <option v-for="u in triagers" :key="u.id" :value="u.id">{{ u.email }}</option>
          </select>
        </div>
        <div class="col-6 col-md-2">
          <label class="form-label small" for="qa-tr-commit">{{ t('qa.triage.fixedIn') }}</label>
          <input id="qa-tr-commit" v-model.trim="form.resolved_in_commit" maxlength="40" class="form-control form-control-sm" />
        </div>
        <div class="col-6 col-md-2">
          <label class="form-label small" for="qa-tr-dup">{{ t('qa.triage.duplicateOf') }}</label>
          <input id="qa-tr-dup" v-model.number="form.duplicate_of_number" type="number" min="1" class="form-control form-control-sm" />
        </div>
        <div class="col-12 d-flex align-items-center gap-2">
          <button type="submit" class="btn btn-warning btn-sm" :disabled="saving">{{ t('qa.triage.save') }}</button>
          <span v-if="message" class="small" :class="ok ? 'text-success' : 'text-danger'" role="status">{{ message }}</span>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { listTriagers, updateIssue } from '@/qa/api'

const props = defineProps({ issue: { type: Object, required: true } })
const emit = defineEmits(['updated'])
const { t } = useI18n()

const STATUSES = ['new', 'triaged', 'in_progress', 'needs_info', 'fixed', 'verified', 'closed', 'wont_fix', 'duplicate']
const SEVERITIES = ['blocker', 'major', 'minor', 'cosmetic']
const triagers = ref([])
const saving = ref(false)
const message = ref('')
const ok = ref(false)
const form = reactive({})

function fill(issue) {
  form.status = issue.status
  form.severity = issue.severity
  form.assignee_id = issue.assignee?.id || null
  form.resolved_in_commit = issue.resolved_in_commit || ''
  const dup = /(\d+)$/.exec(issue.duplicate_of_reference || '')
  form.duplicate_of_number = dup ? Number(dup[1]) : null
}

async function save() {
  saving.value = true
  message.value = ''
  try {
    const payload = { ...form }
    if (payload.duplicate_of_number === '' || payload.duplicate_of_number === null) payload.duplicate_of_number = null
    await updateIssue(props.issue.id, payload)
    ok.value = true
    message.value = t('qa.triage.saved')
    emit('updated')
  } catch (e) {
    ok.value = false
    const body = e?.response?.data
    message.value = body && typeof body === 'object' ? Object.values(body).flat().join(' ') : t('qa.triage.saveFailed')
  } finally {
    saving.value = false
  }
}

watch(() => props.issue, fill, { immediate: true })
onMounted(async () => {
  try {
    const { data } = await listTriagers()
    triagers.value = data.results || []
  } catch {
    triagers.value = []
  }
})
</script>
