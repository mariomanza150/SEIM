<template>
  <div class="container-fluid py-3" data-testid="qa-accounts-page">
    <h1 class="h3 mb-1">{{ t('qa.switcher.title') }}</h1>
    <p class="text-muted mb-3">{{ t('qa.switcher.intro') }}</p>
    <TesterNotAvailable v-if="qa.loaded && !qa.isTester" />
    <template v-else>
      <div v-if="qa.actingAs" class="alert alert-info" data-testid="qa-accounts-acting">
        {{ t('qa.switcher.currentlyActing', { email: qa.actingAs.email }) }}
      </div>
      <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>
      <div v-if="loading" class="text-muted">{{ t('qa.common.loading') }}</div>
      <div v-else class="row g-3" data-testid="qa-demo-accounts">
        <div v-for="acc in accounts" :key="acc.id" class="col-12 col-md-6 col-xl-4">
          <div class="card h-100">
            <div class="card-body d-flex flex-column">
              <div class="d-flex justify-content-between align-items-start gap-2">
                <h2 class="h6 mb-1 text-break">{{ acc.email }}</h2>
                <span class="badge text-bg-secondary">{{ roleLabel(acc.role) }}</span>
              </div>
              <p class="small text-muted flex-grow-1 mb-2">{{ acc.name }}<template v-if="acc.description"> — {{ acc.description }}</template></p>
              <button
                type="button"
                class="btn btn-primary btn-sm align-self-start"
                :disabled="busyId !== null || qa.actingAs?.id === acc.id"
                :data-testid="`qa-switch-${acc.email}`"
                @click="switchTo(acc)"
              >
                <span v-if="busyId === acc.id" class="spinner-border spinner-border-sm me-1" aria-hidden="true" />
                {{ t('qa.switcher.actAs') }}
              </button>
            </div>
          </div>
        </div>
        <p v-if="!accounts.length" class="text-muted">{{ t('qa.switcher.noAccounts') }}</p>
      </div>
      <p class="small text-muted mt-3">{{ t('qa.switcher.passwordHint') }}</p>

      <section v-if="qa.isTriager && !qa.actingAs" class="mt-4" data-testid="qa-impersonate">
        <h2 class="h5">{{ t('qa.impersonate.title') }}</h2>
        <p class="small text-muted">{{ t('qa.impersonate.intro') }}</p>
        <div class="row g-2 align-items-end">
          <div class="col-12 col-md-5">
            <label for="qa-imp-q" class="form-label small">{{ t('qa.impersonate.search') }}</label>
            <input id="qa-imp-q" v-model="query" type="search" class="form-control form-control-sm" @input="onSearch" />
          </div>
          <div class="col-12 col-md-5">
            <label for="qa-imp-reason" class="form-label small">{{ t('qa.impersonate.reason') }}</label>
            <input id="qa-imp-reason" v-model="reason" type="text" maxlength="500" class="form-control form-control-sm" />
          </div>
        </div>
        <ul v-if="results.length" class="list-group mt-2">
          <li v-for="u in results" :key="u.id" class="list-group-item d-flex justify-content-between align-items-center gap-2">
            <span class="text-break">{{ u.email }} <span class="text-muted small">({{ roleLabel(u.role) }})</span></span>
            <button type="button" class="btn btn-outline-danger btn-sm" :disabled="busyId !== null" @click="impersonateUser(u)">
              {{ t('qa.impersonate.start') }}
            </button>
          </li>
        </ul>
      </section>
    </template>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useQaStore } from '@/stores/qa'
import { listDemoAccounts, searchUsersToImpersonate } from '@/qa/api'
import { startImpersonation, switchToDemo } from '@/qa/roleSwitch'
import TesterNotAvailable from './TesterNotAvailable.vue'

const { t, te } = useI18n()
const qa = useQaStore()
const router = useRouter()
const accounts = ref([])
const loading = ref(false)
const error = ref('')
const busyId = ref(null)
const query = ref('')
const reason = ref('')
const results = ref([])
let searchTimer = null

function roleLabel(role) {
  return te(`qa.roles.${role}`) ? t(`qa.roles.${role}`) : role
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await listDemoAccounts()
    accounts.value = data.results || []
  } catch {
    error.value = t('qa.common.loadFailed')
  } finally {
    loading.value = false
  }
}

async function switchTo(acc) {
  busyId.value = acc.id
  error.value = ''
  try {
    await switchToDemo(acc.id)
    await router.push({ name: 'Dashboard' })
  } catch {
    error.value = t('qa.switcher.failed')
  } finally {
    busyId.value = null
  }
}

function onSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(async () => {
    if (query.value.trim().length < 2) {
      results.value = []
      return
    }
    try {
      const { data } = await searchUsersToImpersonate(query.value.trim())
      results.value = data.results || []
    } catch {
      results.value = []
    }
  }, 250)
}

async function impersonateUser(u) {
  busyId.value = u.id
  error.value = ''
  try {
    await startImpersonation(u.id, reason.value)
    await router.push({ name: 'Dashboard' })
  } catch (e) {
    error.value = e?.response?.status === 403 ? t('qa.impersonate.forbidden') : t('qa.switcher.failed')
  } finally {
    busyId.value = null
  }
}

onMounted(async () => {
  await qa.load()
  if (qa.isTester) await load()
})
</script>
