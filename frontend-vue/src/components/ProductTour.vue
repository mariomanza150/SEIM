<template>
  <div data-testid="product-tour-ready" class="visually-hidden" aria-hidden="true" />
  <Teleport to="body">
    <div
      v-if="open && currentStep"
      class="seim-tour"
      data-testid="product-tour"
      :class="{ 'seim-tour--reduced-motion': reduceMotion }"
    >
      <div
        v-if="!highlightStyle"
        class="seim-tour__backdrop"
        aria-hidden="true"
        @click="skip"
      />
      <div
        v-if="highlightStyle"
        class="seim-tour__highlight"
        :style="highlightStyle"
        aria-hidden="true"
      />
      <button
        v-if="highlightStyle"
        type="button"
        class="seim-tour__dismiss"
        :aria-label="t('tours.skip')"
        data-testid="product-tour-dismiss"
        @click="skip"
      />
      <div
        ref="popoverEl"
        class="seim-tour__popover card shadow"
        role="dialog"
        aria-modal="true"
        :aria-label="currentStep.title"
        :style="popoverStyle"
        @keydown.esc.prevent="skip"
      >
        <div class="card-body">
          <p class="small text-muted mb-1" data-testid="product-tour-progress">
            {{ t('tours.progress', { current: progressCurrent, total: progressTotal }) }}
          </p>
          <h2 class="h5 mb-2" data-testid="product-tour-title">{{ currentStep.title }}</h2>
          <p class="mb-3" data-testid="product-tour-body">{{ currentStep.body }}</p>
          <div class="d-flex flex-wrap gap-2 justify-content-between">
            <button
              type="button"
              class="btn btn-sm btn-outline-secondary"
              data-testid="product-tour-skip"
              @click="skip"
            >
              {{ t('tours.skip') }}
            </button>
            <div class="d-flex gap-2">
              <button
                type="button"
                class="btn btn-sm btn-outline-secondary"
                data-testid="product-tour-back"
                :disabled="stepIndex <= 0"
                @click="back"
              >
                {{ t('tours.back') }}
              </button>
              <button
                ref="primaryBtn"
                type="button"
                class="btn btn-sm btn-primary"
                data-testid="product-tour-next"
                @click="next"
              >
                {{ isLast ? t('tours.done') : t('tours.next') }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useProductTour } from '@/composables/useProductTour'
import { readStoredUiPreferences } from '@/services/uiPreferences'
import {
  DASHBOARD_PAGE_ID,
  buildTourSteps,
  clearTourCompletion,
  filterMountedSteps,
  findNextMountedStepIndex,
  isTourCompleted,
  isTourTargetMounted,
  markTourCompleted,
  resolvePageTourFromRoute,
  resolveTourRole,
  tourIdForPage,
  tourIdForRole,
  tourStorageUserKey,
} from '@/utils/tourDefinitions'

const { t, te } = useI18n()
const route = useRoute()
const authStore = useAuthStore()
const {
  open,
  stepIndex,
  role,
  tourId,
  pageId,
  force,
  pendingPageId,
  openTour,
  closeTour,
  setStepIndex,
  clearPendingPageTour,
} = useProductTour()

const popoverEl = ref(null)
const primaryBtn = ref(null)
const highlightStyle = ref(null)
const popoverStyle = ref({ top: '20vh', left: '50%', transform: 'translateX(-50%)' })
let autoStartTimer = null
let pendingTimer = null

const reduceMotion = computed(() => {
  const prefs = readStoredUiPreferences() || {}
  if (prefs.reduce_motion) return true
  if (typeof window !== 'undefined' && typeof window.matchMedia === 'function') {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches
  }
  return false
})

/** Full step list; missing targets are skipped when advancing so tours never stall. */
const steps = computed(() =>
  buildTourSteps(t, role.value, pageId.value || DASHBOARD_PAGE_ID, { te }),
)

const mountedSteps = computed(() => filterMountedSteps(steps.value))
const currentStep = computed(() => steps.value[stepIndex.value] || null)
const isLast = computed(() => {
  if (!steps.value.length) return true
  return findNextMountedStepIndex(steps.value, stepIndex.value + 1, 1) === -1
})
const progressCurrent = computed(() => {
  const mounted = mountedSteps.value
  if (!mounted.length) return stepIndex.value + 1
  const current = currentStep.value
  const idx = current ? mounted.findIndex((step) => step.id === current.id) : -1
  return (idx >= 0 ? idx : 0) + 1
})
const progressTotal = computed(() => Math.max(mountedSteps.value.length, 1))

function targetRect(selector) {
  if (typeof document === 'undefined') return null
  const el = document.querySelector(selector)
  if (!el) return null
  return el.getBoundingClientRect()
}

function updateSpotlight() {
  const step = currentStep.value
  if (!step) {
    highlightStyle.value = null
    return
  }
  const rect = targetRect(step.selector)
  if (!rect || rect.width < 2 || rect.height < 2) {
    highlightStyle.value = null
    popoverStyle.value = { top: '20vh', left: '50%', transform: 'translateX(-50%)' }
    return
  }
  const pad = 6
  highlightStyle.value = {
    top: `${Math.max(0, rect.top - pad)}px`,
    left: `${Math.max(0, rect.left - pad)}px`,
    width: `${rect.width + pad * 2}px`,
    height: `${rect.height + pad * 2}px`,
  }
  const preferBelow = rect.bottom + 160 < window.innerHeight
  const top = preferBelow ? rect.bottom + 12 : Math.max(12, rect.top - 12)
  popoverStyle.value = {
    top: `${top}px`,
    left: `${Math.min(window.innerWidth - 24, Math.max(12, rect.left))}px`,
    transform: preferBelow ? 'none' : 'translateY(-100%)',
    maxWidth: '360px',
  }
}

function completeAndClose() {
  const userKey = tourStorageUserKey(authStore.user)
  if (userKey && tourId.value) {
    markTourCompleted(userKey, tourId.value)
  }
  closeTour()
}

function skip() {
  completeAndClose()
}

function back() {
  const prev = findNextMountedStepIndex(steps.value, stepIndex.value - 1, -1)
  if (prev < 0) return
  setStepIndex(prev)
}

function next() {
  const nextIdx = findNextMountedStepIndex(steps.value, stepIndex.value + 1, 1)
  if (nextIdx < 0) {
    completeAndClose()
    return
  }
  setStepIndex(nextIdx)
}

/** Jump to the first mounted step (or stay if current is valid). */
function ensureMountedStep() {
  if (!open.value || !steps.value.length) return
  const current = steps.value[stepIndex.value]
  if (current && (!current.selector || isTourTargetMounted(current.selector))) return
  const nextIdx = findNextMountedStepIndex(steps.value, stepIndex.value, 1)
  if (nextIdx >= 0) {
    if (nextIdx !== stepIndex.value) setStepIndex(nextIdx)
    return
  }
  const prevIdx = findNextMountedStepIndex(steps.value, stepIndex.value - 1, -1)
  if (prevIdx >= 0) {
    setStepIndex(prevIdx)
    return
  }
  // No mounted targets yet — keep the current step with a centered popover.
}

function launchTour(nextPageId, { force: nextForce = false } = {}) {
  if (!authStore.isAuthenticated) return
  const userKey = tourStorageUserKey(authStore.user)
  if (!userKey) return
  const nextRole = resolveTourRole(authStore)
  const nextTourId = tourIdForPage(nextPageId, nextRole)
  if (!nextForce && isTourCompleted(userKey, nextTourId)) return
  if (nextForce) clearTourCompletion(userKey, nextTourId)
  openTour({ role: nextRole, tourId: nextTourId, pageId: nextPageId, force: nextForce })
}

function maybeAutoStart() {
  if (!authStore.isAuthenticated) return
  const userKey = tourStorageUserKey(authStore.user)
  if (!userKey) return
  if (route.name !== 'Dashboard') return
  if (open.value) return
  if (pendingPageId.value) return
  const nextRole = resolveTourRole(authStore)
  const nextTourId = tourIdForRole(nextRole)
  if (isTourCompleted(userKey, nextTourId)) return
  openTour({
    role: nextRole,
    tourId: nextTourId,
    pageId: DASHBOARD_PAGE_ID,
    force: false,
  })
}

function maybeStartPendingTour() {
  const pending = pendingPageId.value
  if (!pending || !authStore.isAuthenticated) return
  const routePage = resolvePageTourFromRoute(route.name)
  if (routePage !== pending) return
  if (pendingTimer) clearTimeout(pendingTimer)
  pendingTimer = setTimeout(() => {
    if (pendingPageId.value !== pending) return
    clearPendingPageTour()
    launchTour(pending, { force: force.value || true })
  }, 450)
}

function replayTour() {
  launchTour(DASHBOARD_PAGE_ID, { force: true })
}

function onStartPageTour(event) {
  const nextPageId = event?.detail?.pageId || resolvePageTourFromRoute(route.name) || DASHBOARD_PAGE_ID
  const nextForce = event?.detail?.force !== false
  launchTour(nextPageId, { force: nextForce })
}

watch(
  () => [open.value, stepIndex.value, currentStep.value?.selector, steps.value.length, mountedSteps.value.length],
  async () => {
    if (!open.value) return
    await nextTick()
    if (!steps.value.length) {
      closeTour()
      return
    }
    if (stepIndex.value >= steps.value.length) {
      setStepIndex(Math.max(0, steps.value.length - 1))
      return
    }
    ensureMountedStep()
    await nextTick()
    updateSpotlight()
    primaryBtn.value?.focus?.()
  },
)

watch(
  () => [authStore.isAuthenticated, authStore.user?.id, authStore.user?.email, route.name],
  () => {
    if (autoStartTimer) clearTimeout(autoStartTimer)
    autoStartTimer = setTimeout(() => maybeAutoStart(), 500)
    maybeStartPendingTour()
  },
)

watch(
  () => pendingPageId.value,
  () => {
    maybeStartPendingTour()
  },
)

function onResize() {
  if (open.value) updateSpotlight()
}

onMounted(() => {
  window.addEventListener('resize', onResize)
  window.addEventListener('seim-replay-product-tour', replayTour)
  window.addEventListener('seim-start-page-tour', onStartPageTour)
  autoStartTimer = setTimeout(() => maybeAutoStart(), 600)
  maybeStartPendingTour()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
  window.removeEventListener('seim-replay-product-tour', replayTour)
  window.removeEventListener('seim-start-page-tour', onStartPageTour)
  if (autoStartTimer) clearTimeout(autoStartTimer)
  if (pendingTimer) clearTimeout(pendingTimer)
})

defineExpose({ replayTour, maybeAutoStart, launchTour, maybeStartPendingTour })
</script>

<style scoped>
.seim-tour {
  position: fixed;
  inset: 0;
  z-index: 1300;
  pointer-events: none;
}

.seim-tour__backdrop {
  position: absolute;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  pointer-events: auto;
}

.seim-tour__highlight {
  position: absolute;
  border-radius: 0.5rem;
  box-shadow: 0 0 0 9999px rgba(15, 23, 42, 0.45);
  outline: 2px solid var(--seim-brand-primary, #667eea);
  pointer-events: none;
  transition: top 0.2s ease, left 0.2s ease, width 0.2s ease, height 0.2s ease;
}

.seim-tour__dismiss {
  position: absolute;
  inset: 0;
  border: 0;
  background: transparent;
  pointer-events: auto;
  cursor: default;
}

.seim-tour--reduced-motion .seim-tour__highlight {
  transition: none;
}

.seim-tour__popover {
  position: absolute;
  z-index: 1;
  pointer-events: auto;
  background: var(--seim-surface-bg, #fff);
  color: var(--seim-surface-text, inherit);
  border: 1px solid var(--seim-border-color, #dee2e6);
}
</style>
