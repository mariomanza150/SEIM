import { nextTick, onMounted, onUnmounted, ref } from 'vue'

const registry = new Set()

/**
 * Navbar dropdown that Vue owns (open/close, outside click, Escape).
 * Only one instance stays open at a time.
 */
export function useNavDropdown() {
  const open = ref(false)
  const rootEl = ref(null)

  function focusToggle() {
    const root = rootEl.value
    if (!(root instanceof HTMLElement)) return
    const toggle = root.querySelector(
      'button.dropdown-toggle, button[aria-haspopup], button[data-testid], button',
    )
    if (toggle instanceof HTMLElement) toggle.focus()
  }

  function close({ restoreFocus = false } = {}) {
    if (!open.value) return
    open.value = false
    if (restoreFocus) {
      nextTick(() => focusToggle())
    }
  }

  function toggle(event) {
    event?.stopPropagation?.()
    if (open.value) {
      open.value = false
      return
    }
    for (const other of registry) {
      if (other !== close) other()
    }
    open.value = true
  }

  function onDocumentClick(event) {
    if (!open.value) return
    const root = rootEl.value
    if (root && event.target instanceof Node && root.contains(event.target)) return
    close()
  }

  function onDocumentKeydown(event) {
    if (event.key === 'Escape' && open.value) {
      event.stopPropagation()
      close({ restoreFocus: true })
    }
  }

  onMounted(() => {
    registry.add(close)
    document.addEventListener('click', onDocumentClick)
    document.addEventListener('keydown', onDocumentKeydown)
  })

  onUnmounted(() => {
    registry.delete(close)
    document.removeEventListener('click', onDocumentClick)
    document.removeEventListener('keydown', onDocumentKeydown)
  })

  return { open, rootEl, toggle, close }
}
