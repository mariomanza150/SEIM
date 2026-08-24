/**
 * In-memory GET cache for list resources (applications, programs, documents).
 */
import { defineStore } from 'pinia'
import api from '@/services/api'
import { unwrapPaginatedResults } from '@/utils/apiList'

const DEFAULT_TTL_MS = 30000

function cacheKey(url, params) {
  return `${url}?${JSON.stringify(params || {})}`
}

export const useResourceCacheStore = defineStore('resourceCache', () => {
  const entries = new Map()

  function peek(url, params) {
    const key = cacheKey(url, params)
    const hit = entries.get(key)
    if (!hit) return null
    if (Date.now() > hit.expiresAt) {
      entries.delete(key)
      return null
    }
    return hit.data
  }

  async function get(url, params = {}, { ttlMs = DEFAULT_TTL_MS, force = false } = {}) {
    if (!force) {
      const cached = peek(url, params)
      if (cached) return cached
    }
    const { data } = await api.get(url, { params })
    const key = cacheKey(url, params)
    entries.set(key, { data, expiresAt: Date.now() + ttlMs })
    return data
  }

  function invalidatePrefix(prefix) {
    for (const key of [...entries.keys()]) {
      if (key.startsWith(prefix)) entries.delete(key)
    }
  }

  function clear() {
    entries.clear()
  }

  async function getResults(url, params = {}, options) {
    const data = await get(url, params, options)
    return unwrapPaginatedResults(data)
  }

  return { peek, get, getResults, invalidatePrefix, clear }
})
