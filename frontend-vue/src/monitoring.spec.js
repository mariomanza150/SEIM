import { describe, it, expect, beforeEach } from 'vitest'
import {
  FILTERED,
  initMonitoring,
  isChunkLoadError,
  allowLog,
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
