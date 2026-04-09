import { describe, it, expect } from 'vitest'
import { readinessLevelBadgeClass } from './applicationReadiness'

describe('readinessLevelBadgeClass', () => {
  it('maps known levels', () => {
    expect(readinessLevelBadgeClass('ready')).toContain('success')
    expect(readinessLevelBadgeClass('blocked')).toContain('danger')
  })
})
