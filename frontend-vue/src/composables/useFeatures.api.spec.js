/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import api from '@/services/api'
import { useFeatures } from '@/composables/useFeatures'

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
    patch: vi.fn(),
  },
}))

describe('useFeatures composable', () => {
  beforeEach(() => {
    useFeatures()._resetFeaturesState()
    vi.clearAllMocks()
  })

  it('loads features from API (default enabled)', async () => {
    api.get.mockResolvedValueOnce({
      data: { scholarships_enabled: true, updated_at: '2026-01-01T00:00:00Z' },
    })
    const { loadFeatures, scholarshipsEnabled } = useFeatures()
    await loadFeatures(true)
    expect(api.get).toHaveBeenCalledWith('/api/features/')
    expect(scholarshipsEnabled.value).toBe(true)
  })

  it('reflects disabled scholarships_enabled', async () => {
    api.get.mockResolvedValueOnce({
      data: { scholarships_enabled: false, updated_at: '2026-01-01T00:00:00Z' },
    })
    const { loadFeatures, scholarshipsEnabled } = useFeatures()
    await loadFeatures(true)
    expect(scholarshipsEnabled.value).toBe(false)
  })

  it('fails open to enabled when API errors', async () => {
    api.get.mockRejectedValueOnce(new Error('network'))
    const { loadFeatures, scholarshipsEnabled } = useFeatures()
    await loadFeatures(true)
    expect(scholarshipsEnabled.value).toBe(true)
  })

  it('patches features via updateFeatures', async () => {
    api.patch.mockResolvedValueOnce({
      data: { scholarships_enabled: false, updated_at: '2026-01-02T00:00:00Z' },
    })
    const { updateFeatures, scholarshipsEnabled } = useFeatures()
    await updateFeatures({ scholarships_enabled: false })
    expect(api.patch).toHaveBeenCalledWith('/api/features/', { scholarships_enabled: false })
    expect(scholarshipsEnabled.value).toBe(false)
  })
})
