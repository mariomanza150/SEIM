/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import {
  CHUNK_RELOAD_STORAGE_KEY,
  clearChunkReloadGuard,
  installChunkLoadReloadHandlers,
  isChunkLoadError,
  reloadForChunkLoadError,
} from './chunkLoadReload'

describe('isChunkLoadError', () => {
  it('detects failed dynamic imports and chunk load errors', () => {
    expect(
      isChunkLoadError(
        new TypeError('Failed to fetch dynamically imported module: /static/assets/AppShell-abc.js'),
      ),
    ).toBe(true)
    expect(isChunkLoadError(new Error('Importing a module script failed.'))).toBe(true)
    expect(isChunkLoadError(new Error('Loading chunk AppShell failed'))).toBe(true)
    expect(isChunkLoadError(new Error('ChunkLoadError: Loading chunk 5 failed'))).toBe(true)
    expect(isChunkLoadError(new Error('Network Error'))).toBe(false)
    expect(isChunkLoadError(null)).toBe(false)
  })
})

describe('reloadForChunkLoadError', () => {
  let storage
  let reload

  beforeEach(() => {
    storage = {
      store: {},
      getItem(key) {
        return Object.prototype.hasOwnProperty.call(this.store, key) ? this.store[key] : null
      },
      setItem(key, value) {
        this.store[key] = String(value)
      },
      removeItem(key) {
        delete this.store[key]
      },
    }
    reload = vi.fn()
  })

  it('reloads once for a chunk-load failure and sets the session guard', () => {
    const error = new TypeError('Failed to fetch dynamically imported module: /static/a.js')
    const ok = reloadForChunkLoadError(error, {
      targetHref: 'http://localhost/seim/register',
      storage,
      reload,
    })
    expect(ok).toBe(true)
    expect(reload).toHaveBeenCalledWith('http://localhost/seim/register')
    expect(storage.getItem(CHUNK_RELOAD_STORAGE_KEY)).toBeTruthy()
  })

  it('does not reload for unrelated errors', () => {
    expect(
      reloadForChunkLoadError(new Error('boom'), {
        targetHref: 'http://localhost/seim/',
        storage,
        reload,
      }),
    ).toBe(false)
    expect(reload).not.toHaveBeenCalled()
    expect(storage.getItem(CHUNK_RELOAD_STORAGE_KEY)).toBeNull()
  })

  it('skips a second reload while the session guard is set', () => {
    const error = new TypeError('Failed to fetch dynamically imported module')
    expect(reloadForChunkLoadError(error, { targetHref: '/a', storage, reload })).toBe(true)
    expect(reloadForChunkLoadError(error, { targetHref: '/b', storage, reload })).toBe(false)
    expect(reload).toHaveBeenCalledTimes(1)
    expect(reload).toHaveBeenCalledWith('/a')
  })

  it('allows another reload after the guard is cleared', () => {
    const error = new TypeError('Failed to fetch dynamically imported module')
    reloadForChunkLoadError(error, { targetHref: '/a', storage, reload })
    clearChunkReloadGuard(storage)
    expect(reloadForChunkLoadError(error, { targetHref: '/c', storage, reload })).toBe(true)
    expect(reload).toHaveBeenCalledTimes(2)
    expect(reload).toHaveBeenLastCalledWith('/c')
  })

  it('returns false when storage is unavailable', () => {
    const error = new TypeError('Failed to fetch dynamically imported module')
    expect(
      reloadForChunkLoadError(error, { targetHref: '/a', storage: null, reload }),
    ).toBe(false)
    expect(reload).not.toHaveBeenCalled()
  })

  it('survives storage that throws (private mode)', () => {
    const throwing = {
      getItem() {
        throw new Error('denied')
      },
      setItem() {
        throw new Error('denied')
      },
      removeItem() {
        throw new Error('denied')
      },
    }
    const error = new TypeError('Failed to fetch dynamically imported module')
    expect(
      reloadForChunkLoadError(error, { targetHref: '/a', storage: throwing, reload }),
    ).toBe(true)
    expect(reload).toHaveBeenCalledWith('/a')
    expect(() => clearChunkReloadGuard(throwing)).not.toThrow()
  })
})

describe('installChunkLoadReloadHandlers', () => {
  let storage
  let reload
  let onErrorFn
  let afterEachFn
  let addEventListener
  let win

  beforeEach(() => {
    storage = {
      store: {},
      getItem(key) {
        return Object.prototype.hasOwnProperty.call(this.store, key) ? this.store[key] : null
      },
      setItem(key, value) {
        this.store[key] = String(value)
      },
      removeItem(key) {
        delete this.store[key]
      },
    }
    reload = vi.fn()
    onErrorFn = null
    afterEachFn = null
    addEventListener = vi.fn()
    win = {
      location: { origin: 'http://localhost', href: 'http://localhost/seim/dashboard' },
      addEventListener,
    }
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  function makeRouter() {
    return {
      onError(fn) {
        onErrorFn = fn
      },
      afterEach(fn) {
        afterEachFn = fn
      },
      resolve(to) {
        return { href: typeof to === 'string' ? to : to.fullPath || '/seim/' }
      },
    }
  }

  it('reloads to the target route on router chunk-load errors', () => {
    const router = makeRouter()
    installChunkLoadReloadHandlers(router, {
      getWindow: () => win,
      storage,
      reload,
    })

    onErrorFn(new TypeError('Failed to fetch dynamically imported module'), {
      fullPath: '/seim/register',
      name: 'Register',
    })
    expect(reload).toHaveBeenCalledWith('http://localhost/seim/register')
  })

  it('clears the guard after a successful navigation', () => {
    const router = makeRouter()
    installChunkLoadReloadHandlers(router, {
      getWindow: () => win,
      storage,
      reload,
    })

    onErrorFn(new TypeError('Failed to fetch dynamically imported module'), {
      fullPath: '/seim/register',
    })
    expect(storage.getItem(CHUNK_RELOAD_STORAGE_KEY)).toBeTruthy()
    afterEachFn()
    expect(storage.getItem(CHUNK_RELOAD_STORAGE_KEY)).toBeNull()
  })

  it('handles vite:preloadError with a one-time reload', () => {
    const router = makeRouter()
    installChunkLoadReloadHandlers(router, {
      getWindow: () => win,
      storage,
      reload,
    })

    expect(addEventListener).toHaveBeenCalledWith('vite:preloadError', expect.any(Function))
    const handler = addEventListener.mock.calls.find(([name]) => name === 'vite:preloadError')[1]
    const event = {
      preventDefault: vi.fn(),
      payload: new TypeError('Failed to fetch dynamically imported module'),
    }
    handler(event)
    expect(event.preventDefault).toHaveBeenCalled()
    expect(reload).toHaveBeenCalledWith('http://localhost/seim/dashboard')

    handler(event)
    expect(reload).toHaveBeenCalledTimes(1)
  })

  it('ignores non-chunk router errors', () => {
    const router = makeRouter()
    installChunkLoadReloadHandlers(router, {
      getWindow: () => win,
      storage,
      reload,
    })
    onErrorFn(new Error('Navigation cancelled'), { fullPath: '/seim/' })
    expect(reload).not.toHaveBeenCalled()
  })
})
