/**
 * Move keyboard focus to the app main landmark (SPA route changes).
 */
export function focusMainContent() {
  const el = document.getElementById('main-content')
  if (el && typeof el.focus === 'function') {
    el.focus({ preventScroll: true })
  }
}
