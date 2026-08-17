/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { useToast } from './useToast'

describe('useToast', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    useToast().toasts.value = []
  })

  afterEach(() => {
    useToast().toasts.value = []
    vi.useRealTimers()
  })

  it('shows only one toast when the same message and type are requested twice', () => {
    const { error, toasts } = useToast()
    error('Failed to load profile catalogs')
    error('Failed to load profile catalogs')
    expect(toasts.value).toHaveLength(1)
    expect(toasts.value[0].message).toBe('Failed to load profile catalogs')
    expect(toasts.value[0].type).toBe('error')
  })

  it('still shows distinct messages', () => {
    const { error, toasts } = useToast()
    error('Failed to load profile catalogs')
    error('Failed to save profile')
    expect(toasts.value).toHaveLength(2)
  })
})
