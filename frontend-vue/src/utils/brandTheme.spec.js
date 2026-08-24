import { describe, it, expect } from 'vitest'
import { hexToRgbTriplet } from '@/utils/brandTheme'

describe('brandTheme', () => {
  it('converts 6-digit hex to rgb triplet', () => {
    expect(hexToRgbTriplet('#2E5790')).toBe('46, 87, 144')
    expect(hexToRgbTriplet('667eea')).toBe('102, 126, 234')
  })

  it('converts 3-digit hex to rgb triplet', () => {
    expect(hexToRgbTriplet('#fff')).toBe('255, 255, 255')
  })

  it('returns null for invalid hex', () => {
    expect(hexToRgbTriplet('')).toBeNull()
    expect(hexToRgbTriplet('not-a-color')).toBeNull()
  })
})
