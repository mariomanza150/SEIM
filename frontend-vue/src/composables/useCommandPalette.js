import { reactive, readonly } from 'vue'

const state = reactive({
  open: false,
})

function isEditableTarget(target) {
  if (!target || !(target instanceof Element)) return false
  const tag = target.tagName
  if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return true
  if (target.isContentEditable) return true
  return Boolean(target.closest?.('[contenteditable="true"]'))
}

export function useCommandPalette() {
  function openPalette() {
    state.open = true
  }

  function closePalette() {
    state.open = false
  }

  function togglePalette() {
    state.open = !state.open
  }

  return {
    paletteState: readonly(state),
    openPalette,
    closePalette,
    togglePalette,
  }
}

/**
 * Handle Ctrl/Cmd+K. Returns true if the event was consumed.
 * @param {KeyboardEvent} event
 * @param {{ open: boolean, openPalette: () => void, closePalette: () => void, togglePalette: () => void }} api
 */
export function handleCommandPaletteShortcut(event, api) {
  if (!event) return false
  const key = event.key
  if (!key || key.toLowerCase() !== 'k') return false
  if (!(event.metaKey || event.ctrlKey) || event.altKey) return false

  if (api.open) {
    event.preventDefault()
    api.togglePalette()
    return true
  }

  if (isEditableTarget(event.target)) return false

  event.preventDefault()
  api.openPalette()
  return true
}

export function isCommandPaletteEditableTarget(target) {
  return isEditableTarget(target)
}
