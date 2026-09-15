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
            {{ t('tours.progress', { current: stepIndex + 1, total: steps.length }) }}
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
  buildTourSteps,
  clearTourCompletion,
  isTourCompleted,
  markTourCompleted,
  resolveTourRole,
  tourIdForRole,
  tourStorageUserKey,
} from '@/utils/tourDefinitions'

const { t } = useI18n()
const route = useRoute()
const authStore = useAuthStore()
const { open, stepIndex, role, tourId, openTour, closeTour, setStepIndex } = useProductTour()

const popoverEl = ref(null)
const primaryBtn = ref(null)
const highlightStyle = ref(null)
const popoverStyle = ref({ top: '20vh', left: '50%', transform: 'translateX(-50%)' })
let autoStartTimer = null

const reduceMotion = computed(() => {
  const prefs = readStoredUiPreferences() || {}
  if (prefs.reduce_motion) return true
  if (typeof window !== 'undefined' && typeof window.matchMedia === 'function') {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches
  }
  return false
})

const steps = computed(() => buildTourSteps(t, role.value))
const currentStep = computed(() => steps.value[stepIndex.value] || null)
const isLast = computed(() => stepIndex.value >= steps.value.length - 1)

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
  if (stepIndex.value <= 0) return
  setStepIndex(stepIndex.value - 1)
}

function next() {
  if (isLast.value) {
    completeAndClose()
    return
  }
  setStepIndex(stepIndex.value + 1)
}

function maybeAutoStart() {
  if (!authStore.isAuthenticated) return
  const userKey = tourStorageUserKey(authStore.user)
  if (!userKey) return
  if (route.name !== 'Dashboard') return
  if (open.value) return
  const nextRole = resolveTourRole(authStore)
  const nextTourId = tourIdForRole(nextRole)
  if (isTourCompleted(userKey, nextTourId)) return
  openTour({ role: nextRole, tourId: nextTourId, force: false })
}

function replayTour() {
  if (!authStore.isAuthenticated) return
  const userKey = tourStorageUserKey(authStore.user)
  if (!userKey) return
  const nextRole = resolveTourRole(authStore)
  const nextTourId = tourIdForRole(nextRole)
  clearTourCompletion(userKey, nextTourId)
  openTour({ role: nextRole, tourId: nextTourId, force: true })
}

watch(
  () => [open.value, stepIndex.value, currentStep.value?.selector],
  async () => {
    if (!open.value) return
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
  },
)

function onResize() {
  if (open.value) updateSpotlight()
}

onMounted(() => {
  window.addEventListener('resize', onResize)
  window.addEventListener('seim-replay-product-tour', replayTour)
  autoStartTimer = setTimeout(() => maybeAutoStart(), 600)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
  window.removeEventListener('seim-replay-product-tour', replayTour)
  if (autoStartTimer) clearTimeout(autoStartTimer)
})

defineExpose({ replayTour, maybeAutoStart })
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
