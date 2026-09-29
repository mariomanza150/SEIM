<template>
  <div
    class="toast-container position-fixed seim-toast-container"
    data-testid="toast-container"
    style="pointer-events: none"
  >
    <div
      v-for="toast in toasts"
      :key="toast.id"
      class="toast show"
      role="alert"
      :class="`toast-${toast.type}`"
      style="pointer-events: auto"
      data-testid="toast-item"
    >
      <div class="toast-header">
        <i
          class="bi me-2"
          :class="{
            'bi-check-circle-fill text-success': toast.type === 'success',
            'bi-exclamation-circle-fill text-danger': toast.type === 'error',
            'bi-exclamation-triangle-fill text-warning': toast.type === 'warning',
            'bi-info-circle-fill text-info': toast.type === 'info',
          }"
          aria-hidden="true"
        ></i>
        <strong class="me-auto">
          {{ toastTitle(toast.type) }}
        </strong>
        <button
          type="button"
          class="btn-close"
          data-testid="toast-dismiss"
          @click="removeToast(toast.id)"
          :aria-label="t('toast.close')"
        ></button>
      </div>
      <div class="toast-body">
        {{ toast.message }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { useToast } from '@/composables/useToast'

const { t } = useI18n()
const { toasts, removeToast } = useToast()

function toastTitle(type) {
  switch (type) {
    case 'success':
      return t('toast.success')
    case 'error':
      return t('toast.error')
    case 'warning':
      return t('toast.warning')
    case 'info':
      return t('toast.info')
    default:
      return t('toast.notification')
  }
}
</script>

<style scoped>
.seim-toast-container {
  /* Sit below navbar + page-header actions; inset from the right so panels
     open toward the page interior instead of flush against the viewport edge. */
  top: calc(9.25rem + env(safe-area-inset-top, 0px));
  right: max(0.75rem, env(safe-area-inset-right, 0px));
  left: auto;
  bottom: auto;
  z-index: 1080;
  width: min(22rem, calc(100vw - 1.5rem));
  max-width: calc(100vw - 1.5rem);
  padding: 0;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  box-sizing: border-box;
}

.toast {
  width: 100%;
  min-width: 0;
  max-width: 100%;
  margin-bottom: 0.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  background-color: var(--seim-surface-bg);
  color: var(--seim-surface-text);
  border-color: var(--seim-border-color);
}

.toast-header {
  background-color: var(--seim-surface-bg);
  color: var(--seim-surface-text);
  border-bottom: 1px solid var(--seim-border-color, rgba(0, 0, 0, 0.05));
}

.toast-body {
  word-wrap: break-word;
  overflow-wrap: anywhere;
  background-color: var(--seim-surface-bg);
  color: var(--seim-surface-text);
}
</style>

<!-- Unscoped so empty toast padding cannot intercept header action clicks. -->
<style>
.seim-toast-container {
  pointer-events: none;
}

.seim-toast-container .toast {
  pointer-events: auto;
}
</style>
