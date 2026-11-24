import { describe, it, expect, vi } from 'vitest'
import { usePageState } from '@/composables/usePageState'

describe('usePageState', () => {
  it('loads data successfully', async () => {
    const fetcher = vi.fn().mockResolvedValue({ results: [1, 2] })
    const { loading, error, data, run } = usePageState(fetcher)

    expect(loading.value).toBe(false)
    const result = await run()
    expect(result).toEqual({ results: [1, 2] })
    expect(data.value).toEqual({ results: [1, 2] })
    expect(error.value).toBe('')
    expect(loading.value).toBe(false)
  })

  it('captures API errors', async () => {
    const fetcher = vi.fn().mockRejectedValue({
      response: { data: { detail: 'Not found' } },
    })
    const { error, data, run } = usePageState(fetcher, { errorFallback: 'Failed' })

    await expect(run()).rejects.toBeTruthy()
    expect(error.value).toBe('Not found')
    expect(data.value).toBeNull()
  })

  it('detects empty paginated results', async () => {
    const fetcher = vi.fn().mockResolvedValue({ results: [] })
    const state = usePageState(fetcher)
    await state.run()
    expect(state.isEmpty()).toBe(true)
  })

  it('resets state', async () => {
    const fetcher = vi.fn().mockResolvedValue([1])
    const state = usePageState(fetcher)
    await state.run()
    state.reset()
    expect(state.data.value).toBeNull()
    expect(state.error.value).toBe('')
  })

  it('calls onError callback when fetch fails', async () => {
    const onError = vi.fn()
    const fetcher = vi.fn().mockRejectedValue({ response: { data: { detail: 'Server error' } } })
    const { run } = usePageState(fetcher, { onError })

    await expect(run()).rejects.toBeTruthy()
    expect(onError).toHaveBeenCalledWith('Server error', expect.anything())
  })

  it('ignores stale success when a newer run completes first', async () => {
    let resolveSlow
    const slow = new Promise((resolve) => {
      resolveSlow = resolve
    })
    const fetcher = vi
      .fn()
      .mockImplementationOnce(() => slow)
      .mockResolvedValueOnce({ id: 'new' })

    const { data, loading, run } = usePageState(fetcher)
    const first = run()
    const second = run()
    await second
    expect(data.value).toEqual({ id: 'new' })
    expect(loading.value).toBe(false)

    resolveSlow({ id: 'stale' })
    await first
    expect(data.value).toEqual({ id: 'new' })
    expect(loading.value).toBe(false)
  })

  it('does not clear data when a stale request fails after a newer success', async () => {
    let rejectSlow
    const slowFail = new Promise((_, reject) => {
      rejectSlow = reject
    })
    const fetcher = vi
      .fn()
      .mockImplementationOnce(() => slowFail)
      .mockResolvedValueOnce({ id: 'kept' })

    const onError = vi.fn()
    const { data, error, run } = usePageState(fetcher, { onError, errorFallback: 'Failed' })
    const first = run()
    await run()
    expect(data.value).toEqual({ id: 'kept' })

    rejectSlow({ response: { data: { detail: 'stale fail' } } })
    await expect(first).rejects.toBeTruthy()
    expect(data.value).toEqual({ id: 'kept' })
    expect(error.value).toBe('')
    expect(onError).not.toHaveBeenCalled()
  })
})
