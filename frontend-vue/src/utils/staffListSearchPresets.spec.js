import { describe, it, expect } from 'vitest'
import {
  deserializeAgreementDocumentFilters,
  deserializeDocumentListFilters,
  deserializeExchangeAgreementFilters,
} from './staffListSearchPresets'

describe('staffListSearchPresets', () => {
  it('deserializes agreement filters', () => {
    const o = deserializeExchangeAgreementFilters({
      partner: 'Uni',
      expiring_within_days: '30',
      ordering: '-created_at',
    })
    expect(o.partner).toBe('Uni')
    expect(o.expiring_within_days).toBe(30)
    expect(o.ordering).toBe('-created_at')
  })

  it('deserializes document list filters', () => {
    expect(deserializeDocumentListFilters({ valid: 'true' }).valid).toBe('true')
  })

  it('deserializes agreement document filters', () => {
    expect(deserializeAgreementDocumentFilters({ current_only: true }).current_only).toBe(true)
  })
})
