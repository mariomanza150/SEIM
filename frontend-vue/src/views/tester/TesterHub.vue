<template>
  <div class="container-fluid py-3" data-testid="qa-hub-page">
    <h1 class="h3 mb-1">{{ t('qa.hub.title') }}</h1>
    <p class="text-muted mb-3">{{ t('qa.hub.intro') }}</p>
    <TesterNotAvailable v-if="qa.loaded && !qa.isTester" />
    <template v-else>
      <div class="row g-3 mb-3">
        <div v-for="card in cards" :key="card.name" class="col-12 col-sm-6 col-xl-3">
          <router-link :to="{ name: card.name }" class="card h-100 text-decoration-none">
            <div class="card-body">
              <i :class="`bi ${card.icon} fs-4`" aria-hidden="true" />
              <h2 class="h6 mt-2 mb-1">{{ t(card.label) }}</h2>
              <p class="small text-muted mb-0">{{ t(card.hint) }}</p>
            </div>
          </router-link>
        </div>
      </div>

      <div class="row g-3">
        <div class="col-12 col-lg-6">
          <div class="card h-100" data-testid="qa-hub-build">
            <div class="card-body">
              <h2 class="h6">{{ t('qa.hub.build') }}</h2>
              <dl class="row small mb-0">
                <dt class="col-5">{{ t('qa.hub.tier') }}</dt><dd class="col-7">{{ qa.deployTier }}</dd>
                <dt class="col-5">{{ t('qa.hub.serverVersion') }}</dt><dd class="col-7">{{ qa.backendVersion }} · {{ short(qa.backendCommit) }}</dd>
                <dt class="col-5">{{ t('qa.hub.frontendBuild') }}</dt><dd class="col-7">{{ short(qa.frontendCommit) }} · {{ qa.buildTime }}</dd>
                <template v-if="env">
                  <dt class="col-5">{{ t('qa.hub.emailCapture') }}</dt><dd class="col-7">{{ yesNo(env.email_capture) }}</dd>
                  <dt class="col-5">{{ t('qa.hub.virusScanner') }}</dt><dd class="col-7">{{ env.virus_scanner || '—' }}</dd>
                  <dt class="col-5">{{ t('qa.hub.demoPassword') }}</dt><dd class="col-7">{{ yesNo(env.demo_password_configured) }}</dd>
                </template>
              </dl>
              <p v-if="qa.commitMismatch" class="text-danger small mb-0 mt-2">{{ t('qa.menu.commitMismatch') }}</p>
            </div>
          </div>
        </div>
        <div class="col-12 col-lg-6">
          <div class="card h-100" data-testid="qa-hub-flags">
            <div class="card-body">
              <h2 class="h6">{{ t('qa.hub.flags') }}</h2>
              <div v-if="!flags" class="small text-muted">{{ t('qa.common.loading') }}</div>
              <ul v-else class="list-unstyled small mb-0 row">
                <li v-for="(on, name) in allFlags" :key="name" class="col-12 col-md-6">
                  <i :class="on ? 'bi bi-check-circle text-success' : 'bi bi-x-circle text-muted'" aria-hidden="true" />
                  <span class="ms-1">{{ name }}</span>
                  <span class="visually-hidden">{{ yesNo(on) }}</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
        <div class="col-12 col-lg-6">
          <div class="card h-100">
            <div class="card-body">
              <h2 class="h6">{{ t('qa.hub.samples') }}</h2>
              <p class="small text-muted">{{ t('qa.hub.samplesHint') }}</p>
              <div class="d-flex flex-wrap gap-2">
                <a v-for="s in samples" :key="s.file" :href="`/static/qa-samples/${s.file}`" class="btn btn-outline-secondary btn-sm" download>
                  {{ t(s.label) }}
                </a>
              </div>
            </div>
          </div>
        </div>
        <div v-if="qa.isTriager" class="col-12 col-lg-6">
          <div class="card h-100 border-danger" data-testid="qa-hub-reset">
            <div class="card-body">
              <h2 class="h6">{{ t('qa.hub.reset') }}</h2>
              <p class="small text-muted">{{ t('qa.hub.resetHint') }}</p>
              <div v-if="resetMessage" class="alert py-1 small" :class="resetOk ? 'alert-success' : 'alert-danger'">{{ resetMessage }}</div>
              <button type="button" class="btn btn-outline-danger btn-sm" :disabled="resetting || !!qa.actingAs" @click="reset">
                {{ t('qa.hub.resetButton') }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useQaStore } from '@/stores/qa'
import { getFlags, resetDemoData } from '@/qa/api'
import { shortCommit } from '@/qa/buildInfo'
import { useConfirm } from '@/composables/useConfirm'
import TesterNotAvailable from './TesterNotAvailable.vue'

const { t } = useI18n()
const qa = useQaStore()
const { confirm } = useConfirm()
const flags = ref(null)
const resetting = ref(false)
const resetMessage = ref('')
const resetOk = ref(false)

const cards = [
  { name: 'TesterAccounts', icon: 'bi-people', label: 'qa.menu.accounts', hint: 'qa.hub.accountsHint' },
  { name: 'TesterReports', icon: 'bi-list-check', label: 'qa.menu.myReports', hint: 'qa.hub.reportsHint' },
  { name: 'TesterOutbox', icon: 'bi-envelope', label: 'qa.menu.outbox', hint: 'qa.hub.outboxHint' },
  { name: 'TesterGuide', icon: 'bi-journal-text', label: 'qa.menu.guide', hint: 'qa.hub.guideHint' },
]
const samples = [
  { file: 'sample.pdf', label: 'qa.hub.samplePdf' },
  { file: 'sample.png', label: 'qa.hub.samplePng' },
  { file: 'sample.txt', label: 'qa.hub.sampleTxt' },
]

const env = computed(() => flags.value?.environment || null)
const allFlags = computed(() => ({ ...(flags.value?.feature_flags || {}), ...(flags.value?.institution || {}) }))
const short = (c) => shortCommit(c) || '—'
const yesNo = (v) => (v ? t('qa.common.yes') : t('qa.common.no'))

async function reset() {
  const ok = await confirm({
    title: t('qa.hub.reset'),
    message: t('qa.hub.resetConfirm'),
    confirmText: t('qa.hub.resetButton'),
    variant: 'danger',
  })
  if (!ok) return
  resetting.value = true
  resetMessage.value = ''
  try {
    await resetDemoData()
    resetOk.value = true
    resetMessage.value = t('qa.hub.resetQueued')
  } catch (e) {
    resetOk.value = false
    resetMessage.value = e?.response?.status === 409 ? t('qa.hub.resetRunning') : t('qa.hub.resetFailed')
  } finally {
    resetting.value = false
  }
}

onMounted(async () => {
  await qa.load()
  if (!qa.isTester) return
  try {
    const { data } = await getFlags()
    flags.value = data
  } catch {
    flags.value = { feature_flags: {}, institution: {} }
  }
})
</script>
