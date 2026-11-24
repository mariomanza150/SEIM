/**
 * Recover from stale Vite/Webpack lazy chunks after a deploy.
 *
 * Old tabs keep an HTML shell that points at hashed assets removed by the new
 * build. Detect those load failures and do a one-time full reload (sessionStorage
 * guard) so the browser picks up a fresh shell without looping forever.
 */

export const CHUNK_RELOAD_STORAGE_KEY = 'seim:chunk-reload'

/** True for "Failed to fetch dynamically imported module" style chunk-load failures. */
export function isChunkLoadError(error) {
  const msg = String(error?.message || error || '')
  return /dynamically imported module|Importing a module script failed|error loading dynamically imported|Loading chunk [\w-]+ failed|ChunkLoadError/i.test(
    msg,
  )
}

function safeGetItem(storage, key) {
  try {
    return storage?.getItem?.(key) ?? null
  } catch {
    return null
  }
}

function safeSetItem(storage, key, value) {
  try {
    storage?.setItem?.(key, value)
  } catch {
    /* private mode / quota */
  }
}

function safeRemoveItem(storage, key) {
  try {
    storage?.removeItem?.(key)
  } catch {
    /* private mode */
  }
}

export function clearChunkReloadGuard(storage = defaultStorage()) {
  safeRemoveItem(storage, CHUNK_RELOAD_STORAGE_KEY)
}

function defaultStorage() {
  try {
    return typeof sessionStorage !== 'undefined' ? sessionStorage : null
  } catch {
    return null
  }
}

function defaultReload(href) {
  if (typeof window === 'undefined') return
  window.location.assign(href)
}

/**
 * One-time full page reload when a lazy chunk fails to load.
 * Returns true if a reload was triggered.
 *
 * @param {unknown} error
 * @param {{
 *   targetHref?: string,
 *   storage?: Storage | null,
 *   reload?: (href: string) => void,
 * }} [options]
 */
export function reloadForChunkLoadError(error, options = {}) {
  if (!isChunkLoadError(error)) return false

  const storage = options.storage === undefined ? defaultStorage() : options.storage
  if (!storage) return false
  if (safeGetItem(storage, CHUNK_RELOAD_STORAGE_KEY)) return false

  safeSetItem(storage, CHUNK_RELOAD_STORAGE_KEY, String(Date.now()))

  const href =
    options.targetHref ||
    (typeof window !== 'undefined' ? window.location.href : '/')
  const reload = options.reload || defaultReload
  reload(href)
  return true
}

/**
 * Wire router.onError + vite:preloadError to the reload guard.
 * Clears the guard after a successful navigation (afterEach).
 *
 * @param {import('vue-router').Router | null | undefined} router
 * @param {{
 *   getWindow?: () => Window | null,
 *   storage?: Storage | null,
 *   reload?: (href: string) => void,
 * }} [options]
 */
export function installChunkLoadReloadHandlers(router, options = {}) {
  const getWindow = options.getWindow || (() => (typeof window !== 'undefined' ? window : null))
  const win = getWindow()

  if (router) {
    router.onError((error, to) => {
      let targetHref
      if (to && win) {
        try {
          targetHref = new URL(router.resolve(to).href, win.location.origin).href
        } catch {
          targetHref = win.location.href
        }
      } else if (win) {
        targetHref = win.location.href
      }
      reloadForChunkLoadError(error, {
        targetHref,
        storage: options.storage,
        reload: options.reload,
      })
    })

    router.afterEach(() => {
      clearChunkReloadGuard(options.storage === undefined ? defaultStorage() : options.storage)
    })
  }

  if (win?.addEventListener) {
    win.addEventListener('vite:preloadError', (event) => {
      event.preventDefault?.()
      const err = event?.payload ?? event
      reloadForChunkLoadError(err, {
        targetHref: win.location.href,
        storage: options.storage,
        reload: options.reload,
      })
    })
  }
}
