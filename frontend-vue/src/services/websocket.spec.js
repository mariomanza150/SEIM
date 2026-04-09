import { describe, expect, it, vi, afterEach } from 'vitest'

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
