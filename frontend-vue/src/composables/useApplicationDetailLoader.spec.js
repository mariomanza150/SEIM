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

vi.mock('vue-i18n', async (importOriginal) => {
  const actual = await importOriginal()
  return {
    ...actual,
    useI18n: () => ({
      t: (key) => key,
    }),
  }
})

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

  it('uses a generic error when the API response has no detail', async () => {
    mockGet.mockRejectedValue({ response: { data: {} } })
    const { error, loadApplication } = useApplicationDetailLoader()
    await expect(loadApplication()).rejects.toBeTruthy()
    expect(error.value).toBe('applicationDetailPage.loadError')
    expect(mockErrorToast).toHaveBeenCalledWith('applicationDetailPage.loadToastError')
  })

  it('softReload updates application data without flipping page error state', async () => {
    mockGet
      .mockResolvedValueOnce({ data: { id: 42, status: 'draft' } })
      .mockResolvedValueOnce({ data: { id: 42, status: 'submitted' } })
    const { application, loadApplication, softReload, error } = useApplicationDetailLoader()
    await loadApplication()
    await softReload()
    expect(application.value).toEqual({ id: 42, status: 'submitted' })
    expect(error.value).toBe('')
  })

  it('softReload returns null when the live sync request fails', async () => {
    mockGet
      .mockResolvedValueOnce({ data: { id: 42, status: 'draft' } })
      .mockRejectedValueOnce(new Error('offline'))
    const warn = vi.spyOn(console, 'warn').mockImplementation(() => {})
    const { application, loadApplication, softReload } = useApplicationDetailLoader()
    await loadApplication()
    await expect(softReload()).resolves.toBe(null)
    expect(application.value).toEqual({ id: 42, status: 'draft' })
    warn.mockRestore()
  })

  it('ignores stale softReload responses after the application id changes', async () => {
    let overrideId = '42'
    mockGet.mockImplementation(() => {
      overrideId = '99'
      return Promise.resolve({ data: { id: 42, status: 'draft' } })
    })
    const { application, softReload } = useApplicationDetailLoader(() => overrideId)
    application.value = { id: 99, status: 'submitted' }
    await expect(softReload()).resolves.toEqual({ id: 99, status: 'submitted' })
    expect(application.value).toEqual({ id: 99, status: 'submitted' })
  })
})
