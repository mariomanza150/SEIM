import { reactive, readonly } from 'vue'

const state = reactive({
  open: false,
  title: '',
  message: '',
  confirmText: 'OK',
  cancelText: 'Cancel',
  variant: 'danger', // 'danger' | 'primary'
  resolve: null,
})

export function useConfirm() {
  function confirm({
    title = '',
    message = '',
    confirmText = 'OK',
    cancelText = 'Cancel',
    variant = 'danger',
  } = {}) {
    // If a dialog is already open, resolve it as cancelled.
    if (state.open && typeof state.resolve === 'function') {
      state.resolve(false)
    }

    state.open = true
    state.title = title
    state.message = message
    state.confirmText = confirmText
    state.cancelText = cancelText
    state.variant = variant === 'primary' ? 'primary' : 'danger'

    return new Promise((resolve) => {
      state.resolve = resolve
    })
  }

  return {
    confirm,
    confirmState: readonly(state),
  }
}

export function resolveConfirm(result) {
  if (!state.open) return
  const resolve = state.resolve
  state.open = false
  state.title = ''
  state.message = ''
  state.resolve = null
  if (typeof resolve === 'function') resolve(Boolean(result))
}

