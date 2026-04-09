import i18n from '@/i18n'

export const ROUTE_ANNOUNCE_ID = 'seim-route-announce'

/**
 * Move keyboard focus to the app main landmark (SPA route changes).
 */
export function focusMainContent() {
  const el = document.getElementById('main-content')
  if (el && typeof el.focus === 'function') {
    el.focus({ preventScroll: true })
  }
}

/**
 * Update polite live region so screen readers hear the current view after navigation.
 */
export function announceRouteNavigation(to) {
  if (typeof document === 'undefined') return
  const name = to?.name
  const key = name != null ? `route.names.${String(name)}` : null
  let text
  if (key && i18n.global.te(key)) {
    text = i18n.global.t(key)
  } else {
    const title = (to?.meta && to.meta.title) || ''
    text = String(title).replace(/\s*-\s*SEIM\s*$/i, '').trim() || i18n.global.t('route.fallbackTitle')
  }
  const el = document.getElementById(ROUTE_ANNOUNCE_ID)
  if (!el) return
  el.textContent = ''
  window.requestAnimationFrame(() => {
    el.textContent = text
  })
}
