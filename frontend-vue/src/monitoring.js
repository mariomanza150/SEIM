/**
 * Error reporting and log capture (GlitchTip via the Sentry SDK).
 *
 * Everything is driven by VITE_SENTRY_* build-time env vars; with no VITE_SENTRY_DSN this is a no-op
 * and the SDK is never loaded. The DSN points at the public GlitchTip ingest host, which only accepts
 * /api/<id>/envelope|store. VITE_SENTRY_TUNNEL can route events through a same-origin relay instead.
 *
 * Privacy (public repo, student data): sendDefaultPii is off; request bodies, cookies, auth headers,
 * tokens, names and e-mail addresses are scrubbed from errors, breadcrumbs and logs.
 */

export const FILTERED = '[Filtered]'
/**
 * scrubText returns at most this many characters (plus TRUNCATED). Longer input is cut to a window of
 * MAX_SCRUB_CHARS + SCRUB_WINDOW_SLACK at a token boundary, scrubbed, and the *scrubbed* text is cut
 * again at a token boundary, so a secret straddling the cut is never half-kept.
 */
export const MAX_SCRUB_CHARS = 8192
export const SCRUB_WINDOW_SLACK = 1024
export const TRUNCATED = '\u2026[truncated]'
// Token boundaries for cutting. "." "=" ":" "/" "?" "[" "]" are deliberately not boundaries, so a cut never
// keeps part of a JWT, a key=value pair, a URL or a "[Filtered]" marker.
const CUT_DELIMITERS = new Set([...' \t\r\n\f\v&,;\'"<>(){}|'])
export const UNSERIALIZABLE = '[unserializable]'

const SENSITIVE_KEY_PARTS = [
  'password', 'passwd', 'secret', 'token', 'authorization', 'cookie', 'session', 'csrf',
  'api_key', 'apikey', 'dsn', 'email', 'username', 'first_name', 'last_name', 'full_name',
  'display_name', 'firstname', 'lastname', 'fullname', 'phone', 'birth', 'curp', 'student_id',
]
// Plain 'name' is not here: contexts.os.name etc. are harmless (user.name goes with user).
const SENSITIVE_EXACT = new Set(['user_name', 'address', 'ip_address'])
// The (^|[^...]) prefix anchors the match at the start of a run, so long non-email runs stay linear.
// No lookbehind anywhere in this file: it is a syntax error on Safari/iOS < 16.4 and would break the app.
const EMAIL_RE = /(^|[^\w.+-])[\w.+-]+@[\w-]+(?:\.[\w-]+)+/g
const JWT_RE = /\beyJ[\w-]{5,}\.[\w-]{5,}\.[\w-]{5,}\b/g
const BEARER_RE = /\b(bearer|token|basic)\s+[A-Za-z0-9._~+/=-]{8,}/gi
// Bounded (0-40 chars) key prefix/suffix and a start-of-word prefix group: an open-ended [\w-]* here
// backtracked quadratically on long alphanumeric / base64 blobs (ReDoS). The optional quote on
// each side of the separator also catches JSON / repr / kwargs forms: {"password": "x"}, token='x'.
const KV_SECRET_RE = /(^|[^\w-])([\w-]{0,40}?(?:password|passwd|pwd|secret|token|api[-_]?key)[\w-]{0,40})(["']?\s*[=:]\s*["']?)[^&\s"',;]+/gi
const KV_NAME_RE = /(\b(?:name|nombre|full_name|first_name|last_name|apellidos?)\s*[=:]\s*)[^\s&,;'"=]+(?:\s+(?![\w-]+\s*[=:])[^\s&,;'"=]+){0,3}/gi
const QUERY_SECRET_RE = /([?&](?:token|access|refresh|key|code|password|email|signature|uid)[^=&]{0,40}=)[^&#\s]+/gi

export function isSensitiveKey(key) {
  const k = String(key).toLowerCase()
  return SENSITIVE_EXACT.has(k) || SENSITIVE_KEY_PARTS.some((p) => k.includes(p))
}

export function scrubText(value) {
  if (typeof value !== 'string') return value
  if (value.length <= MAX_SCRUB_CHARS) return scrubPatterns(value)
  const window = cutAtBoundary(value, MAX_SCRUB_CHARS + SCRUB_WINDOW_SLACK)
  return cutAtBoundary(scrubPatterns(window), MAX_SCRUB_CHARS) + TRUNCATED
}

/** First `limit` chars of `text`, minus any partial last token (dropped, never kept). */
function cutAtBoundary(text, limit) {
  if (text.length <= limit || CUT_DELIMITERS.has(text[limit])) return text.slice(0, limit)
  for (let i = limit - 1; i >= 0; i -= 1) {
    if (CUT_DELIMITERS.has(text[i])) return text.slice(0, i + 1)
  }
  return ''
}

function scrubPatterns(value) {
  return value
    .replace(EMAIL_RE, (_m, pre) => pre + FILTERED)
    .replace(JWT_RE, FILTERED)
    .replace(BEARER_RE, (_m, kind) => `${kind} ${FILTERED}`)
    .replace(QUERY_SECRET_RE, (_m, prefix) => prefix + FILTERED)
    .replace(KV_SECRET_RE, (_m, pre, key, sep) => pre + key + sep + FILTERED)
    .replace(KV_NAME_RE, (_m, prefix) => prefix + FILTERED)
}

export function scrub(value, depth = 0) {
  if (depth > 12) return FILTERED
  if (typeof value === 'string') return scrubText(value)
  if (Array.isArray(value)) return value.map((v) => scrub(v, depth + 1))
  if (value && typeof value === 'object') {
    const out = {}
    for (const [k, v] of Object.entries(value)) {
      out[k] = isSensitiveKey(k) ? FILTERED : scrub(v, depth + 1)
    }
    return out
  }
  return value
}

/** String(value) that never throws (e.g. a throwing toString); returns UNSERIALIZABLE instead. */
export function safeString(value) {
  try {
    return String(value)
  } catch {
    return UNSERIALIZABLE
  }
}

function scrubBreadcrumbValues(crumbs) {
  for (const crumb of crumbs || []) {
    if (crumb.message) crumb.message = scrubText(crumb.message)
    if (crumb.data) crumb.data = scrub(crumb.data)
  }
}

/**
 * beforeSend / beforeSendTransaction: strip request bodies, cookies, auth headers and user identity;
 * mask transaction names, spans, URLs (location.href and Referer carry reset/verify tokens) and the rest.
 */
export function scrubEvent(event) {
  if (!event) return event
  if (event.transaction) event.transaction = scrubText(event.transaction)
  for (const span of event.spans || []) {
    if (span.description) span.description = scrubText(span.description)
    if (span.data) span.data = scrub(span.data)
  }
  const req = event.request
  if (req) {
    delete req.data
    delete req.cookies
    if (req.headers) req.headers = scrub(req.headers)
    if (req.url) req.url = scrubText(req.url)
    if (typeof req.query_string === 'string') req.query_string = scrubText(`?${req.query_string}`).slice(1)
  }
  if (event.user) event.user = event.user.id != null ? { id: event.user.id } : {}
  for (const key of ['extra', 'contexts', 'tags']) {
    if (event[key]) event[key] = scrub(event[key])
  }
  if (event.message) event.message = scrubText(event.message)
  if (event.logentry) {
    delete event.logentry.params
    if (event.logentry.message) event.logentry.message = scrubText(event.logentry.message)
  }
  for (const exc of event.exception?.values || []) {
    if (exc.value) exc.value = scrubText(exc.value)
  }
  scrubBreadcrumbValues(event.breadcrumbs)
  return event
}

/** beforeBreadcrumb: keep breadcrumbs bounded and free of secrets (no request/response bodies). */
export function scrubBreadcrumb(crumb) {
  if (!crumb) return crumb
  if (crumb.data) {
    delete crumb.data.body
    delete crumb.data.request_body
    delete crumb.data.response_body
  }
  scrubBreadcrumbValues([crumb])
  if (typeof crumb.message === 'string' && crumb.message.length > 500) {
    crumb.message = `${crumb.message.slice(0, 500)}…`
  }
  return crumb
}

const LOG_WINDOW_MS = 60_000
const LOG_MAX_PER_WINDOW = 30
const logSeen = new Map()
let logWindowStart = 0
let logWindowCount = 0

/** Drop repeats of the same message within a minute and cap logs at 30 per minute. */
export function allowLog(log, now = Date.now()) {
  if (now - logWindowStart > LOG_WINDOW_MS) {
    logWindowStart = now
    logWindowCount = 0
    logSeen.clear()
  }
  const key = `${log.level}:${safeString(log.message).slice(0, 200)}`
  if (logSeen.has(key) || logWindowCount >= LOG_MAX_PER_WINDOW) return false
  logSeen.set(key, now)
  logWindowCount += 1
  return true
}

export function resetLogLimiter() {
  logSeen.clear()
  logWindowStart = 0
  logWindowCount = 0
}

/** beforeSendLog: rate-limit/dedupe, then mask the message and attributes of a structured log. */
export function scrubLog(log) {
  if (!log) return log
  if (!allowLog(log)) return null
  if (typeof log.message === 'string') log.message = scrubText(log.message)
  if (log.attributes) {
    // Drop message parameters entirely (names etc.); the message already holds the scrubbed text.
    const kept = Object.fromEntries(
      Object.entries(log.attributes).filter(([k]) => !k.startsWith('sentry.message.parameter')),
    )
    log.attributes = scrub(kept)
  }
  return log
}

function rate(value, fallback) {
  const n = Number.parseFloat(value)
  return Number.isFinite(n) && n >= 0 && n <= 1 ? n : fallback
}

const LOG_LEVELS = ['trace', 'debug', 'info', 'log', 'warn', 'error']

/** Resolved settings from VITE_SENTRY_* vars (null when disabled). */
export function monitoringConfig(env = import.meta.env) {
  const dsn = (env.VITE_SENTRY_DSN || '').trim()
  if (!dsn) return null
  const logsLevel = String(env.VITE_SENTRY_LOGS_LEVEL ?? 'warn').trim().toLowerCase()
  const at = LOG_LEVELS.indexOf(logsLevel === 'warning' ? 'warn' : logsLevel)
  return {
    dsn,
    environment: env.VITE_SENTRY_ENVIRONMENT || env.MODE || 'production',
    release: env.VITE_SENTRY_RELEASE || undefined,
    sampleRate: rate(env.VITE_SENTRY_SAMPLE_RATE, 1),
    tracesSampleRate: rate(env.VITE_SENTRY_TRACES_SAMPLE_RATE, 0.05),
    tunnel: env.VITE_SENTRY_TUNNEL || undefined,
    consoleLevels: at < 0 ? [] : LOG_LEVELS.slice(at),
    maxBreadcrumbs: 50,
  }
}

/** True for "Failed to fetch dynamically imported module" style chunk-load failures. */
export function isChunkLoadError(error) {
  const msg = String(error?.message || error || '')
  return /dynamically imported module|Importing a module script failed|error loading dynamically imported|Loading chunk [\w-]+ failed|ChunkLoadError/i.test(msg)
}

/** Anchored trace-propagation targets: relative paths and our exact origin only. */
export function ownOriginTargets(origin) {
  const targets = [/^\/(?!\/)/]
  if (origin) {
    const escaped = origin.replace(/[.*+?^${}()|[\]\\/]/g, '\\$&')
    targets.push(new RegExp(`^${escaped}(?:/|$)`))
  }
  return targets
}

/** Run initMonitoring but give up waiting after timeoutMs so a hanging SDK chunk can't blank the page. */
export function initMonitoringWithTimeout(app, router, timeoutMs = 3000, init = initMonitoring) {
  let timer
  const timeout = new Promise((resolve) => {
    timer = setTimeout(() => resolve(false), timeoutMs)
  })
  return Promise.race([Promise.resolve().then(() => init(app, router)).catch(() => false), timeout]).finally(() =>
    clearTimeout(timer),
  )
}

let sentry = null

/**
 * Initialise reporting for the Vue app. Resolves to false (and loads nothing) without a DSN.
 * Unhandled errors and promise rejections are captured by the SDK's global handlers; Vue component
 * errors by its errorHandler; router navigation and failed lazy route imports via router.onError.
 */
export async function initMonitoring(app, router, env = import.meta.env) {
  const cfg = monitoringConfig(env)
  if (!cfg) return false
  try {
    sentry = await import('@sentry/vue')
  } catch {
    return false
  }
  const integrations = [
    sentry.browserApiErrorsIntegration(),
    sentry.globalHandlersIntegration({ onerror: true, onunhandledrejection: true }),
    sentry.breadcrumbsIntegration({ console: true, dom: true, fetch: true, xhr: true, history: true }),
  ]
  if (cfg.consoleLevels.length) integrations.push(sentry.consoleLoggingIntegration({ levels: cfg.consoleLevels }))
  if (cfg.tracesSampleRate > 0 && router) integrations.push(sentry.browserTracingIntegration({ router }))
  sentry.init({
    app,
    dsn: cfg.dsn,
    environment: cfg.environment,
    release: cfg.release,
    sampleRate: cfg.sampleRate,
    tracesSampleRate: cfg.tracesSampleRate,
    tunnel: cfg.tunnel || undefined,
    sendDefaultPii: false,
    maxBreadcrumbs: cfg.maxBreadcrumbs,
    enableLogs: cfg.consoleLevels.length > 0,
    attachProps: false,
    integrations,
    beforeSend: scrubEvent,
    beforeSendTransaction: scrubEvent,
    // Trace headers only to our own origin (relative /api calls), never to third parties.
    tracePropagationTargets: ownOriginTargets(typeof window !== 'undefined' ? window.location.origin : ''),
    beforeBreadcrumb: scrubBreadcrumb,
    beforeSendLog: scrubLog,
  })
  if (router) {
    router.onError((error, to) => {
      sentry.withScope((scope) => {
        scope.setTag('router_error', isChunkLoadError(error) ? 'chunk_load' : 'navigation')
        if (to?.name) scope.setTag('route', String(to.name))
        sentry.captureException(error)
      })
    })
  }
  return true
}

/** Report a handled error (no-op when monitoring is off). */
export function captureError(error, context) {
  if (sentry) sentry.captureException(error, context ? { extra: scrub(context) } : undefined)
}
