/**
 * Scroll the main content column into view after a route change.
 *
 * Only scrolls when the user is below the top of the main column (so short
 * pages already in view do not jump) and honours ``prefers-reduced-motion``.
 * Also resets the element's own scrollTop for layouts where it scrolls itself.
 */
export function prefersReducedMotion() {
  try {
    return Boolean(window.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches)
  } catch {
    return false
  }
}

export function scrollMainIntoView(el, { offset = 72 } = {}) {
  if (!el || typeof window === 'undefined') return false
  if (el.scrollTop > 0) el.scrollTop = 0
  const rect = el.getBoundingClientRect?.()
  if (!rect) return false
  const currentY = window.scrollY || window.pageYOffset || 0
  const target = Math.max(0, rect.top + currentY - offset)
  if (currentY <= target) return false
  window.scrollTo({ top: target, behavior: prefersReducedMotion() ? 'auto' : 'smooth' })
  return true
}
