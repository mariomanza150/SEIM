<template>
  <div class="toast-container position-fixed end-0 p-3 seim-toast-container">
    <div
      v-for="toast in toasts"
      :key="toast.id"
      class="toast show"
      role="alert"
      :class="`toast-${toast.type}`"
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
        ></i>
        <strong class="me-auto">
          {{ toastTitle(toast.type) }}
        </strong>
        <button
          type="button"
          class="btn-close"
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
  top: calc(3.75rem + env(safe-area-inset-top, 0px));
  z-index: 1080;
}

.toast {
  min-width: 300px;
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
  background-color: var(--seim-surface-bg);
  color: var(--seim-surface-text);
}
</style>
