import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useApplicationDetailLoader } from '@/composables/useApplicationDetailLoader'

const mockGet = vi.fn()
const mockErrorToast = vi.fn()

vi.mock('vue-router', () => ({
  useRoute: () => ({ params: { id: '42' } }),
}))

vi.mock('@/services/api', () => ({
  default: {
    get: (...args) => mockGet(...args),
  },
}))

vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ error: mockErrorToast }),
}))

vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key) => key,
  }),
}))

describe('useApplicationDetailLoader', () => {
  beforeEach(() => {
    mockGet.mockReset()
    mockErrorToast.mockReset()
  })

  it('loads application data', async () => {
    mockGet.mockResolvedValue({ data: { id: 42, status: 'draft' } })
    const { application, loading, loadApplication } = useApplicationDetailLoader()
    await loadApplication()
    expect(application.value).toEqual({ id: 42, status: 'draft' })
    expect(loading.value).toBe(false)
  })

  it('sets error on failure', async () => {
    mockGet.mockRejectedValue({ response: { data: { detail: 'Not found' } } })
    const { error, loadApplication } = useApplicationDetailLoader()
    await expect(loadApplication()).rejects.toBeTruthy()
    expect(error.value).toBeTruthy()
    expect(mockErrorToast).toHaveBeenCalled()
  })
})
