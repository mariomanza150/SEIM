import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import {
  FILTERED,
  MAX_SCRUB_CHARS,
  TRUNCATED,
  safeString,
  initMonitoring,
  isChunkLoadError,
  allowLog,
  ownOriginTargets,
  initMonitoringWithTimeout,
  resetLogLimiter,
  monitoringConfig,
  scrub,
  scrubBreadcrumb,
  scrubEvent,
  scrubLog,
  scrubText,
} from './monitoring'

describe('monitoringConfig', () => {
  it('is disabled without a DSN', () => {
    expect(monitoringConfig({})).toBeNull()
    expect(monitoringConfig({ VITE_SENTRY_DSN: '  ' })).toBeNull()
  })

  it('reads env vars with safe defaults', () => {
    const cfg = monitoringConfig({
      VITE_SENTRY_DSN: 'https://k@gt.example/3',
      VITE_SENTRY_ENVIRONMENT: 'local-prod',
      VITE_SENTRY_RELEASE: 'abc123',
      VITE_SENTRY_SAMPLE_RATE: '0.5',
      VITE_SENTRY_TRACES_SAMPLE_RATE: 'nope',
    })
    expect(cfg).toMatchObject({
      environment: 'local-prod',
      release: 'abc123',
      sampleRate: 0.5,
      tracesSampleRate: 0.05,
      tunnel: undefined,
      consoleLevels: ['warn', 'error'],
    })
  })

  it('can turn log capture off or widen it', () => {
    const base = { VITE_SENTRY_DSN: 'https://k@gt.example/3' }
    expect(monitoringConfig({ ...base, VITE_SENTRY_LOGS_LEVEL: 'off' }).consoleLevels).toEqual([])
    expect(monitoringConfig({ ...base, VITE_SENTRY_LOGS_LEVEL: 'info' }).consoleLevels).toEqual([
      'info', 'log', 'warn', 'error',
    ])
  })
})

describe('initMonitoring', () => {
  it('is a no-op without a DSN', async () => {
    expect(await initMonitoring({}, null, {})).toBe(false)
  })
})

describe('scrubbing', () => {
  beforeEach(() => resetLogLimiter())

  it('masks emails, tokens and secret query params in text', () => {
    const out = scrubText(
      'user ana@uni.mx Bearer abcdefghijkl eyJhbGciOi.eyJzdWIiOi.c2lnbmF0dXJl /x?token=s3cr3t&page=2'
    )
    expect(out).not.toMatch(/ana@uni\.mx|abcdefghijkl|eyJhbGciOi|s3cr3t/)
    expect(out).toContain('page=2')
  })

  it('masks sensitive keys recursively but keeps others', () => {
    expect(scrub({ password: 'x', nested: { first_name: 'Ana', email: 'a@b.co', count: 2 }, os: { name: 'Linux' } })).toEqual({
      password: FILTERED,
      nested: { first_name: FILTERED, email: FILTERED, count: 2 },
      os: { name: 'Linux' },
    })
  })

  it('strips request bodies, cookies, auth headers and user identity from events', () => {
    const event = scrubEvent({
      request: {
        url: 'https://seim.test/reset?token=abc123',
        data: '{"password":"x"}',
        cookies: { sessionid: 'y' },
        headers: { Authorization: 'Bearer zzzzzzzzzz', Accept: 'json' },
      },
      user: { id: 7, email: 'a@b.co', username: 'ana' },
      exception: { values: [{ value: 'failed for a@b.co' }] },
      breadcrumbs: [{ message: 'login a@b.co', data: { url: '/api?token=t0k3n' } }],
    })
    expect(event.request.data).toBeUndefined()
    expect(event.request.cookies).toBeUndefined()
    expect(event.request.headers).toEqual({ Authorization: FILTERED, Accept: 'json' })
    expect(event.request.url).not.toContain('abc123')
    expect(event.user).toEqual({ id: 7 })
    expect(event.exception.values[0].value).not.toContain('a@b.co')
    expect(event.breadcrumbs[0].message).not.toContain('a@b.co')
    expect(event.breadcrumbs[0].data.url).not.toContain('t0k3n')
  })

  it('bounds breadcrumbs and drops bodies', () => {
    const crumb = scrubBreadcrumb({ message: 'x'.repeat(900), data: { body: 'secret', status_code: 500 } })
    expect(crumb.message.length).toBeLessThanOrEqual(501)
    expect(crumb.data).toEqual({ status_code: 500 })
  })

  it('masks key=value secrets and uid params', () => {
    const out = scrubText('password=hunter2 api_key: abc123 /verify?uid=MTIz&page=1')
    expect(out).not.toMatch(/hunter2|abc123|MTIz/)
    expect(out).toContain('page=1')
  })

  it('scrubs transactions: name, request URL/Referer, spans, breadcrumbs and user', () => {
    const tx = scrubEvent({
      type: 'transaction',
      transaction: '/seim/reset?token=t0k3n&email=a@b.co',
      request: { url: 'https://s/seim/verify?uid=MTIz&token=zz', headers: { Referer: 'https://s/reset?token=r3f' } },
      spans: [{ description: 'GET /api/x?token=sp4n', data: { 'http.url': '/api/x?email=a@b.co', url: '/y?token=d4t4' } }],
      breadcrumbs: [{ category: 'navigation', data: { from: '/reset?token=n4v', to: '/home' } }],
      user: { id: 9, name: 'Ana', email: 'a@b.co', ip_address: '1.2.3.4' },
    })
    const json = JSON.stringify(tx)
    expect(json).not.toMatch(/t0k3n|a@b\.co|MTIz|zz"|r3f|sp4n|d4t4|n4v|Ana|1\.2\.3\.4/)
    expect(tx.user).toEqual({ id: 9 })
  })

  it('scrubs structured logs', () => {
    const log = scrubLog({ message: 'hi a@b.co', attributes: { token: 't', route: 'home' } })
    expect(log).toEqual({ message: `hi ${FILTERED}`, attributes: { token: FILTERED, route: 'home' } })
  })
})

describe('isChunkLoadError', () => {
  it('detects failed dynamic imports', () => {
    expect(isChunkLoadError(new TypeError('Failed to fetch dynamically imported module: /static/a.js'))).toBe(true)
    expect(isChunkLoadError(new Error('boom'))).toBe(false)
  })
})

describe('message parameters', () => {
  beforeEach(() => resetLogLimiter())

  it('are dropped from logs and events', () => {
    const log = scrubLog({
      level: 'warn',
      message: 'hi',
      attributes: { 'sentry.message.template': 'hi %s', 'sentry.message.parameter.0': 'Ana Perez' },
    })
    expect(log.attributes).toEqual({ 'sentry.message.template': 'hi %s' })
    const event = scrubEvent({ logentry: { message: 'hi %s', params: ['Ana Perez'] } })
    expect(JSON.stringify(event)).not.toContain('Ana Perez')
  })
})

describe('log limiter', () => {
  beforeEach(() => resetLogLimiter())

  it('drops duplicate messages within a minute and caps volume', () => {
    expect(allowLog({ level: 'warn', message: 'x' }, 1000)).toBe(true)
    expect(allowLog({ level: 'warn', message: 'x' }, 2000)).toBe(false)
    for (let i = 0; i < 40; i += 1) allowLog({ level: 'warn', message: `m${i}` }, 3000)
    expect(allowLog({ level: 'warn', message: 'new' }, 4000)).toBe(false)
    expect(allowLog({ level: 'warn', message: 'x' }, 70_000)).toBe(true)
  })

  it('beforeSendLog drops a repeat', () => {
    expect(scrubLog({ level: 'warn', message: 'dup' })).not.toBeNull()
    expect(scrubLog({ level: 'warn', message: 'dup' })).toBeNull()
  })
})

describe('compound secret and name keys', () => {
  it('masks access_token, client_secret, secret_key, apiKey and name fields', () => {
    const out = scrubText(
      'access_token=a1 client_secret=b2 secret_key: c3 apiKey=d4 X-Api-Key=e5 name=Ana nombre=Ana full_name=Ana Perez filename=report.pdf',
    )
    for (const leaked of ['a1', 'b2', 'c3', 'd4', 'e5', 'Ana']) expect(out).not.toContain(leaked)
    expect(out).toContain('filename=report.pdf')
  })

  it('stringifies non-plain values via scrub', () => {
    expect(scrub({ n: 5, ok: true, none: null })).toEqual({ n: 5, ok: true, none: null })
  })
})

describe('ownOriginTargets', () => {
  const match = (targets, url) => targets.some((re) => re.test(url))
  it('matches only relative paths and our exact origin', () => {
    const t = ownOriginTargets('https://seim.incognitoslw.com')
    expect(match(t, '/api/x')).toBe(true)
    expect(match(t, 'https://seim.incognitoslw.com/api/x')).toBe(true)
    expect(match(t, 'https://evil.example/?next=https://seim.incognitoslw.com/')).toBe(false)
    expect(match(t, 'https://seim.incognitoslw.com.evil.example/')).toBe(false)
    expect(match(t, '//evil.example/x')).toBe(false)
  })
})

describe('initMonitoringWithTimeout', () => {
  it('resolves false after the timeout when the SDK hangs', async () => {
    vi.useFakeTimers()
    const p = initMonitoringWithTimeout({}, null, 3000, () => new Promise(() => {}))
    vi.advanceTimersByTime(3000)
    await expect(p).resolves.toBe(false)
    vi.useRealTimers()
  })

  it('passes through a fast init and swallows errors', async () => {
    await expect(initMonitoringWithTimeout({}, null, 3000, async () => true)).resolves.toBe(true)
    await expect(initMonitoringWithTimeout({}, null, 3000, async () => { throw new Error('x') })).resolves.toBe(false)
  })
})

describe('ReDoS regression', () => {
  const bestOf = (fn, runs = 3) => {
    let best = Infinity
    for (let i = 0; i < runs; i += 1) {
      const start = performance.now()
      fn()
      best = Math.min(best, performance.now() - start)
    }
    return best
  }

  it.each([
    ['dash-separated 100 KB', 'a-'.repeat(51200)],
    ['alphanumeric 100 KB', 'Zx9Qa7Lm3Kp2Vb8N'.repeat(6400)],
  ])('scrubs %s in under 100 ms', (_label, payload) => {
    expect(payload.length).toBeGreaterThanOrEqual(100 * 1024)
    const elapsed = bestOf(() => scrubText(payload))
    expect(elapsed).toBeLessThan(100)
    const out = scrubText(payload)
    expect(out.endsWith(TRUNCATED)).toBe(true)
    expect(out.length).toBeLessThanOrEqual(MAX_SCRUB_CHARS + 20)
  })

  it('keeps key=value secret masking with the bounded regex', () => {
    const out = scrubText('pwd=p1 db_password = p2, token:p3;ok=1 user_secret_value=p4')
    for (const leaked of ['p1', 'p2', 'p3', 'p4']) expect(out).not.toContain(leaked)
    expect(out).toContain(`db_password = ${FILTERED},`)
    expect(out).toContain('ok=1')
  })

  it('truncates before masking so emails stay masked', () => {
    const out = scrubText(`ana@uni.mx ${'x'.repeat(MAX_SCRUB_CHARS * 2)}`)
    expect(out).not.toContain('ana@uni.mx')
    expect(out.endsWith(TRUNCATED)).toBe(true)
  })

  it('safeString never throws', () => {
    const broken = { toString() { throw new Error('boom') } }
    expect(safeString(broken)).toBe('[unserializable]')
    expect(safeString(42)).toBe('42')
  })
})

// import.meta.url is not a file: URL under the jsdom environment, so resolve from this spec's path.
const MONITORING_DIR = dirname(fileURLToPath(new URL(import.meta.url, 'file:///')))

describe('truncation and browser compatibility', () => {
  const bestOf = (fn, runs = 3) => {
    let best = Infinity
    for (let i = 0; i < runs; i += 1) {
      const start = performance.now()
      fn()
      best = Math.min(best, performance.now() - start)
    }
    return best
  }

  it.each([
    ['blob then space', 'Zx9Qa7Lm3Kp2Vb8N'.repeat(570) + ' ' + 'a-'.repeat(50000)],
    ['?token 100 KB', '?token'.repeat(17100)],
    ['spaced ?token 100 KB', ('?token'.repeat(1600) + ' ').repeat(11)],
  ])('scrubs %s in under 100 ms', (_label, payload) => {
    expect(payload.length).toBeGreaterThanOrEqual(100 * 1024)
    expect(bestOf(() => scrubText(payload))).toBeLessThan(100)
  })

  const secrets = {
    email: 'ana.perez@uni.edu',
    jwt: 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjMifQ.c2lnbmF0dXJlLXZhbHVl',
    bearer: 'Bearer s3cr3tT0k3nValue99',
  }

  it.each(Object.keys(secrets))('leaves no %s fragment at any cut position', (kind) => {
    const secret = secrets[kind]
    expect(secret).not.toContain('~')
    const filler = '~ '.repeat(3000)
    for (let offset = -2; offset < secret.length + 3; offset += 1) {
      const prefixLen = MAX_SCRUB_CHARS - offset
      const text = '~ '.repeat(Math.floor(prefixLen / 2) + 1).slice(0, prefixLen) + secret + ' ' + filler
      const out = scrubText(text)
      expect(out.endsWith(TRUNCATED)).toBe(true)
      const residue = out.replace(TRUNCATED, '').split(FILTERED).join('').split('Bearer').join('')
      expect(residue, `${kind} leaked at cut offset ${offset}: ${out.slice(-60)}`).toMatch(/^[~ ]*$/)
    }
  })

  it('masks emails and secret keys at the very start of the text', () => {
    expect(scrubText('ana@uni.edu')).toBe(FILTERED)
    expect(scrubText('pwd=p1')).toBe(`pwd=${FILTERED}`)
    expect(scrubText('a@b.co,c@d.co')).toBe(`${FILTERED},${FILTERED}`)
  })

  it('uses no regex lookbehind (Safari/iOS < 16.4 cannot parse it)', () => {
    const source = readFileSync(resolve(MONITORING_DIR, 'monitoring.js'), 'utf8')
    expect(source).not.toContain('(?<')
  })
})

describe('quoted secret keys', () => {
  it.each([
    ['{"password": "x"}', `{"password": "${FILTERED}"}`],
    ["{'api_key': 'x'}", `{'api_key': '${FILTERED}'}`],
    ['password="x"', `password="${FILTERED}"`],
    ["token='x'", `token='${FILTERED}'`],
    ['{"access_token":"x"}', `{"access_token":"${FILTERED}"}`],
  ])('masks %s', (text, expected) => {
    expect(scrubText(text)).toBe(expected)
  })

  it.each([
    ['my_access_token=abc', `my_access_token=${FILTERED}`],
    ['x-api-key: abc', `x-api-key: ${FILTERED}`],
    ['token=1&token=2', `token=${FILTERED}&token=${FILTERED}`],
    ['status code: 500', 'status code: 500'],
    ['filename="a.txt"', 'filename="a.txt"'],
  ])('keeps unquoted behaviour for %s', (text, expected) => {
    expect(scrubText(text)).toBe(expected)
  })
})
