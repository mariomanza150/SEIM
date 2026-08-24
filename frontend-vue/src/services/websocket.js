/**
 * WebSocket client for real-time notifications (Django Channels).
 * Connects with JWT from query string; shows toasts and optional refresh on notification.new.
 */

import { getStoredAccessToken } from '@/utils/authTokens'
const RECONNECT_INITIAL_MS = 2000
const RECONNECT_MAX_MS = 30000
const RECONNECT_DECAY = 1.5
const RECONNECT_MAX_ATTEMPTS = 10
const NOTIFICATION_PATH = '/ws/notifications/'
const PLACEHOLDER_HOST_FRAGMENT = 'your-domain.com'
const AUTH_CLOSE_CODES = new Set([4001, 4003, 4401, 4403])

function hasPlaceholderHost(url) {
  if (!url) return false

  try {
    return new URL(url).hostname.includes(PLACEHOLDER_HOST_FRAGMENT)
  } catch {
    return url.includes(PLACEHOLDER_HOST_FRAGMENT)
  }
}

function buildNotificationUrl(baseUrl) {
  const normalizedBase = baseUrl.replace(/\/$/, '')
  return normalizedBase.includes(NOTIFICATION_PATH)
    ? normalizedBase.endsWith('/')
      ? normalizedBase
      : `${normalizedBase}/`
    : `${normalizedBase}${NOTIFICATION_PATH}`
}

export function resolveNotificationWsUrl(
  env = import.meta.env,
  currentLocation = typeof location !== 'undefined' ? location : null
) {
  const wsEnv = env.VITE_WS_BASE_URL
  if (wsEnv) {
    if (!hasPlaceholderHost(wsEnv)) {
      return buildNotificationUrl(wsEnv)
    }
  }

  const base = env.VITE_API_BASE_URL || ''
  if (base) {
    if (!hasPlaceholderHost(base)) {
      const wsBase = base.replace(/^http/i, 'ws')
      return buildNotificationUrl(wsBase)
    }
  }

  if (currentLocation) {
    const protocol = currentLocation.protocol === 'https:' ? 'wss:' : 'ws:'
    return `${protocol}//${currentLocation.host}${NOTIFICATION_PATH}`
  }

  return 'ws://localhost:5173/ws/notifications/'
}

function getWsUrl() {
  return resolveNotificationWsUrl()
}

class NotificationWebSocket {
  constructor(options = {}) {
    this.onNotification = options.onNotification || (() => {})
    this.onConnect = options.onConnect || (() => {})
    this.onDisconnect = options.onDisconnect || (() => {})
    this.getToken = options.getToken || (() => {
      try {
        return getStoredAccessToken()
      } catch {
        return null
      }
    })
    this.refreshToken = options.refreshToken || null
    this.ws = null
    this.pingTimer = null
    this.reconnectTimer = null
    this.reconnectAttempts = 0
    this.intentionalClose = false
    this._networkBound = false
    this._onOnline = null
    this._onOffline = null
  }

  connect(token) {
    if (!token) return
    const baseUrl = getWsUrl()
    if (!baseUrl) return
    if (this.ws && this.ws.readyState === WebSocket.OPEN) return

    this.intentionalClose = false
    this._bindNetworkListeners()
    const url = `${baseUrl}?token=${encodeURIComponent(token)}`
    try {
      this.ws = new WebSocket(url)
      this.ws.onopen = () => this._onOpen()
      this.ws.onmessage = (e) => this._onMessage(e)
      this.ws.onerror = (e) => this._onError(e)
      this.ws.onclose = (e) => this._onClose(e)
    } catch (err) {
      console.warn('WebSocket connect error:', err)
      this._scheduleReconnect(token)
    }
  }

  disconnect() {
    this.intentionalClose = true
    this._clearTimers()
    this._unbindNetworkListeners()
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.reconnectAttempts = 0
    this.onDisconnect()
  }

  _clearTimers() {
    if (this.pingTimer) {
      clearInterval(this.pingTimer)
      this.pingTimer = null
    }
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
  }

  _onOpen() {
    this.reconnectAttempts = 0
    this._startPing()
    this.onConnect()
  }

  _onMessage(event) {
    try {
      const data = JSON.parse(event.data)
      const type = data.type
      if (type === 'connection_established') {
        // optional: log or show connected
        return
      }
      if (type === 'notification.new' && data.notification) {
        this.onNotification(data.notification)
        return
      }
      if (type === 'application.sync' && data.application_id) {
        if (typeof window !== 'undefined') {
          window.dispatchEvent(
            new CustomEvent('seim-application-sync', {
              detail: {
                applicationId: data.application_id,
                changeType: data.change_type,
                documentId: data.document_id,
              },
            })
          )
        }
        return
      }
      if (type === 'pong') return
      if (type === 'error') {
        console.warn('WebSocket server error:', data.message)
        return
      }
    } catch (err) {
      console.warn('WebSocket message parse error:', err)
    }
  }

  _onError() {
    // Details often not available; rely on onclose for reconnect
  }

  _onClose(event) {
    this._clearTimers()
    this.ws = null
    if (this.intentionalClose) return
    if (typeof navigator !== 'undefined' && navigator.onLine === false) return
    const token = typeof this.getToken === 'function' ? this.getToken() : null
    if (token || this.refreshToken) {
      this._scheduleReconnect(token, {
        forceRefresh: AUTH_CLOSE_CODES.has(event?.code) || !token,
      })
    }
  }

  _startPing() {
    this.pingTimer = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: 'ping', timestamp: Date.now() }))
      }
    }, PING_INTERVAL_MS)
  }

  _scheduleReconnect(token, { forceRefresh = false } = {}) {
    if (this.reconnectAttempts >= RECONNECT_MAX_ATTEMPTS) return
    const delay = Math.min(
      RECONNECT_INITIAL_MS * Math.pow(RECONNECT_DECAY, this.reconnectAttempts),
      RECONNECT_MAX_MS
    )
    this.reconnectAttempts += 1
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null
      void this._connectWithFreshToken(token, forceRefresh)
    }, delay)
  }

  async _connectWithFreshToken(fallbackToken, forceRefresh = false) {
    let token = (typeof this.getToken === 'function' ? this.getToken() : null) || fallbackToken
    if (this.refreshToken && (forceRefresh || !token)) {
      try {
        const refreshed = await this.refreshToken()
        if (refreshed) token = refreshed
      } catch (err) {
        console.warn('WebSocket token refresh failed:', err)
        this.onDisconnect()
        return
      }
    }
    if (token) this.connect(token)
  }

  _bindNetworkListeners() {
    if (this._networkBound || typeof window === 'undefined') return
    this._onOnline = () => {
      this.reconnectAttempts = 0
      if (this.intentionalClose || this.isConnected()) return
      void this._connectWithFreshToken()
    }
    this._onOffline = () => {
      this._clearTimers()
    }
    window.addEventListener('online', this._onOnline)
    window.addEventListener('offline', this._onOffline)
    this._networkBound = true
  }

  _unbindNetworkListeners() {
    if (!this._networkBound || typeof window === 'undefined') return
    if (this._onOnline) window.removeEventListener('online', this._onOnline)
    if (this._onOffline) window.removeEventListener('offline', this._onOffline)
    this._onOnline = null
    this._onOffline = null
    this._networkBound = false
  }

  isConnected() {
    return this.ws != null && this.ws.readyState === WebSocket.OPEN
  }
}

let sharedInstance = null

/**
 * Get or create the shared notification WebSocket client.
 * @param {Object} options - { onNotification, onConnect, onDisconnect }
 * @returns {NotificationWebSocket}
 */
export function getNotificationWebSocket(options = {}) {
  if (!sharedInstance) {
    sharedInstance = new NotificationWebSocket(options)
  } else if (Object.keys(options).length > 0) {
    if (options.onNotification) sharedInstance.onNotification = options.onNotification
    if (options.onConnect) sharedInstance.onConnect = options.onConnect
    if (options.onDisconnect) sharedInstance.onDisconnect = options.onDisconnect
    if (options.getToken) sharedInstance.getToken = options.getToken
    if (options.refreshToken) sharedInstance.refreshToken = options.refreshToken
  }
  return sharedInstance
}

/**
 * Connect WebSocket when authenticated; disconnect on logout.
 * Call from App.vue with auth store and toast.
 * @param {Object} authStore - Pinia auth store
 * @param {Object} callbacks - { onNotification(notification), onConnect?, onDisconnect? }
 */
export function useNotificationWebSocket(authStore, callbacks = {}) {
  const ws = getNotificationWebSocket({
    onNotification: callbacks.onNotification || (() => {}),
    onConnect: callbacks.onConnect,
    onDisconnect: callbacks.onDisconnect,
    getToken: () => authStore.accessToken,
    refreshToken: typeof authStore.refreshToken === 'function' ? () => authStore.refreshToken() : null,
  })

  function connectIfAuthenticated() {
    if (authStore.isAuthenticated && authStore.accessToken) {
      ws.connect(authStore.accessToken)
    } else {
      ws.disconnect()
    }
  }

  function disconnect() {
    ws.disconnect()
  }

  return {
    connectIfAuthenticated,
    disconnect,
    isConnected: () => ws.isConnected(),
    getSocket: () => ws,
  }
}

export default NotificationWebSocket
