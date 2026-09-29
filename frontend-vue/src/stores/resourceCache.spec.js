/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useResourceCacheStore } from './resourceCache'
import api from '@/services/api'

vi.mock('@/services/api', () => ({
  default: { get: vi.fn() },
}))

describe('resourceCache store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('unwraps paginated results and caches GET payloads', async () => {
    api.get.mockResolvedValue({ data: { results: [{ id: 1 }], count: 1 } })
    const store = useResourceCacheStore()
    const rows = await store.getResults('/api/programs/', { page_size: 100 })
    expect(rows).toEqual([{ id: 1 }])
    await store.getResults('/api/programs/', { page_size: 100 })
    expect(api.get).toHaveBeenCalledTimes(1)
  })
})
