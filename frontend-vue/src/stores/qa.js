/**
 * Tester toolkit state. The backend 404s /api/qa/context/ unless the server has
 * TESTER_TOOLS_ENABLED + DEPLOY_TIER=test; then the toolkit simply stays hidden.
 * Every QA endpoint re-checks permissions server-side; this store is cosmetic.
 */
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import api from '@/services/api'
import { APP_BUILD_TIME, APP_COMMIT } from '@/qa/buildInfo'

export const useQaStore = defineStore('qa', () => {
  const context = ref(null)
  const loaded = ref(false)
  const widgetOpen = ref(false)
  let inflight = null

  const enabled = computed(() => Boolean(context.value?.enabled))
  const isTester = computed(() => enabled.value && Boolean(context.value?.is_tester))
  const isTriager = computed(() => isTester.value && Boolean(context.value?.is_triager))
  const actingAs = computed(() => (isTester.value ? context.value?.acting_as || null : null))
  const backendVersion = computed(() => context.value?.version || '')
  const backendCommit = computed(() => context.value?.commit || '')
  const deployTier = computed(() => context.value?.deploy_tier || '')
  const limits = computed(
    () => context.value?.limits || { max_attachments: 5, max_image_mb: 10, max_video_mb: 25 },
  )
  const frontendCommit = APP_COMMIT
  const buildTime = APP_BUILD_TIME
  const commitMismatch = computed(() => {
    const a = (backendCommit.value || '').slice(0, 7)
    const b = (frontendCommit || '').slice(0, 7)
    return Boolean(a && b && a !== b)
  })

  async function load(force = false) {
    if (loaded.value && !force) return context.value
    if (inflight && !force) return inflight
    inflight = api
      .get('/api/qa/context/')
      .then(({ data }) => {
        context.value = data
        return data
      })
      .catch(() => {
        context.value = null
        return null
      })
      .finally(() => {
        loaded.value = true
        inflight = null
      })
    return inflight
  }

  function reset() {
    context.value = null
    loaded.value = false
    widgetOpen.value = false
  }

  function openWidget() {
    if (isTester.value) widgetOpen.value = true
  }

  function closeWidget() {
    widgetOpen.value = false
  }

  return {
    context,
    loaded,
    widgetOpen,
    enabled,
    isTester,
    isTriager,
    actingAs,
    backendVersion,
    backendCommit,
    deployTier,
    limits,
    frontendCommit,
    buildTime,
    commitMismatch,
    load,
    reset,
    openWidget,
    closeWidget,
  }
})
