<template>
  <div class="alert alert-success" data-testid="qa-verify-panel">
    <p class="mb-2">
      <strong>{{ t('qa.verify.title') }}</strong>
      <span v-if="issue.resolved_in_commit" class="ms-1 small">{{ t('qa.verify.fixedIn', { commit: issue.resolved_in_commit.slice(0, 7) }) }}</span>
    </p>
    <p class="small mb-2">{{ t('qa.verify.hint') }}</p>
    <textarea
      v-if="reopening"
      v-model="comment"
      class="form-control form-control-sm mb-2"
      rows="2"
      :placeholder="t('qa.verify.reopenPlaceholder')"
      :aria-label="t('qa.verify.reopenPlaceholder')"
    />
    <div class="d-flex flex-wrap gap-2">
      <button type="button" class="btn btn-success btn-sm" :disabled="busy" data-testid="qa-verify-ok" @click="send('verified')">
        <i class="bi bi-check2 me-1" aria-hidden="true" />{{ t('qa.verify.works') }}
      </button>
      <button
        type="button"
        class="btn btn-outline-danger btn-sm"
        :disabled="busy || (reopening && !comment.trim())"
        data-testid="qa-verify-reopen"
        @click="reopening ? send('reopen') : (reopening = true)"
      >
        {{ reopening ? t('qa.verify.sendReopen') : t('qa.verify.reopen') }}
      </button>
    </div>
    <div v-if="error" class="text-danger small mt-1">{{ error }}</div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { verifyIssue } from '@/qa/api'

const props = defineProps({ issue: { type: Object, required: true } })
const emit = defineEmits(['updated'])
const { t } = useI18n()
const reopening = ref(false)
const comment = ref('')
const busy = ref(false)
const error = ref('')

async function send(result) {
  busy.value = true
  error.value = ''
  try {
    await verifyIssue(props.issue.id, result, comment.value.trim())
    reopening.value = false
    comment.value = ''
    emit('updated')
  } catch {
    error.value = t('qa.triage.saveFailed')
  } finally {
    busy.value = false
  }
}
</script>
