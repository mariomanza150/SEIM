<template>
  <div class="toast-container position-fixed top-0 end-0 p-3" style="z-index: 9999">
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
.toast {
  min-width: 300px;
  margin-bottom: 0.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.toast-header {
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.toast-body {
  word-wrap: break-word;
}
</style>
