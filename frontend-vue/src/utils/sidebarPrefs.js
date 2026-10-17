/** localStorage keys + helpers for persisted sidebar UI state. */
export const SIDEBAR_COLLAPSED_KEY = 'seim.sidebarCollapsed'
export const SIDEBAR_SECTIONS_KEY = 'seim.sidebarSectionsCollapsed'

export function readSidebarCollapsed() {
  try {
    return localStorage.getItem(SIDEBAR_COLLAPSED_KEY) === '1'
  } catch {
    return false
  }
}

export function writeSidebarCollapsed(value) {
  try {
    localStorage.setItem(SIDEBAR_COLLAPSED_KEY, value ? '1' : '0')
  } catch {
    /* storage unavailable */
  }
}

/** Map of section key -> true when that section is collapsed. */
export function readCollapsedSections() {
  try {
    const raw = localStorage.getItem(SIDEBAR_SECTIONS_KEY)
    const parsed = raw ? JSON.parse(raw) : {}
    if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) return {}
    return Object.fromEntries(Object.entries(parsed).filter(([, v]) => v === true))
  } catch {
    return {}
  }
}

export function writeCollapsedSections(map) {
  try {
    localStorage.setItem(SIDEBAR_SECTIONS_KEY, JSON.stringify(map || {}))
  } catch {
    /* storage unavailable */
  }
}
