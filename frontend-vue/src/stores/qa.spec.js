/**
 * @vitest-environment jsdom
 */
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import api from '@/services/api'
import { useQaStore } from './qa'

vi.mock('@/services/api', () => ({ default: { get: vi.fn() } }))

describe('qa store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('stays disabled when the context endpoint 404s', async () => {
    api.get.mockRejectedValue({ response: { status: 404 } })
    const qa = useQaStore()
    await qa.load()
    expect(qa.loaded).toBe(true)
    expect(qa.enabled).toBe(false)
    expect(qa.isTester).toBe(false)
    qa.openWidget()
    expect(qa.widgetOpen).toBe(false)
  })

  it('exposes tester and triager flags', async () => {
    api.get.mockResolvedValue({
      data: { enabled: true, is_tester: true, is_triager: true, deploy_tier: 'test', version: '1.0', commit: 'abcdef1234', acting_as: { email: 'demo@x' } },
    })
    const qa = useQaStore()
    await qa.load()
    expect(qa.isTester).toBe(true)
    expect(qa.isTriager).toBe(true)
    expect(qa.actingAs.email).toBe('demo@x')
    expect(qa.deployTier).toBe('test')
    qa.openWidget()
    expect(qa.widgetOpen).toBe(true)
    qa.reset()
    expect(qa.widgetOpen).toBe(false)
    expect(qa.enabled).toBe(false)
  })

  it('caches the context unless forced', async () => {
    api.get.mockResolvedValue({ data: { enabled: true, is_tester: false } })
    const qa = useQaStore()
    await qa.load()
    await qa.load()
    expect(api.get).toHaveBeenCalledTimes(1)
    await qa.load(true)
    expect(api.get).toHaveBeenCalledTimes(2)
  })
})
