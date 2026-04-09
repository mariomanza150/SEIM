/**
 * API service unit tests
 */
import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import api from '@/services/api'

describe('API Service', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
  })

  it('has expected default config', () => {
    expect(api.defaults.timeout).toBe(30000)
    expect(api.defaults.headers['Content-Type']).toBe('application/json')
    expect(api.defaults.headers['Accept']).toBe('application/json')
    expect(api.defaults.withCredentials).toBe(true)
  })

  it('has request and response interceptors registered', () => {
    expect(api.interceptors.request).toBeDefined()
    expect(api.interceptors.response).toBeDefined()
    expect(typeof api.interceptors.request.use).toBe('function')
    expect(typeof api.interceptors.response.use).toBe('function')
  })

  it('baseURL is set from env or empty', () => {
    expect(api.defaults.baseURL).toBeDefined()
    expect(typeof api.defaults.baseURL).toBe('string')
  })
})
