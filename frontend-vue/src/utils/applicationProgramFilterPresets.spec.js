import { describe, it, expect } from 'vitest'
import {
  deserializeApplicationProgramFilters,
  serializeApplicationProgramFilters,
  defaultApplicationProgramFilterState,
} from './applicationProgramFilterPresets'

describe('applicationProgramFilterPresets', () => {
  it('serializes booleans and trims strings', () => {
    expect(
      serializeApplicationProgramFilters({
        search: '  erasmus  ',
        required_language: ' English ',
        min_language_level: 'B2',
        start_date_after: '2026-01-01',
        start_date_before: '',
        min_gpa_max: '3.2',
        accepting_applications: true,
        ordering: '-start_date',
      }),
    ).toEqual({
      search: 'erasmus',
      required_language: 'English',
      min_language_level: 'B2',
      start_date_after: '2026-01-01',
      start_date_before: '',
      min_gpa_max: 3.2,
      accepting_applications: true,
      ordering: '-start_date',
    })
  })

  it('roundtrips through deserialize', () => {
    const state = {
      ...defaultApplicationProgramFilterState(),
      search: 'Asia',
      min_gpa_max: '2.5',
      accepting_applications: true,
    }
    const again = deserializeApplicationProgramFilters(serializeApplicationProgramFilters(state))
    expect(again.search).toBe('Asia')
    expect(again.min_gpa_max).toBe('2.5')
    expect(again.accepting_applications).toBe(true)
    expect(again.ordering).toBe('name')
  })
})
