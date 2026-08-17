import { describe, expect, it, vi, afterEach, beforeEach } from 'vitest'

import NotificationWebSocket, { resolveNotificationWsUrl } from '@/services/websocket'

describe('resolveNotificationWsUrl', () => {
  const browserLocation = {
    protocol: 'http:',
    host: '127.0.0.1:8001',
  }

  it('uses configured websocket base when it is valid', () => {
    const url = resolveNotificationWsUrl(
      { VITE_WS_BASE_URL: 'ws://localhost:8001' },
      browserLocation
    )

    expect(url).toBe('ws://localhost:8001/ws/notifications/')
  })

  it('falls back to same-origin when websocket env uses a placeholder host', () => {
    const url = resolveNotificationWsUrl(
      { VITE_WS_BASE_URL: 'wss://your-domain.com' },
      browserLocation
    )

    expect(url).toBe('ws://127.0.0.1:8001/ws/notifications/')
  })

  it('falls back to same-origin when api env uses a placeholder host', () => {
    const url = resolveNotificationWsUrl(
      { VITE_API_BASE_URL: 'https://your-domain.com' },
      browserLocation
    )

    expect(url).toBe('ws://127.0.0.1:8001/ws/notifications/')
  })
})

describe('NotificationWebSocket application.sync', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('dispatches seim-application-sync for application.sync payloads', () => {
    const spy = vi.spyOn(window, 'dispatchEvent')
    const ws = new NotificationWebSocket()
    ws._onMessage({
      data: JSON.stringify({
        type: 'application.sync',
        application_id: 'app-1',
        change_type: 'comment_added',
        document_id: 'doc-9',
      }),
    })
    const custom = spy.mock.calls.find((c) => c[0]?.type === 'seim-application-sync')
    expect(custom).toBeTruthy()
    expect(custom[0].detail.applicationId).toBe('app-1')
    expect(custom[0].detail.documentId).toBe('doc-9')
  })
})

describe('NotificationWebSocket reconnect and heartbeat', () => {
  let sockets

  beforeEach(() => {
    sockets = []
    vi.useFakeTimers()
    vi.stubGlobal(
      'WebSocket',
      class MockWebSocket {
        static OPEN = 1
        static CLOSED = 3
        constructor(url) {
          this.url = url
          this.readyState = MockWebSocket.OPEN
          this.sent = []
          sockets.push(this)
        }
        send(payload) {
          this.sent.push(payload)
        }
        close() {
          this.readyState = MockWebSocket.CLOSED
        }
      }
    )
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.unstubAllGlobals()
    vi.restoreAllMocks()
  })

  it('sends ping heartbeats while connected', () => {
    const ws = new NotificationWebSocket()
    ws.connect('access-token')
    ws._onOpen()

    vi.advanceTimersByTime(30000)

    expect(sockets[0].sent[0]).toContain('"type":"ping"')
  })

  it('refreshes JWT before reconnecting after an unexpected close', async () => {
    const refreshToken = vi.fn().mockResolvedValue('fresh-token')
    const ws = new NotificationWebSocket({
      getToken: () => 'stale-token',
      refreshToken,
    })
    ws.connect('stale-token')
    ws._onClose({ code: 4001 })

    await vi.advanceTimersByTimeAsync(2000)

    expect(refreshToken).toHaveBeenCalled()
    expect(sockets.at(-1).url).toContain('fresh-token')
  })

  it('reconnects with a fresh token when the browser comes back online', async () => {
    const refreshToken = vi.fn().mockResolvedValue('online-token')
    const ws = new NotificationWebSocket({
      getToken: () => null,
      refreshToken,
    })
    ws.connect('initial-token')
    ws.ws = null
    ws._onOnline()

    await Promise.resolve()

    expect(refreshToken).toHaveBeenCalled()
    expect(sockets.at(-1).url).toContain('online-token')
  })

  it('does not refresh JWT on a generic socket drop when an access token is still present', async () => {
    const refreshToken = vi.fn().mockResolvedValue('fresh-token')
    const ws = new NotificationWebSocket({
      getToken: () => 'stale-token',
      refreshToken,
    })
    ws.connect('stale-token')
    ws._onClose({ code: 1006 })

    await vi.advanceTimersByTimeAsync(2000)

    expect(refreshToken).not.toHaveBeenCalled()
    expect(sockets.at(-1).url).toContain('stale-token')
  })
})
