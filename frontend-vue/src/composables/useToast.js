/**
 * Toast notification composable
 * Simple toast notifications without external dependencies
 */
import { ref } from 'vue'

const toasts = ref([])
let toastId = 0

export function useToast() {
  function showToast(message, type = 'info', duration = 5000) {
    const id = toastId++
    const toast = {
      id,
      message,
      type, // 'success', 'error', 'warning', 'info'
      duration,
    }

    toasts.value.push(toast)

    // Auto-remove after duration
    if (duration > 0) {
      setTimeout(() => {
        removeToast(id)
      }, duration)
    }

    return id
  }

  function removeToast(id) {
    const index = toasts.value.findIndex(t => t.id === id)
    if (index > -1) {
      toasts.value.splice(index, 1)
    }
  }

  function success(message, duration) {
    return showToast(message, 'success', duration)
  }

  function error(message, duration) {
    return showToast(message, 'error', duration)
  }

  function warning(message, duration) {
    return showToast(message, 'warning', duration)
  }

  function info(message, duration) {
    return showToast(message, 'info', duration)
  }

  return {
    toasts,
    showToast,
    removeToast,
    success,
    error,
    warning,
    info,
  }
}
