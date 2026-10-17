/**
 * In-memory diagnostics ring buffers for the tester "Report issue" widget.
 *
 * Nothing here is sent anywhere on its own: buffers live in memory and are only
 * attached to a report when a designated tester submits one (and can untick it).
 * No request/response bodies, headers, cookies or tokens are captured.
 */

const MAX_CONSOLE = 30
const MAX_REQUESTS = 20
const MAX_BREADCRUMBS = 10
const MAX_MESSAGE = 1000
const MAX_STACK = 2000

const SENSITIVE_PARAM = /(token|code|password|passwd|secret|key|auth|session|signature|sig|otp)/i
const JWT_LIKE = /eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}/g

const state = {
  installed: false,
  consoleErrors: [],
  failedRequests: [],
  breadcrumbs: [],
}

function push(list, item, max) {
  list.push(item)
  if (list.length > max) list.splice(0, list.length - max)
}

export function redactText(value, max = MAX_MESSAGE) {
  if (value === null || value === undefined) return ''
  return String(value).replace(JWT_LIKE, '[redacted-jwt]').slice(0, max)
}

export function scrubUrl(raw) {
  if (!raw) return ''
  try {
    const base = typeof window !== 'undefined' ? window.location.origin : 'http://localhost'
    const url = new URL(String(raw), base)
    for (const key of [...url.searchParams.keys()]) {
      if (SENSITIVE_PARAM.test(key)) url.searchParams.set(key, '[redacted]')
    }
    url.hash = ''
    const sameOrigin = typeof window !== 'undefined' && url.origin === window.location.origin
    const out = sameOrigin ? `${url.pathname}${url.search}` : url.toString()
    return redactText(out, 500)
  } catch {
    return redactText(String(raw).split('?')[0], 500)
  }
}

function stringifyArg(arg) {
  if (arg instanceof Error) return `${arg.name}: ${arg.message}`
  if (typeof arg === 'string') return arg
  try {
    return JSON.stringify(arg)
  } catch {
    return String(arg)
  }
}

export function recordConsole(level, args) {
  const list = Array.from(args || [])
  const err = list.find((a) => a instanceof Error)
  push(
    state.consoleErrors,
    {
      level,
      message: redactText(list.map(stringifyArg).join(' ')),
      stack: err?.stack ? redactText(err.stack, MAX_STACK) : '',
      at: new Date().toISOString(),
    },
    MAX_CONSOLE,
  )
}

/** Record a failed axios request (called from the api.js interceptor). */
export function recordFailedRequest(error) {
  try {
    const config = error?.config || {}
    const response = error?.response
    const started = config.__qaStart
    const headers = response?.headers || {}
    const requestId =
      (typeof headers.get === 'function' ? headers.get('x-request-id') : headers['x-request-id']) || ''
    push(
      state.failedRequests,
      {
        method: String(config.method || 'get').toUpperCase(),
        url: scrubUrl(`${config.baseURL || ''}${config.url || ''}`),
        status: response?.status ?? 0,
        durationMs: started ? Date.now() - started : null,
        requestId: redactText(requestId, 128),
        code: error?.code ? String(error.code).slice(0, 50) : '',
        at: new Date().toISOString(),
      },
      MAX_REQUESTS,
    )
  } catch {
    /* never let diagnostics break the app */
  }
}

export function recordNavigation(to, from) {
  push(
    state.breadcrumbs,
    {
      to: scrubUrl(to?.fullPath || ''),
      from: scrubUrl(from?.fullPath || ''),
      name: to?.name ? String(to.name) : '',
      at: new Date().toISOString(),
    },
    MAX_BREADCRUMBS,
  )
}

export function installDiagnostics(target = typeof window !== 'undefined' ? window : null) {
  if (state.installed || !target) return
  state.installed = true
  const cons = target.console || console
  for (const level of ['error', 'warn']) {
    const original = cons[level]
    if (typeof original !== 'function') continue
    cons[level] = function patched(...args) {
      try {
        recordConsole(level, args)
      } catch {
        /* ignore */
      }
      return original.apply(this, args)
    }
  }
  target.addEventListener?.('error', (event) => {
    recordConsole('error', [event?.error || event?.message || 'Script error'])
  })
  target.addEventListener?.('unhandledrejection', (event) => {
    recordConsole('error', ['Unhandled promise rejection:', event?.reason])
  })
}

export function snapshotDiagnostics() {
  return {
    consoleErrors: state.consoleErrors.map((e) => ({ ...e })),
    failedRequests: state.failedRequests.map((e) => ({ ...e })),
    breadcrumbs: state.breadcrumbs.map((e) => ({ ...e })),
  }
}

export function environmentInfo() {
  if (typeof window === 'undefined') return {}
  const nav = window.navigator || {}
  const uaData = nav.userAgentData
  return {
    userAgent: redactText(nav.userAgent || '', 500),
    platform: uaData?.platform || nav.platform || '',
    mobile: typeof uaData?.mobile === 'boolean' ? uaData.mobile : undefined,
    language: nav.language || '',
    viewport: `${window.innerWidth}x${window.innerHeight}@${window.devicePixelRatio || 1}`,
    screen: window.screen ? `${window.screen.width}x${window.screen.height}` : '',
    theme: document.documentElement?.dataset?.bsTheme || '',
    online: typeof nav.onLine === 'boolean' ? nav.onLine : undefined,
  }
}

/** Test helper. */
export function _resetDiagnostics() {
  state.consoleErrors.length = 0
  state.failedRequests.length = 0
  state.breadcrumbs.length = 0
}
