const STORAGE_KEY = 'seim.reviewQueue.nav'

/**
 * Persist an ordered review-queue id list for ApplicationDetail prev/next.
 * @param {Array<string|number>} ids
 * @param {string|number} currentId
 */
export function setReviewQueueNav(ids, currentId) {
  if (typeof sessionStorage === 'undefined') return
  const normalized = (Array.isArray(ids) ? ids : []).map((id) => String(id)).filter(Boolean)
  if (!normalized.length) {
    clearReviewQueueNav()
    return
  }
  const current = String(currentId)
  const index = normalized.indexOf(current)
  sessionStorage.setItem(
    STORAGE_KEY,
    JSON.stringify({
      ids: normalized,
      index: index >= 0 ? index : 0,
    }),
  )
}

export function clearReviewQueueNav() {
  if (typeof sessionStorage === 'undefined') return
  sessionStorage.removeItem(STORAGE_KEY)
}

/**
 * @param {string|number} currentId
 * @returns {{ ids: string[], index: number, prevId: string|null, nextId: string|null } | null}
 */
export function getReviewQueueNav(currentId) {
  if (typeof sessionStorage === 'undefined') return null
  let raw
  try {
    raw = sessionStorage.getItem(STORAGE_KEY)
  } catch {
    return null
  }
  if (!raw) return null
  let parsed
  try {
    parsed = JSON.parse(raw)
  } catch {
    clearReviewQueueNav()
    return null
  }
  const ids = Array.isArray(parsed?.ids) ? parsed.ids.map(String).filter(Boolean) : []
  if (!ids.length) {
    clearReviewQueueNav()
    return null
  }
  const current = String(currentId)
  const index = ids.indexOf(current)
  if (index < 0) return null
  return {
    ids,
    index,
    prevId: index > 0 ? ids[index - 1] : null,
    nextId: index < ids.length - 1 ? ids[index + 1] : null,
  }
}

/**
 * Update stored index when navigating within an existing queue.
 * @param {string|number} currentId
 */
export function syncReviewQueueNavIndex(currentId) {
  const nav = getReviewQueueNav(currentId)
  if (!nav) return null
  setReviewQueueNav(nav.ids, currentId)
  return getReviewQueueNav(currentId)
}
