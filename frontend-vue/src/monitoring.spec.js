import { describe, it, expect } from 'vitest'
import {
  FILTERED,
  initMonitoring,
  isChunkLoadError,
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
      tracesSampleRate: 0,
      tunnel: '/api/monitoring/envelope/',
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
  it('masks emails, tokens and secret query params in text', () => {
    const out = scrubText(
      'user ana@uni.mx Bearer abcdefghijkl eyJhbGciOi.eyJzdWIiOi.c2lnbmF0dXJl /x?token=s3cr3t&page=2'
    )
    expect(out).not.toMatch(/ana@uni\.mx|abcdefghijkl|eyJhbGciOi|s3cr3t/)
    expect(out).toContain('page=2')
  })

  it('masks sensitive keys recursively but keeps others', () => {
    expect(scrub({ password: 'x', nested: { first_name: 'Ana', email: 'a@b.co', count: 2 }, name: 'Ana' })).toEqual({
      password: FILTERED,
      nested: { first_name: FILTERED, email: FILTERED, count: 2 },
      name: FILTERED,
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
