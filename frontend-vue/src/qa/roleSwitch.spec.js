/**
 * @vitest-environment jsdom
 */
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { STASH_KEY, clearStash, readStash, returnToMyAccount, startImpersonation, switchToDemo } from './roleSwitch'

vi.mock('@/services/api', () => ({ default: { get: vi.fn(), post: vi.fn(), patch: vi.fn() } }))

describe('role switcher', () => {
  let auth
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
    vi.clearAllMocks()
    auth = useAuthStore()
    auth.adoptTokens = vi.fn(async (a, r) => {
      localStorage.setItem('access_token', a)
      localStorage.setItem('refresh_token', r)
      auth.accessToken = a
    })
    auth.logout = vi.fn()
    auth.accessToken = 'tester-access'
    auth.user = { email: 'me@x.com' }
    localStorage.setItem('refresh_token', 'tester-refresh')
    api.get.mockResolvedValue({ data: { enabled: true, is_tester: true } })
  })

  it('stashes the tester session and adopts demo tokens', async () => {
    api.post.mockResolvedValue({ data: { access: 'demo-a', refresh: 'demo-r', acting_as: { email: 's@test.com' } } })
    const acting = await switchToDemo('u1')
    expect(api.post).toHaveBeenCalledWith('/api/qa/demo-login/', { user_id: 'u1' })
    expect(acting.email).toBe('s@test.com')
    expect(readStash()).toEqual({ access: 'tester-access', refresh: 'tester-refresh', email: 'me@x.com' })
    expect(auth.adoptTokens).toHaveBeenCalledWith('demo-a', 'demo-r')
  })

  it('keeps the original stash when switching twice', async () => {
    api.post.mockResolvedValue({ data: { access: 'demo-a', refresh: 'demo-r' } })
    await switchToDemo('u1')
    api.post.mockResolvedValue({ data: { access: 'demo-b', refresh: 'demo-r2' } })
    await switchToDemo('u2')
    expect(readStash().access).toBe('tester-access')
  })

  it('impersonation sends the reason', async () => {
    api.post.mockResolvedValue({ data: { access: 'x', refresh: 'y' } })
    await startImpersonation('u9', 'QA-3')
    expect(api.post).toHaveBeenCalledWith('/api/qa/impersonate/', { user_id: 'u9', reason: 'QA-3' })
  })

  it('returns to the stashed account and clears the stash', async () => {
    localStorage.setItem(STASH_KEY, JSON.stringify({ access: 'ta', refresh: 'tr', email: 'me@x.com' }))
    localStorage.setItem('refresh_token', 'demo-r')
    api.post.mockResolvedValue({ status: 204 })
    expect(await returnToMyAccount()).toBe(true)
    expect(api.post).toHaveBeenCalledWith('/api/qa/demo-login/return/', { refresh: 'demo-r' })
    expect(auth.adoptTokens).toHaveBeenCalledWith('ta', 'tr')
    expect(readStash()).toBeNull()
  })

  it('logs out when nothing is stashed', async () => {
    api.post.mockRejectedValue(new Error('net'))
    expect(await returnToMyAccount()).toBe(false)
    expect(auth.logout).toHaveBeenCalled()
  })

  it('ignores corrupt stash data', () => {
    localStorage.setItem(STASH_KEY, '{bad')
    expect(readStash()).toBeNull()
    clearStash()
    expect(localStorage.getItem(STASH_KEY)).toBeNull()
  })
})
