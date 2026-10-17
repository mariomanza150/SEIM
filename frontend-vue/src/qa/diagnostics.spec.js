/**
 * @vitest-environment jsdom
 */
import { beforeEach, describe, expect, it } from 'vitest'
import {
  _resetDiagnostics,
  environmentInfo,
  installDiagnostics,
  recordConsole,
  recordFailedRequest,
  recordNavigation,
  redactText,
  scrubUrl,
  snapshotDiagnostics,
} from './diagnostics'

describe('qa diagnostics', () => {
  beforeEach(() => _resetDiagnostics())

  it('scrubs sensitive query params and fragments', () => {
    const out = scrubUrl('/seim/reset?token=abc&tab=2&password=x#frag')
    expect(out).toContain('tab=2')
    expect(out).not.toContain('abc')
    expect(out).not.toContain('password=x')
    expect(out).not.toContain('frag')
  })

  it('redacts JWT-looking strings', () => {
    // Built at runtime so secret scanners do not flag the fixture.
    const jwt = ['eyJ' + 'hbGciOiJIUzI1NiJ9', 'eyJ' + 'zdWIiOiIxMjM0NSJ9', 'abcdefghijkl'].join('.')
    expect(redactText(`Bearer ${jwt}`)).toBe('Bearer [redacted-jwt]')
  })

  it('records failed requests without bodies or headers', () => {
    recordFailedRequest({
      config: { method: 'post', url: '/api/x/?code=123', data: { password: 'p' }, headers: { Authorization: 'B' }, __qaStart: Date.now() - 50 },
      response: { status: 500, headers: { 'x-request-id': 'req-1' }, data: { secret: 1 } },
    })
    const [entry] = snapshotDiagnostics().failedRequests
    expect(entry.method).toBe('POST')
    expect(entry.status).toBe(500)
    expect(entry.requestId).toBe('req-1')
    expect(entry.url).not.toContain('123')
    expect(JSON.stringify(entry)).not.toContain('password')
    expect(JSON.stringify(entry)).not.toContain('Authorization')
    expect(entry.durationMs).toBeGreaterThanOrEqual(0)
  })

  it('keeps ring buffers bounded', () => {
    for (let i = 0; i < 50; i += 1) recordConsole('error', [`e${i}`])
    for (let i = 0; i < 30; i += 1) recordFailedRequest({ config: { url: `/api/${i}` }, response: { status: 404 } })
    for (let i = 0; i < 20; i += 1) recordNavigation({ fullPath: `/p${i}`, name: 'X' }, { fullPath: '/' })
    const snap = snapshotDiagnostics()
    expect(snap.consoleErrors).toHaveLength(30)
    expect(snap.consoleErrors.at(-1).message).toBe('e49')
    expect(snap.failedRequests).toHaveLength(20)
    expect(snap.breadcrumbs).toHaveLength(10)
  })

  it('install patches console.error and window errors once', () => {
    const fake = { console: { error: () => {}, warn: () => {} }, addEventListener: (name, fn) => { fake[name] = fn } }
    installDiagnostics(fake)
    fake.console.error(new Error('kaput'))
    fake.unhandledrejection({ reason: 'nope' })
    const msgs = snapshotDiagnostics().consoleErrors.map((e) => e.message)
    expect(msgs[0]).toContain('kaput')
    expect(msgs[1]).toContain('nope')
  })

  it('reports environment info', () => {
    const env = environmentInfo()
    expect(env.viewport).toMatch(/\d+x\d+@/)
  })
})
