import { describe, it, expect } from 'vitest'
import {
  deserializeAgreementDocumentFilters,
  deserializeCalendarFilters,
  deserializeDocumentListFilters,
  deserializeExchangeAgreementFilters,
  serializeCalendarFilters,
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

  it('roundtrips calendar filters', () => {
    const state = {
      rangeStart: '2026-01-10',
      rangeEnd: '2026-06-01',
      show: { program: true, deadline: false, application: true, agreement: false },
    }
    const raw = serializeCalendarFilters(state)
    expect(raw.range_start).toBe('2026-01-10')
    expect(raw.show_deadline).toBe(false)
    const back = deserializeCalendarFilters(raw)
    expect(back.rangeStart).toBe('2026-01-10')
    expect(back.show.deadline).toBe(false)
    expect(back.show.program).toBe(true)
  })
})
